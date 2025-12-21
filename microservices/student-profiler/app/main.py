from fastapi import FastAPI
from app.api import endpoints
from app.core.database import engine, Base
import logging
import uvicorn

# Initialize Logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# Create Database Tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="StudentProfiler Microservice",
    description="API for analyzing student behavior and clustering profiles.",
    version="1.0.0"
)

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "StudentProfiler"}

app.include_router(endpoints.router)

# For debugging locally via python app/main.py
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
