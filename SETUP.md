# Quick Setup - CDN Checker

## 🎯 Zero-Configuration Deployment

This app works anywhere without any hardcoded URLs or configuration!

### For localhost:
```bash
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt && python app.py
```
**Access:** `http://localhost:5000`

### For Nginx subpath (e.g., /cdn-check):
```nginx
location /cdn-check/ {
    proxy_pass http://127.0.0.1:5000/;
    proxy_set_header Host $host;
}
location = /cdn-check { return 301 /cdn-check/; }
```
```bash
gunicorn -w 4 -b 127.0.0.1:5000 app:app
```
**Access:** `https://yourdomain.com/cdn-check/`

### For subdomain:
```nginx
server {
    server_name cdn.yourdomain.com;
    location / { proxy_pass http://127.0.0.1:5000; }
}
```
**Access:** `https://cdn.yourdomain.com/`

### For Docker:
```bash
docker build -t cdn-checker . && docker run -p 5000:5000 cdn-checker
```
**Access:** `http://localhost:5000`

---

**No config files. No environment variables. Just works! 🚀**
