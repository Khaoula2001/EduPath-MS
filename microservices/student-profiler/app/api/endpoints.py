from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.pydantic_models import StudentFeatures, PredictionResult
from app.services.profiler import profiling_service
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/predict_clusters", response_model=PredictionResult, status_code=status.HTTP_200_OK)
def predict_clusters(features: StudentFeatures, db: Session = Depends(get_db)):
    """
    Receives student features, applies the ML pipeline, updates the database, 
    and returns the predicted cluster profile.
    """
    try:
        result = profiling_service.predict_profile(features, db)
        return result
    except ValueError as ve:
        logger.error(f"Validation Error: {ve}")
        raise HTTPException(status_code=503, detail=str(ve))
    except Exception as e:
        logger.error(f"Internal Server Error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error during prediction.")

@router.get("/profile/{student_id}")
def get_student_profile(student_id: int, db: Session = Depends(get_db)):
    """
    Retrieves the profile for a specific student.
    """
    # This is a mock implementation. In a real scenario, you would query the database.
    # For now, we return mock data to satisfy the path-predictor service.
    return {
        "student_id": student_id,
        "mean_score": 75.5,
        "progress_rate": 0.65,
        "cluster_id": 2,
        "profile_name": "Balanced"
    }
