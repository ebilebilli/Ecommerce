# Redis Service

In-memory data store for caching and session management. Used primarily for JWT token blacklisting and high-performance caching operations.

## Overview

Redis provides fast, in-memory storage for the e-commerce platform. It's primarily used by the Gateway Service for token blacklisting, enabling efficient logout functionality and token revocation.

## Role

- **Token Blacklisting**: Stores revoked JWT tokens
- **Caching**: High-performance data caching
- **Session Storage**: Temporary session data
- **Rate Limiting**: Can be used for API rate limiting

## Technologies

- **Redis**: 7.2
- **Persistence**: AOF (Append-Only File) enabled
- **Network**: Accessible via `shared_network` and `internal_net`

## Configuration

### Default Settings

- **Port**: 6379 (internal only, not exposed)
- **Persistence**: AOF enabled for data durability
- **Memory**: In-memory storage with optional persistence

### Data Structures

- **Sets**: Used for token blacklist (`blacklisted_tokens`)
- **Strings**: Key-value storage for caching
- **Hashes**: Structured data storage

## Setup

1. **Start Redis**:
```bash
docker-compose up -d
```

2. **Verify connection**:
```bash
docker exec -it redis_service redis-cli ping
# Should return: PONG
```

## Integration

### Gateway Service

Primary use case - token blacklisting:

```python
# Add token to blacklist
redis_client.sadd("blacklisted_tokens", token)

# Check if token is blacklisted
is_blacklisted = redis_client.sismember("blacklisted_tokens", token)
```

### Connection

Services connect via:
- **Host**: `redis_service` (Docker) or `localhost` (local)
- **Port**: `6379`
- **Library**: `redis` (Python)

## Data Persistence

- **AOF**: Append-Only File enabled
- **Volume**: `redis_data` Docker volume
- **Durability**: Data survives container restarts

## Performance

- **In-Memory**: Sub-millisecond response times
- **Atomic Operations**: Thread-safe operations
- **High Throughput**: Handles thousands of operations per second

## Use Cases

1. **JWT Token Blacklist**: Gateway service stores revoked tokens
2. **Session Caching**: Temporary user session data
3. **API Response Caching**: Cache frequently accessed data
4. **Rate Limiting**: Track API request rates

## License

Part of the EcommerceLocal platform.

