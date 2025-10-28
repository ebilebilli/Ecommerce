import httpx
import os
import logging
from typing import Optional
from rest_framework import status
from rest_framework.exceptions import  APIException
from dotenv impor load_dotenv


logger = logging.getLogger(__name__)

load_dotenv()

SHOPCART_SERVICE_URL = os.getenv('SHOPCART_SERVICE_URL')


class ShopCartServiceDataCheck:
    def __init__(self):
        self.base_url = SHOPCART_SERVICE_URL
        self.timeout = 30.0
    
    def get_shopcart_data(self, user_uuid: str) -> Optional[dict]:
        url = f'{self.base_url}/shopcart/mycart/'
        
        try:
            with httpx.Client(timeout=self.timeout, follow_redirects=True) as client:
                response = client.get(
                    url,
                    headers={
                        'Content-Type': 'application/json',
                        'X-User-ID': user_uuid
                    }
                )
            
            if response.status_code == 200:
                cart_data = response.json()
                cart_id = cart_data.get('id')
                logger.info(f'Shopcart data retrieved successfully - Cart ID: {cart_id}, User: {user_uuid}')
                return cart_data
            elif response.status_code == 404:
                logger.warning(f'No shopcart found for user: {user_uuid}')
                return None
            else:
                logger.error(f'Shopcart service error - Status: {response.status_code}, User: {user_uuid}')
                raise APIException(f'Shopcart Service error: {response.status_code}')
        except httpx.RequestError as e:
            logger.error(f'Failed to connect to Shopcart Service - User: {user_uuid}, Error: {str(e)}')
            raise APIException(f'Failed to connect to Shopcart Service: {str(e)}')
        except Exception as e:
            logger.error(f'Unexpected error in shopcart request - User: {user_uuid}, Error: {str(e)}')
            raise


shopcart_client = ShopCartServiceDataCheck()
