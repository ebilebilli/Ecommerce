# Product Service

A microservice for managing products, categories, variations, images, and comments in an e-commerce platform. Built with FastAPI, this service provides comprehensive product management capabilities with event-driven architecture, stock management, and integration with shop service.

## Overview

The Product Service is responsible for handling all product-related operations including product creation, category management, product variations, images, comments, and stock management. It integrates with shop service for shop validation and publishes product lifecycle events to RabbitMQ. The service also consumes order events to automatically reduce stock when orders are created.

## Technologies

- **Framework**: FastAPI 0.118.0+
- **ORM**: SQLAlchemy 2.0.35+
- **Database**: PostgreSQL 15+
- **Message Broker**: RabbitMQ (Pika 1.3.2)
- **HTTP Client**: httpx 0.28.1
- **Migrations**: Alembic 1.13.1+
- **Validation**: Pydantic 2.9.2+
- **Web Server**: Uvicorn 0.30.6+
- **Python Version**: 3.11+

## Features

### Product Management
- Create, read, update, and delete products
- Product status management (active/inactive)
- Product flags (on_sale, top_sale, top_popular)
- SKU (Stock Keeping Unit) management
- Base price tracking
- Shop association (products belong to shops)
- Product lifecycle events (created, updated, deleted)

### Category Management
- Create, read, update, and delete categories
- Product-category associations (many-to-many)
- Category-based product filtering

### Product Variations
- Multiple variations per product (size, color, etc.)
- Stock management (amount, amount_limit)
- Variation-specific pricing (price, original_price, discount)
- Stock count tracking
- Automatic stock reduction on order creation

### Product Images
- Multiple images per product variation
- Image management (create, read, delete)
- Variation-specific image galleries

### Comments
- User comments on product variations
- User ID tracking via header authentication
- Comment retrieval by variation

### Stock Management
- Real-time stock tracking per variation
- Automatic stock reduction when orders are created
- Stock validation before order creation (handled by order service)
- Stock amount and limit tracking

### Event-Driven Architecture
- Publishes `product.created` events to RabbitMQ
- Publishes `product.updated` events
- Publishes `product.deleted` events
- Consumes `order.created` events to reduce stock
- Asynchronous event processing

## Architecture

### Components

1. **Web Service**: FastAPI application serving REST API endpoints
2. **Order Consumer**: Background service consuming order events from RabbitMQ to reduce stock
3. **Event Publisher**: Publishes product lifecycle events to other services

### Database Models

- `Product`: Core product entity
  - UUID primary key
  - Shop association
  - Title, description, SKU
  - Status flags (on_sale, is_active, top_sale, top_popular)
  - Base price
  - Many-to-many relationship with categories

- `Category`: Product categories
  - UUID primary key
  - Category name and metadata

- `ProductVariation`: Product variations (size, color, etc.)
  - UUID primary key
  - Foreign key to Product
  - Size, color attributes
  - Stock tracking (amount, amount_limit)
  - Pricing (price, original_price, discount)
  - Count tracking

- `ProductImage`: Product variation images
  - UUID primary key
  - Foreign key to ProductVariation
  - Image URL/path

- `Comment`: User comments on variations
  - UUID primary key
  - Foreign key to ProductVariation
  - User ID association
  - Comment content

### API Structure

All endpoints are prefixed with `/api/` and include:
- Product CRUD operations
- Category management
- Product variation management
- Product image management
- Comment management

### Service Integrations

- **Shop Service**: Validates shop ownership when creating products
- **Order Service**: Receives order events to reduce stock

## Setup & Installation

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- RabbitMQ
- Docker & Docker Compose (optional)
- Access to shop service

### Local Development

1. **Clone and navigate to the service**:
```bash
cd product-service
```

2. **Install dependencies** (using uv or pip):
```bash
uv sync
# or
pip install -r requirements.txt
```

3. **Configure environment variables**:
Create a `.env` file with:
```env
DATABASE_URL=postgresql+psycopg2://postgres:password@localhost:5432/mydb
SHOP_SERVICE_URL=http://localhost:8007
RABBITMQ_HOST=localhost
RABBITMQ_PORT=5672
RABBITMQ_USER=admin
RABBITMQ_PASS=admin12345
SECRET_KEY=your-secret-key
```

4. **Run migrations**:
```bash
alembic upgrade head
```

5. **Run the development server**:
```bash
uvicorn src.app.main:app --reload --host 0.0.0.0 --port 8000
```

6. **Run the consumer** (in a separate terminal):
```bash
python consumer.py
```

### Docker Deployment

1. **Build and start services**:
```bash
docker-compose up -d
```

This will start:
- PostgreSQL database
- FastAPI web service
- Order consumer service

2. **Access the service**:
- API: `http://localhost:8002` (if port mapping enabled)
- API Docs: `http://localhost:8002/docs` (Swagger UI)
- Admin: `http://product-admin.localhost` (via Traefik)

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | Required |
| `SHOP_SERVICE_URL` | Shop service URL | `http://localhost:8007` |
| `RABBITMQ_HOST` | RabbitMQ host | `rabbitmq` |
| `RABBITMQ_PORT` | RabbitMQ port | `5672` |
| `RABBITMQ_USER` | RabbitMQ username | `admin` |
| `RABBITMQ_PASS` | RabbitMQ password | Required |
| `SECRET_KEY` | Application secret key | Required |

## API Endpoints

### Products

- `GET /api/products/` - List all products (with pagination: skip, limit)
- `GET /api/products/{product_id}` - Get product by ID
- `POST /api/products/` - Create new product
  - Requires: `X-User-ID` header (validates shop ownership)
  - Body: Product data with categories
  - Publishes `product.created` event
- `PUT /api/products/{product_id}` - Update product (full update)
  - Publishes `product.updated` event
- `PATCH /api/products/{product_id}` - Update product (partial update)
  - Requires: `X-User-ID` header (validates ownership)
  - Publishes `product.updated` event
- `DELETE /api/products/{product_id}` - Delete product
  - Publishes `product.deleted` event

### Categories

- `GET /api/categories/` - List all categories
- `GET /api/categories/{category_id}` - Get category by ID
- `POST /api/categories/` - Create new category
- `PUT /api/categories/{category_id}` - Update category
- `DELETE /api/categories/{category_id}` - Delete category

### Product Variations

- `GET /api/products/{product_id}/variations/` - List variations for a product
- `GET /api/products/variations/{variation_id}` - Get variation by ID
- `POST /api/products/{product_id}/variations/` - Create variation
- `PUT /api/products/variations/{variation_id}` - Update variation
- `DELETE /api/products/variations/{variation_id}` - Delete variation

### Product Images

- `GET /api/products/variations/{variation_id}/images/` - List images for a variation
- `POST /api/products/variations/{variation_id}/images/` - Upload image
- `DELETE /api/products/variations/{variation_id}/images/{image_id}` - Delete image

### Comments

- `GET /api/products/variations/{variation_id}/comments/` - List comments for a variation
- `POST /api/products/variations/{variation_id}/comments/` - Create comment
  - Requires: `X-User-ID` header

## Authentication

The service uses Gateway Header Authentication. Include the `X-User-ID` header with a valid UUID in API requests:

```bash
curl -H "X-User-ID: <user-uuid>" http://localhost:8002/api/products/
```

### Shop Ownership Validation

When creating products, the service:
1. Extracts `X-User-ID` from headers
2. Calls shop service to get user's shop
3. Associates product with the shop
4. Returns error if user doesn't have a shop

## Stock Management

### Stock Reduction Flow

1. **Order Service** creates an order and publishes `order.created` event
2. **Product Service Consumer** receives the event
3. **Stock Reduction**:
   - Finds product variations by ID
   - Reduces `amount` (stock) by ordered quantity
   - Commits changes to database
   - Logs stock changes
4. **Error Handling**:
   - Logs errors for missing variations
   - Continues processing other items
   - Stock can go negative (shouldn't happen with proper validation)

### Stock Fields

- `amount`: Current stock quantity (BigInteger)
- `amount_limit`: Stock limit/warning threshold (BigInteger)
- `count`: Additional count tracking (BigInteger)

## Testing

Run tests using pytest:

```bash
pytest
```

## API Documentation

Interactive API documentation is available via Swagger/OpenAPI at:
- `/docs` - Swagger UI
- `/redoc` - ReDoc
- `/openapi.json` - OpenAPI schema JSON

## Event Messaging

### Published Events

The service publishes events to the `product_events` exchange:

- `product.created` - When a product is created
  - Payload: `{event_type, product_id, product_data: {id, shop_id, title, about, on_sale, is_active, top_sale, top_popular, sku, created_at}}`

- `product.updated` - When a product is updated
  - Payload: Same as `product.created`

- `product.deleted` - When a product is deleted
  - Payload: `{event_type, product_id}`

### Consumed Events

The service consumes events from the `order_events` exchange:

- `order.created` - Reduces stock for ordered variations
  - Payload: `{event_type, data: {order_id, user_uuid, cart_id, items: [{product_variation_id, quantity}]}}`
  - Processing:
    - Finds each variation by ID
    - Reduces `amount` by `quantity`
    - Commits changes
    - Logs success/errors

### Event Exchange

- **Exchange**: `product_events` (topic exchange, durable)
- **Queue**: `product_events` (durable)
- **Connection**: New connection per publish (closes after publishing)

## Database Migrations

The service uses Alembic for database migrations:

```bash
# Create a new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1
```

## Logging

Logs are written to:
- Console: Standard output
- File: `logs/product_service.log` (if configured)

Log levels are configurable via environment variables:
- `LOG_LEVEL`: Logging level (default: INFO)
- `LOG_FORMAT`: Log format string
- `LOG_FILE`: Log file path

## Service Clients

### Shop Client

- `get_shop_by_user_id(user_id)` - Get user's shop ID
  - Returns shop UUID if user has a shop
  - Returns None if user doesn't have a shop
  - Raises HTTPException on service errors

## Error Handling

### Product Creation Errors

- **400 Bad Request**: Missing or invalid user ID
- **400 Bad Request**: User doesn't have a shop
- **503 Service Unavailable**: Shop service connection error

### Stock Reduction Errors

- Missing variations are logged but don't stop processing
- Stock can go negative (shouldn't happen with proper validation)
- Errors are logged with full traceback

## Security Features

- Gateway header authentication
- Shop ownership validation
- SQL injection protection (SQLAlchemy ORM)
- Input validation via Pydantic schemas
- UUID validation

## License

This service is part of the EcommerceLocal platform.

