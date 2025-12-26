from sentence_transformers import SentenceTransformer
from app.core.config import settings

class BertModelHolder:
    def __init__(self):
        print(f"Loading BERT model: {settings.BERT_MODEL_NAME}...")
        self.model = SentenceTransformer(settings.BERT_MODEL_NAME)

    def encode(self, texts):
        return self.model.encode(texts)

bert_model = BertModelHolder()
