from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
import pika
import json
import os

app = FastAPI(title="StudentCoach API")

RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'rabbitmq')
RABBITMQ_USER = os.getenv('RABBITMQ_USER', 'edupath')
RABBITMQ_PASS = os.getenv('RABBITMQ_PASS', 'edupath')

@app.get("/")
def read_root():
    return {"service": "StudentCoach API", "status": "running"}

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/notifications/{student_id}")
def get_notifications(student_id: int):
    # En production, on lirait depuis une DB ou un cache
    # Ici on simule une réponse
    return [
        {
            "id": 101,
            "title": "Nouvelle recommandation",
            "message": "Un nouveau tutoriel vidéo est disponible pour votre cours de mathématiques.",
            "type": "reco"
        },
        {
            "id": 102,
            "title": "Alerte de progression",
            "message": "Attention, vous avez du retard sur le module 3.",
            "type": "alert"
        }
    ]

# Background Task to consume RabbitMQ messages
def start_consumer():
    try:
        credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST, credentials=credentials))
        channel = connection.channel()
        channel.queue_declare(queue='student_alerts')

        def callback(ch, method, properties, body):
            data = json.loads(body)
            print(f" [x] Received alert: {data}")
            # Logique pour stocker l'alerte en base pour l'étudiant

        channel.basic_consume(queue='student_alerts', on_message_callback=callback, auto_ack=True)
        print(' [*] Waiting for messages. To exit press CTRL+C')
        channel.start_consuming()
    except Exception as e:
        print(f"RabbitMQ Consumer Error: {e}")

# Note: In a real FastAPI app, you'd run this in a separate thread or process
# For this task, we just show the implementation structure.
