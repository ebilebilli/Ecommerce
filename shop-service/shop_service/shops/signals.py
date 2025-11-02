from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Shop
from events.publisher import publish_event


@receiver(post_save, sender=Shop)
def shop_created(sender, instance, created, **kwargs):
    if created:
        publish_event('SHOP CREATED', {'user_id': str(instance.user)})