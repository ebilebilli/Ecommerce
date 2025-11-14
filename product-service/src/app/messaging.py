import pika
import json
import os
import logging
from typing import Dict, Any
from uuid import UUID
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger('product_service')


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

    def publish_product_created(self, product_data: Dict[str, Any]):
        """Publish product.created event to RabbitMQ"""
        try:
            conn = self.get_connection()
            channel = conn.channel()
            channel.exchange_declare(
                exchange='product_events',
                exchange_type='topic',
                durable=True
            )

            message = {
                'event_type': 'product.created',
                'product_id': str(product_data.get('id')),
                'product_data': {
                    'id': str(product_data.get('id')),
                    'shop_id': str(product_data.get('shop_id')) if product_data.get('shop_id') else None,
                    'title': product_data.get('title'),
                    'about': product_data.get('about'),
                    'on_sale': product_data.get('on_sale', False),
                    'is_active': product_data.get('is_active', True),
                    'top_sale': product_data.get('top_sale', False),
                    'top_popular': product_data.get('top_popular', False),
                    'sku': product_data.get('sku'),
                    'created_at': product_data.get('created_at').isoformat() if product_data.get('created_at') else None,
                }
            }

            channel.basic_publish(
                exchange='product_events',
                routing_key='product.created',
                body=json.dumps(message),
                properties=pika.BasicProperties(
                    delivery_mode=2,  # Make message persistent
                    content_type='application/json'
                )
            )

            logger.info(f"Published product.created event for product {product_data.get('id')}")
            conn.close()
            return True

        except Exception as e:
            logger.error(f"Failed to publish product.created event: {e}", exc_info=True)
            return False

    def publish_product_variation_created(self, variation_data: Dict[str, Any]):
        """Publish product_variation.created event to RabbitMQ"""
        try:
            conn = self.get_connection()
            channel = conn.channel()
            channel.exchange_declare(
                exchange='product_events',
                exchange_type='topic',
                durable=True
            )

            message = {
                'event_type': 'product_variation.created',
                'variation_id': str(variation_data.get('id')),
                'variation_data': {
                    'id': str(variation_data.get('id')),
                    'product_id': str(variation_data.get('product_id')),
                    'size': variation_data.get('size'),
                    'color': variation_data.get('color'),
                    'count': variation_data.get('count', 0),
                    'amount': variation_data.get('amount', 0),
                    'price': float(variation_data.get('price')) if variation_data.get('price') else None,
                    'discount': float(variation_data.get('discount')) if variation_data.get('discount') else None,
                }
            }

            channel.basic_publish(
                exchange='product_events',
                routing_key='product_variation.created',
                body=json.dumps(message),
                properties=pika.BasicProperties(
                    delivery_mode=2,  # Make message persistent
                    content_type='application/json'
                )
            )

            logger.info(f"Published product_variation.created event for variation {variation_data.get('id')}")
            conn.close()
            return True

        except Exception as e:
            logger.error(f"Failed to publish product_variation.created event: {e}", exc_info=True)
            return False

    def publish_product_updated(self, product_data: Dict[str, Any]):
        """Publish product.updated event to RabbitMQ"""
        try:
            conn = self.get_connection()
            channel = conn.channel()
            channel.exchange_declare(
                exchange='product_events',
                exchange_type='topic',
                durable=True
            )

            message = {
                'event_type': 'product.updated',
                'product_id': str(product_data.get('id')),
                'product_data': {
                    'id': str(product_data.get('id')),
                    'shop_id': str(product_data.get('shop_id')) if product_data.get('shop_id') else None,
                    'title': product_data.get('title'),
                    'about': product_data.get('about'),
                    'on_sale': product_data.get('on_sale', False),
                    'is_active': product_data.get('is_active', True),
                    'top_sale': product_data.get('top_sale', False),
                    'top_popular': product_data.get('top_popular', False),
                    'sku': product_data.get('sku'),
                    'created_at': product_data.get('created_at').isoformat() if product_data.get('created_at') else None,
                }
            }

            channel.basic_publish(
                exchange='product_events',
                routing_key='product.updated',
                body=json.dumps(message),
                properties=pika.BasicProperties(
                    delivery_mode=2,
                    content_type='application/json'
                )
            )

            logger.info(f"Published product.updated event for product {product_data.get('id')}")
            conn.close()
            return True

        except Exception as e:
            logger.error(f"Failed to publish product.updated event: {e}", exc_info=True)
            return False

    def publish_product_deleted(self, product_id: UUID):
        """Publish product.deleted event to RabbitMQ"""
        try:
            conn = self.get_connection()
            channel = conn.channel()
            channel.exchange_declare(
                exchange='product_events',
                exchange_type='topic',
                durable=True
            )

            message = {
                'event_type': 'product.deleted',
                'product_id': str(product_id)
            }

            channel.basic_publish(
                exchange='product_events',
                routing_key='product.deleted',
                body=json.dumps(message),
                properties=pika.BasicProperties(
                    delivery_mode=2,
                    content_type='application/json'
                )
            )

            logger.info(f"Published product.deleted event for product {product_id}")
            conn.close()
            return True

        except Exception as e:
            logger.error(f"Failed to publish product.deleted event: {e}", exc_info=True)
            return False

    def publish_product_variation_updated(self, variation_data: Dict[str, Any]):
        """Publish product_variation.updated event to RabbitMQ"""
        try:
            conn = self.get_connection()
            channel = conn.channel()
            channel.exchange_declare(
                exchange='product_events',
                exchange_type='topic',
                durable=True
            )

            message = {
                'event_type': 'product_variation.updated',
                'variation_id': str(variation_data.get('id')),
                'variation_data': {
                    'id': str(variation_data.get('id')),
                    'product_id': str(variation_data.get('product_id')),
                    'size': variation_data.get('size'),
                    'color': variation_data.get('color'),
                    'count': variation_data.get('count', 0),
                    'amount': variation_data.get('amount', 0),
                    'price': float(variation_data.get('price')) if variation_data.get('price') else None,
                    'discount': float(variation_data.get('discount')) if variation_data.get('discount') else None,
                }
            }

            channel.basic_publish(
                exchange='product_events',
                routing_key='product_variation.updated',
                body=json.dumps(message),
                properties=pika.BasicProperties(
                    delivery_mode=2,
                    content_type='application/json'
                )
            )

            logger.info(f"Published product_variation.updated event for variation {variation_data.get('id')}")
            conn.close()
            return True

        except Exception as e:
            logger.error(f"Failed to publish product_variation.updated event: {e}", exc_info=True)
            return False

    def publish_product_variation_deleted(self, variation_id: UUID):
        """Publish product_variation.deleted event to RabbitMQ"""
        try:
            conn = self.get_connection()
            channel = conn.channel()
            channel.exchange_declare(
                exchange='product_events',
                exchange_type='topic',
                durable=True
            )

            message = {
                'event_type': 'product_variation.deleted',
                'variation_id': str(variation_id)
            }

            channel.basic_publish(
                exchange='product_events',
                routing_key='product_variation.deleted',
                body=json.dumps(message),
                properties=pika.BasicProperties(
                    delivery_mode=2,
                    content_type='application/json'
                )
            )

            logger.info(f"Published product_variation.deleted event for variation {variation_id}")
            conn.close()
            return True

        except Exception as e:
            logger.error(f"Failed to publish product_variation.deleted event: {e}", exc_info=True)
            return False


rabbitmq_publisher = RabbitMQPublisher()

