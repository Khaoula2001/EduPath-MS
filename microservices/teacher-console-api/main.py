from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

app = FastAPI(title="TeacherConsole API")

# Database configuration
DATABASE_URL = f"postgresql://{os.getenv('PG_USER', 'prepadata')}:{os.getenv('PG_PASSWORD', 'prepadata_pwd')}@{os.getenv('PG_HOST', 'postgres')}:{os.getenv('PG_PORT', 5432)}/{os.getenv('PG_DB', 'teacher_db')}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"service": "TeacherConsole API", "status": "running"}

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/alerts")
def get_alerts(db: Session = Depends(get_db)):
    # Simuler des alertes basées sur les données réelles (normalement viendrait du PathPredictor ou d'une table dédiée)
    # Ici on fait un mock pour le dashboard
    alerts = [
        {
            "id": 1,
            "student_name": "Mohamed Chakir",
            "type": "Performance",
            "message": "Note inférieure à 60% - Intervention recommandée",
            "priority": "Urgent",
            "date": "2025-12-19"
        },
        {
            "id": 2,
            "student_name": "Hamza Benjelloun",
            "type": "Absence",
            "message": "Taux de présence faible (60%) - Contact nécessaire",
            "priority": "Urgent",
            "date": "2025-12-18"
        }
    ]
    return alerts

@app.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    return {
        "total_students": 150,
        "at_risk_students": 12,
        "average_engagement": "78%",
        "active_courses": 5
    }
