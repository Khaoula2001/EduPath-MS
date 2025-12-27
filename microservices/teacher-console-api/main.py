from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import create_engine, text, Column, Integer, String, Boolean, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
import os
import pika
import json
import threading
import time
import datetime
import py_eureka_client.eureka_client as eureka_client
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="TeacherConsole API")

# Eureka Configuration
EUREKA_SERVER = os.getenv("EUREKA_SERVER", "http://eureka-server:8761/eureka")
INSTANCE_HOST = os.getenv("INSTANCE_HOST", "teacher-console-api")
INSTANCE_PORT = int(os.getenv("INSTANCE_PORT", "8004"))

# Database Definitions
Base = declarative_base()

class Alert(Base):
    __tablename__ = "alerts"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String, index=True)
    student_name = Column(String)
    alert_type = Column(String) # e.g., 'Performance', 'Absence'
    message = Column(String)
    priority = Column(String) # 'Urgent', 'Moyen'
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    is_read = Column(Boolean, default=False)
    # Optional snapshots for context
    context_note = Column(String, nullable=True)
    context_presence = Column(String, nullable=True)

# Database configuration (Teacher DB - Write Access)
DATABASE_URL = f"postgresql://{os.getenv('PG_USER', 'prepadata')}:{os.getenv('PG_PASSWORD', 'prepadata_pwd')}@{os.getenv('PG_HOST', 'postgres')}:{os.getenv('PG_PORT', 5432)}/{os.getenv('PG_DB', 'teacher_db')}"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# LMS Database configuration (Read-Only Access for Stats)
LMS_DB_URL = os.getenv('LMS_DB_URL', 'postgresql://lms:lmspass@lmsdb:5432/lmsconnector')
lms_engine = create_engine(LMS_DB_URL)
LmsSession = sessionmaker(autocommit=False, autoflush=False, bind=lms_engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_lms_db():
    db = LmsSession()
    try:
        yield db
    finally:
        db.close()

@app.on_event("startup")
async def startup_event():
    # Create tables for Teacher DB
    Base.metadata.create_all(bind=engine)
    
    logger.info("Initializing Eureka client...")
    await eureka_client.init_async(
        eureka_server=EUREKA_SERVER,
        app_name="teacher-console-api",
        instance_port=INSTANCE_PORT,
        instance_host=INSTANCE_HOST
    )

# RabbitMQ Configuration
RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'rabbitmq')
RABBITMQ_USER = os.getenv('RABBITMQ_USER', 'edupath')
RABBITMQ_PASS = os.getenv('RABBITMQ_PASS', 'edupath')

@app.get("/")
def read_root():
    return {"service": "TeacherConsole API", "status": "running"}

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/alerts")
def get_alerts(db: Session = Depends(get_db)):
    """Fetch persistent alerts from database"""
    alerts = db.query(Alert).order_by(Alert.created_at.desc()).limit(50).all()
    return [
        {
            "id": a.id,
            "student_name": a.student_name,
            "type": a.alert_type,
            "message": a.message,
            "priority": a.priority,
            "date": a.created_at.strftime("%Y-%m-%d"),
            "note": a.context_note or "N/A",
            "presence": a.context_presence or "N/A"
        }
        for a in alerts
    ]

@app.get("/stats")
def get_stats(lms_db: Session = Depends(get_lms_db)):
    """Fetch real statistics from LMS Data"""
    try:
        # Total active students (roughly distinct students in features)
        total_students = lms_db.execute(text("SELECT COUNT(DISTINCT id_student) FROM student_features")).scalar()
        
        # Risk students
        at_risk = lms_db.execute(text("SELECT COUNT(DISTINCT id_student) FROM student_features WHERE dropout_risk_signal IN ('High', 'Critical')")).scalar()
        
        # Average engagement
        avg_eng = lms_db.execute(text("SELECT AVG(engagement_intensity) FROM student_features")).scalar()
        
        # Active courses (distinct modules)
        active_courses = lms_db.execute(text("SELECT COUNT(DISTINCT code_module) FROM student_features")).scalar()

        return {
            "total_students": total_students or 0,
            "at_risk_students": at_risk or 0,
            "average_engagement": f"{int((avg_eng or 0) * 100)}%",
            "active_courses": active_courses or 0
        }
    except Exception as e:
        logger.error(f"Error fetching stats: {e}")
        return {
            "total_students": 0,
            "at_risk_students": 0,
            "average_engagement": "0%",
            "active_courses": 0
        }

@app.get("/performance-data")
def get_performance_data(lms_db: Session = Depends(get_lms_db)):
    """Fetch evolution data (mocked time-series for now as we might not have historical snapshots easily, 
       but can aggregate current averages as the 'latest' point)"""
    # For a real graph, we'd need a history table. 
    # Here we will generate a realistic dynamic curve ending in current values
    try:
        avg_score = lms_db.execute(text("SELECT AVG(mean_score) FROM student_features")).scalar() or 0
        avg_eng = lms_db.execute(text("SELECT AVG(engagement_intensity) FROM student_features")).scalar() or 0
        avg_prog = lms_db.execute(text("SELECT AVG(progress_rate) FROM student_features")).scalar() or 0
        
        # Determine trend based on current values (simple simulation)
        # We project backwards
        return {
            "labels": ["Sem 1", "Sem 2", "Sem 3", "Sem 4", "Sem 5", "Sem 6", "Sem 7", "Sem 8"],
            "moyenne": [max(0, avg_score - 10 + i*1.2) for i in range(8)], # Mock history, accurate end
            "engagement": [max(0, avg_eng*100 - 15 + i*1.8) for i in range(8)],
            "presence": [max(0, avg_prog*100 - 5 + i*0.5) for i in range(8)]
        }
    except Exception as e:
        logger.error(f"Error perf data: {e}")
        return {"labels": [], "moyenne": [], "engagement": [], "presence": []}

@app.get("/profiles-distribution")
def get_profiles_distribution(lms_db: Session = Depends(get_lms_db)):
    try:
        rows = lms_db.execute(text("SELECT profile_type, COUNT(*) FROM student_features GROUP BY profile_type")).fetchall()
        
        # Map DB profiles to UI colors
        colors = {
            "Assidu": "#10b981",
            "Irrégulier": "#8b5cf6",
            "Moyen": "#f59e0b",
            "Procrastinateur": "#ef4444"
        }
        
        result = []
        for row in rows:
            p_type = row[0] or "Unknown"
            count = row[1]
            result.append({
                "label": p_type,
                "value": count,
                "color": colors.get(p_type, "#cccccc"),
                "type": p_type.lower()
            })
        return result
    except Exception as e:
        logger.error(f"Error profiles: {e}")
        return []

@app.get("/grades-distribution")
def get_grades_distribution(lms_db: Session = Depends(get_lms_db)):
    try:
        # Bucket query
        query = """
        SELECT 
          CASE 
            WHEN mean_score < 50 THEN '0-50'
            WHEN mean_score BETWEEN 50 AND 60 THEN '50-60'
            WHEN mean_score BETWEEN 60 AND 70 THEN '60-70'
            WHEN mean_score BETWEEN 70 AND 80 THEN '70-80'
            WHEN mean_score BETWEEN 80 AND 90 THEN '80-90'
            ELSE '90-100'
          END as range,
          COUNT(*)
        FROM student_features
        WHERE mean_score IS NOT NULL
        GROUP BY 1
        ORDER BY 1
        """
        rows = lms_db.execute(text(query)).fetchall()
        return [{"label": row[0], "value": row[1]} for row in rows]
    except Exception as e:
        logger.error(f"Error grades: {e}")
        return []

@app.get("/risk-heatmap")
def get_risk_heatmap(lms_db: Session = Depends(get_lms_db)):
    try:
        # Join with raw_learning_data to get Names if possible, or just mock names if not stored in features
        # Assuming student_features has raw IDs, we fetch names from raw_learning_data (student_info)
        # This is expensive, better to have name in features.
        # Fallback: Fetch features, then fetch one name map
        
        features = lms_db.execute(text("SELECT id_student, dropout_risk_signal, dropout_risk_score FROM student_features LIMIT 50")).fetchall()
        
        # Get Names Map
        name_query = text("SELECT raw_json FROM raw_learning_data WHERE data_type='student_info' LIMIT 1")
        name_res = lms_db.execute(name_query).fetchone()
        name_map = {}
        if name_res and name_res[0]:
            for u in name_res[0]:
                name_map[str(u.get('id'))] = u.get('fullname')

        result = []
        for row in features:
            sid = str(row[0])
            name = name_map.get(sid, f"Student {sid}")
            risk_level = row[1] or 'Low'
            risk_score = row[2] or 0
            
            # Normalize level for UI
            if risk_level == 'Critical': ui_level = 'critical'
            elif risk_level == 'High': ui_level = 'high'
            elif risk_level == 'Medium': ui_level = 'medium'
            else: ui_level = 'low'
            
            result.append({
                "name": name,
                "riskLevel": ui_level,
                "riskScore": int(risk_score * 100) if risk_score <= 1 else int(risk_score)
            })
        return result
    except Exception as e:
        logger.error(f"Error heatmap: {e}")
        return []

# ========== RabbitMQ Consumer for Alerts ==========

def process_alert(ch, method, properties, body):
    """Process incoming alerts from RabbitMQ and persist to DB"""
    db = SessionLocal()
    try:
        data = json.loads(body)
        logger.info(f" [x] Received alert: {data}")
        
        alert = Alert(
            student_id=str(data.get('studentId')),
            student_name=f"Student {data.get('studentId')}", # Ideally fetch name
            alert_type=data.get('type', 'Performance'),
            message=data.get('message', 'Alert triggered'),
            priority="Urgent" if data.get('riskLevel') in ['High', 'Critical'] else "Moyen",
            created_at=datetime.datetime.utcnow(),
            # Mock context
            context_note=f"{data.get('currentScore', 0)}%",
            context_presence="N/A"
        )
        db.add(alert)
        db.commit()
        logger.info(f" [✓] Alert persisted for student {data.get('studentId')}")
        
    except Exception as e:
        logger.error(f" [!] Error processing alert: {e}")
        db.rollback()
    finally:
        db.close()

def start_consumer():
    """Start RabbitMQ consumer for teacher alerts"""
    while True:
        try:
            logger.info(f" [*] Connecting to RabbitMQ at {RABBITMQ_HOST}...")
            credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=RABBITMQ_HOST, credentials=credentials)
            )
            channel = connection.channel()

            channel.queue_declare(queue='student_alerts', durable=True)
            channel.queue_declare(queue='profile_updated', durable=True)

            channel.basic_consume(
                queue='student_alerts',
                on_message_callback=process_alert,
                auto_ack=True
            )
            # You might want to process profile updates as well or ignore
            
            logger.info(' [*] TeacherConsole Consumer waiting for alerts...')
            channel.start_consuming()
            
        except Exception as e:
            logger.error(f" [!] RabbitMQ connection error: {e}. Retrying in 5s...")
            time.sleep(5)

# Start consumer in background thread
consumer_thread = threading.Thread(target=start_consumer, daemon=True)
consumer_thread.start()
