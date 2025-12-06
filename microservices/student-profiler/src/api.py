# ...existing code...
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
from . import service

app = FastAPI(title='Student Profiler')

class TrainResponse(BaseModel):
    status: str
    n_students: int
    artifact: str | None = None
    n_clusters: int | None = None


@app.post('/train', response_model=TrainResponse)
async def train():
    try:
        result = service.train_and_persist()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return result


@app.get('/profiles/{student_id}')
async def get_profile(student_id: str):
    p = service.get_latest_profile(student_id)
    if p is None:
        raise HTTPException(status_code=404, detail='Profile not found')
    return p

# ...existing code...
