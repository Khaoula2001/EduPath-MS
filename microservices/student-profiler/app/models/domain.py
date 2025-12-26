from sqlalchemy import Column, Integer, String, DateTime, Float
from sqlalchemy.sql import func
from app.core.database import Base

class StudentProfile(Base):
    __tablename__ = "student_profiles"

    student_id = Column(String, primary_key=True, index=True)
    cluster_id = Column(Integer, nullable=False)
    profil_type = Column(String, nullable=True)
    mean_score = Column(Float, default=0.0)
    progress_rate = Column(Float, default=0.0)
    risk_level = Column(String, default="Low")
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
