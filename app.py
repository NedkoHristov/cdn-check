from flask import Flask, render_template, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import requests
import socket
import dns.resolver
import re
import urllib.parse
from typing import Dict, List, Optional
import time
from datetime import datetime

app = Flask(__name__)

# Rate limiting setup
limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"]
)

class CDNDetector:
    def __init__(self):
        # Known CDN providers and their identifying characteristics
        self.cdn_signatures = {
            'CloudFlare': {
                'headers': ['cf-ray', 'cf-cache-status', 'cf-request-id'],
                'cname_patterns': [r'\.cloudflare\.', r'\.cloudflaressl\.'],
                'server_headers': ['cloudflare'],
                'domains': ['cloudflare.com', 'cloudflaressl.com']
            },
            'Amazon CloudFront': {
                'headers': ['x-amz-cf-id', 'x-amzn-requestid', 'x-amz-cf-pop'],
                'cname_patterns': [r'\.cloudfront\.net', r'\.amazonaws\.'],
                'server_headers': ['amazon', 'cloudfront'],
                'domains': ['cloudfront.net', 'amazonaws.com']
            },
            'Fastly': {
                'headers': ['fastly-debug-digest', 'x-served-by', 'x-cache'],
                'cname_patterns': [r'\.fastly\.', r'\.fastlylb\.'],
                'server_headers': ['fastly'],
                'domains': ['fastly.com', 'fastlylb.net']
            },
            'KeyCDN': {
                'headers': ['x-edge-location', 'x-cache'],
                'cname_patterns': [r'\.kxcdn\.'],
                'server_headers': ['keycdn'],
                'domains': ['kxcdn.com']
            },
            'MaxCDN/StackPath': {
                'headers': ['x-maxcdn-pop', 'x-pull', 'x-cache'],
                'cname_patterns': [r'\.maxcdn\.', r'\.stackpathdns\.'],
                'server_headers': ['maxcdn', 'stackpath'],
                'domains': ['maxcdn.com', 'stackpathdns.com']
            },
            'Akamai': {
                'headers': ['x-akamai-edgescape', 'x-akamai-config-log-detail'],
                'cname_patterns': [r'\.akamai\.', r'\.edgesuite\.', r'\.edgekey\.'],
                'server_headers': ['akamai'],
                'domains': ['akamai.net', 'edgesuite.net', 'edgekey.net']
            },
            'Azure CDN': {
                'headers': ['x-azure-ref', 'x-cache'],
                'cname_patterns': [r'\.azureedge\.', r'\.vo\.msecnd\.'],
                'server_headers': ['azure', 'microsoft'],
                'domains': ['azureedge.net', 'vo.msecnd.net']
            },
            'Google Cloud CDN': {
                'headers': ['x-goog-generation', 'x-guploader-uploadid'],
                'cname_patterns': [r'\.googleusercontent\.', r'\.gstatic\.'],
                'server_headers': ['gws', 'google'],
                'domains': ['googleusercontent.com', 'gstatic.com']
            },
            'Incapsula': {
                'headers': ['x-iinfo', 'x-cdn'],
                'cname_patterns': [r'\.incapdns\.'],
                'server_headers': ['incapsula'],
                'domains': ['incapdns.net']
            },
            'BunnyCDN': {
                'headers': ['cdn-pullzone', 'cdn-requestcountrycode'],
                'cname_patterns': [r'\.b-cdn\.'],
                'server_headers': ['bunnycdn'],
                'domains': ['b-cdn.net']
            }
        }

    def validate_url(self, url: str) -> Optional[str]:
        """Validate and normalize the input URL"""
        if not url:
            return None
            
        # Remove any extra whitespace
        url = url.strip()
        
        # Add protocol if missing
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        # Parse and validate the URL
        try:
            parsed = urllib.parse.urlparse(url)
            if not parsed.netloc:
                return None
            
            # Check if domain is valid (basic validation)
            domain_pattern = re.compile(
                r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$'
            )
            
            if not domain_pattern.match(parsed.netloc):
                return None
                
            return url
            
        except Exception:
            return None

    def get_http_headers(self, url: str) -> Dict:
        """Get HTTP headers from the website"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (CDN-Checker-Bot/1.0)'
            }
            response = requests.head(url, headers=headers, timeout=10, allow_redirects=True)
            return dict(response.headers)
        except Exception as e:
            try:
                # Fallback to GET request with minimal data
                response = requests.get(url, headers=headers, timeout=10, stream=True)
                response.close()
                return dict(response.headers)
            except Exception:
                return {}

    def get_cname_records(self, domain: str) -> List[str]:
        """Get CNAME records for the domain"""
        cnames = []
        try:
            # Remove protocol and www if present
            clean_domain = domain.replace('https://', '').replace('http://', '')
            clean_domain = clean_domain.split('/')[0]
            
            # Try both with and without www
            domains_to_check = [clean_domain]
            if not clean_domain.startswith('www.'):
                domains_to_check.append('www.' + clean_domain)
            else:
                domains_to_check.append(clean_domain[4:])
            
            for check_domain in domains_to_check:
                try:
                    answers = dns.resolver.resolve(check_domain, 'CNAME')
                    for answer in answers:
                        cnames.append(str(answer.target))
                except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
                    continue
                except Exception:
                    continue
                    
        except Exception:
            pass
            
        return cnames

    def get_ip_address(self, domain: str) -> Optional[str]:
        """Get IP address of the domain"""
        try:
            clean_domain = domain.replace('https://', '').replace('http://', '')
            clean_domain = clean_domain.split('/')[0]
            ip = socket.gethostbyname(clean_domain)
            return ip
        except Exception:
            return None

    def detect_cdn(self, url: str) -> Dict:
        """Main function to detect CDN"""
        result = {
            'url': url,
            'cdn_detected': None,
            'confidence': 0,
            'evidence': [],
            'headers': {},
            'cnames': [],
            'ip_address': None,
            'timestamp': datetime.now().isoformat(),
            'error': None
        }
        
        try:
            # Validate URL
            validated_url = self.validate_url(url)
            if not validated_url:
                result['error'] = 'Invalid URL format'
                return result
                
            result['url'] = validated_url
            
            # Get headers
            headers = self.get_http_headers(validated_url)
            result['headers'] = headers
            
            # Get CNAME records
            cnames = self.get_cname_records(validated_url)
            result['cnames'] = cnames
            
            # Get IP address
            ip_address = self.get_ip_address(validated_url)
            result['ip_address'] = ip_address
            
            # Analyze for CDN signatures
            cdn_scores = {}
            evidence = []
            
            for cdn_name, signatures in self.cdn_signatures.items():
                score = 0
                
                # Check headers
                for header_name in signatures['headers']:
                    if any(header_name.lower() in h.lower() for h in headers.keys()):
                        score += 3
                        evidence.append(f"Header '{header_name}' indicates {cdn_name}")
                
                # Check server header
                server_header = headers.get('Server', '').lower()
                for server_sig in signatures['server_headers']:
                    if server_sig.lower() in server_header:
                        score += 2
                        evidence.append(f"Server header indicates {cdn_name}")
                
                # Check CNAME patterns
                for cname in cnames:
                    for pattern in signatures['cname_patterns']:
                        if re.search(pattern, cname.lower()):
                            score += 4
                            evidence.append(f"CNAME '{cname}' indicates {cdn_name}")
                
                if score > 0:
                    cdn_scores[cdn_name] = score
            
            # Determine the most likely CDN
            if cdn_scores:
                best_cdn = max(cdn_scores, key=cdn_scores.get)
                result['cdn_detected'] = best_cdn
                result['confidence'] = min(cdn_scores[best_cdn] * 10, 100)
                result['evidence'] = evidence
            else:
                result['cdn_detected'] = 'None detected'
                result['confidence'] = 0
                
        except Exception as e:
            result['error'] = f"Analysis failed: {str(e)}"
            
        return result

# Initialize the detector
detector = CDNDetector()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/check', methods=['POST'])
@limiter.limit("10 per minute")
def check_cdn():
    try:
        data = request.get_json()
        if not data or 'url' not in data:
            return jsonify({'error': 'URL is required'}), 400
        
        url = data['url']
        
        # Additional security: length check
        if len(url) > 2048:
            return jsonify({'error': 'URL too long'}), 400
        
        result = detector.detect_cdn(url)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify({'error': 'Rate limit exceeded. Please try again later.'}), 429

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
