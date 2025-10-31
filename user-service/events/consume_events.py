import pika
import json
import os
import django
from dotenv import load_dotenv
import uuid


load_dotenv()
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Core.settings')
django.setup()

RABBITMQ_HOST = os.getenv('RABBITMQ_HOST')
RABBITMQ_USER = os.getenv('RABBITMQ_USER')
RABBITMQ_PASS = os.getenv('RABBITMQ_PASS')

credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST, credentials=credentials))
channel = connection.channel()
channel.queue_declare(queue='user_events')

def callback(ch, method, properties, body):
    from user_service.models import User
    try:
        message = json.loads(body)
        user_str = message['data']['user_id']
        user_uuid = uuid.UUID(user_str)
        user_instance = User.objects.get(id=user_uuid)
        user_instance.is_shop_owner = True
        user_instance.save()
        ch.basic_ack(delivery_tag=method.delivery_tag)

    except Exception as e:
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)


channel.basic_consume(queue='user_events', on_message_callback=callback)
channel.start_consuming()
