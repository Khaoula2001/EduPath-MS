from fastapi import FastAPI

app = FastAPI(title="TeacherConsole API")

@app.get("/")
def read_root():
    return {"service": "TeacherConsole API", "status": "running"}

@app.get("/health")
def health_check():
    return {"status": "ok"}
