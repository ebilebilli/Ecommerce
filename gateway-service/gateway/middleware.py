import httpx
import json
from fastapi import Request
from fastapi.responses import JSONResponse
from .logging import logger
from .auth import verify_jwt, PUBLIC_PATHS, handle_login, handle_logout
from .services import SERVICE_URLS


async def log_requests_middleware(request: Request, call_next):
    logger.info(f'Incoming request: {request.method} {request.url}')
    try:
        response = await call_next(request)
    except Exception as e:
        logger.error(f'Error handling request: {e}')
        return JSONResponse({'error': str(e)}, status_code=500)
    logger.info(f'Response status: {response.status_code} for {request.method} {request.url}')
    return response


async def auth_middleware(request: Request, call_next):
    path = request.url.path

    if path == '/user/api/user/login/' and request.method == 'POST':
        return await handle_login(request)
    
    if path == '/user/api/user/logout/' and request.method == 'POST':
        # First verify JWT
        try:
            payload = await verify_jwt(request)
            request.state.user = payload
        except Exception as e:
            logger.error(f'JWT verification failed for logout: {e}')
            return JSONResponse({"detail": str(e)}, status_code=401)
        
        # Then handle logout
        return await handle_logout(request)

    if not any(path == p or path.startswith(p + '/') for p in PUBLIC_PATHS):
        try:
            payload = await verify_jwt(request)
            request.state.user = payload
            logger.info(f'User set in request.state: {payload}')
        except Exception as e:
            logger.error(f'JWT verification failed: {e}')
            return JSONResponse({"detail": str(e)}, status_code=401)

    response = await call_next(request)
    return response



