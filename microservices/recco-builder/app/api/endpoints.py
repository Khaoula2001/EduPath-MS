from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.schemas.recommendation import RecommendationRequest, RecommendationResponse, ResourceCreate, ResourceRead
from app.services.recommender import recommender_service
from app.services.embeddings import embedding_service
from app.models.domain import Resource
from app.models.vector_index import vector_index

router = APIRouter()

@router.post("/recommend", response_model=RecommendationResponse)
def recommend(request: RecommendationRequest, db: Session = Depends(get_db)):
    if vector_index.ntotal == 0:
        raise HTTPException(status_code=404, detail="Index is empty. No resources available.")
    
    recommendations, augmented_query = recommender_service.get_recommendations(
        db, 
        request.query, 
        request.top_k, 
        request.student_id, 
        request.student_profile, 
        request.risk_level
    )
    
    return {
        "student_id": request.student_id,
        "recommendations": recommendations,
        "metadata": {
            "profile_used": request.student_profile,
            "risk_used": request.risk_level,
            "augmented_query": augmented_query
        }
    }

@router.post("/resources", response_model=dict)
def add_resource(resource: ResourceCreate, db: Session = Depends(get_db)):
    new_res = Resource(
        title=resource.title,
        description=resource.description,
        type=resource.type,
        url=resource.url,
        tags=resource.tags
    )
    db.add(new_res)
    db.commit()
    db.refresh(new_res)
    
    # Rebuild index
    embedding_service.rebuild_index(db)
    
    return {"message": "Resource added", "id": str(new_res.id)}

@router.get("/health")
def health():
    return {"status": "ok", "index_size": vector_index.ntotal}
