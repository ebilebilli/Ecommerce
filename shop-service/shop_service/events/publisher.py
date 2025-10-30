import json
import pika
import os


RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "admin")
RABBITMQ_PASS = os.getenv("RABBITMQ_PASS", "supersecret123")


def publish_event(event_name: str, payload: dict):
    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
    connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST, credentials=credentials))
    channel = connection.channel()
    channel.queue_declare(queue="user_events")

    message = {
        "event": event_name,
        "data": payload,
    }

    channel.basic_publish(exchange="", routing_key="user_events", body=json.dumps(message))
    connection.close()
