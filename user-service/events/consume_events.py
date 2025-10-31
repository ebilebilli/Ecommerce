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

print(f" [*] RabbitMQ Connection Info:")
print(f" [*]   Host: {RABBITMQ_HOST}")
print(f" [*]   User: {RABBITMQ_USER}")
print(f" [*] Connecting to RabbitMQ...")

credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST, credentials=credentials))
channel = connection.channel()
channel.queue_declare(queue='user_events')

print(f" [*] Connected to RabbitMQ successfully!")
print(f" [*] Queue 'user_events' declared/checked")
print(f" [*] Waiting for messages. To exit press CTRL+C")

def callback(ch, method, properties, body):
    from user_service.models import User
    try:
        print(f"\n [x] Received message")
        print(f" [x] Raw body: {body.decode()}")
        
        message = json.loads(body)
        print(f" [x] Parsed message: {message}")
        
        user_str = message['data']['user_id']
        print(f" [x] User ID string: {user_str}")
        
        user_uuid = uuid.UUID(user_str)
        print(f" [x] User UUID: {user_uuid}")
        
        user_instance = User.objects.get(id=user_uuid)
        print(f" [x] Found user: {user_instance.email}")
        print(f" [x] Current is_shop_owner: {user_instance.is_shop_owner}")
        
        user_instance.is_shop_owner = True
        user_instance.save()
        
        print(f" [+] User {user_uuid} marked as shop owner successfully!")
        ch.basic_ack(delivery_tag=method.delivery_tag)

    except Exception as e:
        print(f" [!] ERROR processing message: {str(e)}")
        print(f" [!] Exception type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)


channel.basic_consume(queue='user_events', on_message_callback=callback)
print(f" [*] Consumer started, listening for messages...")
channel.start_consuming()
