from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.schemas.recommendation import RecommendationRequest, RecommendationResponse, ResourceCreate, ResourceRead
from app.services.recommender import recommender_service
from app.services.embeddings import embedding_service
from app.services.storage import storage_service
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

@router.post("/resources")
async def add_resource(
    title: str = Form(...),
    description: str = Form(...),
    type: str = Form(...),
    tags: Optional[str] = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # 1. Upload file to MinIO
    file_content = await file.read()
    file_url = storage_service.upload_file(
        file_content, 
        file.filename, 
        file.content_type
    )

    # 2. Save to Postgres
    new_res = Resource(
        title=title,
        description=description,
        type=type,
        url=file_url,
        tags=tags
    )
    db.add(new_res)
    db.commit()
    db.refresh(new_res)
    
    # 3. Rebuild index
    embedding_service.rebuild_index(db)
    
    return {"message": "Resource added with file", "id": str(new_res.id), "url": file_url}

@router.delete("/resources/{resource_id}", response_model=dict)
def delete_resource(resource_id: str, db: Session = Depends(get_db)):
    # 1. Find resource in DB
    res = db.query(Resource).filter(Resource.id == resource_id).first()
    if not res:
        raise HTTPException(status_code=404, detail="Resource not found")

    # 2. Delete from MinIO if URL exists
    if res.url:
        try:
            # Extract filename from URL (http://endpoint/bucket/filename)
            filename = res.url.split("/")[-1]
            storage_service.delete_file(filename)
        except Exception as e:
            print(f"Error deleting from MinIO: {e}")
            # We continue even if MinIO fails, to keep DB in sync

    # 3. Delete from Postgres
    db.delete(res)
    db.commit()

    # 4. Rebuild index
    embedding_service.rebuild_index(db)

    return {"message": "Resource deleted successfully", "id": resource_id}

@router.get("/resources", response_model=List[ResourceRead])
def get_resources(db: Session = Depends(get_db)):
    resources = db.query(Resource).all()
    return resources

@router.get("/health")
def health():
    return {"status": "ok", "index_size": vector_index.ntotal}
