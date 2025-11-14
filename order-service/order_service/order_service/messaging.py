import pika
import json
import os
import logging
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger('order_service')


class RabbitMQPublisher:
    def __init__(self):
        self.host = os.getenv('RABBITMQ_HOST', 'rabbitmq')
        self.port = int(os.getenv('RABBITMQ_PORT', 5672))
        self.user = os.getenv('RABBITMQ_USER', 'admin')
        self.password = os.getenv('RABBITMQ_PASS', 'admin12345')
        
    def get_connection(self):
        credentials = pika.PlainCredentials(self.user, self.password)
        parameters = pika.ConnectionParameters(
            host=self.host,
            port=self.port,
            credentials=credentials,
            heartbeat=600,
            blocked_connection_timeout=300
        )
        return pika.BlockingConnection(parameters)
    
    def publish_order_items(self, order_id: str, items: list):
        """
        Publish 'order.item_variation' event for each item in an order.
        Example of `items`:
        [
            {
                "shop_id": "uuid-of-shop",
                "item_id": "id-of-item",
                "quantity": 3,
                "variation_data": {...}
            },
            ...
        ]
        """
        try:
            connection = self.get_connection()
            channel = connection.channel()
            
            # Declare exchange (durable so it persists between restarts)
            channel.exchange_declare(
                exchange='order_events',
                exchange_type='topic',
                durable=True
            )

            for item in items:
                message = {
                    'event_type': 'order.item_validation',
                    'order_id': str(order_id),
                    'shop_id': str(item['shop_id']),
                    'item_id': str(item['item_id']),
                    'quantity': item['quantity'],
                    'variation_data': item.get('variation_data')
                }

                channel.basic_publish(
                    exchange='order_events',
                    routing_key='order.item_variation',
                    body=json.dumps(message),
                    properties=pika.BasicProperties(
                        delivery_mode=2,
                        content_type='application/json'
                    )
                )

                logger.info(f"published order.item_variation event | order={order_id} shop={item['shop_id']} item={item['item_id']}")
            
            connection.close()

        except Exception as e:
            logger.error(f"failed to publish order.item_variation event: {e}", exc_info=True)


    def publish_order_created(self, order_id: str, user_id: str, total_price: str, shop_id: str, status: str, created_at: str):
        """
        Publish 'order.created' event when a new order is created.
        """
        try:
            connection = self.get_connection()
            channel = connection.channel()

            # Declare exchange (topic exchange like your current setup)
            channel.exchange_declare(
                exchange='order_events',
                exchange_type='topic',
                durable=True
            )

            message = {
                'event_type': 'order.created',
                'order_id': str(order_id),
                'user_id': str(user_id),
                'total_price': str(total_price),
                'shop_id': str(shop_id) if shop_id else None,
                'status': status,
                'created_at': created_at
            }

            channel.basic_publish(
                exchange='order_events',
                routing_key='order.created',
                body=json.dumps(message),
                properties=pika.BasicProperties(
                    delivery_mode=2,
                    content_type='application/json'
                )
            )

            logger.info(
                f"published order.created event | order={order_id} user={user_id} shop={shop_id}"
            )

            connection.close()
            return True

        except Exception as e:
            logger.error(f"failed to publish order.created event: {e}", exc_info=True)
            return False


# Singleton instance
publisher = RabbitMQPublisher()


