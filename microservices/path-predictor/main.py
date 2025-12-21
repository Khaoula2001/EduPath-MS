from fastapi import FastAPI
import os

app = FastAPI(title="PathPredictor API")

@app.get("/")
def read_root():
    return {"service": "PathPredictor", "status": "running"}

@app.get("/health")
def health_check():
    return {"status": "ok"}
