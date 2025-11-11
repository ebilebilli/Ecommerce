# analitic/product_client.py - TAM FAYL
import requests
from django.conf import settings

class ProductClient:
    def __init__(self):
        self.base_url = getattr(settings, 'PRODUCT_SERVICE', 'http://product-service:8000')
    
    def get_product_variation_data(self, product_variation_uuid, user_id=None):
        """Product servisindən variation məlumatlarını al"""
        try:
            headers = {}
            if user_id:
                headers['X-User-ID'] = str(user_id)
            
            response = requests.get(
                f"{self.base_url}/api/products/variations/{product_variation_uuid}/",
                headers=headers
            )
            if response.status_code == 200:
                data = response.json()
                return {
                    'shop_uuid': data.get('shop_id'),
                    'variation_uuid': product_variation_uuid
                }
            return None
        except requests.RequestException as e:
            print(f"Product service error: {e}")
            return None

# ✅ DÜZGÜN İNSTANCE YARADIN
product_client = ProductClient()