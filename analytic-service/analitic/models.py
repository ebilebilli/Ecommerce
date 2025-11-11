# models.py - DÜZƏLDİLMİŞ VERSİYA
import uuid
from django.db import models  # ✅ ƏLAVƏ EDİN
from django.utils import timezone

# ƏVVƏLCƏK MÖVCUD MODELLƏR
class Shop(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    external_id = models.UUIDField(unique=True)
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(default=timezone.now, editable=False)

    def __str__(self):
        return f"{self.name} ({self.external_id})"

class Product(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    external_id = models.UUIDField(unique=True)
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(default=timezone.now, editable=False)

    def __str__(self):
        return f"{self.name} ({self.external_id})"

class ShopView(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name="views")
    viewed_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Shop View - {self.shop}"

class ProductView(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="views")
    viewed_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Product View - {self.product}"

class AnalyticsProduct(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    shop = models.UUIDField()
    product_variation = models.UUIDField()
    count = models.IntegerField(default=0)
    original_price = models.DecimalField(max_digits=10, decimal_places=2)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now, editable=False)

    def __str__(self):
        return f"Analytics: {self.shop} / {self.product_variation}"

# YENİ MODEL - ORDER ANALYTICS
class OrderAnalytics(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order_id = models.IntegerField()
    user_id = models.UUIDField()  # UUID formatında
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    product_variation_id = models.UUIDField()  # UUID formatında
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    shop_id = models.UUIDField(null=True, blank=True)
    is_enriched = models.BooleanField(default=False)

    def __str__(self):
        return f"Order {self.order_id} - User {self.user_id}"