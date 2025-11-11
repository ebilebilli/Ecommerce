# serializers.py - DÜZƏLDİLMİŞ VERSİYA
from rest_framework import serializers  # ✅ ƏLAVƏ EDİN
from .models import ShopView, ProductView, AnalyticsProduct, OrderAnalytics

class ShopViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShopView
        fields = "__all__"

class ProductViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductView
        fields = "__all__"

class AnalyticsProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnalyticsProduct
        fields = "__all__"

class OrderAnalyticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderAnalytics
        fields = "__all__"

class OrderReceiveSerializer(serializers.Serializer):
    """Order servisindən gələn data formatı"""
    id = serializers.IntegerField()
    user_id = serializers.UUIDField()
    created_at = serializers.DateTimeField()
    items = serializers.ListField(child=serializers.DictField())

    def validate_items(self, items):
        for item in items:
            if 'product_variation' not in item:
                raise serializers.ValidationError("product_variation is required in items")
            if 'quantity' not in item:
                raise serializers.ValidationError("quantity is required in items")
            if 'price' not in item:
                raise serializers.ValidationError("price is required in items")
        return items