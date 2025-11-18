# product_client.py
import requests


class ProductClient:
    def __init__(self):
        self.base_url = "http://product-service:8000"

    def get_product_variation_data(self, variation_id):
        try:
            response = requests.get(
                f"{self.base_url}/api/v1/products/variations/{variation_id}"
            )

            if response.status_code == 200:
                data = response.json()
                return {
                    "base_price": data.get("original_price"),
                    "original_price": data.get("original_price"),
                    "size": data.get("size"),
                    "color": data.get("color"),
                    "product_title": data["product"]["title"],
                    "product_sku": data["product"]["sku"],
                    "shop_id": data["product"]["shop_id"],
                }

        except Exception as e:
            print("Product service error:", e)

        return None


product_client = ProductClient()
