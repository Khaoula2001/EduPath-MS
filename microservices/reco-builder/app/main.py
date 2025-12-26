from fastapi import FastAPI
import py_eureka_client.eureka_client as eureka_client
import os
from app.api import endpoints
from app.core.database import SessionLocal, Base, engine
from app.services.embeddings import embedding_service
import uvicorn
import threading
import logging

logger = logging.getLogger(__name__)

app = FastAPI(title="RecommendationBuilder API", version="2.0.0")

# Eureka Configuration
EUREKA_SERVER = os.getenv("EUREKA_SERVER", "http://eureka-server:8761/eureka")
INSTANCE_HOST = os.getenv("INSTANCE_HOST", "reco-builder")
INSTANCE_PORT = int(os.getenv("INSTANCE_PORT", "8003"))

@app.on_event("startup")
async def startup_event():
    print("Initializing Eureka client...")
    await eureka_client.init_async(
        eureka_server=EUREKA_SERVER,
        app_name="reco-builder",
        instance_port=INSTANCE_PORT,
        instance_host=INSTANCE_HOST
    )

# Create tables
Base.metadata.create_all(bind=engine)

# Initial index build
db = SessionLocal()
try:
    embedding_service.rebuild_index(db)
finally:
    db.close()

app.include_router(endpoints.router)

# Start RabbitMQ consumer in background
def run_consumer():
    try:
        from app.services.consumer import start_consumer
        logger.info("Starting RabbitMQ consumer for RecoBuilder...")
        start_consumer()
    except Exception as e:
        logger.error(f"Failed to start RabbitMQ consumer: {e}")

consumer_thread = threading.Thread(target=run_consumer, daemon=True)
consumer_thread.start()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8003)
