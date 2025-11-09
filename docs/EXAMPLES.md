# Usage Examples

This document provides practical examples of using the CDN Checker tool.

## Web Interface Examples

### Example 1: Checking a Popular Website

**Input:** `github.com`

**Expected Output:**
- CDN Detected: Amazon CloudFront or Fastly
- Confidence: 80-100%
- CNAME records showing CloudFront or Fastly domains
- Headers like `x-amz-cf-id` or `x-served-by`

### Example 2: Checking with www Prefix

**Input:** `www.cloudflare.com`

**Expected Output:**
- CDN Detected: CloudFlare
- Confidence: 90-100%
- CNAME records showing cloudflare domains
- Headers like `cf-ray`, `cf-cache-status`

### Example 3: Site Without CDN

**Input:** `your-local-hosting.com`

**Expected Output:**
- CDN Detected: None detected
- Confidence: 0%
- Regular server headers (Apache, Nginx, etc.)

## API Examples

### cURL Examples

#### Basic Check
```bash
curl -X POST http://localhost:5000/api/check \
  -H "Content-Type: application/json" \
  -d '{"url": "github.com"}'
```

#### With Output Formatting (using jq)
```bash
curl -s -X POST http://localhost:5000/api/check \
  -H "Content-Type: application/json" \
  -d '{"url": "github.com"}' | jq '.'
```

#### Extract Only CDN Name
```bash
curl -s -X POST http://localhost:5000/api/check \
  -H "Content-Type: application/json" \
  -d '{"url": "github.com"}' | jq -r '.cdn_detected'
```

### Python Examples

#### Basic Usage
```python
import requests
import json

url = "github.com"
response = requests.post(
    'http://localhost:5000/api/check',
    json={'url': url}
)

result = response.json()
print(f"CDN: {result['cdn_detected']}")
print(f"Confidence: {result['confidence']}%")
```

#### Check Multiple Sites
```python
import requests

sites = ['github.com', 'amazon.com', 'cloudflare.com', 'google.com']

for site in sites:
    response = requests.post(
        'http://localhost:5000/api/check',
        json={'url': site}
    )
    result = response.json()
    print(f"{site}: {result['cdn_detected']} ({result['confidence']}%)")
```

#### With Error Handling
```python
import requests
from requests.exceptions import RequestException

def check_cdn(url):
    try:
        response = requests.post(
            'http://localhost:5000/api/check',
            json={'url': url},
            timeout=15
        )
        response.raise_for_status()
        
        result = response.json()
        
        if result.get('error'):
            print(f"Error: {result['error']}")
            return None
            
        return result
        
    except RequestException as e:
        print(f"Request failed: {e}")
        return None

# Usage
result = check_cdn('github.com')
if result:
    print(f"CDN: {result['cdn_detected']}")
    print(f"IP: {result.get('ip_address', 'N/A')}")
    print(f"CNAMEs: {', '.join(result.get('cnames', []))}")
```

### JavaScript/Node.js Example

```javascript
const fetch = require('node-fetch');

async function checkCDN(url) {
    try {
        const response = await fetch('http://localhost:5000/api/check', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ url: url })
        });
        
        const data = await response.json();
        
        console.log(`CDN: ${data.cdn_detected}`);
        console.log(`Confidence: ${data.confidence}%`);
        console.log(`IP: ${data.ip_address}`);
        
        return data;
    } catch (error) {
        console.error('Error:', error);
    }
}

// Usage
checkCDN('github.com');
```

### Bash Script Example

Create a file `check-cdn.sh`:

```bash
#!/bin/bash

# CDN Checker CLI Script

if [ -z "$1" ]; then
    echo "Usage: $0 <website-url>"
    echo "Example: $0 github.com"
    exit 1
fi

URL=$1

echo "Checking CDN for: $URL"
echo "---"

RESPONSE=$(curl -s -X POST http://localhost:5000/api/check \
  -H "Content-Type: application/json" \
  -d "{\"url\": \"$URL\"}")

CDN=$(echo $RESPONSE | jq -r '.cdn_detected')
CONFIDENCE=$(echo $RESPONSE | jq -r '.confidence')
IP=$(echo $RESPONSE | jq -r '.ip_address')

echo "CDN Detected: $CDN"
echo "Confidence: $CONFIDENCE%"
echo "IP Address: $IP"
```

Usage:
```bash
chmod +x check-cdn.sh
./check-cdn.sh github.com
```

## Integration Examples

### Monitor CDN Changes

Check if a website's CDN has changed:

```python
import requests
import time
import json
from datetime import datetime

def monitor_cdn(url, interval=3600):
    """Monitor CDN changes every hour"""
    last_cdn = None
    
    while True:
        response = requests.post(
            'http://localhost:5000/api/check',
            json={'url': url}
        )
        result = response.json()
        current_cdn = result['cdn_detected']
        
        if last_cdn and current_cdn != last_cdn:
            print(f"[{datetime.now()}] CDN CHANGED!")
            print(f"  From: {last_cdn}")
            print(f"  To: {current_cdn}")
        else:
            print(f"[{datetime.now()}] CDN: {current_cdn}")
        
        last_cdn = current_cdn
        time.sleep(interval)

# Monitor every hour
monitor_cdn('example.com', interval=3600)
```

### Save Results to File

```python
import requests
import json
from datetime import datetime

def check_and_save(url, filename='cdn_results.json'):
    response = requests.post(
        'http://localhost:5000/api/check',
        json={'url': url}
    )
    result = response.json()
    
    # Add timestamp
    result['checked_at'] = datetime.now().isoformat()
    
    # Save to file
    with open(filename, 'a') as f:
        f.write(json.dumps(result) + '\n')
    
    print(f"Results saved to {filename}")
    return result

# Check and save
check_and_save('github.com')
```

### Bulk Checking with CSV Export

```python
import requests
import csv
from datetime import datetime

def bulk_check_to_csv(urls, output_file='cdn_report.csv'):
    with open(output_file, 'w', newline='') as csvfile:
        fieldnames = ['url', 'cdn_detected', 'confidence', 'ip_address', 'checked_at']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        
        for url in urls:
            print(f"Checking {url}...")
            
            response = requests.post(
                'http://localhost:5000/api/check',
                json={'url': url}
            )
            result = response.json()
            
            writer.writerow({
                'url': result['url'],
                'cdn_detected': result['cdn_detected'],
                'confidence': result['confidence'],
                'ip_address': result.get('ip_address', 'N/A'),
                'checked_at': datetime.now().isoformat()
            })
    
    print(f"Report saved to {output_file}")

# Usage
sites = ['github.com', 'amazon.com', 'cloudflare.com', 'google.com']
bulk_check_to_csv(sites)
```

## Testing Different Scenarios

### Valid Inputs
- `example.com` - Domain only
- `www.example.com` - With www
- `https://example.com` - With protocol
- `http://example.com` - HTTP protocol
- `example.com/path/to/page` - With path

### Expected Invalid Inputs
These should return errors:
- `not-a-valid-url` - Missing TLD
- `http://` - Incomplete URL
- `` (empty) - Empty input
- Very long URLs (>2048 chars) - Length limit exceeded

## Rate Limit Handling

```python
import requests
import time

def check_with_retry(url, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = requests.post(
                'http://localhost:5000/api/check',
                json={'url': url}
            )
            
            if response.status_code == 429:
                # Rate limited
                print(f"Rate limited. Waiting 60 seconds...")
                time.sleep(60)
                continue
                
            return response.json()
            
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            time.sleep(5)
    
    return None
```

## Production URL

When deploying to production, replace `http://localhost:5000` with your actual domain:

```python
API_URL = 'https://your-cdn-checker.herokuapp.com/api/check'

response = requests.post(API_URL, json={'url': 'github.com'})
```

---

For more examples and use cases, check the [README.md](README.md) or open an issue on GitHub!
