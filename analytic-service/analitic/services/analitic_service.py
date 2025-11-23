# services/analitic_service.py

import uuid
from datetime import datetime
from decimal import Decimal
from .product_client import product_client
from ..models import Order, OrderItem


class AnaliticService:

    def process_order_completed(self, data):
        """
        Order tamamlandıqda analitik servisdə qeyd yaratmaq
        """

        created_at = data["created_at"]
        if isinstance(created_at, str):
            if created_at.endswith('Z'):
                created_at = created_at.replace('Z', '+00:00')
            created_at = datetime.fromisoformat(created_at)

        # Convert order_id and user_id to UUID
        order_id = data["id"]
        if not isinstance(order_id, uuid.UUID):
            # If it's a string or integer, convert to UUID
            if isinstance(order_id, int):
                # Convert integer to UUID using a deterministic method
                order_id = uuid.uuid5(uuid.NAMESPACE_DNS, f"order-{order_id}")
            else:
                order_id = uuid.UUID(str(order_id))
        
        user_id = data["user_id"]
        if not isinstance(user_id, uuid.UUID):
            user_id = uuid.UUID(str(user_id))

        # 1) ORDER YARAT və ya YENİLƏ
        order, _ = Order.objects.update_or_create(
            order_id=order_id,
            defaults={
                "user_id": user_id,
                "created_at": created_at
            }
        )

        # 2) HƏR ORDER ITEM ÜÇÜN PRODUCT SERVİSDƏN MƏLUMAT AL VƏ DB-YƏ YAZ
        for item in data["items"]:
            variation_id = item["product_variation"]
            if not isinstance(variation_id, uuid.UUID):
                variation_id = uuid.UUID(str(variation_id))

            # Product mikroservisə GET sorğusu
            variation = product_client.get_product_variation_data(variation_id)

            if not variation:
                continue  # əgər məhsul tapılmadısa keç

            # Convert item id to UUID
            item_id = item["id"]
            if not isinstance(item_id, uuid.UUID):
                if isinstance(item_id, int):
                    # Convert integer to UUID using a deterministic method
                    item_id = uuid.uuid5(uuid.NAMESPACE_DNS, f"order-item-{item_id}")
                else:
                    item_id = uuid.UUID(str(item_id))

            # Convert price to Decimal
            price = item["price"]
            if not isinstance(price, Decimal):
                price = Decimal(str(price))

            # Convert base_price and original_price to Decimal
            base_price = variation.get("base_price")
            if base_price is not None and not isinstance(base_price, Decimal):
                base_price = Decimal(str(base_price))
            elif base_price is None:
                base_price = Decimal('1.00')  # Default value
            
            original_price = variation.get("original_price")
            if original_price is not None and not isinstance(original_price, Decimal):
                original_price = Decimal(str(original_price))

            # Convert shop_id to UUID if it's a string
            shop_id = variation.get("shop_id")
            if shop_id is not None and not isinstance(shop_id, uuid.UUID):
                shop_id = uuid.UUID(str(shop_id))

            # OrderItem-i DB-yə yaz
            OrderItem.objects.update_or_create(
                id=item_id,
                defaults={
                    "order": order,
                    "product_variation_id": variation_id,
                    "quantity": item["quantity"],
                    "price": price,

                    # Product API-dən alınan məlumatlar
                    "base_price": base_price,
                    "original_price": original_price,
                    "size": variation.get("size"),
                    "color": variation.get("color"),
                    "product_title": variation.get("product_title"),
                    "product_sku": variation.get("product_sku"),
                    "shop_id": shop_id,
                }
            )

        return order
