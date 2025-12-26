from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
import os
import random
import py_eureka_client.eureka_client as eureka_client

app = FastAPI(title="PathPredictor API")

# Eureka Configuration
EUREKA_SERVER = os.getenv("EUREKA_SERVER", "http://eureka-server:8761/eureka")
INSTANCE_HOST = os.getenv("INSTANCE_HOST", "path-predictor")
INSTANCE_PORT = int(os.getenv("INSTANCE_PORT", "8002"))

@app.on_event("startup")
async def startup_event():
    print("Initializing Eureka client...")
    await eureka_client.init_async(
        eureka_server=EUREKA_SERVER,
        app_name="path-predictor",
        instance_port=INSTANCE_PORT,
        instance_host=INSTANCE_HOST
    )

class StudentFeatures(BaseModel):
    student_id: str
    features: Dict[str, Any]

@app.get("/")
def read_root():
    return {"service": "PathPredictor", "status": "running"}

@app.post("/predict")
def predict_path(data: StudentFeatures):
    # This is a placeholder for the XGBoost model logic
    # In a real scenario, we would load the MLflow model and predict
    
    # Mocking logic for now
    risk_score = random.uniform(0, 1)
    risk_level = "Low"
    if risk_score > 0.7:
        risk_level = "High"
    elif risk_score > 0.4:
        risk_level = "Medium"
        
    return {
        "student_id": data.student_id,
        "risk_score": round(risk_score, 2),
        "risk_level": risk_level,
        "recommendation_priority": "High" if risk_level == "High" else "Normal"
    }

@app.get("/health")
def health_check():
    return {"status": "ok"}
