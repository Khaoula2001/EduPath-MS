import pika
import json
import logging
import os
import time
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.services.profiler import profiling_service
from app.core.database import SessionLocal
from app.schemas.pydantic_models import StudentFeatures

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

RABBITMQ_URL = os.getenv('RABBITMQ_URL', 'amqp://edupath:edupath@rabbitmq:5672')
LMS_DB_URL = os.getenv('LMS_DB_URL', 'postgresql://lms:lmspass@lmsdb:5432/lmsconnector')

# Engine for LMS database to fetch features
lms_engine = create_engine(LMS_DB_URL)
LmsSession = sessionmaker(bind=lms_engine)

def process_message(ch, method, properties, body):
    try:
        data = json.loads(body)
        student_id = data.get('studentId')
        
        logger.info(f" [x] Processing update for student {student_id}")

        # 1. Fetch features from LMS DB - Filter out records without scores/progress
        with LmsSession() as lms_session:
            result = lms_session.execute(
                text("""
                    SELECT * FROM student_features 
                    WHERE id_student = :sid 
                    AND (mean_score IS NOT NULL OR progress_rate > 0)
                    ORDER BY synced_at DESC LIMIT 1
                """),
                {"sid": student_id}
            ).fetchone()

            if result:
                # Map row to StudentFeatures pydantic model
                features = StudentFeatures(
                    student_id=str(result.id_student),
                    total_clicks=result.total_clicks or 0,
                    assessment_submissions_count=result.assessment_submissions_count or 0,
                    mean_score=float(result.mean_score or 0),
                    active_days=result.active_days or 0,
                    study_duration=float(result.study_duration or 0),
                    progress_rate=float(result.progress_rate or 0)
                )

                # 2. Run prediction and save to Profiler DB
                with SessionLocal() as profiler_db:
                    profiling_service.predict_profile(features, profiler_db)
                    logger.info(f" [v] Profile updated for student {student_id}")
            else:
                logger.warning(f" [!] No features found for student {student_id} in LMS DB")

    except Exception as e:
        logger.error(f" [!] Error processing message: {e}")

def start_consumer():
    while True:
        try:
            logger.info(f" [*] Attempting to connect to RabbitMQ at {RABBITMQ_URL}...")
            # Use URLParameters instead of plain string if needed, or just connection parameters
            params = pika.URLParameters(RABBITMQ_URL)
            connection = pika.BlockingConnection(params)
            channel = connection.channel()

            channel.queue_declare(queue='student_features_updated', durable=True)
            channel.basic_consume(queue='student_features_updated', on_message_callback=process_message, auto_ack=True)

            logger.info(' [*] Profiler Consumer waiting for messages. To exit press CTRL+C')
            channel.start_consuming()
        except Exception as e:
            logger.error(f" [!] RabbitMQ connection error: {e}. Retrying in 5 seconds...")
            time.sleep(5)

if __name__ == "__main__":
    start_consumer()
