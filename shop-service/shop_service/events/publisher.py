import json
import pika
import os
from dotenv import load_dotenv


load_dotenv()

RABBITMQ_HOST = os.getenv('RABBITMQ_HOST')
RABBITMQ_USER = os.getenv('RABBITMQ_USER')
RABBITMQ_PASS = os.getenv('RABBITMQ_PASS')


def publish_event(event_name: str, payload: dict):
    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
    connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST, credentials=credentials))
    channel = connection.channel()
    channel.queue_declare(queue='user_events')

    message = {
        'event': event_name,
        'data': payload,
    }

    channel.basic_publish(exchange='', routing_key='user_events', body=json.dumps(message, default=str))
    connection.close()
