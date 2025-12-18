# Product Service

A microservice for managing products, categories, variations, images, and comments in an e-commerce platform.

Built with FastAPI, the Product Service handles product data, stock management, and event-driven communication while enforcing strict ownership-based authorization.

## Overview

The Product Service is responsible for all product-related operations, including:

- Product and category management
- Product variations and images
- User comments
- Stock tracking and validation

The service communicates with other services using RabbitMQ events and performs background processing using Celery.

Authentication is handled by the API Gateway, while authorization is enforced inside the Product Service using database-level ownership checks.

## Technologies

- **Framework**: FastAPI
- **ORM**: SQLAlchemy (2.x)
- **Database**: PostgreSQL
- **Message Broker**: RabbitMQ
- **Async Tasks & Scheduling**: Celery + Celery Beat
- **Migrations**: Alembic
- **Validation**: Pydantic
- **Web Server**: Uvicorn
- **Python**: 3.11+

## Features

### Product Management

- Create, read, update, and delete products
- Product status flags (`active`, `on_sale`, `top_sale`, `top_popular`)
- SKU and base price tracking
- Product lifecycle event publishing

### Category Management

- CRUD operations for categories
- Many-to-many product–category relationships

### Product Variations

- Multiple variations per product (size, color, etc.)
- Stock tracking (`amount`, `amount_limit`)
- Variation-level pricing and discounts
- Automatic stock reduction on order creation

### Product Images

- Multiple images per product variation
- Image upload and deletion
- Ownership-based access control

### Comments

- User comments on product variations
- User-based authorization for comment modification

## Event-Driven Architecture

The Product Service communicates asynchronously with other services using events.

### Published Events

- `product.created`
- `product.updated`
- `product.deleted`

### Consumed Events

- `order.created`  
  Used to reduce stock for ordered product variations.

Event processing is asynchronous and does not block API requests.

## Architecture

### Runtime Components

1. **Web API (FastAPI)**
   - Handles HTTP requests
   - Performs validation and database operations
   - Publishes product lifecycle events

2. **Order Consumer**
   - Dedicated background process
   - Listens to `order.created` events
   - Reduces stock for ordered variations
   - Runs independently of the API

3. **Celery Worker**
   - Executes asynchronous background tasks
   - Handles non-request-based business logic

4. **Celery Beat**
   - Schedules periodic background tasks
   - Triggers daily stock monitoring

All components are built from the same codebase and run as separate containers.

## Authentication & Authorization

### Authentication (Gateway-Based)

- The API Gateway validates the user token
- If the authenticated user owns a shop, the Gateway injects the header:  
  `X-Shop-ID`
- The user identifier is also extracted from the token when required

The Product Service does **not** communicate with a Shop Service for ownership validation.

### Authorization Policies

Authorization is enforced inside the Product Service using explicit permission classes.  
All authorization checks are performed at the database level.

#### Shop-Based Authorization

Applied to:

- Products
- Product variations
- Product images

**Rule**: The resource must belong to the shop identified by `X-Shop-ID`.

Authorization is enforced by querying ownership relationships in the database:

- A product must belong to the shop
- A variation must belong to a product of the shop
- An image must belong to a variation of a shop-owned product

If the resource is missing or not owned by the shop, a **403 Forbidden** error is returned.

#### Comment Authorization (User-Based)

Applied to:

- Comments on product variations

**Rule**: A comment can only be modified by its author.

**Authorization steps**:

1. Fetch comment by ID
2. Compare `comment.user_id` with authenticated user ID
3. Reject the request if they do not match

#### Authorization Failure Handling

- **403 Forbidden** – Authenticated but not authorized
- **404 Not Found** – Resource does not exist (used to hide unauthorized resources)
- Authorization errors immediately stop request processing

## Stock Management

### Real-Time Stock Reduction (Order-Based)

1. Order Service publishes `order.created`
2. Product Service consumer receives the event
3. Stock (`amount`) is reduced per variation
4. Changes are persisted to the database

Errors for missing variations are logged and do not stop processing.

### Periodic Stock Monitoring (Celery)

In addition to real-time stock reduction, the Product Service performs daily stock monitoring using Celery.

#### Business Rule

Each product variation has:

- `amount` – current stock
- `amount_limit` – warning threshold

A variation is considered low stock when:
amount <= amount_limit


#### Periodic Check Logic

- Celery Beat schedules the task once per day
- Celery Worker executes the task
- All product variations are scanned
- Low-stock variations trigger a message

This process runs entirely outside the HTTP request lifecycle.

#### Purpose of Low-Stock Events

Low-stock messages can be consumed by Analytics service.

The Product Service only detects and reports low-stock conditions.

## API Structure

All endpoints are prefixed with `/api/`.

### Products

- `GET /api/products/`
- `GET /api/products/{id}`
- `POST /api/products/`
- `PUT /api/products/{id}`
- `PATCH /api/products/{id}`
- `DELETE /api/products/{id}`

### Categories

- `GET /api/categories/`
- `POST /api/categories/`
- `PUT /api/categories/{id}`
- `DELETE /api/categories/{id}`

### Variations

- `GET /api/products/{id}/variations/`
- `GET /api/products/variations/{id}`
- `POST /api/products/{id}/variations/`
- `PUT /api/products/variations/{id}`
- `DELETE /api/products/variations/{id}`

### Images

- `GET /api/products/variations/{id}/images/`
- `GET /api/products/variations/images/{id}`
- `POST /api/products/variations/{id}/images/`
- `PUT /api/products/variations/images/{id}`
- `DELETE /api/products/variations/images/{image_id}`

### Comments

- `GET /api/products/variations/{id}/comments/`
- `GET /api/products/variations/comments/{id}`
- `POST /api/products/variations/{id}/comments/`
- `PUT /api/products/variations/comments/{id}`
- `DELETE /api/products/variations/comments/{id}`

## Setup & Installation

### Environment Variables

```env
DATABASE_URL=postgresql+psycopg2://postgres:password@localhost:5432/mydb
RABBITMQ_HOST=rabbitmq
RABBITMQ_PORT=5672
RABBITMQ_USER=admin
RABBITMQ_PASS=admin12345
SECRET_KEY=your-secret-key
```

### Local Development

`alembic upgrade head`
`uvicorn src.app.main:app --reload`

##### Run the order consumer separately:

python consumer.py

### Docker Deployment

`docker-compose up -d`

Starts:
- PostgreSQL
- FastAPI web service
- Order consumer
- Celery worker
- Celery beat

### Database Migrations

`alembic revision --autogenerate -m "description"`
`alembic upgrade head`

### Logging

- Console logging by default
- File logging supported via configuration
- Log level configurable via environment variables


### Security

- Gateway-based authentication
- Ownership-based authorization
- Database-level access control
- Input validation via Pydantic
- ORM-based SQL injection protection
- UUID validation

### License

This service is part of the Ecommerce platform.

This is your complete, single, unified `README.md` file. Everything is included in one block with no separate parts or extra text. Just copy the entire content above and save it as `README.md` in your project repository. It will render perfectly on GitHub!

