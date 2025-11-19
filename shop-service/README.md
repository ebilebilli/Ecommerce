# Shop Service

A microservice for managing shops, branches, comments, media, and order items in an e-commerce platform. Built with Django REST Framework, this service provides comprehensive shop management capabilities with event-driven architecture.

## Overview

The Shop Service is responsible for handling all shop-related operations including shop creation, management, branch management, user comments, media uploads, and order item tracking. It integrates with other microservices through RabbitMQ messaging and provides RESTful APIs for shop operations.

## Technologies

- **Framework**: Django 5.2.7
- **API**: Django REST Framework 3.16.1
- **Authentication**: JWT via Gateway Header Authentication
- **Database**: PostgreSQL 16
- **Message Broker**: RabbitMQ (Pika 1.3.2)
- **Image Processing**: Pillow 11.3.0
- **HTTP Client**: httpx 0.28.1
- **API Documentation**: drf-spectacular 0.28.0
- **Web Server**: Gunicorn 23.0.0
- **Testing**: pytest 8.4.2, pytest-django 4.11.1
- **Python Version**: 3.13+

## Features

### Shop Management
- Create, read, update, and delete shops
- Shop status management (APPROVED, PENDING, REJECTED)
- Shop verification system
- Shop profile images
- Unique slug generation for SEO-friendly URLs
- User-based shop ownership

### Shop Branches
- Multiple branch support per shop
- Geographic location (latitude/longitude)
- Branch-specific information and contact details
- Branch activation/deactivation

### Comments & Ratings
- User comments on shops
- 1-5 star rating system
- Comment moderation capabilities
- Chronological ordering

### Media Management
- Shop profile images
- Multiple media uploads per shop
- Alt text support for accessibility

### Social Media Integration
- Link multiple social media accounts per shop
- Support for various social platforms

### Order Item Tracking
- Real-time order item synchronization via RabbitMQ
- Order status management (Processing, Shipped, Delivered, Cancelled)
- Shop-specific order item views
- Integration with order service

### Event-Driven Architecture
- Publishes shop events (created, updated, deleted) to RabbitMQ
- Consumes order item events from order service
- Asynchronous event processing

## Architecture

### Components

1. **Web Service**: Main Django application serving REST API endpoints
2. **Order Consumer**: Background service consuming order item events from RabbitMQ
3. **Event Publisher**: Publishes shop lifecycle events to other services

### Database Models

- `Shop`: Core shop entity with status, verification, and ownership
- `ShopBranch`: Physical locations/branches of shops
- `ShopComment`: User reviews and ratings
- `ShopMedia`: Image galleries for shops
- `ShopSocialMedia`: Social media links
- `ShopOrderItem`: Order items associated with shops

### API Structure

All endpoints are prefixed with `/api/` and include:
- Shop CRUD operations
- Branch management
- Comment management
- Media upload/delete
- Social media management
- Order item queries and status updates

## Setup & Installation

### Prerequisites

- Python 3.13+
- PostgreSQL 16
- RabbitMQ
- Docker & Docker Compose (optional)

### Local Development

1. **Clone and navigate to the service**:
```bash
cd shop-service
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
POSTGRES_DB=shop_db
POSTGRES_USER=shop_user
POSTGRES_PASSWORD=shop_password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
RABBITMQ_HOST=localhost
RABBITMQ_PORT=5672
RABBITMQ_USER=admin
RABBITMQ_PASS=admin12345
```

4. **Run migrations**:
```bash
cd shop_service
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
- Order item consumer service

2. **Access the service**:
- API: `http://localhost:8007` (if port mapping enabled)
- Admin: `http://shop-admin.localhost` (via Traefik)

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

### Cloud Run Support

The service supports Google Cloud Run deployment with Cloud SQL integration. Set `RUNNING_ON_CLOUDRUN=true` and configure `CLOUD_SQL_CONNECTION_NAME` for Cloud SQL socket connections.

## API Endpoints

### Shops
- `GET /api/shops/` - List all shops
- `GET /api/shops/<uuid>/` - Get shop by UUID
- `GET /api/shops/<slug>/` - Get shop by slug
- `POST /api/create/` - Create new shop
- `GET/PUT/DELETE /api/shops/<slug>/management/` - Manage shop
- `GET /api/user/<user_id>/` - Get user's shop

### Branches
- `GET /api/branches/<shop_slug>/` - List shop branches
- `GET /api/branches/<branch_slug>/` - Get branch details
- `POST /api/branches/<shop_slug>/create/` - Create branch
- `GET/PUT/DELETE /api/branches/<branch_slug>/management/` - Manage branch

### Comments
- `GET /api/comments/<shop_slug>/` - List shop comments
- `POST /api/comments/<shop_slug>/create/` - Create comment
- `GET/PUT/DELETE /api/comments/<id>/management/` - Manage comment

### Media
- `GET /api/media/<shop_slug>/` - List shop media
- `POST /api/media/<shop_slug>/create/` - Upload media
- `DELETE /api/media/<id>/delete/` - Delete media

### Social Media
- `GET /api/social-media/<shop_slug>/` - List social media links
- `POST /api/social-media/<shop_slug>/create/` - Add social media
- `GET/PUT/DELETE /api/social-media/<id>/management/` - Manage social media

### Order Items
- `GET /api/order-items/<shop_slug>/` - List shop order items
- `GET /api/order-items/<id>/` - Get order item details
- `PATCH /api/order-items/<id>/status/` - Update order item status

## Authentication

The service uses Gateway Header Authentication. Include the `X-User-ID` header with a valid UUID in API requests:

```bash
curl -H "X-User-ID: <user-uuid>" http://localhost:8007/api/shops/
```

## Testing

Run tests using pytest:

```bash
pytest
```

Or with Django test runner:

```bash
python manage.py test
```

## API Documentation

Interactive API documentation is available via Swagger/OpenAPI at:
- `/api/schema/swagger-ui/` - Swagger UI
- `/api/schema/redoc/` - ReDoc
- `/api/schema/` - OpenAPI schema

## Event Messaging

### Published Events

The service publishes events to the `shop_events` exchange:

- `shop.approved` - When a shop status changes to APPROVED
- `shop.updated` - When a shop is updated
- `shop.deleted` - When a shop is deleted

### Consumed Events

The service consumes events from the `order_events` exchange:

- `order.item.created` - Creates `ShopOrderItem` records when orders are placed

## Logging

Logs are written to:
- File: `shop_service/logs/drf_api.log`
- Console: Standard output

Log levels are configurable via Django settings.

## Static & Media Files

- Static files: Collected to `staticfiles/` directory
- Media files: Stored in `shop_service/media/`
  - Shop profiles: `shop_profiles/`
  - Shop media: `shop_media/`

## License

This service is part of the EcommerceLocal platform.

