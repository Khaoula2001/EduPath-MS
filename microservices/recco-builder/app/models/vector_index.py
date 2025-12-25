import faiss
import numpy as np
from app.core.config import settings

class VectorIndex:
    def __init__(self):
        self.index = faiss.IndexFlatL2(settings.FAISS_DIMENSION)
        self.resource_ids = []

    def reset(self, dimension=None):
        dim = dimension or settings.FAISS_DIMENSION
        self.index = faiss.IndexFlatL2(dim)
        self.resource_ids = []

    def add_embeddings(self, embeddings, ids):
        self.index.add(np.array(embeddings).astype('float32'))
        self.resource_ids.extend([str(i) for i in ids])

    def search(self, query_vector, top_k):
        if self.index.ntotal == 0:
            return [], []
        distances, indices = self.index.search(np.array(query_vector).astype('float32'), top_k)
        return distances[0], indices[0]

    @property
    def ntotal(self):
        return self.index.ntotal

vector_index = VectorIndex()
