import os
import sys
import json
import time
import asyncio
from pathlib import Path
import logging
import aio_pika
from elasticsearch import Elasticsearch
from dotenv import load_dotenv

from elastic.models import ShopSchema
from elastic.logging_config import logging

# Load environment variables from .env file
load_dotenv()



# Setup logging first
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("consumer")

ELASTIC_HOST = os.getenv('ELASTIC_HOST', 'http://elasticsearch:9200')
ELASTIC_USERNAME = os.getenv('ELASTIC_USERNAME', 'elastic')
ELASTIC_PASSWORD = os.getenv('ELASTIC_PASSWORD', '')

# Create Elasticsearch client with proper authentication
es_config = {
    'hosts': [ELASTIC_HOST],
    'verify_certs': False,
    'ssl_show_warn': False,
    'request_timeout': 10
}

# Add authentication if password is provided
if ELASTIC_PASSWORD:
    es_config['basic_auth'] = (ELASTIC_USERNAME, ELASTIC_PASSWORD)
    logger.info(f"Elasticsearch authentication enabled for user: {ELASTIC_USERNAME}")
else:
    logger.warning("ELASTIC_PASSWORD not set - authentication may fail if Elasticsearch security is enabled")

es = Elasticsearch(**es_config)

INDEX_NAME = "shops"


def wait_for_elasticsearch(max_retries=30, delay=2):
    logger.info(f"Waiting for Elasticsearch at {ELASTIC_HOST}...")
    for i in range(max_retries):
        try:
            # Try to get cluster info instead of ping to verify authentication
            info = es.info()
            if info:
                logger.info("Elasticsearch is available.")
                logger.info(f"Connected to Elasticsearch cluster: {info.get('cluster_name', 'unknown')}")
                logger.info(f"Elasticsearch version: {info.get('version', {}).get('number', 'unknown')}")
                return True
        except Exception as e:
            error_msg = str(e)
            if i % 5 == 0:  # Log every 5th attempt to reduce log spam
                logger.warning(f"Elasticsearch not ready (attempt {i+1}/{max_retries}): {error_msg}")
            # Check if it's an authentication error
            if '401' in error_msg or '403' in error_msg or 'authentication' in error_msg.lower():
                logger.error(f"Elasticsearch authentication failed. Check ELASTIC_USERNAME and ELASTIC_PASSWORD.")
        time.sleep(delay)
    logger.error("Elasticsearch is not available after retries.")
    logger.error(f"Please check: 1) Elasticsearch is running, 2) ELASTIC_HOST={ELASTIC_HOST}, 3) ELASTIC_USERNAME={ELASTIC_USERNAME}, 4) ELASTIC_PASSWORD is set")
    return False

def wait_for_rabbitmq(max_retries=30, delay=2):
    rabbit_host = os.getenv("RABBITMQ_HOST", "rabbitmq")
    rabbit_port = int(os.getenv("RABBITMQ_PORT", 5672))
    rabbit_user = os.getenv("RABBITMQ_USER", "admin")
    rabbit_pass = os.getenv("RABBITMQ_PASS", "admin12345")

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
    rabbit_user = os.getenv("RABBITMQ_USER", "admin")
    rabbit_pass = os.getenv("RABBITMQ_PASS", "admin12345")
    rabbit_url = f"amqp://{rabbit_user}:{rabbit_pass}@{rabbit_host}:{rabbit_port}/"

    logger.info("Connecting to RabbitMQ...")
    connection = await aio_pika.connect_robust(rabbit_url)
    channel = await connection.channel()
    
    # Declare exchange
    exchange = await channel.declare_exchange(
        "shop_events",
        aio_pika.ExchangeType.TOPIC,
        durable=True
    )
    
    # Declare queue
    queue = await channel.declare_queue("shop_queue", durable=True)
    
    # Bind queue to exchange with routing keys
    await queue.bind(exchange, routing_key="shop.approved")
    await queue.bind(exchange, routing_key="shop.updated")
    await queue.bind(exchange, routing_key="shop.deleted")
    
    logger.info("RabbitMQ consumer started. Waiting for messages...")
    logger.info("Listening for shop events: shop.approved, shop.updated, shop.deleted")

    async with queue.iterator() as queue_iter:
        async for message in queue_iter:
            async with message.process():
                try:
                    data = json.loads(message.body)
                    event_type = data.get("event_type")
                    shop_data = data.get("shop_data", {})
                    shop_id = data.get("shop_id")

                    logger.info(f"Received event: {event_type} for shop: {shop_id}")

                    if event_type == "shop.deleted":
                        es.delete(index=INDEX_NAME, id=shop_id, ignore=[404])
                        logger.info(f"Deleted shop {shop_id} from Elasticsearch")
                    elif event_type in ["shop.approved", "shop.updated"]:
                        if not shop_data:
                            logger.warning(f"No shop_data provided for event {event_type}, skipping")
                            continue
                        shop = ShopSchema(**shop_data)
                        es.index(index=INDEX_NAME, id=shop_id, document=shop.model_dump())
                        logger.info(f"Indexed shop {shop_id} ({shop.name}) to Elasticsearch")
                    else:
                        logger.warning(f"Unknown event type: {event_type}, skipping")
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
