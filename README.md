# CDN Checker 🌐

![CI Build](https://github.com/NedkoHristov/cdn-check/workflows/CI%20-%20Build%20and%20Test/badge.svg)
![Docker Build](https://github.com/NedkoHristov/cdn-check/workflows/Build%20and%20Deploy%20Docker%20Image/badge.svg)
![Python Version](https://img.shields.io/badge/python-3.11-blue)
![License](https://img.shields.io/badge/license-MIT-green)

A comprehensive web security and performance analysis tool that detects CDN providers, analyzes security headers, SSL certificates, CMS platforms, and provides detailed technology stack information. Built with Python Flask and vanilla JavaScript.

## Live Demo

🔗 [View Demo](https://www.nedko.info/cdn-check/)

## 📖 Documentation

- **[docs/WATCHTOWER.md](docs/WATCHTOWER.md)** - ⭐ Automatic deployments with Watchtower webhook (recommended)
- **[docs/PRODUCTION.md](docs/PRODUCTION.md)** - Complete production deployment guide (Systemd + Docker)
- **[docs/DOCKER.md](docs/DOCKER.md)** - Docker deployment quick reference
- **[docs/GITHUB_ACTIONS.md](docs/GITHUB_ACTIONS.md)** - CI/CD pipelines and Docker image builds
- **[docs/MANUAL_WORKFLOWS.md](docs/MANUAL_WORKFLOWS.md)** - Running GitHub Actions manually
- **[docs/ERROR_HANDLING.md](docs/ERROR_HANDLING.md)** - Error handling and troubleshooting
- **[docs/QUICKSTART.md](docs/QUICKSTART.md)** - Get started in 5 minutes
- **[docs/EXAMPLES.md](docs/EXAMPLES.md)** - API usage examples
- **[docs/CONTRIBUTING.md](docs/CONTRIBUTING.md)** - Contributing guidelines
- **[docs/CHANGELOG.md](docs/CHANGELOG.md)** - Version history and changes

## ✨ Features

### 🌐 CDN Detection
- Identifies 10+ major CDN providers (CloudFlare, AWS CloudFront, Fastly, Akamai, Azure CDN, Google Cloud CDN, KeyCDN, BunnyCDN, SiteGround CDN, Vercel)
- HTTP header analysis
- DNS CNAME record inspection
- Confidence scoring

### 🔒 Security Analysis
- **Security Headers Audit** - Grades security posture (A+ to F)
- HSTS, CSP, X-Frame-Options, X-Content-Type-Options
- X-XSS-Protection, Referrer-Policy, Permissions-Policy
- **SSL/TLS Certificate Info** - Issuer, expiration, TLS version
- **Email Security** - SPF, DMARC, MX records

### 💻 Technology Stack Detection
- **CMS Detection** - WordPress, Joomla, Drupal, Shopify, Wix, Magento, PrestaShop (with version detection)
- **Web Server** - Apache, Nginx, IIS, LiteSpeed
- **Programming Languages** - PHP, ASP.NET, Node.js, Python
- **Frontend Frameworks** - React, Vue.js, Angular, Next.js
- **Analytics** - Google Analytics, Facebook Pixel, Hotjar
- **Hosting Provider** - AWS, Google Cloud, Azure, DigitalOcean, Cloudflare

### 📊 Domain & Performance
- **Domain Age** - Creation date, expiration, registrar information
- **Performance Metrics** - Response time, compression (gzip/brotli), page size
- **DNS Information** - IP address, CNAME records, mail servers

### 🔐 Additional Features
- Rate limiting (10/min, 50/hour, 200/day per IP)
- Input validation and XSS protection
- Real-time version tracking (Git SHA + build timestamp)
- Responsive mobile-first design
- Dark theme UI

## 🚀 What's New

### Recent Updates
- ✅ **Watchtower Webhook Integration** - Instant deployments via GitHub Actions (< 5 seconds)
- ✅ **Comprehensive Security Scanning** - Trivy, Gitleaks, Semgrep in CI/CD
- ✅ **Technology Stack Detection** - Full framework and analytics detection
- ✅ **Security Headers Analysis** - A-F grading system
- ✅ **SSL/TLS Certificate Info** - Expiration tracking and TLS version
- ✅ **CMS Platform Detection** - WordPress, Joomla, Drupal, Shopify, Wix, Magento, PrestaShop with version detection
- ✅ **Domain Age & History** - WHOIS integration
- ✅ **Email Security** - SPF, DMARC, MX validation
- ✅ **Performance Metrics** - Response time, compression, page size
- ✅ **Version Display** - Git SHA and build timestamp in footer

## How It Works

The tool performs comprehensive website analysis through multiple techniques:

### CDN Detection
1. **HTTP Headers** - CDN-specific headers (e.g., `cf-ray`, `x-amz-cf-id`)
2. **DNS CNAME Records** - CDN provider domains in DNS
3. **Server Response** - CDN signatures and patterns

### Security Analysis
1. **Header Inspection** - Security headers presence and configuration
2. **SSL Certificate** - Validation, expiration, issuer information
3. **Email Security** - SPF, DMARC, MX record verification

### Technology Detection
1. **HTML Parsing** - Meta tags, framework signatures, analytics scripts
2. **HTTP Headers** - Server software, language versions
3. **DNS Analysis** - Hosting provider identification

## Supported Technologies

### CDN Providers
CloudFlare • Amazon CloudFront • Fastly • Akamai • Azure CDN • Google Cloud CDN • KeyCDN • BunnyCDN • SiteGround CDN

### CMS Platforms
WordPress • Joomla • Drupal • Shopify • Wix • Magento • PrestaShop

### Web Servers
Apache • Nginx • IIS • LiteSpeed

### Hosting Providers
AWS • Google Cloud • Azure • DigitalOcean • Cloudflare • Linode • Vultr • Hetzner • OVH

## Installation

### Prerequisites

- Python 3.8 or higher
- pip

### Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/cdn-checker.git
cd cdn-checker
```

2. Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
python app.py
```

5. Open your browser and navigate to:
```
http://localhost:5000
```

## Deployment

### Quick Start (Development)

```bash
python app.py
```

Visit `http://localhost:5000`

### Production Deployment

See [docs/PRODUCTION.md](docs/PRODUCTION.md) for comprehensive deployment guides including:

- **Systemd Service** (Recommended for VPS)
  - Full setup with automatic restart
  - Nginx reverse proxy configuration
  - SSL/HTTPS setup
  - Service management commands

- **Docker Deployment**
  - Single container setup
  - Docker Compose configuration
  - Production best practices

#### Quick Docker Setup

```bash
# Using Docker Compose (Recommended)
docker-compose up -d

# Or using plain Docker
docker build -t cdn-checker .
docker run -d -p 5000:5000 --name cdn-checker cdn-checker
```

#### Quick Systemd Setup (VPS)

```bash
# 1. Setup project
git clone https://github.com/yourusername/cdn-checker.git
cd cdn-checker
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Create systemd service (see PRODUCTION.md for full config)
sudo nano /etc/systemd/system/cdn-checker.service

# 3. Enable and start
sudo systemctl daemon-reload
sudo systemctl enable --now cdn-checker
```

### Platform-as-a-Service

#### Heroku

```bash
echo "web: gunicorn app:app" > Procfile
heroku create your-app-name
git push heroku main
```

#### Railway / Render / Fly.io

These platforms auto-detect Flask apps. Just connect your GitHub repository.

## API Usage

### Check CDN Endpoint

**POST** `/api/check`

Request body:
```json
{
  "url": "example.com"
}
```

Response:
```json
{
  "url": "https://example.com",
  "cdn_detected": "CloudFlare",
  "confidence": 90,
  "evidence": ["Header 'cf-ray' indicates CloudFlare"],
  "headers": { ... },
  "cnames": ["example.com.cdn.cloudflare.net"],
  "ip_address": "104.21.x.x",
  "cms": "WordPress",
  "cms_version": "6.4.2",
  "server": "nginx",
  "security": {
    "score": 85,
    "grade": "A",
    "headers": { ... }
  },
  "ssl": {
    "issuer": "Let's Encrypt",
    "valid_until": "2026-02-10",
    "days_remaining": 92,
    "tls_version": "TLSv1.3"
  },
  "domain_info": {
    "age_years": 10,
    "created": "2015-01-15",
    "expires": "2026-01-15",
    "registrar": "GoDaddy"
  },
  "email_security": {
    "spf": "Configured",
    "dmarc": "Configured",
    "mx": ["mail.example.com"]
  },
  "hosting_provider": "Amazon",
  "performance": {
    "response_time_ms": 145.23,
    "compression": "gzip",
    "page_size_kb": 42.5
  },
  "timestamp": "2025-11-10T02:30:00Z"
}
```

### Rate Limits

- 10 requests per minute per IP
- 50 requests per hour per IP
- 200 requests per day per IP

## Security Features

- ✅ Input validation and sanitization
- ✅ URL length limits (max 2048 chars)
- ✅ Rate limiting with Flask-Limiter
- ✅ Timeout protection on external requests
- ✅ XSS protection with HTML escaping
- ✅ Accepts only valid domain patterns

## Project Structure

```text
cdn-check/
├── app.py                      # Flask app with comprehensive analysis
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Multi-stage Alpine build
├── docker-compose.yml          # Production setup with Watchtower
├── templates/
│   └── index.html             # Responsive UI
├── static/
│   ├── css/
│   │   └── style.css          # Dark theme styling
│   └── js/
│       └── app.js             # Frontend logic
├── .github/workflows/
│   ├── docker-build-deploy.yml # CI/CD pipeline with webhook
│   └── ci.yml                  # Build and security scans
├── docs/                       # Documentation
│   ├── WATCHTOWER.md
│   ├── PRODUCTION.md
│   ├── DOCKER.md
│   └── ...
└── README.md
```

## CI/CD & Deployment

### Automated Deployment Pipeline

- **GitHub Actions** - Builds Docker images on every push
- **Security Scanning** - Trivy (container), Gitleaks (secrets), Semgrep (SAST)
- **Watchtower Webhook** - Instant deployments (< 5 seconds) via HTTP API
- **Multi-platform** - linux/amd64, linux/arm64 support
- **Version Tracking** - Git SHA + timestamp embedded in images

See [docs/GITHUB_ACTIONS.md](docs/GITHUB_ACTIONS.md) and [docs/WATCHTOWER.md](docs/WATCHTOWER.md) for details.

## Contributing

Contributions are welcome! See [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md) for guidelines.

**Ideas for Contributions:**
- Add more CMS platforms and versions
- Improve security header recommendations
- Add export functionality (PDF/JSON reports)
- Historical tracking and comparison
- Dark/light theme toggle
- Multi-language support

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- CDN providers for making the internet faster
- Flask - Python micro web framework
- dnspython - DNS toolkit
- python-whois - Domain information
- BeautifulSoup - HTML parsing
- OpenSSL - SSL/TLS analysis

## Author

**Nedko Hristov**

- GitHub: [@NedkoHristov](https://github.com/NedkoHristov)
- Website: [nedko.info](https://nedko.info)

## Support

If you find this tool helpful:

- ⭐ Star the repository
- 🐛 Report bugs
- 💡 Suggest features
- 🔀 Contribute code
- 📢 Share with others

---

Made with ❤️ for web security and performance analysis
