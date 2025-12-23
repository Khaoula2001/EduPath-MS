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
    # Simulation d'alertes plus riches pour le frontend
    alerts = [
        {
            "id": 1,
            "student_name": "Mohamed Chakir",
            "type": "Performance",
            "message": "Note inférieure à 60% - Intervention recommandée",
            "priority": "Urgent",
            "date": "2025-12-19",
            "note": "58%",
            "presence": "65%"
        },
        {
            "id": 2,
            "student_name": "Hamza Benjelloun",
            "type": "Absence",
            "message": "Taux de présence faible (60%) - Contact nécessaire",
            "priority": "Urgent",
            "date": "2025-12-18",
            "note": "55%",
            "presence": "60%"
        },
        {
            "id": 3,
            "student_name": "Amine Fassi",
            "type": "Engagement",
            "message": "Engagement en baisse - Suivi recommandé",
            "priority": "Moyen",
            "date": "2025-12-17",
            "note": "62%",
            "presence": "70%"
        },
        {
            "id": 4,
            "student_name": "Khawla Idrissi",
            "type": "Performance",
            "message": "Performance en baisse légère",
            "priority": "Moyen",
            "date": "2025-12-16",
            "note": "72%",
            "presence": "85%"
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

@app.get("/performance-data")
def get_performance_data(db: Session = Depends(get_db)):
    return {
        "labels": ["Sem 1", "Sem 2", "Sem 3", "Sem 4", "Sem 5", "Sem 6", "Sem 7", "Sem 8"],
        "moyenne": [65, 68, 70, 73, 75, 78, 80, 80],
        "engagement": [70, 72, 75, 78, 82, 86, 88, 90],
        "presence": [85, 88, 86, 92, 90, 94, 96, 97]
    }

@app.get("/profiles-distribution")
def get_profiles_distribution(db: Session = Depends(get_db)):
    return [
        {"label": "Assidu", "value": 42, "color": "#10b981", "type": "assidu"},
        {"label": "Irrégulier", "value": 8, "color": "#8b5cf6", "type": "irregulier"},
        {"label": "Moyen", "value": 33, "color": "#f59e0b", "type": "moyen"},
        {"label": "Procrastinateur", "value": 17, "color": "#ef4444", "type": "procrastinateur"}
    ]

@app.get("/grades-distribution")
def get_grades_distribution(db: Session = Depends(get_db)):
    return [
        {"label": "0-50", "value": 1},
        {"label": "50-60", "value": 2},
        {"label": "60-70", "value": 3},
        {"label": "70-80", "value": 5},
        {"label": "80-90", "value": 4},
        {"label": "90-100", "value": 2}
    ]

@app.get("/risk-heatmap")
def get_risk_heatmap(db: Session = Depends(get_db)):
    return [
        {"name": "Omar El Fassi", "riskLevel": "low", "riskScore": 12},
        {"name": "Nisrine Alami", "riskLevel": "low", "riskScore": 18},
        {"name": "Salma Bennani", "riskLevel": "low", "riskScore": 22},
        {"name": "Rim Alaoui", "riskLevel": "medium", "riskScore": 45},
        {"name": "Amine Tazi", "riskLevel": "medium", "riskScore": 48},
        {"name": "Youssef Idrissi", "riskLevel": "high", "riskScore": 72},
        {"name": "Fatima Zahra", "riskLevel": "high", "riskScore": 78},
        {"name": "Mohamed Chakir", "riskLevel": "critical", "riskScore": 88},
        {"name": "Anas Moussaoui", "riskLevel": "critical", "riskScore": 92},
        {"name": "Karim Teral", "riskLevel": "medium", "riskScore": 55},
    ]
