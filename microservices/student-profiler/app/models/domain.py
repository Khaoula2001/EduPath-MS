from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.core.database import Base

class StudentProfile(Base):
    __tablename__ = "student_profiles"

    student_id = Column(Integer, primary_key=True, index=True)
    cluster_id = Column(Integer, nullable=False)
    profil_type = Column(String, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
