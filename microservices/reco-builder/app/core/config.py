import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PG_USER: str = os.getenv("PG_USER", "prepadata")
    PG_PASSWORD: str = os.getenv("PG_PASSWORD", "prepadata_pwd")
    PG_HOST: str = os.getenv("PG_HOST", "postgres")
    PG_PORT: str = os.getenv("PG_PORT", "5432")
    PG_DB: str = os.getenv("PG_DB", "analytics")

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.PG_USER}:{self.PG_PASSWORD}@{self.PG_HOST}:{self.PG_PORT}/{self.PG_DB}"

    BERT_MODEL_NAME: str = "all-MiniLM-L6-v2"
    FAISS_DIMENSION: int = 384

    # MinIO Settings
    MINIO_ENDPOINT: str = os.getenv("MINIO_ENDPOINT", "minio:9000")
    MINIO_ACCESS_KEY: str = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
    MINIO_SECRET_KEY: str = os.getenv("MINIO_SECRET_KEY", "minioadminpassword")
    MINIO_BUCKET_NAME: str = os.getenv("MINIO_BUCKET_NAME", "resources")
    MINIO_SECURE: bool = os.getenv("MINIO_SECURE", "False").lower() == "true"

settings = Settings()
