import httpx
import os
from typing import Optional
from fastapi import HTTPException, status


PRODUCT_SERVICE_URL = os.getenv('PRODUCT_SERVICE_URL', 'http://fastapi_app:8000')


class ProductServiceDataCheck:
    def __init__(self):
        self.base_url = PRODUCT_SERVICE_URL
        self.timeout = 30.0
    
    async def get_product_data_by_variation_id(self, product_id: str) -> Optional[dict]:
        try:
            url = f'{self.base_url}/api/products/{product_id}'    # Tempororily it is product id beacause of 
                                                                # there is not product variation endpoint for spesific product variation id
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    url,
                    headers={'Content-Type': 'application/json'}
                )
                
                if response.status_code == 200:
                    product_data = response.json()
                    product_id = product_data.get('id')
                    return product_id
                elif response.status_code == 404:
                    return None  
                else:
                    raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                        detail=f'Product Service error: {response.status_code} - {response.text}'
                    )           
        except httpx.RequestError as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f'Failed to connect to Product Service: {str(e)}'
            )

product_client = ProductServiceDataCheck()
