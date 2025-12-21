from fastapi import FastAPI

app = FastAPI(title="StudentCoach API")

@app.get("/")
def read_root():
    return {"service": "StudentCoach API", "status": "running"}

@app.get("/health")
def health_check():
    return {"status": "ok"}
