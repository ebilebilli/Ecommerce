# Gateway Service

A unified API gateway for the e-commerce microservices platform. Built with FastAPI, this service acts as the single entry point for all client requests, providing authentication, request routing, and unified API documentation.

## Overview

The Gateway Service is the central entry point for all API requests in the e-commerce platform. It handles authentication, request forwarding to backend services, JWT token management, and merges OpenAPI schemas from all microservices into a single unified API documentation. It implements the API Gateway pattern, providing a single point of access and simplifying client interactions with the microservices architecture.

## Role & Responsibilities

### Central Entry Point
- Single entry point for all client requests
- Routes requests to appropriate backend services
- Hides internal service architecture from clients
- Provides unified API interface

### Authentication & Authorization
- JWT token validation and management
- Token blacklisting for logout functionality
- Public endpoint whitelisting
- User context propagation to backend services

### Request Routing
- Dynamic service routing based on URL path
- Request/response transformation
- Header management and forwarding
- Error handling and service availability checks

### API Documentation
- Merges OpenAPI schemas from all microservices
- Provides unified Swagger UI and ReDoc documentation
- Periodic schema refresh (every 30 seconds)
- Single documentation endpoint for all services

## Technologies

- **Framework**: FastAPI 0.119.0+
- **HTTP Client**: httpx 0.28.1 (async HTTP requests)
- **Authentication**: python-jose 3.5.0 (JWT encoding/decoding)
- **Caching**: Redis 7.0.1 (token blacklist storage)
- **Web Server**: Uvicorn 0.37.0+
- **Python Version**: 3.13+

## Architecture

### Components

1. **API Gateway**: Main FastAPI application handling all incoming requests
2. **Authentication Middleware**: JWT validation and user context extraction
3. **Request Forwarding**: Async HTTP client for proxying requests to backend services
4. **OpenAPI Merger**: Aggregates schemas from all microservices
5. **Redis Client**: Token blacklist management

### Supported Services

The gateway routes requests to the following microservices:

- **user**: User authentication and profile management
- **shop**: Shop management and operations
- **product**: Product catalog and variations
- **cart**: Shopping cart operations
- **order**: Order processing
- **wishlist**: Wishlist management
- **analytic**: Analytics and reporting
- **elasticsearch**: Search functionality

### Request Flow

1. Client sends request to gateway: `/{service}/{path}`
2. Authentication middleware validates JWT (if required)
3. Gateway extracts user context from JWT
4. Request is forwarded to appropriate backend service
5. User ID is added to `X-User-ID` header
6. Response is returned to client

## Features

### Authentication

- **JWT Token Validation**: Verifies JWT tokens on protected endpoints
- **Token Blacklisting**: Redis-based token revocation for logout
- **Public Endpoints**: Whitelist of endpoints that don't require authentication
- **User Context**: Extracts user ID from JWT and forwards to backend services

### Request Forwarding

- **Dynamic Routing**: Routes based on service name in URL path
- **Header Management**: Filters and forwards appropriate headers
- **Query Parameters**: Preserves query strings in forwarded requests
- **Error Handling**: Graceful handling of service unavailability
- **Timeout Management**: 30-second timeout for service requests

### OpenAPI Schema Merging

- **Automatic Aggregation**: Fetches OpenAPI schemas from all services
- **Path Prefixing**: Adds service name prefix to all paths
- **Schema Merging**: Combines components and schemas from all services
- **Periodic Refresh**: Updates schemas every 30 seconds
- **Retry Logic**: 3 retry attempts with exponential backoff

### Public Endpoints

The following endpoints are publicly accessible without authentication:

- **User Service**: Login, register, password reset
- **Shop Service**: Shop listings, shop details (GET only)
- **Product Service**: Product listings, product details (GET only)
- **Elasticsearch Service**: Search endpoints (GET only)
- **Documentation**: Swagger UI, ReDoc, OpenAPI JSON

## Request Routing

### URL Pattern

All requests follow the pattern: `/{service}/{path}`

Examples:
- `GET /user/api/user/profile/` → Routes to user service
- `POST /shop/api/create/` → Routes to shop service
- `GET /product/api/products/` → Routes to product service
- `GET /cart/api/mycart` → Routes to shopcart service

### Header Forwarding

The gateway:
- Forwards `Authorization` header to backend services
- Adds `X-User-ID` header extracted from JWT token
- Filters out internal headers (host, connection, etc.)
- Preserves custom headers from client

## Authentication Flow

### Login

1. Client sends credentials to `/user/api/user/login/`
2. Gateway forwards to user service
3. User service validates credentials and returns user UUID
4. Gateway generates JWT access and refresh tokens
5. Tokens returned to client

### Protected Requests

1. Client includes `Authorization: Bearer <token>` header
2. Gateway validates JWT token
3. Checks token blacklist in Redis
4. Extracts user ID from token payload
5. Adds `X-User-ID` header to forwarded request

### Logout

1. Client sends logout request with `Authorization` header
2. Gateway extracts access token
3. Adds token to Redis blacklist
4. Optionally blacklists refresh token if provided

## JWT Configuration

- **Access Token Lifetime**: Configurable (default: 60 minutes)
- **Refresh Token Lifetime**: Configurable (default: 7 days)
- **Algorithm**: Configurable (typically HS256)
- **Secret**: Environment variable `JWT_SECRET`
- **Token Format**: `Bearer <token>`

## Token Blacklisting

- **Storage**: Redis set `blacklisted_tokens`
- **Check**: Validated on every authenticated request
- **Persistence**: Tokens remain blacklisted until Redis flush
- **Logout**: Both access and refresh tokens can be blacklisted

## Public Endpoints Configuration

Public endpoints are defined in two ways:

1. **Public Paths**: Exact path matches (e.g., `/docs`, `/openapi.json`)
2. **Public Endpoints**: Path patterns with allowed HTTP methods

Examples:
- `/user/api/user/login/` - POST only
- `/shop/api/shops/` - GET only
- `/product/api/products/` - GET only

## OpenAPI Schema Merging

### Process

1. On startup, fetches `/openapi.json` from all services
2. Prefixes all paths with service name
3. Merges all schemas into single OpenAPI document
4. Adds Bearer authentication scheme
5. Refreshes every 30 seconds

### Features

- **Retry Logic**: 3 attempts per service with 2-second delay
- **Error Handling**: Continues if a service schema is unavailable
- **Path Transformation**: `/api/users/` → `/user/api/users/`
- **Tag Organization**: Groups endpoints by service name

## Error Handling

### Service Unavailable (503)
- Returned when backend service is unreachable
- Includes error message in response

### Unauthorized (401)
- Missing or invalid JWT token
- Token is blacklisted
- Token expired

### Bad Request (400)
- Unknown service name in URL
- Invalid request format

## Logging

Logs are written to:
- **File**: `gateway.log`
- **Console**: Standard output

Log format: `%(asctime)s [%(levelname)s] %(message)s`

Logs include:
- Incoming requests (method, URL)
- Forwarded requests (service, URL)
- Response status codes
- Authentication events
- OpenAPI schema refresh events

## Setup & Installation

### Prerequisites

- Python 3.13+
- Docker & Docker Compose
- Redis (for token blacklisting)
- All backend microservices running

### Quick Start

1. **Create `.env` file**:
```env
JWT_SECRET=your-secret-key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_LIFETIME_MINUTES=60
REFRESH_TOKEN_LIFETIME_DAYS=7
REDIS_HOST=localhost
REDIS_PORT=6379
USER_SERVICE=http://user-service:8000
SHOP_SERVICE=http://shop-service:8000
PRODUCT_SERVICE=http://product-service:8000
SHOPCART_SERVICE=http://shopcart-service:8000
ORDER_SERVICE=http://order-service:8000
WISHLIST_SERVICE=http://wishlist-service:8000
ANALYTIC_SERVICE=http://analytic-service:8000
ELASTICSEARCH_SERVICE=http://elasticsearch-service:8000
```

2. **Start with Docker**:
```bash
docker-compose up -d
```

3. **Access gateway**:
- API: `http://gateway.localhost`
- Docs: `http://gateway.localhost/docs`

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `JWT_SECRET` | Secret key for JWT encoding | Required |
| `JWT_ALGORITHM` | JWT algorithm | `HS256` |
| `ACCESS_TOKEN_LIFETIME_MINUTES` | Access token lifetime | `60` |
| `REFRESH_TOKEN_LIFETIME_DAYS` | Refresh token lifetime | `7` |
| `REDIS_HOST` | Redis host | `localhost` |
| `REDIS_PORT` | Redis port | `6379` |
| `{SERVICE}_SERVICE` | Backend service URLs | Required |

## API Documentation

The gateway provides unified API documentation:

- **Swagger UI**: `http://gateway.localhost/docs`
- **ReDoc**: `http://gateway.localhost/redoc`
- **OpenAPI JSON**: `http://gateway.localhost/openapi.json`

All endpoints from all microservices are available in a single documentation interface.

## Security Features

- **JWT Validation**: Secure token verification
- **Token Blacklisting**: Prevents use of revoked tokens
- **Header Filtering**: Removes sensitive internal headers
- **CORS Support**: Configurable CORS middleware
- **Request Timeout**: Prevents hanging requests

## Performance Considerations

- **Async Operations**: All HTTP requests are asynchronous
- **Connection Pooling**: httpx maintains connection pools
- **Schema Caching**: OpenAPI schemas cached and refreshed periodically
- **Redis Caching**: Fast token blacklist lookups

## License

This service is part of the EcommerceLocal platform.

