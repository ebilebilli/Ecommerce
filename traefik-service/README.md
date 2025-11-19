# Traefik Service

Reverse proxy and load balancer for the e-commerce microservices platform. Provides unified routing, SSL termination, and service discovery for all microservices.

## Overview

Traefik acts as the entry point for all HTTP/HTTPS traffic, automatically routing requests to appropriate microservices based on Docker labels. It provides service discovery, load balancing, and SSL/TLS termination capabilities.

## Role

- **Reverse Proxy**: Routes incoming requests to backend services
- **Service Discovery**: Automatically discovers services via Docker labels
- **Load Balancing**: Distributes traffic across service instances
- **SSL/TLS**: Handles HTTPS termination (ready for Let's Encrypt)
- **Dashboard**: Provides web UI for monitoring and configuration

## Technologies

- **Traefik**: v2.10
- **Docker**: Service discovery via Docker provider
- **Let's Encrypt**: SSL certificate management (configured)

## Configuration

### Entry Points

- **web**: HTTP traffic on port 80
- **websecure**: HTTPS traffic on port 443

### Ports

- `80`: HTTP traffic
- `443`: HTTPS traffic
- `8080`: Traefik dashboard

### Docker Provider

- Auto-discovery enabled
- Services must have `traefik.enable=true` label
- Uses `shared_network` for service communication

## Service Routing

Services are routed based on Docker labels:

```yaml
labels:
  - "traefik.enable=true"
  - "traefik.http.routers.{service}.rule=Host(`{service}.localhost`)"
  - "traefik.http.routers.{service}.entrypoints=web"
  - "traefik.http.services.{service}.loadbalancer.server.port={port}"
```

## Setup

1. **Create shared network**:
```bash
docker network create shared_network
```

2. **Start Traefik**:
```bash
docker-compose up -d
```

3. **Access dashboard**:
- Dashboard: `http://traefik.localhost`
- API: `http://localhost:8080`

## Integration

All microservices connect to Traefik via:
- Docker labels for service discovery
- `shared_network` for internal communication
- Automatic routing based on host rules

## License

Part of the EcommerceLocal platform.

