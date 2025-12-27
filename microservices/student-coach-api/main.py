from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import create_engine, text
import pika
import json
import os
import threading
import time
import logging
import py_eureka_client.eureka_client as eureka_client

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("StudentCoach")

app = FastAPI(title="StudentCoach API")

# Eureka Configuration
EUREKA_SERVER = os.getenv("EUREKA_SERVER", "http://eureka-server:8761/eureka")
INSTANCE_HOST = os.getenv("INSTANCE_HOST", "student-coach-api")
INSTANCE_PORT = int(os.getenv("INSTANCE_PORT", "8005"))

@app.on_event("startup")
async def startup_event():
    logger.info("Initializing Eureka client...")
    await eureka_client.init_async(
        eureka_server=EUREKA_SERVER,
        app_name="student-coach-api",
        instance_port=INSTANCE_PORT,
        instance_host=INSTANCE_HOST
    )

# Configuration
RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'rabbitmq')
RABBITMQ_USER = os.getenv('RABBITMQ_USER', 'edupath')
RABBITMQ_PASS = os.getenv('RABBITMQ_PASS', 'edupath')
LMS_DB_URL = os.getenv('LMS_DB_URL', 'postgresql://lms:lmspass@lmsdb:5432/lmsconnector')

# Database Engine for LMS features
lms_engine = create_engine(LMS_DB_URL)
LmsSession = sessionmaker(bind=lms_engine)

@app.get("/")
def read_root():
    return {"service": "StudentCoach API", "status": "running"}

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/notifications/{student_id}")
def get_notifications(student_id: str):
    # Retrieve high risk status or custom alerts from DB if needed
    # For now, keeping mock but supporting string IDs
    return [
        {
            "id": 101,
            "title": "Nouvelle recommandation",
            "message": "Un nouveau tutoriel vidéo est disponible pour votre cours.",
            "type": "reco"
        }
    ]

@app.get("/student/stats/{student_id}")
def get_student_stats(student_id: str):
    try:
        with LmsSession() as session:
            # Fetch latest meaningful features for the student
            query = text("""
                SELECT study_duration, assessment_submissions_count, progress_rate, engagement_intensity, mean_score
                FROM student_features 
                WHERE id_student = :sid 
                AND (mean_score IS NOT NULL OR progress_rate > 0)
                ORDER BY synced_at DESC LIMIT 1
            """)
            result = session.execute(query, {"sid": student_id}).fetchone()

            if not result:
                return {
                    "hours_studied": "0h",
                    "quizzes_completed": "0/0",
                    "current_streak": "0 days",
                    "completion_rate": "0%",
                    "engagement_score": 0.0
                }

            return {
                "hours_studied": f"{round(result.study_duration or 0, 1)}h",
                "quizzes_completed": f"{result.assessment_submissions_count or 0}",
                "current_streak": "Active",
                "completion_rate": f"{int((result.progress_rate or 0) * 100)}%",
                "engagement_score": round(result.engagement_intensity or 0, 2),
                "mean_score": round(result.mean_score or 0, 2)
            }
    except Exception as e:
        logger.error(f"Error fetching student stats: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/students")
def get_students():
    """
    Fetch list of students from the raw LMS data (Moodle sync).
    """
    try:
        with LmsSession() as session:
            # Query the latest student_info raw data
            # We assume lms-connector saved it with data_type='student_info'
            query = text("""
                SELECT raw_json 
                FROM raw_learning_data 
                WHERE source='MOODLE' AND data_type='student_info' 
                ORDER BY created_at DESC 
                LIMIT 1
            """)
            result = session.execute(query).fetchone()

            if not result or not result[0]:
                return []

            # raw_json is likely a list of users from core_enrol_get_enrolled_users
            users_data = result[0]
            
            # Extract relevant fields
            students = []
            if isinstance(users_data, list):
                for user in users_data:
                    # Moodle typically returns 'id', 'fullname', 'email'
                    students.append({
                        "id": str(user.get("id")),
                        "name": user.get("fullname"),
                        "email": user.get("email"),
                        # These will be enriched by other calls or defaults
                        "initials": "".join([n[0] for n in user.get("fullname", "S").split(" ")]).upper()[:2]
                    })
            
            return students

    except Exception as e:
        logger.error(f"Error fetching students: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Background RabbitMQ Consumer
def start_consumer():
    while True:
        try:
            logger.info(f" [*] Connecting to RabbitMQ at {RABBITMQ_HOST}...")
            credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
            connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST, credentials=credentials))
            channel = connection.channel()
            
            # Subscribed to alerts and updates
            channel.queue_declare(queue='student_alerts', durable=True)
            channel.queue_declare(queue='student_features_updated', durable=True)

            def callback(ch, method, properties, body):
                try:
                    data = json.loads(body)
                    logger.info(f" [x] Received event: {data}")
                    # Logic to generate alerts based on data changes could go here
                except Exception as e:
                    logger.error(f"Error handling message: {e}")

            channel.basic_consume(queue='student_alerts', on_message_callback=callback, auto_ack=True)
            channel.basic_consume(queue='student_features_updated', on_message_callback=callback, auto_ack=True)

            logger.info(' [*] Coach Consumer waiting for messages...')
            channel.start_consuming()
        except Exception as e:
            logger.error(f"RabbitMQ Consumer Error: {e}. Retrying in 5s...")
            time.sleep(5)

# Start consumer in background
threading.Thread(target=start_consumer, daemon=True).start()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005)
