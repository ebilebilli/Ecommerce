import os
from dotenv import load_dotenv


load_dotenv()


SHOPCART_SERVICE = os.getenv('SHOPCART_SERVICE')
WISHLIST_SERVICE = os.getenv('WISHLIST_SERVICE', 'http://localhost:8002')
ORDER_SERVICE = os.getenv('ORDER_SERVICE', 'http://localhost:8003')
ANALYTIC_SERVICE = os.getenv('ANALYTIC_SERVICE', 'http://localhost:8004')
USER_SERVICE = os.getenv('USER_SERVICE', 'http://localhost:8005')
PRODUCT_SERVICE = os.getenv('PRODUCT_SERVICE', 'http://localhost:8006')
SHOP_SERVICE = os.getenv('SHOP_SERVICE', 'http://localhost:8007')


SERVICE_URLS = {
    'shop': SHOP_SERVICE,
    'cart': SHOPCART_SERVICE,
    'wishlist': WISHLIST_SERVICE,
    'order': ORDER_SERVICE,
    'analytic': ANALYTIC_SERVICE,
    'user': USER_SERVICE,
    'product': PRODUCT_SERVICE
}
