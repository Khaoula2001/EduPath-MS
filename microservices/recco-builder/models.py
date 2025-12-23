from sqlalchemy import Column, String, Text, UUID
from sqlalchemy.ext.declarative import declarative_base
import uuid

Base = declarative_base()

class Resource(Base):
    __tablename__ = 'resources'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    type = Column(String(50))  # e.g., 'video', 'pdf', 'exercise'
    url = Column(Text)         # Link to MinIO or external
    tags = Column(String(255)) # Comma separated tags
