import httpx
import asyncio
from dotenv import load_dotenv
from fastapi import FastAPI, Request, HTTPException
from fastapi.openapi.utils import get_openapi
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .logging import logger
from .auth import verify_jwt, PUBLIC_PATHS, handle_login
from .forward import forward_request
from .services import SERVICE_URLS

load_dotenv()

app = FastAPI(
    title="API Gateway",
    version="1.0.0",
    swagger_ui_init_oauth=None,
)
merged_openapi_schema = None

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


@app.middleware('http')
async def log_requests(request: Request, call_next):
    logger.info(f'Incoming request: {request.method} {request.url}')
    try:
        response = await call_next(request)
    except Exception as e:
        logger.error(f'Error handling request: {e}')
        return JSONResponse({'error': str(e)}, status_code=500)
    logger.info(f'Response status: {response.status_code} for {request.method} {request.url}')
    return response


@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    path = request.url.path

    if path == '/user/api/user/login/' and request.method == 'POST':
        return await handle_login(request)

    if not any(path == p or path.startswith(p + '/') for p in PUBLIC_PATHS):
        try:
            payload = await verify_jwt(request)
            request.state.user = payload
            logger.info(f"User set in request.state: {payload}")
        except HTTPException as e:
            logger.error(f"JWT verification failed: {e.detail}")
            return JSONResponse({"detail": e.detail}, status_code=e.status_code)

    response = await call_next(request)
    return response


@app.api_route('/{service}/{full_path:path}', methods=['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])
async def proxy(service: str, full_path: str, request: Request):
    return await forward_request(service, full_path, request)


async def fetch_openapi(service_name: str, url: str, retries=6, delay=2):
    for attempt in range(retries):
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                r = await client.get(f'{url}/openapi.json')
                r.raise_for_status()
                data = r.json()
                new_paths = {f'/{service_name}{p}': v for p, v in data.get('paths', {}).items()}

                for path, methods in new_paths.items():
                    for method_name, method_data in methods.items():
                        method_data['tags'] = [service_name.capitalize()]
                data['paths'] = new_paths
                return data
        except Exception as e:
            print(f'[{service_name}] attempt {attempt+1} failed: {e}')
            await asyncio.sleep(delay)
    return None


async def merge_openapi_schemas():
    merged = get_openapi(title='Gateway API', version='1.0.0', routes=app.routes)
    merged['paths'] = {}

    schemas = await asyncio.gather(
        *[fetch_openapi(name, url) for name, url in SERVICE_URLS.items()]
    )

    for schema in schemas:
        if schema:
            merged['paths'].update(schema.get('paths', {}))
            if 'components' in schema:
                components = merged.setdefault('components', {})
                for key, value in schema['components'].items():
                    components.setdefault(key, {}).update(value)

    # Swagger üçün BearerAuth əlavə et
    merged.setdefault("components", {}).setdefault("securitySchemes", {})["BearerAuth"] = {
        "type": "http",
        "scheme": "bearer",
        "bearerFormat": "JWT"
    }
    for path in merged["paths"].values():
        for method in path.values():
            method["security"] = [{"BearerAuth": []}]

    return merged


async def periodic_refresh(interval: int = 30):
    while True:
        global merged_openapi_schema
        merged_openapi_schema = await merge_openapi_schemas()
        await asyncio.sleep(interval)


@app.on_event('startup')
async def startup_event():
    global merged_openapi_schema
    merged_openapi_schema = await merge_openapi_schemas()
    asyncio.create_task(periodic_refresh())
    print('Merged OpenAPI schema loaded and periodic refresh started.')


@app.get('/openapi.json', include_in_schema=False)
async def custom_openapi():
    if merged_openapi_schema is None:
        return JSONResponse({'error': 'OpenAPI schema not ready'}, status_code=503)
    return JSONResponse(merged_openapi_schema)


@app.get('/', include_in_schema=False)
def root():
    return {'message': 'API Gateway is running'}


app.openapi = lambda: merged_openapi_schema
