from pydantic import BaseModel, HttpUrl
from typing import List, Optional
from uuid import UUID

class ResourceBase(BaseModel):
    title: str
    description: str
    type: Optional[str] = 'other'
    url: Optional[str] = ''
    tags: Optional[str] = ''

class ResourceCreate(ResourceBase):
    pass

class ResourceRead(ResourceBase):
    id: UUID

    class Config:
        from_attributes = True

class RecommendationRequest(BaseModel):
    query: str
    top_k: Optional[int] = 3
    student_id: Optional[str] = None
    student_profile: Optional[str] = None
    risk_level: Optional[str] = None

class Recommendation(BaseModel):
    id: str
    title: str
    type: Optional[str]
    url: Optional[str]
    distance: float
    relevance_boosted: bool

class RecommendationResponse(BaseModel):
    student_id: Optional[str]
    recommendations: List[Recommendation]
    metadata: dict
