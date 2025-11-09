from flask import Flask, render_template, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import requests
import socket
import dns.resolver
import re
from datetime import datetime

app = Flask(__name__)
limiter = Limiter(key_func=get_remote_address, app=app, default_limits=["200/day", "50/hour"])

# CDN signatures - streamlined for production
CDNS = {
    'CloudFlare': {'headers': ['cf-ray', 'cf-cache-status'], 'cname': r'\.cloudflare\.'},
    'Amazon CloudFront': {'headers': ['x-amz-cf-id'], 'cname': r'\.cloudfront\.net'},
    'Fastly': {'headers': ['fastly-debug-digest', 'x-served-by'], 'cname': r'\.fastly\.'},
    'Akamai': {'headers': ['x-akamai-edgescape'], 'cname': r'\.akamai\.|\.edgesuite\.'},
    'Azure CDN': {'headers': ['x-azure-ref'], 'cname': r'\.azureedge\.'},
    'Google Cloud CDN': {'headers': ['x-goog-generation'], 'cname': r'\.googleusercontent\.'},
    'KeyCDN': {'headers': ['x-edge-location'], 'cname': r'\.kxcdn\.'},
    'BunnyCDN': {'headers': ['cdn-pullzone'], 'cname': r'\.b-cdn\.'},
}

def validate_url(url):
    """Validate and normalize URL"""
    url = url.strip()
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    if not re.match(r'^https?://[a-zA-Z0-9]([a-zA-Z0-9\-\.]+)?[a-zA-Z0-9]$', url):
        return None
    return url

def check_cdn(url):
    """Main CDN detection logic"""
    result = {'url': url, 'cdn_detected': None, 'confidence': 0, 'evidence': [], 
              'ip_address': None, 'cnames': [], 'headers': {}, 'timestamp': datetime.now().isoformat()}
    
    url = validate_url(url)
    if not url:
        result['error'] = 'Invalid URL format'
        return result
    
    try:
        # Get headers
        headers = requests.head(url, timeout=10, allow_redirects=True).headers
        result['headers'] = dict(headers)
        
        # Get IP
        domain = url.replace('https://', '').replace('http://', '').split('/')[0]
        result['ip_address'] = socket.gethostbyname(domain)
        
        # Get CNAMEs
        for d in [domain, 'www.' + domain if not domain.startswith('www.') else domain[4:]]:
            try:
                result['cnames'].extend([str(r.target) for r in dns.resolver.resolve(d, 'CNAME')])
            except:
                pass
        
        # Detect CDN
        scores = {}
        for cdn, sigs in CDNS.items():
            score = 0
            for h in sigs['headers']:
                if any(h.lower() in k.lower() for k in headers.keys()):
                    score += 3
                    result['evidence'].append(f"Header '{h}' → {cdn}")
            for cname in result['cnames']:
                if re.search(sigs['cname'], cname.lower()):
                    score += 4
                    result['evidence'].append(f"CNAME '{cname}' → {cdn}")
            if score > 0:
                scores[cdn] = score
        
        if scores:
            result['cdn_detected'] = max(scores, key=scores.get)
            result['confidence'] = min(scores[result['cdn_detected']] * 10, 100)
        else:
            result['cdn_detected'] = 'None detected'
            
    except Exception as e:
        result['error'] = str(e)
    
    return result

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/check', methods=['POST'])
@limiter.limit("10/minute")
def api_check():
    data = request.get_json()
    if not data or 'url' not in data:
        return jsonify({'error': 'URL required'}), 400
    if len(data['url']) > 2048:
        return jsonify({'error': 'URL too long'}), 400
    return jsonify(check_cdn(data['url']))

@app.errorhandler(429)
def ratelimit(e):
    return jsonify({'error': 'Rate limit exceeded'}), 429

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
