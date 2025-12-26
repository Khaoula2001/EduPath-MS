from minio import Minio
import uuid

minio_client = Minio(
    "minio:9000",
    access_key="minioadmin",
    secret_key="minioadminpassword",
    secure=False
)

BUCKET = "resources"

# Create bucket if not exists
if not minio_client.bucket_exists(BUCKET):
    minio_client.make_bucket(BUCKET)

def upload_to_minio(file_bytes: bytes, filename: str) -> str:
    object_name = f"{uuid.uuid4().hex}_{filename}"

    minio_client.put_object(
        BUCKET, object_name,
        data=file_bytes,
        length=len(file_bytes),
        content_type="application/octet-stream"
    )

    return f"http://localhost:9000/{BUCKET}/{object_name}"
