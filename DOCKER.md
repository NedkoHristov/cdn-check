# Docker Deployment Guide 🐳

Quick reference for running CDN Checker with Docker.

## Prerequisites

- Docker installed ([Get Docker](https://docs.docker.com/get-docker/))
- Docker Compose installed (included with Docker Desktop)

## Quick Start

### Option 1: Docker Compose (Recommended)

```bash
# Clone and start
git clone https://github.com/yourusername/cdn-checker.git
cd cdn-checker
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

Access at: `http://localhost:5000`

### Option 2: Docker CLI

```bash
# Build
docker build -t cdn-checker .

# Run
docker run -d \
  --name cdn-checker \
  -p 5000:5000 \
  --restart unless-stopped \
  cdn-checker

# View logs
docker logs -f cdn-checker

# Stop and remove
docker stop cdn-checker
docker rm cdn-checker
```

## Configuration

### Custom Port

**Docker Compose:** Edit `docker-compose.yml`
```yaml
ports:
  - "8080:5000"  # Expose on port 8080
```

**Docker CLI:**
```bash
docker run -d -p 8080:5000 --name cdn-checker cdn-checker
```

### Worker Processes

**Docker Compose:** Edit `docker-compose.yml`
```yaml
environment:
  - WORKERS=8  # Number of workers
```

**Docker CLI:**
```bash
docker run -d -p 5000:5000 -e WORKERS=8 --name cdn-checker cdn-checker
```

**Formula:** `workers = (2 × CPU_cores) + 1`

### Bind to Localhost Only

For use with Nginx/Traefik:

**Docker Compose:**
```yaml
ports:
  - "127.0.0.1:5000:5000"
```

**Docker CLI:**
```bash
docker run -d -p 127.0.0.1:5000:5000 --name cdn-checker cdn-checker
```

## With Nginx Reverse Proxy

### 1. Run Docker Container on Localhost

```bash
docker run -d \
  --name cdn-checker \
  -p 127.0.0.1:5000:5000 \
  --restart unless-stopped \
  cdn-checker
```

### 2. Configure Nginx

Create `/etc/nginx/sites-available/cdn-checker`:

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location /cdn-check/ {
        proxy_pass http://127.0.0.1:5000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location = /cdn-check {
        return 301 /cdn-check/;
    }
}
```

### 3. Enable and Reload

```bash
sudo ln -s /etc/nginx/sites-available/cdn-checker /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 4. Add SSL (Optional but Recommended)

```bash
sudo certbot --nginx -d yourdomain.com
```

## Docker Compose Full Example

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  cdn-checker:
    build: .
    container_name: cdn-checker
    ports:
      - "127.0.0.1:5000:5000"
    restart: unless-stopped
    environment:
      - WORKERS=4
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 256M
    healthcheck:
      test: ["CMD", "python", "-c", "import requests; requests.get('http://localhost:5000/', timeout=5)"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 5s
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

## Management Commands

### View Logs

```bash
# Last 100 lines
docker logs --tail 100 cdn-checker

# Follow logs in real-time
docker logs -f cdn-checker

# With timestamps
docker logs -t cdn-checker
```

### Restart Container

```bash
docker restart cdn-checker
```

### Update Container

```bash
# Pull latest code
git pull

# Rebuild and restart
docker-compose up -d --build

# Or with Docker CLI:
docker stop cdn-checker
docker rm cdn-checker
docker build -t cdn-checker .
docker run -d -p 5000:5000 --name cdn-checker cdn-checker
```

### Check Container Status

```bash
# Is it running?
docker ps | grep cdn-checker

# Detailed info
docker inspect cdn-checker

# Resource usage
docker stats cdn-checker
```

### Execute Commands Inside Container

```bash
# Open shell
docker exec -it cdn-checker /bin/bash

# Run single command
docker exec cdn-checker python --version
```

## Troubleshooting

### Container Exits Immediately

```bash
# Check logs
docker logs cdn-checker

# Run interactively
docker run -it --rm cdn-checker /bin/bash
```

### Port Already in Use

```bash
# Find what's using port 5000
sudo lsof -i :5000

# Use different port
docker run -d -p 5001:5000 --name cdn-checker cdn-checker
```

### Can't Connect to Container

```bash
# Check if container is running
docker ps

# Check container IP
docker inspect cdn-checker | grep IPAddress

# Test from host
curl http://localhost:5000
```

### Out of Disk Space

```bash
# Clean up unused images
docker image prune -a

# Clean up everything
docker system prune -a --volumes
```

## Multi-Container Setup (Advanced)

Run with Redis cache and PostgreSQL logging:

```yaml
version: '3.8'

services:
  cdn-checker:
    build: .
    container_name: cdn-checker
    ports:
      - "127.0.0.1:5000:5000"
    environment:
      - REDIS_URL=redis://redis:6379/0
      - DATABASE_URL=postgresql://postgres:password@db:5432/cdnchecker
    depends_on:
      - redis
      - db
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    container_name: cdn-checker-redis
    restart: unless-stopped

  db:
    image: postgres:15-alpine
    container_name: cdn-checker-db
    environment:
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=cdnchecker
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

volumes:
  postgres_data:
```

## Production Checklist

- ✅ Set resource limits
- ✅ Configure health checks
- ✅ Set restart policy (unless-stopped)
- ✅ Bind to localhost if using reverse proxy
- ✅ Configure log rotation
- ✅ Use Docker Compose for easier management
- ✅ Set up SSL/HTTPS via reverse proxy
- ✅ Regular backups (if using volumes)
- ✅ Monitor resource usage
- ✅ Keep base image updated

## Performance Tips

1. **Multi-stage builds** - Already implemented in Dockerfile
2. **Layer caching** - Dependencies installed before code copy
3. **Non-root user** - Security best practice implemented
4. **Health checks** - Container restarts if unhealthy
5. **Resource limits** - Prevents one container from hogging resources

## Security

The Docker image includes:

- ✅ Non-root user (appuser)
- ✅ Minimal base image (python:3.11-slim)
- ✅ No unnecessary packages
- ✅ Security updates via regular rebuilds
- ✅ Bind to localhost by default in compose file

## Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Best practices for writing Dockerfiles](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)
- [Docker security best practices](https://docs.docker.com/develop/security-best-practices/)
