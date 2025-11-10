from flask import Flask, render_template, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import requests
import socket
import dns.resolver
import re
from datetime import datetime, timedelta
import urllib3
import os
import whois
from bs4 import BeautifulSoup
import ssl
import OpenSSL
from urllib.parse import urlparse

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

# CMS detection signatures
CMS_SIGNATURES = {
    'WordPress': {
        'headers': ['x-powered-by'],
        'header_values': {'x-powered-by': r'WordPress'},
        'meta_tags': [r'<meta name="generator" content="WordPress ([0-9.]+)"'],
        'paths': ['/wp-content/', '/wp-includes/', '/wp-json/'],
        'cookies': ['wordpress_']
    },
    'Joomla': {
        'meta_tags': [r'<meta name="generator" content="Joomla!?\s*([0-9.]+)"'],
        'paths': ['/components/', '/modules/', '/templates/'],
        'headers': ['x-content-encoded-by'],
        'header_values': {'x-content-encoded-by': r'Joomla'}
    },
    'Drupal': {
        'headers': ['x-drupal-cache', 'x-generator'],
        'header_values': {'x-generator': r'Drupal ([0-9.]+)'},
        'meta_tags': [r'<meta name="generator" content="Drupal ([0-9.]+)"'],
        'paths': ['/sites/default/', '/core/']
    },
    'Shopify': {
        'headers': ['x-shopid', 'x-shopify-stage'],
        'paths': ['/cdn.shopify.com/'],
        'cookies': ['_shopify_']
    },
    'Wix': {
        'headers': ['x-wix-request-id', 'x-wix-renderer-server'],
        'paths': ['static.wixstatic.com']
    },
    'Magento': {
        'cookies': ['frontend='],
        'paths': ['/media/catalog/', '/skin/frontend/'],
        'headers': ['x-magento-']
    },
    'PrestaShop': {
        'cookies': ['PrestaShop-'],
        'paths': ['/modules/', '/themes/']
    }
}

def detect_cms(url, headers, html_content=None):
    """Detect CMS and version from headers and HTML content"""
    cms_info = {'name': None, 'version': None}
    
    for cms_name, signatures in CMS_SIGNATURES.items():
        # Check headers
        if 'headers' in signatures:
            for header in signatures['headers']:
                if any(header.lower() in k.lower() for k in headers.keys()):
                    cms_info['name'] = cms_name
                    # Check for version in header value
                    if 'header_values' in signatures:
                        for hdr, pattern in signatures['header_values'].items():
                            if hdr.lower() in [k.lower() for k in headers.keys()]:
                                header_val = headers.get(hdr) or headers.get(hdr.lower()) or headers.get(hdr.upper())
                                if header_val:
                                    match = re.search(pattern, str(header_val), re.IGNORECASE)
                                    if match and match.groups():
                                        cms_info['version'] = match.group(1)
        
        # Check cookies
        if 'cookies' in signatures:
            set_cookie = headers.get('set-cookie', '')
            for cookie_sig in signatures['cookies']:
                if cookie_sig.lower() in set_cookie.lower():
                    cms_info['name'] = cms_name
        
        # Check HTML content for meta tags
        if html_content and 'meta_tags' in signatures:
            for pattern in signatures['meta_tags']:
                match = re.search(pattern, html_content, re.IGNORECASE)
                if match:
                    cms_info['name'] = cms_name
                    if match.groups():
                        cms_info['version'] = match.group(1)
        
        # Check for common paths in HTML
        if html_content and 'paths' in signatures:
            for path in signatures['paths']:
                if path in html_content:
                    cms_info['name'] = cms_name
        
        if cms_info['name']:
            break
    
    return cms_info

def detect_technologies(headers, html_content):
    """Detect web technologies from headers and HTML"""
    tech = {'server': None, 'language': [], 'frameworks': [], 'analytics': []}
    
    # Server detection
    server_header = headers.get('server', headers.get('Server', ''))
    if server_header:
        tech['server'] = server_header
    
    # Language detection from headers
    x_powered_by = headers.get('x-powered-by', headers.get('X-Powered-By', ''))
    if x_powered_by:
        if 'PHP' in x_powered_by:
            tech['language'].append(x_powered_by)
        elif 'ASP.NET' in x_powered_by:
            tech['language'].append(x_powered_by)
    
    if html_content:
        # Framework detection
        if 'react' in html_content.lower() or '__react' in html_content.lower():
            tech['frameworks'].append('React')
        if 'vue.js' in html_content.lower() or '__vue' in html_content.lower():
            tech['frameworks'].append('Vue.js')
        if 'ng-version' in html_content.lower() or 'angular' in html_content.lower():
            tech['frameworks'].append('Angular')
        if 'next.js' in html_content.lower() or '__next' in html_content.lower():
            tech['frameworks'].append('Next.js')
        
        # Analytics detection
        if 'google-analytics.com' in html_content or 'gtag' in html_content:
            tech['analytics'].append('Google Analytics')
        if 'connect.facebook.net' in html_content or 'fbq(' in html_content:
            tech['analytics'].append('Facebook Pixel')
        if 'hotjar.com' in html_content:
            tech['analytics'].append('Hotjar')
    
    return tech

def analyze_security_headers(headers):
    """Analyze security headers and provide a score"""
    security = {
        'score': 0,
        'max_score': 100,
        'headers': {},
        'grade': 'F'
    }
    
    security_headers = {
        'strict-transport-security': {'points': 20, 'name': 'HSTS'},
        'content-security-policy': {'points': 20, 'name': 'CSP'},
        'x-frame-options': {'points': 15, 'name': 'X-Frame-Options'},
        'x-content-type-options': {'points': 15, 'name': 'X-Content-Type-Options'},
        'x-xss-protection': {'points': 10, 'name': 'X-XSS-Protection'},
        'referrer-policy': {'points': 10, 'name': 'Referrer-Policy'},
        'permissions-policy': {'points': 10, 'name': 'Permissions-Policy'}
    }
    
    for header, config in security_headers.items():
        header_value = None
        for h in headers.keys():
            if h.lower() == header:
                header_value = headers[h]
                break
        
        if header_value:
            security['score'] += config['points']
            security['headers'][config['name']] = '✓ Present'
        else:
            security['headers'][config['name']] = '✗ Missing'
    
    # Calculate grade
    if security['score'] >= 90:
        security['grade'] = 'A+'
    elif security['score'] >= 80:
        security['grade'] = 'A'
    elif security['score'] >= 70:
        security['grade'] = 'B'
    elif security['score'] >= 60:
        security['grade'] = 'C'
    elif security['score'] >= 50:
        security['grade'] = 'D'
    else:
        security['grade'] = 'F'
    
    return security

def get_ssl_info(domain):
    """Get SSL certificate information"""
    try:
        context = ssl.create_default_context()
        with socket.create_connection((domain, 443), timeout=5) as sock:
            with context.wrap_socket(sock, server_hostname=domain) as ssock:
                cert = ssock.getpeercert()
                
                # Parse certificate
                issuer = dict(x[0] for x in cert['issuer'])
                subject = dict(x[0] for x in cert['subject'])
                
                # Get expiry date
                not_after = datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
                days_until_expiry = (not_after - datetime.now()).days
                
                # Get TLS version
                tls_version = ssock.version()
                
                return {
                    'issuer': issuer.get('organizationName', 'Unknown'),
                    'subject': subject.get('commonName', domain),
                    'valid_until': not_after.strftime('%Y-%m-%d'),
                    'days_remaining': days_until_expiry,
                    'tls_version': tls_version,
                    'status': 'Valid' if days_until_expiry > 0 else 'Expired'
                }
    except Exception as e:
        return {'error': 'Could not retrieve SSL information'}

def get_domain_info(domain):
    """Get domain registration and age information"""
    try:
        # Remove www. prefix if present
        clean_domain = domain.replace('www.', '')
        
        w = whois.whois(clean_domain)
        
        # Get creation date
        creation_date = w.creation_date
        if isinstance(creation_date, list):
            creation_date = creation_date[0]
        
        # Get expiration date
        expiration_date = w.expiration_date
        if isinstance(expiration_date, list):
            expiration_date = expiration_date[0]
        
        # Calculate age
        if creation_date:
            age_days = (datetime.now() - creation_date).days
            age_years = age_days // 365
            
            return {
                'age_years': age_years,
                'age_days': age_days,
                'created': creation_date.strftime('%Y-%m-%d') if creation_date else 'Unknown',
                'expires': expiration_date.strftime('%Y-%m-%d') if expiration_date else 'Unknown',
                'registrar': w.registrar if hasattr(w, 'registrar') else 'Unknown'
            }
    except Exception as e:
        pass
    
    return None

def get_email_security(domain):
    """Check email security records (SPF, DMARC, MX)"""
    email_sec = {'spf': None, 'dmarc': None, 'mx': []}
    
    # Remove www. prefix
    clean_domain = domain.replace('www.', '')
    
    try:
        # Check SPF
        try:
            spf_records = dns.resolver.resolve(clean_domain, 'TXT')
            for record in spf_records:
                txt = str(record)
                if 'v=spf1' in txt:
                    email_sec['spf'] = 'Configured'
                    break
            if not email_sec['spf']:
                email_sec['spf'] = 'Not found'
        except:
            email_sec['spf'] = 'Not found'
        
        # Check DMARC
        try:
            dmarc_records = dns.resolver.resolve(f'_dmarc.{clean_domain}', 'TXT')
            for record in dmarc_records:
                txt = str(record)
                if 'v=DMARC1' in txt:
                    email_sec['dmarc'] = 'Configured'
                    break
            if not email_sec['dmarc']:
                email_sec['dmarc'] = 'Not found'
        except:
            email_sec['dmarc'] = 'Not found'
        
        # Check MX records
        try:
            mx_records = dns.resolver.resolve(clean_domain, 'MX')
            email_sec['mx'] = [str(r.exchange) for r in mx_records]
        except:
            email_sec['mx'] = []
    except:
        pass
    
    return email_sec

def detect_hosting_provider(ip_address, domain):
    """Detect hosting provider based on IP and reverse DNS"""
    providers = {
        'Amazon': ['amazonaws.com', 'aws', 'ec2'],
        'Google Cloud': ['googleusercontent.com', 'google.com', 'gcp'],
        'Microsoft Azure': ['azure', 'microsoft.com'],
        'Cloudflare': ['cloudflare.com'],
        'DigitalOcean': ['digitalocean.com'],
        'Linode': ['linode.com'],
        'Vultr': ['vultr.com'],
        'Hetzner': ['hetzner.com'],
        'OVH': ['ovh.net', 'ovh.com']
    }
    
    try:
        # Reverse DNS lookup
        reverse_dns = socket.gethostbyaddr(ip_address)[0]
        
        for provider, patterns in providers.items():
            for pattern in patterns:
                if pattern in reverse_dns.lower():
                    return provider
    except:
        pass
    
    return 'Unknown'

def get_performance_metrics(response, start_time):
    """Calculate performance metrics"""
    metrics = {}
    
    # Response time
    response_time = (datetime.now() - start_time).total_seconds() * 1000  # in ms
    metrics['response_time_ms'] = round(response_time, 2)
    
    # Check compression
    content_encoding = response.headers.get('content-encoding', '').lower()
    if 'gzip' in content_encoding:
        metrics['compression'] = 'gzip'
    elif 'br' in content_encoding:
        metrics['compression'] = 'brotli'
    else:
        metrics['compression'] = 'none'
    
    # HTTP version (approximation)
    metrics['http_version'] = 'HTTP/1.1'  # Most common, hard to detect HTTP/2 with requests library
    
    # Page size
    content_length = response.headers.get('content-length')
    if content_length:
        size_kb = int(content_length) / 1024
        metrics['page_size_kb'] = round(size_kb, 2)
    
    return metrics

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
    start_time = datetime.now()  # Track start time for performance metrics
    result = {'url': url, 'cdn_detected': None, 'confidence': 0, 'evidence': [], 
              'ip_address': None, 'cnames': [], 'headers': {}, 'timestamp': start_time.isoformat()}
    
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
        
        # Get headers and HTML content with better error handling
        html_content = None
        try:
            response = requests.get(url, timeout=10, allow_redirects=True, verify=True)
            result['headers'] = dict(response.headers)
            headers = response.headers
            html_content = response.text[:50000]  # Only first 50KB for CMS detection
        except requests.exceptions.SSLError:
            # Try without SSL verification if certificate is invalid
            try:
                response = requests.get(url, timeout=10, allow_redirects=True, verify=False)
                result['headers'] = dict(response.headers)
                headers = response.headers
                html_content = response.text[:50000]  # Only first 50KB for CMS detection
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
        
        # Detect CMS
        cms_info = detect_cms(url, headers, html_content)
        if cms_info['name']:
            result['cms'] = cms_info['name']
            if cms_info['version']:
                result['cms_version'] = cms_info['version']
                result['evidence'].append(f"CMS: {cms_info['name']} {cms_info['version']}")
            else:
                result['evidence'].append(f"CMS: {cms_info['name']}")
        
        # Detect technologies
        tech = detect_technologies(headers, html_content)
        if tech['server']:
            result['server'] = tech['server']
        if tech['language']:
            result['language'] = tech['language']
        if tech['frameworks']:
            result['frameworks'] = tech['frameworks']
        if tech['analytics']:
            result['analytics'] = tech['analytics']
        
        # Analyze security headers
        security = analyze_security_headers(headers)
        result['security'] = security
        
        # Get SSL information
        ssl_info = get_ssl_info(domain)
        if 'error' not in ssl_info:
            result['ssl'] = ssl_info
        
        # Get domain information
        domain_info = get_domain_info(domain)
        if domain_info:
            result['domain_info'] = domain_info
        
        # Get email security
        email_sec = get_email_security(domain)
        result['email_security'] = email_sec
        
        # Detect hosting provider
        if result.get('ip_address'):
            hosting = detect_hosting_provider(result['ip_address'], domain)
            result['hosting_provider'] = hosting
        
        # Get performance metrics
        end_time = datetime.now()
        metrics = get_performance_metrics(response, start_time)
        result['performance'] = metrics
            
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
    # Only for local development - use gunicorn in production
    app.run(host='127.0.0.1', port=5000, debug=True)
