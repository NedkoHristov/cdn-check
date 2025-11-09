# CDN Checker - Project Overview

## 📁 Project Structure

```
cdn-checker/
├── 📄 app.py                      # Main Flask application with CDN detection logic
├── 📄 requirements.txt            # Python dependencies
├── 📄 Procfile                    # Heroku deployment config
├── 📄 Dockerfile                  # Docker container config
├── 📄 runtime.txt                 # Python version specification
├── 📄 setup.sh                    # Automatic setup script
├── 📄 test_app.py                 # Test suite
├── 📄 .env.example                # Environment variables template
├── 📄 .gitignore                  # Git ignore rules
├── 📄 README.md                   # Main documentation
├── 📄 QUICKSTART.md               # Quick start guide
├── 📄 CONTRIBUTING.md             # Contribution guidelines
├── 📄 LICENSE                     # MIT License
├── 📁 templates/
│   └── 📄 index.html              # Main HTML interface
├── 📁 static/
│   ├── 📁 css/
│   │   └── 📄 style.css           # All styling
│   └── 📁 js/
│       └── 📄 app.js              # Frontend JavaScript
└── 📁 .github/
    └── 📁 workflows/
        └── 📄 ci.yml              # GitHub Actions CI/CD
```

## 🚀 Key Features

### Backend (app.py)
- **Flask web server** with API endpoints
- **CDN detection algorithm** analyzing:
  - HTTP headers (10+ specific headers per CDN)
  - DNS CNAME records
  - Server response headers
  - IP address resolution
- **Security features**:
  - URL validation and sanitization
  - Rate limiting (10/min, 50/hour, 200/day)
  - Input length restrictions
  - Timeout protection
- **10+ CDN providers** supported:
  - CloudFlare, AWS CloudFront, Fastly
  - Akamai, Azure CDN, Google Cloud CDN
  - KeyCDN, MaxCDN/StackPath, Incapsula, BunnyCDN

### Frontend
- **Modern, responsive UI** with gradient design
- **Real-time validation** of user input
- **Animated results** with confidence meter
- **Detailed information display**:
  - CDN provider with confidence level
  - IP address
  - CNAME records
  - HTTP headers
  - Evidence list
- **Mobile-friendly** design
- **Client-side input validation**

### Security Best Practices
- ✅ Input sanitization (URL validation)
- ✅ Rate limiting per IP
- ✅ XSS protection (HTML escaping)
- ✅ Request timeouts
- ✅ Length limits on inputs
- ✅ Safe regex patterns
- ✅ No eval() or dangerous functions

## 🔧 Technology Stack

- **Backend**: Python 3.11 + Flask
- **DNS Resolution**: dnspython
- **HTTP Requests**: requests library
- **Rate Limiting**: Flask-Limiter
- **Frontend**: Vanilla JavaScript (no frameworks)
- **Styling**: Pure CSS with CSS Grid/Flexbox
- **Deployment**: Gunicorn WSGI server

## 📊 API Specification

### Endpoint: POST /api/check

**Request:**
```json
{
  "url": "example.com"
}
```

**Response:**
```json
{
  "url": "https://example.com",
  "cdn_detected": "CloudFlare",
  "confidence": 90,
  "evidence": [
    "Header 'cf-ray' indicates CloudFlare",
    "CNAME 'example.com.cdn.cloudflare.net' indicates CloudFlare"
  ],
  "headers": {
    "Server": "cloudflare",
    "CF-Ray": "..."
  },
  "cnames": ["example.com.cdn.cloudflare.net"],
  "ip_address": "104.21.x.x",
  "timestamp": "2025-11-09T10:30:00"
}
```

## 🎨 Design Principles

1. **Simplicity**: One input field, one button, clear results
2. **Performance**: Fast detection (< 5 seconds typical)
3. **Reliability**: Fallback mechanisms for network issues
4. **User Experience**: Smooth animations, clear feedback
5. **Accessibility**: Semantic HTML, keyboard navigation
6. **Mobile-First**: Responsive design for all screen sizes

## 🔍 CDN Detection Algorithm

```
1. Normalize URL (add protocol, handle www)
2. Validate URL format
3. Make HTTP HEAD request (fallback to GET)
4. Query DNS for CNAME records
5. Resolve IP address
6. Score each CDN provider based on:
   - Header matches (+3 points each)
   - Server header matches (+2 points each)
   - CNAME pattern matches (+4 points each)
7. Return highest-scoring CDN with confidence %
```

## 📦 Deployment Options

- **Local**: `python app.py`
- **Production**: `gunicorn app:app`
- **Docker**: `docker run -p 5000:5000 cdn-checker`
- **Heroku**: One-click deploy with Procfile
- **Railway/Render**: Auto-deploy from GitHub
- **Cloud VMs**: Works on any Linux server

## 🧪 Testing

Run the test suite:
```bash
python test_app.py
```

Tests verify:
- Server is running
- API endpoint is responsive
- CDN detection works for known sites
- Error handling is correct

## 📈 Future Enhancements

Potential improvements:
- [ ] Cache results to reduce API calls
- [ ] Historical tracking of CDN changes
- [ ] Bulk checking multiple URLs
- [ ] Export results (JSON/CSV/PDF)
- [ ] More CDN providers
- [ ] Geographic CDN edge location detection
- [ ] Performance metrics (response time, TTFB)
- [ ] Browser extension version
- [ ] CLI tool version

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📝 License

MIT License - see [LICENSE](LICENSE) file.

## 👨‍💻 Maintenance

This project is:
- ✅ Production-ready
- ✅ Well-documented
- ✅ Actively maintained
- ✅ Open for contributions

---

**Built with ❤️ for the web development community**
