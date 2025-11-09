# Deployment Guide - CDN Checker

This application is designed to work seamlessly in any environment without hardcoded URLs or paths.

## ✅ What's Configured for Portability

1. **Relative URLs**: All static files use relative paths
2. **Relative API calls**: JavaScript uses `api/check` (relative to current path)
3. **Dynamic URL parameters**: Uses browser's `window.location` for URL updates
4. **No hardcoded hosts**: Works with any domain or subdomain
5. **Path-agnostic**: Works at root (`/`) or subpath (`/cdn-check/`)

## 🚀 Quick Start Options

### Option 1: Standalone (Root Path)

```bash
# Clone and setup
git clone <your-repo-url>
cd cdn-check
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run
python app.py
# Access at: http://localhost:5000
```

### Option 2: Behind Nginx (Subpath)

**Nginx Configuration:**
```nginx
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
```

**Run the app:**
```bash
cd /path/to/cdn-check
source venv/bin/activate
gunicorn -w 4 -b 127.0.0.1:5000 app:app --daemon
```

Access at: `https://yourdomain.com/cdn-check/`

### Option 3: Subdomain

**Nginx Configuration:**
```nginx
server {
    listen 80;
    server_name cdn.yourdomain.com;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

Access at: `http://cdn.yourdomain.com/`

### Option 4: Docker

```bash
docker build -t cdn-checker .
docker run -p 5000:5000 cdn-checker
```

Access at: `http://localhost:5000`

### Option 5: Systemd Service (Auto-start)

Create `/etc/systemd/system/cdn-checker.service`:
```ini
[Unit]
Description=CDN Checker Application
After=network.target

[Service]
User=youruser
WorkingDirectory=/path/to/cdn-check
Environment="PATH=/path/to/cdn-check/venv/bin"
ExecStart=/path/to/cdn-check/venv/bin/gunicorn -w 4 -b 127.0.0.1:5000 app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable cdn-checker
sudo systemctl start cdn-checker
```

## 🔧 Configuration

The app requires **ZERO configuration** for most deployments:

- ✅ No config files needed
- ✅ No environment variables required
- ✅ Works at any URL path
- ✅ Detects its own base path automatically

## 📋 Requirements

- Python 3.8+
- Dependencies in `requirements.txt`
- No database required
- No external services required

## 🎯 Tested Scenarios

✅ Root path: `http://localhost:5000/`
✅ Subpath: `https://domain.com/cdn-check/`
✅ Subdomain: `https://cdn.domain.com/`
✅ Docker: Container with port mapping
✅ Multiple instances: Different ports/paths

## 🔒 Security Notes

- Rate limiting: Built-in (10/min, 50/hour, 200/day per IP)
- Input validation: URL format checking
- XSS protection: All outputs are escaped
- No database: No SQL injection risk
- HTTPS: Use nginx/proxy for SSL termination

## 🐛 Troubleshooting

**Static files not loading?**
- Ensure trailing slash in nginx location block
- Check that proxy_pass has trailing slash too

**404 on API calls?**
- Verify nginx config has trailing slashes
- Check gunicorn is running on correct port

**Rate limiting issues?**
- Adjust limits in `app.py` if needed
- Consider Redis for distributed rate limiting

## 📝 Notes

- The app uses in-memory rate limiting (fine for single instance)
- For multiple instances, consider Redis-based rate limiting
- The app is stateless - can scale horizontally
- No data persistence - all checks are real-time

---

**That's it!** The application is fully portable and can be deployed anywhere without modification.
