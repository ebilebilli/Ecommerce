# services.py
import requests
from django.db import transaction
from .models import Order, OrderItem
from datetime import datetime

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
            
            # Order kaydını oluştur veya güncelle
            order, created = Order.objects.update_or_create(
                order_id=order_data['id'],
                defaults={
                    'user_id': order_data['user_id'],
                    'created_at': created_at  # ✅ ÇEVRİLMİŞ TARİX
                }
            )
            
            # Order items'ları işle
            for item_data in order_data['items']:
                variation_data = self.get_product_variation(item_data['product_variation'])
                
                base_price = item_data['price']
                shop_id = None
                product_id = None
                product_title = ""
                size = ""
                color = ""
                product_sku = ""

                if variation_data:
                    base_price = variation_data.get('original_price', item_data['price'])
                    shop_id = variation_data.get('product', {}).get('shop_id')
                    product_id = variation_data.get('product_id')
                    product_title = variation_data.get('product', {}).get('title', '')
                    size = variation_data.get('size', '')
                    color = variation_data.get('color', '')
                    product_sku = variation_data.get('product', {}).get('sku', '')
                
                # Order item'ı oluştur veya güncelle
                OrderItem.objects.update_or_create(
                    id=item_data['id'],
                    defaults={
                        'order': order,
                        'product_variation_id': item_data['product_variation'],
                        'quantity': item_data['quantity'],
                        'price': item_data['price'],
                        'base_price': base_price,
                        'shop_id': shop_id,
                        'product_id': product_id,
                        'product_title': product_title,
                        'size': size,
                        'color': color,
                        'product_sku': product_sku
                    }
                )
            
            return order