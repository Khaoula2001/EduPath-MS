from minio import Minio
from app.core.config import settings
import io

class StorageService:
    def __init__(self):
        self.client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE
        )
        self._ensure_bucket_exists()

    def _ensure_bucket_exists(self):
        if not self.client.bucket_exists(settings.MINIO_BUCKET_NAME):
            self.client.make_bucket(settings.MINIO_BUCKET_NAME)

    def upload_file(self, file_data: bytes, file_name: str, content_type: str):
        data_stream = io.BytesIO(file_data)
        self.client.put_object(
            settings.MINIO_BUCKET_NAME,
            file_name,
            data_stream,
            length=len(file_data),
            content_type=content_type
        )
        return f"http://{settings.MINIO_ENDPOINT}/{settings.MINIO_BUCKET_NAME}/{file_name}"

    def get_presigned_url(self, file_name: str):
        return self.client.presigned_get_object(
            settings.MINIO_BUCKET_NAME,
            file_name
        )

    def delete_file(self, file_name: str):
        self.client.remove_object(
            settings.MINIO_BUCKET_NAME,
            file_name
        )

storage_service = StorageService()
