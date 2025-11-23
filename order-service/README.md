# Order Service

A microservice for managing orders and order items in an e-commerce platform. Built with Django REST Framework, this service provides comprehensive order management capabilities with event-driven architecture, stock validation, and integration with multiple services.

## Overview

The Order Service is responsible for handling all order-related operations including order creation from shopping carts, order item management, status tracking, and order approval workflows. It integrates with shopcart, product, shop, and analytics services through HTTP clients and RabbitMQ messaging.

## Technologies

- **Framework**: Django 5.2.7
- **API**: Django REST Framework 3.16.1
- **Authentication**: JWT via Gateway Header Authentication
- **Database**: PostgreSQL 16
- **Message Broker**: RabbitMQ (Pika 1.3.2)
- **HTTP Client**: httpx 0.28.1, requests 2.32.3
- **API Documentation**: drf-spectacular 0.28.0, drf-yasg 1.21.7
- **Web Server**: Gunicorn 23.0.0
- **Testing**: pytest 8.4.2, pytest-django 4.11.1
- **Python Version**: 3.13+

## Features

### Order Management
- Create orders from shopping carts
- View, update, and delete orders
- Order approval workflow (automatic when all items are delivered/cancelled)
- User-based order ownership
- Order history tracking

### Order Item Management
- Create, read, update, and delete order items
- Order item status tracking (Processing, Shipped, Delivered, Cancelled)
- Product variation and shop association
- Price tracking (stored in smallest currency unit)
- Quantity management

### Shopping Cart Integration
- Create orders directly from shopping cart
- Automatic stock validation before order creation
- Automatic cart cleanup after successful order
- Cart item auto-fix for stock issues (remove out-of-stock items, update quantities)
- Conflict handling when cart is modified

### Stock Validation
- Pre-order stock availability checks
- Real-time stock validation from product service
- Automatic cart updates for insufficient stock
- Product and variation validation
- Active product verification

### Order Approval System
- Automatic order approval when all items reach final status (Delivered/Cancelled)
- Integration with analytics service for approved orders
- Order status tracking

### Event-Driven Architecture
- Publishes `order.created` events to RabbitMQ
- Publishes `order.item.created` events for shop service
- Publishes `order.item.status.updated` events
- Asynchronous event processing

## Architecture

### Components

1. **Web Service**: Main Django application serving REST API endpoints
2. **Event Publisher**: Publishes order lifecycle events to RabbitMQ
3. **Service Clients**: HTTP clients for inter-service communication

### Database Models

- `Order`: Core order entity
  - BigAutoField primary key
  - User UUID association
  - Creation timestamp
  - Approval status
  - Related order items

- `OrderItem`: Individual items in an order
  - Foreign key to Order
  - Status tracking (Processing, Shipped, Delivered, Cancelled)
  - Product variation UUID
  - Product ID and Shop ID (cached from product service)
  - Quantity and price (in smallest currency unit)
  - Indexed for performance

### API Structure

All endpoints are prefixed with `/api/` and include:
- Order CRUD operations
- Order item management
- Order creation from shopping cart
- Order item status updates

### Service Integrations

- **Shopcart Service**: Retrieves cart data, updates/removes cart items
- **Product Service**: Validates products, variations, and stock availability
- **Shop Service**: Receives order item events for shop order tracking
- **Analytics Service**: Sends approved orders for analytics processing

## Setup & Installation

### Prerequisites

- Python 3.13+
- PostgreSQL 16
- RabbitMQ
- Docker & Docker Compose (optional)
- Access to shopcart, product, shop, and analytics services

### Local Development

1. **Clone and navigate to the service**:
```bash
cd order-service
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
SECRET_KEY=your-secret-key
DEBUG=True
POSTGRES_DB=order_db
POSTGRES_USER=order_user
POSTGRES_PASSWORD=order_password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
RABBITMQ_HOST=localhost
RABBITMQ_PORT=5672
RABBITMQ_USER=admin
RABBITMQ_PASS=admin12345
SHOPCART_SERVICE=http://localhost:8004
PRODUCT_SERVICE=http://localhost:8002
SHOP_SERVICE=http://localhost:8007
ANALYTIC_SERVICE=http://localhost:8006
```

4. **Run migrations**:
```bash
cd order_service
python manage.py migrate
```

5. **Create superuser** (optional):
```bash
python manage.py createsuperuser
```

6. **Run the development server**:
```bash
python manage.py runserver
```

### Docker Deployment

1. **Build and start services**:
```bash
docker-compose up -d
```

This will start:
- PostgreSQL database
- Django web service (Gunicorn)

2. **Access the service**:
- API: `http://localhost:8003` (if port mapping enabled)
- Admin: `http://order-admin.localhost` (via Traefik)

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Django secret key | Required |
| `DEBUG` | Debug mode | `True` |
| `POSTGRES_DB` | Database name | Required |
| `POSTGRES_USER` | Database user | Required |
| `POSTGRES_PASSWORD` | Database password | Required |
| `POSTGRES_HOST` | Database host | `localhost` |
| `POSTGRES_PORT` | Database port | `5432` |
| `RABBITMQ_HOST` | RabbitMQ host | `rabbitmq` |
| `RABBITMQ_PORT` | RabbitMQ port | `5672` |
| `RABBITMQ_USER` | RabbitMQ username | `admin` |
| `RABBITMQ_PASS` | RabbitMQ password | Required |
| `SHOPCART_SERVICE` | Shopcart service URL | Required |
| `PRODUCT_SERVICE` | Product service URL | Required |
| `SHOP_SERVICE` | Shop service URL | Required |
| `ANALYTIC_SERVICE` | Analytics service URL | Required |

### Cloud Run Support

The service supports Google Cloud Run deployment with Cloud SQL integration. Set `RUNNING_ON_CLOUDRUN=true` and configure `CLOUD_SQL_CONNECTION_NAME` for Cloud SQL socket connections.

## API Endpoints

### Orders

- `GET /api/orders/` - List all orders
- `POST /api/orders/` - Create new order
- `GET /api/orders/<id>/` - Get order by ID (requires authentication, owner only)
- `PATCH /api/orders/<id>/` - Update order (requires authentication, owner only)
- `DELETE /api/orders/<id>/` - Delete order (requires authentication, owner only)

### Order Items

- `GET /api/order-items/` - List all order items
- `POST /api/order-items/` - Create new order item
- `GET /api/order-items/<id>/` - Get order item by ID (requires authentication, owner only)
- `PATCH /api/order-items/<id>/` - Update order item (requires authentication, owner only)
- `DELETE /api/order-items/<id>/` - Delete order item (requires authentication, owner only)
- `PATCH /api/order-items/<id>/status/` - Update order item status (requires authentication)

### Order Creation from Cart

- `POST /api/orders-from-shopcart/` - Create order from user's shopping cart
  - Requires authentication
  - Validates stock before creating order
  - Automatically fixes cart issues (removes out-of-stock items, updates quantities)
  - Returns 409 Conflict if cart was modified (user must retry)
  - Publishes `order.created` event to RabbitMQ

## Authentication

The service uses Gateway Header Authentication. Include the `X-User-ID` header with a valid UUID in API requests:

```bash
curl -H "X-User-ID: <user-uuid>" http://localhost:8003/api/orders/
```

### Ownership Verification

- Orders and order items can only be accessed/modified by their owner (user_id)
- Status updates can be performed by shop owners (verified by shop service before calling)

## Order Creation Flow

1. **User initiates order creation** from shopping cart
2. **Service retrieves cart data** from shopcart service
3. **Stock validation** for all cart items:
   - Checks product variation existence
   - Validates product is active
   - Verifies stock availability
   - Handles insufficient stock (updates quantity or removes item)
4. **Cart auto-fix** if issues found:
   - Removes out-of-stock items
   - Updates quantities for insufficient stock
   - Returns 409 Conflict with details
5. **Order creation** if all items validated:
   - Creates order record
   - Creates order items
   - Publishes `order.created` event
6. **Event processing** (by other services):
   - Product service reduces stock
   - Shopcart service clears cart
   - Shop service creates shop order items

## Order Approval Flow

1. **Order items** are updated to final status (Delivered=3 or Cancelled=4)
2. **Order model** checks if all items are in final status
3. **Automatic approval** when all items complete
4. **Analytics integration** sends approved order to analytics service

## Testing

Run tests using pytest:

```bash
pytest
```

Or with Django test runner:

```bash
python manage.py test
```

Test files are located in `order_service/tests/`:
- `unit/tests_models_v1.py` - Model tests
- `unit/tests_orders_v1.py` - View and API tests

## API Documentation

Interactive API documentation is available via Swagger/OpenAPI at:
- `/api/schema/swagger-ui/` - Swagger UI
- `/api/schema/redoc/` - ReDoc
- `/api/schema/` - OpenAPI schema

## Event Messaging

### Published Events

The service publishes events to the `order_events` exchange:

- `order.created` - When an order is created from shopping cart
  - Payload: `{order_id, user_uuid, cart_id, items: [{product_variation_id, quantity}]}`
  - Consumed by: Product service (stock reduction), Shopcart service (cart clearing)

- `order.item.created` - When an order item is created
  - Payload: `{order_item_id, order_id, shop_id, product_id, product_variation, quantity, price, status, user_id}`
  - Consumed by: Shop service (creates ShopOrderItem)

- `order.item.status.updated` - When an order item status changes
  - Payload: `{order_item_id, order_id, shop_id, status}`
  - Consumed by: Notification service, Analytics service

### Event Exchange

- **Exchange**: `order_events` (topic exchange, durable)
- **Connection**: Singleton RabbitMQ publisher with connection reuse
- **Error Handling**: Automatic reconnection on connection loss

## Service Clients

### Shopcart Client

- `get_shopcart_data(user_uuid)` - Retrieve user's shopping cart
- `update_cart_item(cart_item_id, quantity, user_id)` - Update cart item quantity
- `delete_cart_item(cart_item_id, user_id)` - Remove cart item

### Product Client

- `get_variation(variation_id, user_id)` - Get product variation details
- `get_product(product_id, user_id)` - Get product details

### Analytics Client

- `send_order(order)` - Send approved order to analytics service

## Logging

Logs are written to:
- File: `order_service/logs/drf_api.log`
- Console: Standard output

Log levels are configurable via Django settings. Separate loggers for:
- `order_service` - Service-specific logs
- `django` - Django framework logs

## Static & Media Files

- Static files: Collected to `staticfiles/` directory
- Media files: Stored in `order_service/media/` (if needed in future)

## Order Item Status

Order items have the following status values:

- `1` - **Processing**: Order item is being prepared
- `2` - **Shipped**: Order item has been shipped
- `3` - **Delivered**: Order item has been delivered (final status)
- `4` - **Cancelled**: Order item has been cancelled (final status)

An order is automatically approved when all its items reach a final status (3 or 4).

## Error Handling

### Stock Validation Errors

When creating an order from cart, if stock issues are detected:
- **409 Conflict** response with details
- Cart is automatically fixed (items removed/updated)
- User must review cart and retry order creation

### Service Communication Errors

- HTTP client errors are logged and raised as API exceptions
- RabbitMQ connection errors trigger automatic reconnection
- Failed event publishing is logged but doesn't fail order creation

## Security Features

- Gateway header authentication
- Ownership verification for order access
- CSRF protection
- SQL injection protection (Django ORM)
- XSS protection
- Input validation via serializers

## License

This service is part of the EcommerceLocal platform.
