import pika
import json
import logging
import os

logger = logging.getLogger(__name__)

RABBITMQ_URL = os.getenv('RABBITMQ_URL', 'amqp://edupath:edupath@rabbitmq:5672')

class ProfilePublisher:
    def __init__(self):
        self.url = RABBITMQ_URL
        self.queue = 'profile_updated'
        self.connection = None
        self.channel = None
        
    def connect(self):
        """Establish connection to RabbitMQ"""
        try:
            params = pika.URLParameters(self.url)
            self.connection = pika.BlockingConnection(params)
            self.channel = self.connection.channel()
            self.channel.queue_declare(queue=self.queue, durable=True)
            logger.info(f"[RabbitMQ] Connected to {self.url} and queue {self.queue} asserted.")
        except Exception as error:
            logger.error(f'[RabbitMQ] Connection error: {error}')
            self.connection = None
            self.channel = None

    def publish_profile_update(self, student_id, profile_type, risk_level, cluster_id):
        """Publish profile update event"""
        try:
            if not self.channel:
                self.connect()
            
            if self.channel:
                message = {
                    'studentId': str(student_id),
                    'profileType': profile_type,
                    'riskLevel': risk_level,
                    'clusterId': cluster_id,
                    'timestamp': str(os.times())
                }
                
                self.channel.basic_publish(
                    exchange='',
                    routing_key=self.queue,
                    body=json.dumps(message)
                )
                logger.info(f"[RabbitMQ] Published profile update for student {student_id}: {profile_type}")
        except Exception as error:
            logger.error(f'[RabbitMQ] Publishing error: {error}')
            # Try to reconnect
            self.connection = None
            self.channel = None

# Global publisher instance
profile_publisher = ProfilePublisher()
