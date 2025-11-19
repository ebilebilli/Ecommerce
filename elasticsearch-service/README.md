# Elasticsearch Service

A microservice for providing full-text search capabilities across shops and products in an e-commerce platform. Built with FastAPI and Elasticsearch, this service indexes shop and product data in real-time and provides powerful search functionality with fuzzy matching and multi-field search.

## Overview

The Elasticsearch Service is responsible for indexing shops and products from other microservices and providing unified search functionality. It consumes events from RabbitMQ to keep the search index synchronized with the source data and exposes RESTful APIs for searching across shops and products.

## Technologies

- **Framework**: FastAPI 0.121.1+
- **Search Engine**: Elasticsearch 8.12.1
- **Message Broker**: RabbitMQ (aio-pika 9.5.8, pika 1.3.2)
- **HTTP Client**: Built-in FastAPI
- **Data Validation**: Pydantic 2.12.4+
- **Web Server**: Uvicorn 0.38.0+
- **Visualization**: Kibana 8.12.1 (optional)
- **Python Version**: 3.11+

## Features

### Search Capabilities
- **Unified Search**: Search across both shops and products in a single query
- **Fuzzy Matching**: Automatic typo tolerance with `fuzziness: AUTO`
- **Multi-field Search**: Products searched across title (boosted) and description
- **Shop-specific Product Search**: Get all products for a specific shop
- **Real-time Indexing**: Automatic index updates via event consumption

### Indexing
- **Automatic Index Creation**: Creates indices with proper mappings on startup
- **Real-time Sync**: Consumes events from shop and product services
- **Event-driven Updates**: Indexes, updates, and deletes documents based on events
- **Schema Validation**: Uses Pydantic models for data validation

### Indices

#### Shops Index (`shops`)
- **Fields**:
  - `name`: Text field with standard analyzer
  - `id`: Document ID (shop UUID)
  - Additional shop metadata

#### Products Index (`products`)
- **Fields**:
  - `id`: Keyword field (product UUID)
  - `shop_id`: Keyword field (shop UUID reference)
  - `title`: Text field with standard analyzer (boosted in search)
  - `about`: Text field with standard analyzer
  - `on_sale`: Boolean
  - `is_active`: Boolean
  - `top_sale`: Boolean
  - `top_popular`: Boolean
  - `sku`: Keyword field
  - `created_at`: Date field

## Architecture

### Components

1. **FastAPI Web Service**: Main application serving search API endpoints
2. **RabbitMQ Consumer**: Background service consuming events to update search index
3. **Elasticsearch Cluster**: Search engine (single-node for development)
4. **Kibana** (optional): Visualization and management UI

### Event Processing

The service consumes events from two exchanges:

- **Shop Events** (`shop_events` exchange):
  - `shop.approved` - Index new shop
  - `shop.updated` - Update shop in index
  - `shop.deleted` - Delete shop from index

- **Product Events** (`product_events` exchange):
  - `product.created` - Index new product
  - `product.updated` - Update product in index
  - `product.deleted` - Delete product from index

## Setup & Installation

### Prerequisites

- Python 3.11+
- Docker & Docker Compose
- RabbitMQ

### Quick Start

1. **Create `.env` file**:
```env
ELASTIC_HOST=http://localhost:9200
ELASTIC_USERNAME=elastic
ELASTIC_PASSWORD=your-password
RABBITMQ_HOST=localhost
RABBITMQ_PORT=5672
RABBITMQ_USER=admin
RABBITMQ_PASS=admin12345
```

2. **Start with Docker**:
```bash
docker-compose up -d
```

This starts Elasticsearch, Kibana, API service, and consumer automatically.

3. **Access services**:
- API: `http://elasticsearch-api.localhost`
- Kibana: `http://kibana-admin.localhost`

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `ELASTIC_HOST` | Elasticsearch host URL | `http://elasticsearch:9200` |
| `ELASTIC_USERNAME` | Elasticsearch username | `elastic` |
| `ELASTIC_PASSWORD` | Elasticsearch password | Required |
| `RABBITMQ_HOST` | RabbitMQ host | `rabbitmq` |
| `RABBITMQ_PORT` | RabbitMQ port | `5672` |
| `RABBITMQ_USER` | RabbitMQ username | `admin` |
| `RABBITMQ_PASS` | RabbitMQ password | `admin12345` |
| `LOG_DIR` | Log directory path | `/app/logs` |
| `KIBANA_SYSTEM_PASSWORD` | Kibana system user password | Same as ELASTIC_PASSWORD |

### Elasticsearch Configuration

- **Security**: X-Pack security enabled
- **Node Type**: Single-node (development)
- **Authentication**: Basic auth with username/password
- **SSL**: Disabled for development (verify_certs=False)

## API Endpoints

### Search

- `GET /api/elasticsearch/search/` - Unified search across shops and products
  - Query Parameters:
    - `query` (required): Search query string
    - `size` (optional): Number of results per type (default: 10)
  - Returns:
    ```json
    {
      "shops": [...],
      "products": [...]
    }
    ```
  - Features:
    - Fuzzy matching for shops (name field)
    - Multi-field search for products (title boosted 2x, about field)
    - Automatic typo tolerance

- `GET /api/elasticsearch/shop/{shop_id}/products/` - Get all products for a shop
  - Path Parameters:
    - `shop_id`: Shop UUID
  - Query Parameters:
    - `size` (optional): Number of results (default: 100)
  - Returns:
    ```json
    {
      "products": [...],
      "total": 42
    }
    ```
  - Features:
    - Exact match search by shop_id
    - Fallback to match query if term query fails

## Search Features

### Fuzzy Matching

Both shop and product searches use fuzzy matching with `fuzziness: AUTO`, which:
- Tolerates typos and misspellings
- Handles character transpositions
- Adjusts fuzziness based on query length

### Field Boosting

Product search uses field boosting:
- `title^2`: Title matches are weighted 2x more than description matches
- `about`: Description field for additional context

### Query Types

- **Match Query**: Used for shop name search (text analysis)
- **Multi-match Query**: Used for product search across multiple fields
- **Term Query**: Used for exact shop_id matching (keyword field)

## Event Messaging

### Consumed Events

The service consumes events from RabbitMQ to keep the search index synchronized:

#### Shop Events
- **Routing Key**: `shop.*`
- **Queue**: `shop_queue`
- **Events**:
  - `shop.approved` / `shop.updated`: Index or update shop
  - `shop.deleted`: Delete shop from index

#### Product Events
- **Routing Key**: `product.*`
- **Queue**: `product_queue`
- **Events**:
  - `product.created` / `product.updated`: Index or update product
  - `product.deleted`: Delete product from index

### Event Processing

- Events are processed asynchronously using `aio_pika`
- Multiple queues are consumed concurrently
- Error handling with logging for failed messages
- Automatic retry on connection failures

## Data Models

### ShopSchema
```python
{
  "id": str,           # Shop UUID
  "name": str,         # Shop name
  "about": Optional[str],
  "profile": Optional[str],
  "is_verified": bool,
  "is_active": bool
}
```

### ProductSchema
```python
{
  "id": str,           # Product UUID
  "shop_id": Optional[str],
  "title": str,
  "about": Optional[str],
  "on_sale": bool,
  "is_active": bool,
  "top_sale": bool,
  "top_popular": bool,
  "sku": Optional[str],
  "created_at": Optional[str]
}
```

## Index Mappings

### Shops Index
- `name`: Analyzed text field for full-text search
- Dynamic mapping for other fields

### Products Index
- `id`, `shop_id`, `sku`: Keyword fields (exact match)
- `title`, `about`: Analyzed text fields (full-text search)
- `on_sale`, `is_active`, `top_sale`, `top_popular`: Boolean fields
- `created_at`: Date field

## Kibana Integration

Kibana is included for:
- **Index Management**: View and manage Elasticsearch indices
- **Search Testing**: Test queries interactively
- **Monitoring**: Monitor Elasticsearch cluster health
- **Visualization**: Create dashboards and visualizations

Access Kibana at: `http://kibana-admin.localhost`

## Logging

Logs are written to:
- **File**: `logs/consumer.log` (consumer service)
- **Console**: Standard output (all services)

Log format: `%(asctime)s - %(levelname)s - %(message)s`

## Error Handling

- **Index Not Found**: Returns error message if index doesn't exist
- **Connection Errors**: Retries with exponential backoff
- **Invalid Data**: Logs errors and continues processing
- **Search Errors**: Returns partial results if one index fails

## Performance Considerations

- **Fuzzy Matching**: May be slower on large indices
- **Multi-field Search**: Efficient with proper field mappings
- **Index Size**: Monitor index size and optimize mappings as needed
- **Query Caching**: Elasticsearch caches frequent queries automatically

## Health Checks

The consumer service includes health checks:
- **Elasticsearch**: Waits up to 60 seconds for Elasticsearch to be ready
- **RabbitMQ**: Waits up to 60 seconds for RabbitMQ to be ready
- **Index Creation**: Creates indices on startup if they don't exist

## Security

- **Authentication**: Elasticsearch uses X-Pack security with username/password
- **Network**: Services communicate over internal Docker network
- **SSL**: Disabled for development (enable for production)

## Testing

Test search functionality:

```bash
# Search for shops and products
curl "http://localhost:8000/api/elasticsearch/search/?query=electronics&size=5"

# Get products by shop
curl "http://localhost:8000/api/elasticsearch/shop/{shop_id}/products/?size=50"
```

## API Documentation

Interactive API documentation is available via FastAPI's automatic docs:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- OpenAPI JSON: `http://localhost:8000/openapi.json`

## Troubleshooting

### Index Not Found
- Ensure consumer has started and created indices
- Check Elasticsearch connection and authentication
- Verify indices exist: `curl -u elastic:password http://localhost:9200/_cat/indices`

### No Search Results
- Verify data has been indexed (check via Kibana)
- Check event consumption logs
- Verify RabbitMQ connection

### Connection Errors
- Check Elasticsearch is running and accessible
- Verify credentials in environment variables
- Check network connectivity between services

## License

This service is part of the EcommerceLocal platform.

