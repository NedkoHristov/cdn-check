# Changelog

All notable changes to the CDN Checker project will be documented in this file.

## [Unreleased]

### Added
- **SiteGround CDN Detection** - Added support for detecting SiteGround CDN
  - Header detection: `sg-cdn`
  - CNAME pattern matching: `.sgcdn.` and `.siteground.`
  - Icon: 🌐

- **Enhanced URL Validation**
  - Now accepts both HTTP and HTTPS protocols explicitly
  - Supports URLs with ports (e.g., `example.com:8080`)
  - Supports URLs with paths (e.g., `https://example.com/path`)
  - Better domain validation regex pattern
  - More descriptive validation error messages

- **Improved Error Handling**
  - SSL Certificate Errors: Gracefully handles sites with invalid/expired certificates
    - Attempts connection with SSL verification first
    - Falls back to unverified connection with warning if certificate fails
    - Displays warning indicator in evidence list
  - Connection Errors: User-friendly messages for common issues:
    - `ConnectionError` → "Website could not be reached" message
    - `Timeout` → "Website took too long to respond" message
    - `TooManyRedirects` → "Website may have a redirect loop" message
    - `SSLError` → Handled automatically with fallback
  - DNS Resolution Errors: Clear message when domain doesn't exist
  - Rate Limiting: Informative message about request limits
  - Network Errors: Friendly message for general network issues

### Changed
- **Backend (`app.py`)**
  - Refactored `validate_url()` function to return tuple `(url, error)`
  - Enhanced `check_cdn()` with comprehensive try-catch blocks
  - Added `urllib3` to suppress SSL warnings in logs
  - Better domain extraction from URLs with ports and paths
  - Specific exception handling for different request failure scenarios

- **Frontend (`app.js`)**
  - Improved URL validation regex to support ports and paths
  - Enhanced error display logic with context-aware messages
  - Added SiteGround CDN icon to the icon mapping
  - Better error message formatting in catch blocks

- **Styling (`style.css`)**
  - Enhanced error message appearance:
    - Added gradient background
    - Increased padding and improved typography
    - Added warning emoji prefix automatically
    - Added subtle shadow for better visibility
    - Improved line-height for readability

### Documentation
- Updated `README.md` to include SiteGround CDN in supported providers list
- Created `CHANGELOG.md` to track all project changes

## [1.0.0] - 2025-11-09

### Initial Release
- CDN detection for 10+ major providers
- HTTP header analysis
- DNS CNAME record checking
- IP address resolution
- Rate limiting (10/min, 50/hour, 200/day)
- URL sharing via query parameters
- Responsive web interface
- Docker support
- Systemd service configuration
- Production deployment documentation
