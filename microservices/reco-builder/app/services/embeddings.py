from app.models.bert_model import bert_model
from app.models.vector_index import vector_index
from app.models.domain import Resource
from sqlalchemy.orm import Session

class EmbeddingService:
    def rebuild_index(self, db: Session):
        print("Rebuilding Faiss index...")
        resources = db.query(Resource).all()
        if not resources:
            print("No resources found in DB to index.")
            vector_index.reset()
            return

        descriptions = [r.description for r in resources]
        embeddings = bert_model.encode(descriptions)
        
        vector_index.reset()
        vector_index.add_embeddings(embeddings, [r.id for r in resources])
        print(f"Indexed {len(resources)} resources.")

embedding_service = EmbeddingService()
