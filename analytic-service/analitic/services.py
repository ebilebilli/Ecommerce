# services.py
import requests
import uuid
from django.db import transaction
from .models import Order, OrderItem
from datetime import datetime
from decimal import Decimal

class AnaliticService:
    def __init__(self):
        # Docker şəbəkəsinə uyğun hostname
        self.product_service_url = "http://ecommerce-product:8000/api/v1/products/variations"

    
    def get_product_variation(self, variation_id):
        """Product servisinden variation detaylarını getir"""
        try:
            response = requests.get(f"{self.product_service_url}/{variation_id}/")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Product servisine erişim hatası: {e}")
            return None

    def process_order_completed(self, order_data):
        """Sipariş tamamlandığında analitik işlemleri"""
        with transaction.atomic():
            # Tarixi string formatından datetime obyektinə çevir
            created_at = order_data['created_at']
            if isinstance(created_at, str):
                # ISO formatından çevir (Zulu time üçün)
                if created_at.endswith('Z'):
                    created_at = created_at.replace('Z', '+00:00')
                created_at = datetime.fromisoformat(created_at)
            
            # Convert order_id to integer (order service-dən integer gəlir)
            order_id = order_data['id']
            if not isinstance(order_id, int):
                order_id = int(order_id)
            
            # Convert user_id to UUID
            user_id = order_data['user_id']
            if not isinstance(user_id, uuid.UUID):
                user_id = uuid.UUID(str(user_id))
            
            # Order kaydını oluştur veya güncelle
            order, created = Order.objects.update_or_create(
                order_id=order_id,
                defaults={
                    'user_id': user_id,
                    'created_at': created_at  # ✅ ÇEVRİLMİŞ TARİX
                }
            )
            
            # Order items'ları işle
            for item_data in order_data['items']:
                # Convert variation_id to UUID
                variation_id = item_data['product_variation']
                if not isinstance(variation_id, uuid.UUID):
                    variation_id = uuid.UUID(str(variation_id))
                
                variation_data = self.get_product_variation(str(variation_id))
                
                # Convert price to Decimal
                price = item_data['price']
                if not isinstance(price, Decimal):
                    price = Decimal(str(price))
                
                base_price = price
                original_price = None
                shop_id = None
                product_id = None
                product_title = ""
                size = ""
                color = ""
                product_sku = ""

                if variation_data:
                    original_price = variation_data.get('original_price')
                    if original_price is not None:
                        original_price = Decimal(str(original_price))
                    
                    base_price = original_price if original_price else price
                    
                    product = variation_data.get('product', {})
                    shop_id_str = product.get('shop_id')
                    if shop_id_str:
                        shop_id = uuid.UUID(str(shop_id_str)) if not isinstance(shop_id_str, uuid.UUID) else shop_id_str
                    
                    product_id_str = variation_data.get('product_id')
                    if product_id_str:
                        product_id = uuid.UUID(str(product_id_str)) if not isinstance(product_id_str, uuid.UUID) else product_id_str
                    
                    product_title = product.get('title', '')
                    size = variation_data.get('size', '')
                    color = variation_data.get('color', '')
                    product_sku = product.get('sku', '')
                
                # Convert item_id to integer (order service-dən integer gəlir)
                item_id = item_data['id']
                if not isinstance(item_id, int):
                    item_id = int(item_id)
                
                # Order item'ı oluştur veya güncelle
                OrderItem.objects.update_or_create(
                    id=item_id,
                    defaults={
                        'order': order,
                        'product_variation_id': variation_id,
                        'quantity': item_data['quantity'],
                        'price': price,
                        'base_price': base_price,
                        'original_price': original_price,
                        'shop_id': shop_id,
                        'product_id': product_id,
                        'product_title': product_title,
                        'size': size,
                        'color': color,
                        'product_sku': product_sku
                    }
                )
            
            return order