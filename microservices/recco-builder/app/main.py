from fastapi import FastAPI
from app.api import endpoints
from app.core.database import SessionLocal, Base, engine
from app.services.embeddings import embedding_service
import uvicorn

app = FastAPI(title="RecoBuilder API", version="2.0.0")

# Create tables
Base.metadata.create_all(bind=engine)

# Initial index build
db = SessionLocal()
try:
    embedding_service.rebuild_index(db)
finally:
    db.close()

app.include_router(endpoints.router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8003)
