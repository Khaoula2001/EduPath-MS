from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
import os
import random

app = FastAPI(title="PathPredictor API")

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
