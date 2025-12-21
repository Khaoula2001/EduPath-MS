from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class StudentFeatures(BaseModel):
    student_id: int
    total_clicks: int
    assessment_submissions_count: int
    mean_score: float
    active_days: int
    study_duration: float
    progress_rate: float

    class Config:
        from_attributes = True

class PredictionResult(BaseModel):
    student_id: int
    cluster_id: int
    profil_type: Optional[str] = None
    timestamp: datetime

    class Config:
        from_attributes = True
