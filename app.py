from flask import Flask, render_template, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import requests
import socket
import dns.resolver
import re
from datetime import datetime
import urllib3
import os

# Suppress SSL warnings for sites with invalid certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)
limiter = Limiter(key_func=get_remote_address, app=app, default_limits=["200/day", "50/hour"])

# Version info - set via environment variables during build
VERSION = os.environ.get('APP_VERSION', 'dev')
BUILD_TIME = os.environ.get('BUILD_TIME', 'local')

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
    'SiteGround CDN': {
        'headers': ['sg-cdn'],
        'cname': r'\.sgcdn\.|\.siteground\.'
    },
}

def validate_url(url):
    """Validate and normalize URL with improved handling"""
    url = url.strip()
    
    # Remove trailing slashes
    url = url.rstrip('/')
    
    # Add protocol if missing
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    # Extract domain for validation
    domain_pattern = r'^https?://([a-zA-Z0-9]([a-zA-Z0-9\-]*[a-zA-Z0-9])?\.)*[a-zA-Z0-9]([a-zA-Z0-9\-]*[a-zA-Z0-9])?(\:[0-9]+)?(/.*)?$'
    if not re.match(domain_pattern, url):
        return None, 'Invalid URL format. Please enter a valid domain (e.g., example.com or https://example.com)'
    
    return url, None

def check_cdn(url):
    """Main CDN detection logic with improved error handling"""
    result = {'url': url, 'cdn_detected': None, 'confidence': 0, 'evidence': [], 
              'ip_address': None, 'cnames': [], 'headers': {}, 'timestamp': datetime.now().isoformat()}
    
    # Validate URL
    validated_url, error = validate_url(url)
    if error:
        result['error'] = error
        return result
    
    url = validated_url
    result['url'] = url
    
    try:
        # Extract domain from URL
        domain = url.replace('https://', '').replace('http://', '').split('/')[0].split(':')[0]
        
        # Get headers with better error handling
        try:
            response = requests.head(url, timeout=10, allow_redirects=True, verify=True)
            result['headers'] = dict(response.headers)
            headers = response.headers
        except requests.exceptions.SSLError:
            # Try without SSL verification if certificate is invalid
            try:
                response = requests.head(url, timeout=10, allow_redirects=True, verify=False)
                result['headers'] = dict(response.headers)
                headers = response.headers
                result['evidence'].append('⚠️ SSL certificate verification failed - results may be inaccurate')
            except Exception as e:
                result['error'] = f'Unable to connect to website. The site may be down or unreachable.'
                return result
        except requests.exceptions.ConnectionError:
            result['error'] = f'Connection failed. The website "{domain}" could not be reached. Please verify the URL is correct.'
            return result
        except requests.exceptions.Timeout:
            result['error'] = f'Connection timeout. The website "{domain}" took too long to respond.'
            return result
        except requests.exceptions.TooManyRedirects:
            result['error'] = 'Too many redirects. The website may have a redirect loop.'
            return result
        except requests.exceptions.RequestException as e:
            result['error'] = f'Unable to check website. Please verify the URL is correct and accessible.'
            return result
        
        # Get IP address
        try:
            result['ip_address'] = socket.gethostbyname(domain)
        except socket.gaierror:
            result['error'] = f'Domain "{domain}" does not exist or cannot be resolved.'
            return result
        except Exception as e:
            result['evidence'].append('⚠️ Could not resolve IP address')
        
        # Get CNAMEs
        for d in [domain, 'www.' + domain if not domain.startswith('www.') else domain[4:]]:
            try:
                result['cnames'].extend([str(r.target) for r in dns.resolver.resolve(d, 'CNAME')])
            except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.resolver.NoNameservers):
                pass
            except Exception:
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
        result['error'] = f'An unexpected error occurred while checking the website.'
    
    return result

@app.route('/')
def index():
    return render_template('index.html', version=VERSION, build_time=BUILD_TIME)

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
