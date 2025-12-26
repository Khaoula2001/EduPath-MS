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

from app.models.domain import StudentProfile

@router.get("/profile/{student_id}")
def get_student_profile(student_id: str, db: Session = Depends(get_db)):
    """
    Retrieves the profile for a specific student from the database.
    """
    profile = db.query(StudentProfile).filter(StudentProfile.student_id == student_id).first()
    
    if profile:
        return {
            "student_id": profile.student_id,
            "mean_score": profile.mean_score,
            "progress_rate": profile.progress_rate,
            "cluster_id": profile.cluster_id,
            "profile_name": profile.profil_type,
            "risk_level": profile.risk_level
        }
    
    # Fallback for unknown students (or those not yet analyzed)
    return {
        "student_id": student_id,
        "mean_score": 0.0,
        "progress_rate": 0.0,
        "cluster_id": -1,
        "profile_name": "Non démarré (Not Started)",
        "risk_level": "High"
    }
