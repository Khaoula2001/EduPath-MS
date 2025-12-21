
import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PG_USER: str = os.getenv("PG_USER", "prepadata")
    PG_PASSWORD: str = os.getenv("PG_PASSWORD", "prepadata_pwd")
    PG_HOST: str = os.getenv("PG_HOST", "localhost")
    PG_PORT: str = os.getenv("PG_PORT", "5432")
    PG_DB: str = os.getenv("PG_DB", "analytics")

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.PG_USER}:{self.PG_PASSWORD}@{self.PG_HOST}:{self.PG_PORT}/{self.PG_DB}"

    MODEL_FILENAME: str = "student_profiler_model.joblib"
    
    class Config:
        env_file = ".env"

settings = Settings()
