# consumer.py
import os
import sys
import json
import time
import asyncio
from pathlib import Path
import logging
import aio_pika
from elasticsearch import Elasticsearch

from elastic.models import ShopSchema


LOG_DIR = Path(os.getenv("LOG_DIR", "/app/logs"))
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / "consumer.log"
FORMAT = '%(asctime)s - %(levelname)s - %(message)s'

logging.basicConfig(
    level=logging.INFO,
    format=FORMAT,
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(LOG_FILE)
    ]
)

logger = logging.getLogger("consumer")


ELASTIC_HOST = os.getenv('ELASTIC_HOST', 'http://elasticsearch:9200')
ELASTIC_USERNAME = os.getenv('ELASTIC_USERNAME', 'elastic')
ELASTIC_PASSWORD = os.getenv('ELASTIC_PASSWORD', '')

es = Elasticsearch(
    [ELASTIC_HOST],
    basic_auth=(ELASTIC_USERNAME, ELASTIC_PASSWORD) if ELASTIC_PASSWORD else None,
    verify_certs=False,
    ssl_show_warn=False,
    request_timeout=10
)

INDEX_NAME = "shops"


def wait_for_elasticsearch(max_retries=30, delay=2):
    for i in range(max_retries):
        try:
            if es.ping():
                logger.info("Elasticsearch is available.")
                return True
        except Exception as e:
            logger.warning(f"Elasticsearch not ready: {e}")
        time.sleep(delay)
    logger.error("Elasticsearch is not available after retries.")
    return False

def wait_for_rabbitmq(max_retries=30, delay=2):
    rabbit_host = os.getenv("RABBITMQ_HOST", "rabbitmq")
    rabbit_port = int(os.getenv("RABBITMQ_PORT", 5672))
    rabbit_user = os.getenv("RABBITMQ_USER", "guest")
    rabbit_pass = os.getenv("RABBITMQ_PASS", "guest")

    import pika
    for i in range(max_retries):
        try:
            credentials = pika.PlainCredentials(rabbit_user, rabbit_pass)
            parameters = pika.ConnectionParameters(
                host=rabbit_host,
                port=rabbit_port,
                credentials=credentials,
                connection_attempts=1,
                retry_delay=1
            )
            connection = pika.BlockingConnection(parameters)
            connection.close()
            logger.info("RabbitMQ is available.")
            return True
        except Exception as e:
            logger.warning(f"RabbitMQ not ready: {e}")
            time.sleep(delay)
    logger.error("RabbitMQ is not available after retries.")
    return False

async def start_consumer():
    rabbit_host = os.getenv("RABBITMQ_HOST", "rabbitmq")
    rabbit_port = int(os.getenv("RABBITMQ_PORT", 5672))
    rabbit_user = os.getenv("RABBITMQ_USER", "guest")
    rabbit_pass = os.getenv("RABBITMQ_PASS", "guest")
    rabbit_url = f"amqp://{rabbit_user}:{rabbit_pass}@{rabbit_host}:{rabbit_port}/"

    logger.info("Connecting to RabbitMQ...")
    connection = await aio_pika.connect_robust(rabbit_url)
    channel = await connection.channel()
    queue = await channel.declare_queue("shop_queue", durable=True)

    logger.info("RabbitMQ consumer started. Waiting for messages...")

    async with queue.iterator() as queue_iter:
        async for message in queue_iter:
            async with message.process():
                try:
                    data = json.loads(message.body)
                    event_type = data.get("event_type")
                    shop_data = data.get("shop_data", {})
                    shop_id = data.get("shop_id")

                    if event_type == "deleted":
                        es.delete(index=INDEX_NAME, id=shop_id, ignore=[404])
                        logger.info(f"Deleted shop {shop_id} from Elasticsearch")
                    else:
                        shop = ShopSchema(**shop_data)
                        es.index(index=INDEX_NAME, id=shop_id, document=shop.dict())
                        logger.info(f"Indexed shop {shop_id} ({shop.name}) to Elasticsearch")
                except Exception as e:
                    logger.error(f"Failed processing message: {e}", exc_info=True)

def main():
    if not wait_for_elasticsearch():
        sys.exit(1)
    if not wait_for_rabbitmq():
        sys.exit(1)

    try:
        logger.info("Starting consumer...")
        asyncio.run(start_consumer())
    except KeyboardInterrupt:
        logger.info("Consumer stopped by user")
    except Exception:
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
