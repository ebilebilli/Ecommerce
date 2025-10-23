import httpx
import os
from typing import Optional
from fastapi import HTTPException, status


SHOP_SERVICE_URL = os.getenv('SHOP_SERVICE_URL', 'http://shop-service-web-1:8000')


class ShopServiceClient:
    def __init__(self):
        self.base_url = SHOP_SERVICE_URL
        self.timeout = 30.0
    
    async def get_shop_by_user_id(self, user_id: str) -> Optional[str]:
        try:
            url = f'{self.base_url}/api/user/{user_id}/'
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    url,
                    headers={'Content-Type': 'application/json'}
                )
                
                if response.status_code == 200:
                    shop_data = response.json()
                    shop_id = shop_data.get('id')
                    return shop_id
                elif response.status_code == 404:
                    return None  
                else:
                    raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                        detail=f'Shop Service error: {response.status_code} - {response.text}'
                    )           
        except httpx.RequestError as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f'Failed to connect to Shop Service: {str(e)}'
            )

shop_client = ShopServiceClient()
