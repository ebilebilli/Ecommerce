import os
import json
import pika
import aio_pika
from .documents import ELASTIC, INDEX_NAME
from dotenv import load_dotenv

from .models import ShopSchema

load_dotenv('')

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")
RABBITMQ_PORT = os.getenv("RABBITMQ_PORT", "5672")
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "guest")
RABBITMQ_PASS = os.getenv("RABBITMQ_PASS", "guest")

RABBITMQ_URL = f"amqp://{RABBITMQ_USER}:{RABBITMQ_PASS}@{RABBITMQ_HOST}:{RABBITMQ_PORT}/"


async def start_consumer():
    connection = await aio_pika.connect_robust(RABBITMQ_URL)
    channel = await connection.channel()
    queue = await channel.declare_queue("shop_queue", durable=True)

    async with queue.iterator() as queue_iter:
        async for message in queue_iter:
            async with message.process():
                data = json.loads(message.body)
                event_type = data.get("event_type")
                shop_data = data.get("shop_data", {})

                if event_type == "deleted":
                    ELASTIC.delete(index=INDEX_NAME, id=data["shop_id"], ignore=[404])
                    print(f"❌ Deleted: {data['shop_id']}")
                else:
                    shop = ShopSchema(**shop_data)
                    ELASTIC.index(index=INDEX_NAME, id=data["shop_id"], document=shop.model_dump())
                    print(f"✅ Indexed ({event_type}): {shop.name}")
