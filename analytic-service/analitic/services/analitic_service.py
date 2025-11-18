# services/analitic_service.py

from .product_client import product_client
from ..models import Order, OrderItem


class AnaliticService:

    def process_order_completed(self, data):
        """
        Order tamamlandıqda analitik servisdə qeyd yaratmaq
        """

        # 1) ORDER YARAT və ya YENİLƏ
        order, _ = Order.objects.update_or_create(
            order_id=data["id"],
            defaults={
                "user_id": data["user_id"],
                "created_at": data["created_at"]
            }
        )

        # 2) HƏR ORDER ITEM ÜÇÜN PRODUCT SERVİSDƏN MƏLUMAT AL VƏ DB-YƏ YAZ
        for item in data["items"]:
            variation_id = item["product_variation"]

            # Product mikroservisə GET sorğusu
            variation = product_client.get_product_variation_data(variation_id)

            if not variation:
                continue  # əgər məhsul tapılmadısa keç

            # OrderItem-i DB-yə yaz
            OrderItem.objects.update_or_create(
                item_id=item["id"],
                defaults={
                    "order": order,
                    "product_variation_id": variation_id,
                    "quantity": item["quantity"],
                    "price": item["price"],

                    # Product API-dən alınan məlumatlar
                    "base_price": variation.get("base_price"),
                    "original_price": variation.get("original_price"),
                    "size": variation.get("size"),
                    "color": variation.get("color"),
                    "product_title": variation.get("product_title"),
                    "product_sku": variation.get("product_sku"),
                    "shop_id": variation.get("shop_id"),
                }
            )

        return order
