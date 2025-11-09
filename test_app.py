"""
Test script for CDN Checker
Run this to verify the application is working correctly
"""

import sys
import requests
import json

def test_local_server():
    """Test if the local server is running"""
    try:
        response = requests.get('http://localhost:5000', timeout=5)
        if response.status_code == 200:
            print("✓ Server is running on http://localhost:5000")
            return True
        else:
            print(f"✗ Server returned status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("✗ Could not connect to server. Is it running?")
        print("  Run: python app.py")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_api_endpoint(url):
    """Test the API endpoint with a URL"""
    try:
        response = requests.post(
            'http://localhost:5000/api/check',
            json={'url': url},
            headers={'Content-Type': 'application/json'},
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n✓ Successfully checked: {url}")
            print(f"  CDN Detected: {data.get('cdn_detected', 'Unknown')}")
            print(f"  Confidence: {data.get('confidence', 0)}%")
            if data.get('cnames'):
                print(f"  CNAME: {', '.join(data.get('cnames', []))}")
            return True
        else:
            print(f"✗ API returned status code: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"✗ Error testing {url}: {e}")
        return False

def main():
    print("=" * 50)
    print("CDN Checker - Test Suite")
    print("=" * 50)
    print()
    
    # Test 1: Check if server is running
    print("Test 1: Server Status")
    if not test_local_server():
        print("\nPlease start the server first:")
        print("  python app.py")
        sys.exit(1)
    
    print()
    print("=" * 50)
    
    # Test 2: Test API with various websites
    print("Test 2: API Functionality")
    print()
    
    test_urls = [
        'cloudflare.com',
        'github.com',
        'amazon.com',
    ]
    
    success_count = 0
    for url in test_urls:
        if test_api_endpoint(url):
            success_count += 1
    
    print()
    print("=" * 50)
    print(f"Results: {success_count}/{len(test_urls)} tests passed")
    print("=" * 50)
    
    if success_count == len(test_urls):
        print("\n✓ All tests passed! The application is working correctly.")
        return 0
    else:
        print("\n✗ Some tests failed. Please check the errors above.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
