# Quick Start Guide

## Installation (5 minutes)

### Option 1: Automatic Setup (Linux/Mac)

```bash
chmod +x setup.sh
./setup.sh
```

### Option 2: Manual Setup (All platforms)

```bash
# 1. Create virtual environment
python3 -m venv venv

# 2. Activate it
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
```

## Running the Application

### Development Mode

```bash
python app.py
```

Open browser to: `http://localhost:5000`

### Production Mode

```bash
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

## Testing

```bash
# Start the server first
python app.py

# In another terminal, run tests
python test_app.py
```

## Usage Examples

### Web Interface

1. Navigate to `http://localhost:5000`
2. Enter a website URL (e.g., `github.com` or `www.cloudflare.com`)
3. Click "Check CDN"
4. View results

### API Usage

```bash
curl -X POST http://localhost:5000/api/check \
  -H "Content-Type: application/json" \
  -d '{"url": "github.com"}'
```

### Python Script

```python
import requests

response = requests.post(
    'http://localhost:5000/api/check',
    json={'url': 'github.com'}
)

data = response.json()
print(f"CDN: {data['cdn_detected']}")
print(f"Confidence: {data['confidence']}%")
```

## Common Issues

### Port already in use

```bash
# Find and kill the process using port 5000
# Linux/Mac:
lsof -ti:5000 | xargs kill -9

# Windows:
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

### DNS resolution errors

Make sure you have internet connectivity. The tool needs to query DNS records.

### Rate limiting

If you're getting rate limited:
- Wait a minute before trying again
- The limits are: 10/minute, 50/hour, 200/day per IP

## Docker Deployment

```bash
# Build
docker build -t cdn-checker .

# Run
docker run -p 5000:5000 cdn-checker
```

## Environment Variables

Optional environment variables (create `.env` file):

```env
FLASK_APP=app.py
FLASK_ENV=production
SECRET_KEY=your-secret-key-here
```

## Support

- Report issues: GitHub Issues
- Read docs: README.md
- Contribute: CONTRIBUTING.md
