from sqlalchemy.orm import Session
import numpy as np
from app.models.vector_index import vector_index
from app.models.bert_model import bert_model
from app.models.domain import Resource
from app.services.student_context import student_context_service

class RecommenderService:
    def get_recommendations(self, db: Session, query: str, top_k: int, student_id: str = None, student_profile: str = None, risk_level: str = None):
        if vector_index.ntotal == 0:
            return [], query, query

        augmented_query = student_context_service.augment_query(query, student_profile, risk_level)
        
        # Encode query
        query_vector = bert_model.encode([augmented_query])
        
        # Search
        distances, indices = vector_index.search(query_vector, top_k)
        
        recommendations = []
        for i, idx in enumerate(indices):
            if idx != -1 and idx < len(vector_index.resource_ids):
                res_id = vector_index.resource_ids[idx]
                res = db.query(Resource).filter(Resource.id == res_id).first()
                if res:
                    recommendations.append({
                        "id": str(res.id),
                        "title": res.title,
                        "type": res.type,
                        "url": res.url,
                        "distance": float(distances[i]),
                        "relevance_boosted": augmented_query != query
                    })
        
        return recommendations, augmented_query

recommender_service = RecommenderService()
