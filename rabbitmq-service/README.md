# RabbitMQ Service

Message broker for asynchronous communication between microservices. Handles event-driven architecture, message queuing, and service decoupling.

## Overview

RabbitMQ provides reliable message queuing for the e-commerce platform, enabling microservices to communicate asynchronously through events. It supports multiple exchanges and queues for different event types.

## Role

- **Message Broker**: Routes messages between services
- **Event Distribution**: Distributes events to multiple consumers
- **Service Decoupling**: Enables loose coupling between microservices
- **Reliability**: Ensures message delivery and persistence

## Technologies

- **RabbitMQ**: 3-management (with management UI)
- **AMQP**: Advanced Message Queuing Protocol
- **Management Plugin**: Web-based management interface

## Configuration

### Default Settings

- **Port**: 5672 (AMQP)
- **Management UI**: 15672
- **User**: Configured via `RABBITMQ_USER`
- **Password**: Configured via `RABBITMQ_PASS`

### Exchanges

The platform uses topic exchanges:

- **user_events**: User lifecycle events
- **shop_events**: Shop management events
- **product_events**: Product catalog events
- **order_events**: Order processing events

### Common Routing Keys

- `user.created` - New user registration
- `shop.approved` - Shop approval
- `shop.updated` - Shop updates
- `shop.deleted` - Shop deletion
- `product.created` - New product
- `product.updated` - Product updates
- `product.deleted` - Product deletion
- `order.created` - New order
- `order.item.created` - Order item creation

## Setup

1. **Create `.env` file**:
```env
RABBITMQ_USER=admin
RABBITMQ_PASS=admin12345
RABBITMQ_HOST=rabbitmq
RABBITMQ_PORT=5672
```

2. **Start RabbitMQ**:
```bash
docker-compose up -d
```

3. **Access management UI**:
- Management: `http://rabbitmq-admin.localhost`
- Default credentials: `admin` / `admin12345`

## Integration

Microservices connect to RabbitMQ using:
- **Pika**: Python AMQP client (synchronous)
- **aio-pika**: Python AMQP client (asynchronous)
- Connection via `RABBITMQ_HOST` and `RABBITMQ_PORT`

### Publisher Pattern

Services publish events to exchanges:
```python
channel.basic_publish(
    exchange='shop_events',
    routing_key='shop.approved',
    body=json.dumps(message)
)
```

### Consumer Pattern

Services consume events from queues:
```python
channel.queue_bind(
    exchange='shop_events',
    queue='queue_name',
    routing_key='shop.*'
)
```

## Monitoring

- **Management UI**: Web interface for monitoring queues, exchanges, and connections
- **Metrics**: Message rates, queue lengths, consumer counts
- **Health Checks**: Connection status and service availability

## License

Part of the EcommerceLocal platform.

