# Error Handling Guide

This document explains how the CDN Checker handles various error scenarios to provide a better user experience.

## URL Validation Errors

### Invalid URL Format
**Trigger:** URL doesn't match valid domain pattern  
**User Message:** "Invalid URL format. Please enter a valid domain (e.g., example.com or https://example.com)"  
**Example Invalid URLs:**
- `invalid..domain` (double dots)
- `just spaces` (no domain structure)
- `http://` (missing domain)

### Supported URL Formats
The application accepts:
- ✅ `example.com`
- ✅ `www.example.com`
- ✅ `http://example.com`
- ✅ `https://example.com`
- ✅ `example.com:8080` (with port)
- ✅ `https://example.com/path/to/page` (with path)

## Connection Errors

### SSL Certificate Issues
**Trigger:** Website has invalid, expired, or self-signed SSL certificate  
**Behavior:**
1. First attempts connection with SSL verification
2. If SSL verification fails, retries without verification
3. Continues with CDN detection
4. Adds warning to evidence: "⚠️ SSL certificate verification failed - results may be inaccurate"

**User Impact:** Transparent - user gets results with a warning indicator

### Connection Failed
**Trigger:** Website is unreachable (DNS resolves but connection fails)  
**User Message:** "Connection failed. The website '[domain]' could not be reached. Please verify the URL is correct."  
**Common Causes:**
- Website is down
- Firewall blocking connection
- Network connectivity issues

### Domain Not Found
**Trigger:** DNS cannot resolve the domain name  
**User Message:** "Domain '[domain]' does not exist or cannot be resolved."  
**Common Causes:**
- Typo in domain name
- Domain doesn't exist
- DNS server issues

### Connection Timeout
**Trigger:** Website takes too long to respond (>10 seconds)  
**User Message:** "Connection timeout. The website '[domain]' took too long to respond."  
**Common Causes:**
- Server is overloaded
- Slow network connection
- Server blocking requests

### Too Many Redirects
**Trigger:** Website has a redirect loop  
**User Message:** "Too many redirects. The website may have a redirect loop."  
**Common Causes:**
- Misconfigured server redirects
- HTTP/HTTPS redirect loop

## Rate Limiting

### Rate Limit Exceeded
**Trigger:** User exceeds rate limits (10/min, 50/hour, or 200/day)  
**User Message:** "Too many requests. Please wait a moment and try again."  
**HTTP Status:** 429  
**Limits:**
- 10 requests per minute
- 50 requests per hour
- 200 requests per day

## Frontend Errors

### Network Connectivity
**Trigger:** Browser cannot reach the CDN Checker API  
**User Message:** "Unable to connect to the CDN checker service. Please check your internet connection and try again."  
**Common Causes:**
- User's internet connection down
- Service is offline
- CORS issues (if misconfigured)

### Empty URL
**Trigger:** User submits form without entering a URL  
**User Message:** "Please enter a URL"  
**Validation:** Client-side only

### Invalid URL Pattern
**Trigger:** Client-side validation fails before API call  
**User Message:** "Please enter a valid website URL (e.g., example.com or www.example.com)"  
**Validation:** Client-side only

## Error Display Features

### Visual Indicators
- 🔴 Red gradient background
- ⚠️ Warning emoji prefix (automatic)
- Red left border (4px)
- Shake animation on appearance
- Smooth scroll to error message

### Error Persistence
- Errors remain visible until:
  - New check is initiated (error hidden)
  - New error occurs (replaced)
  - Page is refreshed

### Auto-scroll
- Error messages automatically scroll into view
- Smooth scrolling animation
- Respects user's motion preferences

## Backend Error Logging

All errors are logged on the backend for debugging:
```python
try:
    # Check CDN logic
except Exception as e:
    result['error'] = 'User-friendly message'
    # Exception is caught and logged
```

## Best Practices for Users

1. **Check URL spelling** - Most errors are typos
2. **Include protocol** - Specify `http://` or `https://` if site doesn't support both
3. **Wait before retry** - Respect rate limits
4. **Report persistent issues** - If a valid URL consistently fails, report it

## Developer Notes

### Adding New Error Types

To add a new error type:

1. **Backend (`app.py`):**
```python
except NewExceptionType as e:
    result['error'] = 'User-friendly error message'
    return result
```

2. **Frontend (`app.js`):**
```javascript
if (error.message.includes('keyword')) {
    showError('Specific user message');
}
```

3. **Update this guide** with the new error type

### Error Message Guidelines

- **Be specific** about what went wrong
- **Be helpful** by suggesting solutions
- **Be concise** - avoid technical jargon
- **Be consistent** in tone and formatting
- **Include the domain** when relevant for context
