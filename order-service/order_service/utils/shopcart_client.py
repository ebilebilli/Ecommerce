import httpx
import os
from typing import Optional
from fastapi import HTTPException, status


SHOPCART_SERVICE_URL = os.getenv('SHOPCART_SERVICE_URL', 'http://order_service:8000')


class ShopCartServiceDataCheck:
    def __init__(self):
        self.base_url = SHOPCART_SERVICE_URL
        self.timeout = 30.0
    
    async def get_shopcart_data(self, user_uuid: str) -> Optional[dict]:
        try:
            url = f'{self.base_url}/shopcart/mycart/{shopcart_id}'                                                      
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    url,
                    headers={
                        'Content-Type': 'application/json',
                        'X-User-ID': user_uuid
                    })
                
                if response.status_code == 200:
                    shopcart_data = response.json()
                    shopcart_id = shopcart_data.get('id')
                    return shopcart_id
                elif response.status_code == 404:
                    return None  
                else:
                    raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                        detail=f'Product Service error: {response.status_code} - {response.text}'
                    )           
        except httpx.RequestError as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f'Failed to connect to Shopcart Service: {str(e)}'
            )

shopcart_client = ShopCartServiceDataCheck()
