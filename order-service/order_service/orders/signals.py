import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import OrderItem
from order_service.messaging import rabbitmq_producer

logger = logging.getLogger(__name__)

_published_order_items = set()


@receiver(post_save, sender=OrderItem, dispatch_uid="order_item_post_save_unique")
def order_item_post_save(sender, instance, created, **kwargs):
    """Publish order.item.created event when OrderItem is created"""
    if created and instance.shop_id and instance.product_id:
        if instance.id in _published_order_items:
            logger.debug(f'OrderItem {instance.id} event already published, skipping duplicate')
            return
        
        try:
            success = rabbitmq_producer.publish_order_item_created(
                order_item_id=instance.id,
                order_id=instance.order.id,
                shop_id=str(instance.shop_id),
                product_id=str(instance.product_id),
                product_variation=str(instance.product_variation),
                quantity=instance.quantity,
                price=instance.price,
                status=instance.status,
                user_id=str(instance.order.user_id)
            )
            if success:
                _published_order_items.add(instance.id)
                logger.debug(f'Published order.item.created event - OrderItem: {instance.id}, Shop: {instance.shop_id}')
            else:
                logger.warning(f'Failed to publish order.item.created event - OrderItem: {instance.id}')
        except Exception as e:
            logger.error(f'Error publishing order.item.created event: {e}', exc_info=True)
    elif created:
        logger.debug(f'OrderItem {instance.id} created without shop_id or product_id, skipping event publish')

