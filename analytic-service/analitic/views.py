# views.py - DÜZƏLDİLMİŞ VERSİYA
from rest_framework import viewsets, status  # ✅ ƏLAVƏ EDİN
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from .models import OrderAnalytics, ShopView, ProductView, AnalyticsProduct
from .serializers import OrderAnalyticsSerializer, OrderReceiveSerializer, ShopViewSerializer, ProductViewSerializer, AnalyticsProductSerializer
from .product_client import product_client

class ShopViewViewSet(viewsets.ModelViewSet):
    queryset = ShopView.objects.all()
    serializer_class = ShopViewSerializer

class ProductViewViewSet(viewsets.ModelViewSet):
    queryset = ProductView.objects.all()
    serializer_class = ProductViewSerializer

class AnalyticsProductViewSet(viewsets.ModelViewSet):
    queryset = AnalyticsProduct.objects.all()
    serializer_class = AnalyticsProductSerializer

# YENİ VIEWSET - ORDER ANALYTICS
class OrderAnalyticsViewSet(viewsets.ModelViewSet):
    queryset = OrderAnalytics.objects.all()
    serializer_class = OrderAnalyticsSerializer
    
    @action(detail=False, methods=['post'])
    def receive_order(self, request):
        """Order servisindən məlumat qəbul et"""
        serializer = OrderReceiveSerializer(data=request.data)
        if serializer.is_valid():
            order_data = serializer.validated_data
            
            # Hər bir order item-ını saxla
            for item in order_data['items']:
                order_analytics = OrderAnalytics.objects.create(
                    order_id=order_data['id'],
                    user_id=order_data['user_id'],
                    created_at=order_data['created_at'],
                    product_variation_id=item['product_variation'],
                    quantity=item['quantity'],
                    price=item['price']
                )
                
                # Background task - Product servisindən shop məlumatını al
                self.enrich_order_data(order_analytics.id)
            
            return Response({"status": "Order data received successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def enrich_order_data(self, order_analytics_id):
        """Product servisindən shop məlumatlarını al"""
        try:
            order_analytics = OrderAnalytics.objects.get(id=order_analytics_id)
            
            # Product servisinə sorğu at
            product_data = product_client.get_product_variation_data(
                order_analytics.product_variation_id
            )
            
            if product_data:
                order_analytics.shop_id = product_data.get('shop_uuid')
                order_analytics.is_enriched = True
                order_analytics.save()
                
        except Exception as e:
            print(f"Error enriching order data: {e}")
    
    @action(detail=False, methods=['get'])
    def sample_order_format(self, request):
        """Order formatı nümunəsi"""
        sample_data = {
            "id": 123,
            "user_id": "550e8400-e29b-41d4-a716-446655440000",
            "created_at": "2025-10-27T06:57:22.541135Z",
            "items": [
                {
                    "product_variation": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                    "quantity": 2,
                    "price": 29.99
                }
            ]
        }
        return Response(sample_data)