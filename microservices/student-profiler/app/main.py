from fastapi import FastAPI
from app.api import endpoints
from app.core.database import engine, Base
import logging
import uvicorn
import py_eureka_client.eureka_client as eureka_client
import os

# Initialize Logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# Create Database Tables
try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    logging.error(f"Could not create database tables: {e}")

app = FastAPI(
    title="Student Profiler",
    version="1.0.0"
)

# Eureka Configuration
EUREKA_SERVER = os.getenv("EUREKA_SERVER", "http://eureka-server:8761/eureka")
INSTANCE_HOST = os.getenv("INSTANCE_HOST", "student-profiler")
INSTANCE_PORT = int(os.getenv("INSTANCE_PORT", "8000"))

async def init_eureka():
    await eureka_client.init_async(
        eureka_server=EUREKA_SERVER,
        app_name="student-profiler",
        instance_port=INSTANCE_PORT,
        instance_host=INSTANCE_HOST
    )

@app.on_event("startup")
async def startup_event():
    logging.info("Initializing Eureka client...")
    await init_eureka()

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "StudentProfiler"}

app.include_router(endpoints.router)

import threading
from app.services.consumer import start_consumer

# ... (rest of the imports)

# Start RabbitMQ consumer in a background thread
def run_consumer():
    logging.info("Starting RabbitMQ consumer thread...")
    start_consumer()

consumer_thread = threading.Thread(target=run_consumer, daemon=True)
consumer_thread.start()

# For debugging locally via python app/main.py
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
