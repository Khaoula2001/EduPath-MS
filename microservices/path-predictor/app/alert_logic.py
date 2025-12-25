import pika
import json
import os

RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'rabbitmq')
RABBITMQ_USER = os.getenv('RABBITMQ_USER', 'edupath')
RABBITMQ_PASS = os.getenv('RABBITMQ_PASS', 'edupath')

def send_to_rabbitmq(message: dict):
    try:
        credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST, credentials=credentials))
        channel = connection.channel()
        channel.queue_declare(queue='student_alerts')
        
        channel.basic_publish(
            exchange='',
            routing_key='student_alerts',
            body=json.dumps(message)
        )
        connection.close()
    except Exception as e:
        print(f"Failed to send to RabbitMQ: {e}")

def generate_alert(probability_success: float, student_id: int = None) -> str:
    alert_msg = ""
    severity = "INFO"
    
    if probability_success >= 0.60:
        alert_msg = "✅ Fortes chances de réussite"
    elif probability_success >= 0.40:
        alert_msg = "⚠️ Étudiant fragile"
        severity = "WARNING"
    else:
        alert_msg = "🚨 Risque élevé d’échec"
        severity = "CRITICAL"

    if student_id and severity != "INFO":
        send_to_rabbitmq({
            "student_id": student_id,
            "message": alert_msg,
            "severity": severity,
            "type": "performance_alert"
        })

    return alert_msg
