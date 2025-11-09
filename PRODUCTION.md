# Production Deployment Guide

## Option 1: Systemd Service (Recommended for VPS/Dedicated Servers)

### Prerequisites
- Ubuntu/Debian server
- Python 3.8+
- Nginx (optional, for reverse proxy)
- Non-root user account

### Step 1: Clone and Setup

```bash
# As your regular user (e.g., nedko)
cd /path/to/your/projects
git clone https://github.com/nedkohristov/cdn-check.git
cd cdn-check

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Test it works
python app.py
# Press Ctrl+C to stop
```

### Step 2: Create Systemd Service

Create the service file:

```bash
sudo nano /etc/systemd/system/cdn-checker.service
```

Add this configuration (replace paths and user):

```ini
[Unit]
Description=CDN Checker Application
After=network.target

[Service]
Type=notify
User=nedko
Group=nedko
WorkingDirectory=/path/to/your/cdn-check
Environment="PATH=/path/to/your/cdn-check/venv/bin"
ExecStart=/path/to/your/cdn-check/venv/bin/gunicorn -w 4 -b 127.0.0.1:5000 app:app
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

**Important:** Replace `/path/to/your/cdn-check` with your actual path and `nedko` with your username.

### Step 3: Enable and Start Service

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service (start on boot)
sudo systemctl enable cdn-checker

# Start service now
sudo systemctl start cdn-checker

# Check status
sudo systemctl status cdn-checker
```

### Step 4: Configure Nginx (Optional)

For production, use Nginx as reverse proxy:

```bash
sudo nano /etc/nginx/sites-available/cdn-checker
```

Add this configuration:

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

Enable and reload:

```bash
sudo ln -s /etc/nginx/sites-available/cdn-checker /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### Useful Commands

```bash
# View live logs
sudo journalctl -u cdn-checker -f

# Restart after code changes
sudo systemctl restart cdn-checker

# Stop service
sudo systemctl stop cdn-checker

# Disable auto-start
sudo systemctl disable cdn-checker

# Check if running
sudo systemctl status cdn-checker
```

### Updating the Application

```bash
# Stop service
sudo systemctl stop cdn-checker

# Pull updates
cd /path/to/your/cdn-check
git pull

# Update dependencies if needed
source venv/bin/activate
pip install -r requirements.txt

# Restart service
sudo systemctl start cdn-checker
```

---

## Option 2: Docker Deployment

### Prerequisites
- Docker installed
- Docker Compose (optional)

### Step 1: Build Docker Image

The repository includes a `Dockerfile`. Build the image:

```bash
cd cdn-check
docker build -t cdn-checker .
```

### Step 2: Run Container

**Option A: Direct Docker Run**

```bash
docker run -d \
  --name cdn-checker \
  -p 5000:5000 \
  --restart unless-stopped \
  cdn-checker
```

Access at: `http://localhost:5000`

**Option B: With Nginx Proxy**

Run on localhost only:

```bash
docker run -d \
  --name cdn-checker \
  -p 127.0.0.1:5000:5000 \
  --restart unless-stopped \
  cdn-checker
```

Then configure Nginx to proxy to `http://127.0.0.1:5000`

**Option C: Custom Port**

```bash
docker run -d \
  --name cdn-checker \
  -p 8080:5000 \
  --restart unless-stopped \
  cdn-checker
```

Access at: `http://localhost:8080`

### Step 3: Docker Compose (Recommended)

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
```

Run with:

```bash
docker-compose up -d
```

### Docker Management Commands

```bash
# View logs
docker logs -f cdn-checker

# Restart container
docker restart cdn-checker

# Stop container
docker stop cdn-checker

# Remove container
docker rm cdn-checker

# Rebuild and restart
docker-compose up -d --build

# Stop all containers
docker-compose down
```

### Updating Docker Deployment

```bash
# Pull latest code
git pull

# Rebuild and restart
docker-compose up -d --build

# Or with plain docker:
docker stop cdn-checker
docker rm cdn-checker
docker build -t cdn-checker .
docker run -d --name cdn-checker -p 5000:5000 --restart unless-stopped cdn-checker
```

---

## Comparison: Systemd vs Docker

| Feature | Systemd | Docker |
|---------|---------|--------|
| Setup Complexity | Medium | Easy |
| Resource Usage | Lower | Slightly Higher |
| Isolation | Process-level | Container-level |
| Portability | Server-specific | Highly portable |
| Auto-restart | ✅ Yes | ✅ Yes |
| Easy updates | Medium | Easy |
| Best for | VPS, Dedicated | Any platform |

**Recommendation:**
- Use **Systemd** if you have a VPS/dedicated server with other services
- Use **Docker** if you want easy deployment across different environments

---

## SSL/HTTPS Setup

For production, always use HTTPS. With Nginx:

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d yourdomain.com

# Auto-renewal is configured automatically
```

---

## Monitoring

### Check if service is running

**Systemd:**
```bash
sudo systemctl is-active cdn-checker
```

**Docker:**
```bash
docker ps | grep cdn-checker
```

### Check application health

```bash
curl http://localhost:5000/
```

Should return HTML content.

### Check API endpoint

```bash
curl -X POST http://localhost:5000/api/check \
  -H "Content-Type: application/json" \
  -d '{"url":"github.com"}'
```

Should return JSON with CDN detection results.

---

## Troubleshooting

### Systemd Issues

**Service won't start:**
```bash
# Check logs
sudo journalctl -u cdn-checker -n 50

# Check if port is already in use
sudo lsof -i :5000

# Verify paths in service file
cat /etc/systemd/system/cdn-checker.service
```

**Permission errors:**
```bash
# Fix ownership
sudo chown -R yourusername:yourusername /path/to/cdn-check
```

### Docker Issues

**Container exits immediately:**
```bash
# Check logs
docker logs cdn-checker

# Run interactively to debug
docker run -it --rm cdn-checker /bin/bash
```

**Port already in use:**
```bash
# Find what's using the port
sudo lsof -i :5000

# Use different port
docker run -d --name cdn-checker -p 5001:5000 cdn-checker
```

---

## Performance Tuning

### Adjust Worker Processes

**Systemd:**
Edit `/etc/systemd/system/cdn-checker.service`:
```ini
ExecStart=/path/to/venv/bin/gunicorn -w 8 -b 127.0.0.1:5000 app:app
```

**Docker:**
Set environment variable in `docker-compose.yml`:
```yaml
environment:
  - WORKERS=8
```

**Formula:** `workers = (2 × CPU_cores) + 1`

### Timeout Settings

For slow DNS queries, increase timeout:

```bash
gunicorn -w 4 -t 120 -b 127.0.0.1:5000 app:app
```

---

## Security Checklist

- ✅ Run as non-root user
- ✅ Bind to localhost only (127.0.0.1)
- ✅ Use Nginx/proxy for external access
- ✅ Enable HTTPS/SSL
- ✅ Keep dependencies updated
- ✅ Use firewall (ufw/iptables)
- ✅ Regular backups
- ✅ Monitor logs for suspicious activity

---

## Support

If you encounter issues:
1. Check logs (journalctl or docker logs)
2. Verify all paths and permissions
3. Test the app directly: `python app.py`
4. Check GitHub issues
5. Review Nginx logs: `/var/log/nginx/error.log`
