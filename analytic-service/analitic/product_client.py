# product_client.py
import requests
import os
from dotenv import load_dotenv

load_dotenv('')


class ProductClient:
    def __init__(self):
        self.base_url = os.getenv('PRODUCT_SERVICE')
    def get_product_variation_data(self, variation_id):
        try:
            response = requests.get(
                f"{self.base_url}/api/v1/products/variations/{variation_id}"
            )

            if response.status_code == 200:
                data = response.json()
                product = data.get("product")
                if not product:
                    return None
                
                return {
                    "base_price": data.get("original_price"),
                    "original_price": data.get("original_price"),
                    "size": data.get("size"),
                    "color": data.get("color"),
                    "product_title": product.get("title", ""),
                    "product_sku": product.get("sku", ""),
                    "shop_id": product.get("shop_id"),
                }

        except Exception as e:
            pass

        return None


product_client = ProductClient()
