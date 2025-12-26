import pika
import json
import logging
import os
import time
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from app.services.embeddings import embedding_service

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

RABBITMQ_URL = os.getenv('RABBITMQ_URL', 'amqp://edupath:edupath@rabbitmq:5672')
DB_URL = os.getenv('DATABASE_URL', 'postgresql://prepadata:prepadata_pwd@postgres:5432/recco_db')

# Database Engine
engine = create_engine(DB_URL)
SessionLocal = sessionmaker(bind=engine)

def process_profile_update(ch, method, properties, body):
    """Process student profile updates and regenerate recommendations if needed"""
    try:
        data = json.loads(body)
        student_id = data.get('studentId')
        profile_type = data.get('profileType')
        risk_level = data.get('riskLevel')
        
        logger.info(f" [x] Profile update received for student {student_id}: {profile_type} ({risk_level})")
        
        # Rebuild index if needed (for now, we log it)
        # In production, you might want to trigger specific recommendation updates
        # based on the new profile type
        
        with SessionLocal() as db:
            # Optionally rebuild index for high-risk students
            if risk_level == "High":
                logger.info(f" [!] High-risk student detected: {student_id}. Consider priority recommendations.")
                # embedding_service.rebuild_index(db)  # Uncomment if you want to rebuild
        
        logger.info(f" [✓] Processed profile update for student {student_id}")
        
    except Exception as e:
        logger.error(f" [!] Error processing profile update: {e}")

def start_consumer():
    """Start RabbitMQ consumer for profile updates"""
    while True:
        try:
            logger.info(f" [*] Connecting to RabbitMQ at {RABBITMQ_URL}...")
            params = pika.URLParameters(RABBITMQ_URL)
            connection = pika.BlockingConnection(params)
            channel = connection.channel()

            # Declare queue for profile updates
            channel.queue_declare(queue='profile_updated', durable=True)
            
            # Also listen to student features for potential recommendation triggers
            channel.queue_declare(queue='student_features_updated', durable=True)

            channel.basic_consume(
                queue='profile_updated',
                on_message_callback=process_profile_update,
                auto_ack=True
            )
            
            channel.basic_consume(
                queue='student_features_updated',
                on_message_callback=process_profile_update,
                auto_ack=True
            )

            logger.info(' [*] RecoBuilder Consumer waiting for messages...')
            channel.start_consuming()
            
        except Exception as e:
            logger.error(f" [!] RabbitMQ connection error: {e}. Retrying in 5 seconds...")
            time.sleep(5)

if __name__ == "__main__":
    start_consumer()
