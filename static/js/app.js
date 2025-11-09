document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('cdn-form');
    const urlInput = document.getElementById('url-input');
    const checkBtn = document.getElementById('check-btn');
    const btnText = document.querySelector('.btn-text');
    const btnLoader = document.querySelector('.btn-loader');
    const errorMessage = document.getElementById('error-message');
    const results = document.getElementById('results');

    // Form submission
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const url = urlInput.value.trim();
        
        if (!url) {
            showError('Please enter a URL');
            return;
        }

        // Basic client-side validation
        if (!isValidUrl(url)) {
            showError('Please enter a valid website URL (e.g., example.com or www.example.com)');
            return;
        }

        await checkCDN(url);
    });

    // URL validation function
    function isValidUrl(url) {
        // Allow URLs with or without protocol, with or without www
        const pattern = /^(https?:\/\/)?(www\.)?[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$/;
        return pattern.test(url);
    }

    // Main CDN check function
    async function checkCDN(url) {
        // Show loading state
        checkBtn.disabled = true;
        btnText.style.display = 'none';
        btnLoader.style.display = 'block';
        hideError();
        hideResults();

        try {
            const response = await fetch('/api/check', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ url: url })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Failed to check CDN');
            }

            if (data.error) {
                showError(data.error);
            } else {
                displayResults(data);
            }

        } catch (error) {
            console.error('Error:', error);
            showError(error.message || 'An error occurred while checking the CDN. Please try again.');
        } finally {
            // Hide loading state
            checkBtn.disabled = false;
            btnText.style.display = 'block';
            btnLoader.style.display = 'none';
        }
    }

    // Display results
    function displayResults(data) {
        // Set URL
        document.getElementById('result-url').textContent = data.url;

        // Set CDN name and icon
        const cdnName = data.cdn_detected || 'None detected';
        document.getElementById('cdn-name').textContent = cdnName;
        
        // Set icon based on CDN
        const icon = getCDNIcon(cdnName);
        document.getElementById('cdn-icon').textContent = icon;

        // Set confidence
        const confidence = data.confidence || 0;
        document.getElementById('confidence-fill').style.width = confidence + '%';
        document.getElementById('confidence-value').textContent = confidence + '%';

        // Set IP address
        if (data.ip_address) {
            document.getElementById('ip-address').textContent = data.ip_address;
            document.getElementById('ip-card').style.display = 'block';
        } else {
            document.getElementById('ip-card').style.display = 'none';
        }

        // Set CNAME records
        if (data.cnames && data.cnames.length > 0) {
            const cnameList = data.cnames.map(cname => `<div>${cname}</div>`).join('');
            document.getElementById('cname-records').innerHTML = cnameList;
            document.getElementById('cname-card').style.display = 'block';
        } else {
            document.getElementById('cname-records').textContent = 'No CNAME records found';
            document.getElementById('cname-card').style.display = 'block';
        }

        // Set server header
        if (data.headers && data.headers.Server) {
            document.getElementById('server-header').textContent = data.headers.Server;
            document.getElementById('server-card').style.display = 'block';
        } else {
            document.getElementById('server-header').textContent = 'Not disclosed';
            document.getElementById('server-card').style.display = 'block';
        }

        // Set evidence
        if (data.evidence && data.evidence.length > 0) {
            const evidenceList = data.evidence.map(item => `<li>${escapeHtml(item)}</li>`).join('');
            document.getElementById('evidence-list').innerHTML = evidenceList;
            document.getElementById('evidence-card').style.display = 'block';
        } else {
            document.getElementById('evidence-card').style.display = 'none';
        }

        // Display HTTP headers
        if (data.headers && Object.keys(data.headers).length > 0) {
            const headersGrid = document.getElementById('headers-grid');
            headersGrid.innerHTML = '';
            
            // Filter and display important headers
            const importantHeaders = ['Server', 'X-Powered-By', 'X-Cache', 'Cache-Control', 
                                     'Content-Type', 'Vary', 'Age', 'Via'];
            
            Object.entries(data.headers).forEach(([name, value]) => {
                if (importantHeaders.some(h => h.toLowerCase() === name.toLowerCase()) || 
                    name.toLowerCase().startsWith('x-') || 
                    name.toLowerCase().includes('cdn') ||
                    name.toLowerCase().includes('cache')) {
                    
                    const headerItem = document.createElement('div');
                    headerItem.className = 'header-item';
                    headerItem.innerHTML = `
                        <div class="header-name">${escapeHtml(name)}</div>
                        <div class="header-value">${escapeHtml(value)}</div>
                    `;
                    headersGrid.appendChild(headerItem);
                }
            });

            if (headersGrid.children.length > 0) {
                document.getElementById('additional-headers').style.display = 'block';
            } else {
                document.getElementById('additional-headers').style.display = 'none';
            }
        } else {
            document.getElementById('additional-headers').style.display = 'none';
        }

        // Show results
        results.style.display = 'block';
        
        // Smooth scroll to results
        setTimeout(() => {
            results.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }, 100);
    }

    // Get icon for CDN
    function getCDNIcon(cdnName) {
        const icons = {
            'CloudFlare': '☁️',
            'Amazon CloudFront': '🔶',
            'Fastly': '⚡',
            'KeyCDN': '🔑',
            'MaxCDN/StackPath': '📦',
            'Akamai': '🌊',
            'Azure CDN': '🔷',
            'Google Cloud CDN': '🔍',
            'Incapsula': '🛡️',
            'BunnyCDN': '🐰',
            'None detected': '❌'
        };
        return icons[cdnName] || '🚀';
    }

    // Utility functions
    function showError(message) {
        errorMessage.textContent = message;
        errorMessage.style.display = 'block';
        setTimeout(() => {
            errorMessage.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }, 100);
    }

    function hideError() {
        errorMessage.style.display = 'none';
    }

    function hideResults() {
        results.style.display = 'none';
    }

    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    // Auto-focus on input
    urlInput.focus();
});
