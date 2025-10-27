import os
import httpx
from datetime import datetime, timedelta, timezone
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from jose import jwt, JWTError
from dotenv import load_dotenv
from typing import Set

from .services import SERVICE_URLS
from .logging import logger


load_dotenv()


PUBLIC_PATHS = [
    '/', 
    '/openapi.json', 
    '/docs', 
    '/docs/', 
    '/redoc', 
    '/favicon.ico',
    '/public/',
    # User
    '/user/api/user/login/',
    # '/user/api/user/logout/',  # NOT PUBLIC - needs authentication
    '/user/api/user/register/',
    '/user/api/user/password-reset/request/',
    '/user/api/user/password-reset/confirm/',
    '/user/openapi.json',
    # Shop
    '/shop/api/shops/',
    '/shop/api/shops/{shop_slug}/',
    '/shop/api/shops/{shop_uuid}/'
    '/shop/api/branches/{shop_branch_slug}/',
    '/shop/api/comments/{shop_slug}/',
    '/shop/api/media/{shop_slug}/',
    '/shop/api/social-media/{shop_slug}/',
    # Product 
    '/product/api/categories/',
    '/product/api/categories/{category_id}',
    '/product/api/products/{product_id}',
    '/product/api/products/{product_id}/variations/',
    '/product/api/products/{product_id}/variations/{variation_id}',
    '/product/api/products/{product_id}/variations/{variation_id}/images/',
    '/product/api/products/{product_id}/variations/{variation_id}/comments/',

]


JWT_SECRET = os.getenv('JWT_SECRET')
JWT_ALGORITHM = os.getenv('JWT_ALGORITHM')
HEADER = 'Bearer'
ACCESS_TOKEN_LIFETIME_MINUTES = int(os.getenv('ACCESS_TOKEN_LIFETIME_MINUTES', 60))
REFRESH_TOKEN_LIFETIME_DAYS = int(os.getenv('REFRESH_TOKEN_LIFETIME_DAYS', 7))
BLACKLISTED_TOKENS: Set[str] = set()


def add_to_blacklist(token: str):
    BLACKLISTED_TOKENS.add(token)


def is_token_blacklisted(token: str) -> bool:
    return token in BLACKLISTED_TOKENS


def create_access_token(payload: dict):
    expire = datetime.now(tz=timezone.utc) + timedelta(minutes=ACCESS_TOKEN_LIFETIME_MINUTES)
    payload.update({'exp': expire})
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token


def create_refresh_token(payload: dict):
    expire = datetime.now(tz=timezone.utc) + timedelta(days=REFRESH_TOKEN_LIFETIME_DAYS)
    payload.update({'exp': expire})
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token


async def verify_jwt(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer"):
        logger.warning("No Authorization header found or invalid")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token not found or incorrect format."
        )
    
    token = auth_header.split(" ")[1]
    if is_token_blacklisted(token):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has been revoked (logged out).")
    
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        request.state.user = payload  
        logger.info(f"JWT verified for user: {payload.get('sub')}")
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is invalid or expired."
        )


async def handle_login(request):
    body = await request.json()
    async with httpx.AsyncClient() as client:
        res = await client.post(f'{SERVICE_URLS['user']}/api/user/login/', json=body)

    if res.status_code != 200:
        return JSONResponse(res.json(), status_code=res.status_code)

    user = res.json()
    user_uuid = user.get('uuid')
    if not user_uuid:
        return JSONResponse({'detail': 'User UUID not returned'}, status_code=500)

    access = create_access_token({'sub': str(user_uuid)})
    refresh = create_refresh_token({'sub': str(user_uuid)})
    return JSONResponse({
        'access_token': access,
        'refresh_token': refresh,
        'token_type': 'Bearer'
    })


async def handle_logout(request: Request):
    auth_header = request.headers.get("Authorization")
    
    # Parse body safely (optional)
    body = {}
    refresh_token = None
    try:
        body = await request.json()
        refresh_token = body.get("refresh_token")
    except Exception:
        pass  # Body optional
    
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authorization header missing or invalid")

    access_token = auth_header.split(" ")[1]
    add_to_blacklist(access_token)
    
    if refresh_token:
        add_to_blacklist(refresh_token)
    
    return JSONResponse({
        "detail": "Successfully logged out"
    }, status_code=200)

