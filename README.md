# CDN Checker 🌐

A simple, secure web tool to detect which Content Delivery Network (CDN) a website is using. Built with Python Flask and vanilla JavaScript.

## Live Demo

🔗 [View Demo](https://your-demo-url.com) *(Update with your actual demo URL)*

## Features

- ✅ **CDN Detection** - Identifies 10+ major CDN providers including CloudFlare, AWS CloudFront, Fastly, Akamai, and more
- 🔒 **Security First** - Input validation, rate limiting, and sanitization built-in
- 📊 **Detailed Analysis** - Shows HTTP headers, CNAME records, IP address, and detection confidence
- 🎨 **Modern UI** - Clean, responsive design that works on all devices
- ⚡ **Fast & Simple** - No complex setup, just Python and Flask
- 🌍 **Flexible Input** - Accepts URLs with or without `www` prefix

## How It Works

The tool analyzes three main indicators to detect CDN usage:

1. **HTTP Headers** - Looks for CDN-specific headers (e.g., `cf-ray`, `x-amz-cf-id`)
2. **DNS CNAME Records** - Checks for CDN provider domains in DNS records
3. **Server Headers** - Analyzes server response headers for CDN signatures

## Supported CDN Providers

- CloudFlare
- Amazon CloudFront
- Fastly
- Akamai
- Azure CDN
- Google Cloud CDN
- KeyCDN
- MaxCDN/StackPath
- Incapsula
- BunnyCDN

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

### Using Gunicorn (Production)

```bash
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

### Using Docker

Create a `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

Build and run:

```bash
docker build -t cdn-checker .
docker run -p 5000:5000 cdn-checker
```

### Deploy to Various Platforms

#### Heroku

```bash
# Add Procfile
echo "web: gunicorn app:app" > Procfile

# Deploy
heroku create your-app-name
git push heroku main
```

#### Railway / Render / Fly.io

These platforms auto-detect Flask apps. Just connect your GitHub repository and they'll handle the deployment.

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
  "evidence": [
    "Header 'cf-ray' indicates CloudFlare",
    "CNAME 'example.com.cdn.cloudflare.net' indicates CloudFlare"
  ],
  "headers": { ... },
  "cnames": ["example.com.cdn.cloudflare.net"],
  "ip_address": "104.21.x.x",
  "timestamp": "2025-11-09T10:30:00"
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

```
cdn-checker/
├── app.py                 # Flask application and CDN detection logic
├── requirements.txt       # Python dependencies
├── templates/
│   └── index.html        # Frontend HTML
├── static/
│   ├── css/
│   │   └── style.css     # Styling
│   └── js/
│       └── app.js        # Frontend JavaScript
└── README.md
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. Here are some areas that could use improvement:

- Add more CDN providers
- Improve detection accuracy
- Add caching for repeated checks
- Add export functionality (JSON/CSV)
- Add historical tracking

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Thanks to all the CDN providers for making the internet faster
- Built with Flask, the Python micro web framework
- DNS resolution powered by dnspython

## Author

**Your Name**
- GitHub: [@yourusername](https://github.com/yourusername)
- Website: [your-website.com](https://your-website.com)

## Support

If you find this tool helpful, please consider:
- ⭐ Starring the repository
- 🐛 Reporting bugs
- 💡 Suggesting new features
- 🔀 Contributing code

---

Made with ❤️ for the web development community
