# User Service

A microservice for managing user authentication, registration, profiles, and user-related operations in an e-commerce platform. Built with Django REST Framework, this service provides secure user management, password reset functionality, and event-driven integration with other services.

## Overview

The User Service is responsible for handling all user-related operations including registration, profile management, password reset, and shop owner status tracking. It integrates with other microservices through RabbitMQ messaging and provides RESTful APIs for user operations.

## Technologies

- **Framework**: Django 5.2.7
- **API**: Django REST Framework 3.16.1
- **Authentication**: UUID-based header authentication (JWT library available but not used in login)
- **Database**: PostgreSQL 16
- **Message Broker**: RabbitMQ (Pika 1.3.2)
- **Image Processing**: Pillow 11.3.0
- **HTTP Client**: requests 2.32.5
- **API Documentation**: drf-spectacular 0.28.0
- **Python Version**: 3.10+

## Features

### User Management
- User registration with email validation
- Custom user model with UUID primary keys
- Email-based authentication (email as USERNAME_FIELD)
- User profiles with image upload support
- User verification system
- Unique slug generation for user profiles
- Shop owner status tracking

### Authentication
- UUID-based authentication via `X-User-ID` header
- Gateway header authentication for inter-service communication
- Secure password hashing
- Email-based login (no JWT tokens returned)

### Password Management
- Password reset via email
- Secure token-based password reset links
- Frontend-integrated password reset flow
- Password validation and confirmation

### Profile Management
- View and update user profile
- Profile image upload
- User information management (first name, last name, phone number)
- Read-only fields (slug, creation date, shop owner status)

### Event-Driven Architecture
- Publishes `user.created` events to RabbitMQ when users register
- Consumes `shop.approved` and `shop.deleted` events from shop service
- Automatically updates `is_shop_owner` flag based on shop events
- Asynchronous event processing

## Architecture

### Components

1. **Web Service**: Main Django application serving REST API endpoints
2. **Shop Event Consumer**: Background service consuming shop events from RabbitMQ to update user shop owner status

### Database Models

- `User`: Custom user model extending AbstractUser
  - UUID primary key
  - Email-based authentication
  - Shop owner flag
  - Unique slug for profiles
  - Phone number support
  
- `Profile`: One-to-one relationship with User
  - Profile image storage
  - Verification status
  - Auto-created on user registration

### API Structure

All endpoints are prefixed with `/api/user/` and include:
- Authentication endpoints (register, login, logout)
- Profile management
- Password reset flow

## Setup & Installation

### Prerequisites

- Python 3.10+
- PostgreSQL 16
- RabbitMQ
- Docker & Docker Compose (optional)
- SMTP server for email functionality (Gmail configured by default)

### Local Development

1. **Clone and navigate to the service**:
```bash
cd user-service
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
POSTGRES_DB=ecommerce_db
POSTGRES_USER=ecommerce_user
POSTGRES_PASSWORD=StrongPass123!
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
RABBITMQ_HOST=localhost
RABBITMQ_PORT=5672
RABBITMQ_USER=admin
RABBITMQ_PASS=admin12345
```

4. **Configure email settings** (in `Core/settings.py` or via environment):
```python
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
FRONTEND_PASSWORD_RESET_URL = 'http://localhost:3000/reset-password'
```

5. **Run migrations**:
```bash
python manage.py migrate
```

6. **Create superuser** (optional):
```bash
python manage.py createsuperuser
```

7. **Run the development server**:
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
- Django web service
- Shop event consumer service

2. **Access the service**:
- API: `http://localhost:8005` (if port mapping enabled)
- Admin: `http://user-admin.localhost` (via Traefik)

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Django secret key | Required |
| `DEBUG` | Debug mode | `True` |
| `POSTGRES_DB` | Database name | `ecommerce_db` |
| `POSTGRES_USER` | Database user | `ecommerce_user` |
| `POSTGRES_PASSWORD` | Database password | `StrongPass123!` |
| `POSTGRES_HOST` | Database host | `localhost` |
| `POSTGRES_PORT` | Database port | `5432` |
| `RABBITMQ_HOST` | RabbitMQ host | `rabbitmq` |
| `RABBITMQ_PORT` | RabbitMQ port | `5672` |
| `RABBITMQ_USER` | RabbitMQ username | `admin` |
| `RABBITMQ_PASS` | RabbitMQ password | `admin12345` |

### Email Configuration

The service uses SMTP for sending password reset emails. Configure in `Core/settings.py`:
- SMTP host and port
- TLS/SSL settings
- Email credentials
- Frontend password reset URL

## API Endpoints

### Authentication
- `POST /api/user/register/` - Register a new user
  - Body: `{first_name, last_name, email, phone_number, password}`
  - Returns: User data with UUID

- `POST /api/user/login/` - Authenticate user
  - Body: `{email, password}`
  - Returns: `{uuid, email}` (UUID is used for subsequent authenticated requests)

- `POST /api/user/logout/` - Logout user
  - Returns: Success message

### Profile Management
- `GET /api/user/profile/` - Get user profile
  - Requires: `X-User-ID` header
  - Returns: User profile data

- `PUT /api/user/profile/` - Update user profile (full update)
  - Requires: `X-User-ID` header
  - Body: `{first_name, last_name, email, phone_number}`

- `PATCH /api/user/profile/` - Update user profile (partial update)
  - Requires: `X-User-ID` header
  - Body: Partial user data

### Password Reset
- `POST /api/user/password-reset/request/` - Request password reset
  - Body: `{email}`
  - Sends reset link to user's email

- `POST /api/user/password-reset/confirm/` - Confirm password reset
  - Body: `{uid, token, new_password, confirm_password}`
  - Resets user password

## Authentication

### Gateway Header Authentication

For inter-service communication, include the `X-User-ID` header with a valid UUID:

```bash
curl -H "X-User-ID: <user-uuid>" http://localhost:8005/api/user/profile/
```

### Client Authentication Flow

For client applications, authentication works as follows:

```bash
# 1. Login to get user UUID
curl -X POST http://localhost:8005/api/user/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password"}'

# Response: {"uuid": "...", "email": "user@example.com"}

# 2. Use UUID in X-User-ID header for authenticated requests
curl -H "X-User-ID: <user-uuid>" http://localhost:8005/api/user/profile/
```

**Note**: The service uses UUID-based authentication via headers. JWT configuration exists in settings but is not currently used by the login endpoint.

## Testing

Run tests using Django test runner:

```bash
python manage.py test
```

## API Documentation

Interactive API documentation is available via Swagger/OpenAPI at:
- `/api/schema/swagger/` - Swagger UI
- `/api/schema/redoc/` - ReDoc
- `/openapi.json` - OpenAPI schema JSON

## Event Messaging

### Published Events

The service publishes events to the `user_events` exchange:

- `user.created` - When a new user registers
  - Payload: `{event_type, user_uuid, email, is_active}`

### Consumed Events

The service consumes events from the `shop_events` exchange:

- `shop.approved` - Updates user's `is_shop_owner` flag to `True`
- `shop.deleted` - Updates user's `is_shop_owner` flag to `False`

The consumer automatically updates user shop owner status when shops are approved or deleted.

## User Model

### Custom User Model

The service uses a custom `User` model extending Django's `AbstractUser`:

- **Primary Key**: UUID (not auto-increment integer)
- **Username Field**: Email (unique, required)
- **Required Fields**: `first_name`, `last_name`, `email`
- **Optional Fields**: `username`, `phone_number`
- **Auto-generated**: `slug` (unique, SEO-friendly)
- **Shop Owner**: `is_shop_owner` (boolean, updated via events)

### Profile Model

Each user automatically gets a `Profile` instance:
- One-to-one relationship with User
- Profile image storage
- Verification status

## Password Reset Flow

1. User requests password reset via `/api/user/password-reset/request/`
2. Service generates secure token and sends email with reset link
3. Reset link includes `uid` (base64 encoded user ID) and `token`
4. User clicks link and is redirected to frontend with query parameters
5. Frontend calls `/api/user/password-reset/confirm/` with `uid`, `token`, and new password
6. Service validates token and updates password

## Logging

Logs are written to:
- File: `logs/drf_api.log`
- Console: Standard output

Log levels are configurable via Django settings. Separate logger for `user_events` consumer.

## Static & Media Files

- Static files: Collected to `staticfiles/` directory
- Media files: Stored in `user_service/media/`
  - Profile images: `profile_images/`

## Security Features

- Password hashing using Django's PBKDF2 algorithm
- Secure password reset tokens
- Email validation
- UUID-based authentication
- CSRF protection
- SQL injection protection (Django ORM)
- XSS protection

## License

This service is part of the EcommerceLocal platform.
