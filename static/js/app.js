document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('cdn-form');
    const urlInput = document.getElementById('url-input');
    const checkBtn = document.getElementById('check-btn');
    const btnText = document.querySelector('.btn-text');
    const btnLoader = document.querySelector('.btn-loader');
    const errorMessage = document.getElementById('error-message');
    const results = document.getElementById('results');

    // Check if URL parameter exists and auto-check
    const urlParams = new URLSearchParams(window.location.search);
    const urlParam = urlParams.get('url');
    if (urlParam) {
        urlInput.value = urlParam;
        checkCDN(urlParam);
    }

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

    // URL validation function - improved to accept http/https
    function isValidUrl(url) {
        // Allow URLs with or without protocol (http/https), with or without www, with optional port and path
        const pattern = /^(https?:\/\/)?(www\.)?[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*(:[0-9]{1,5})?(\/.*)?$/;
        return pattern.test(url);
    }

    // Main CDN check function
    async function checkCDN(url) {
        // Update URL in browser address bar
        const newUrl = new URL(window.location);
        newUrl.searchParams.set('url', url);
        window.history.pushState({}, '', newUrl);

        // Show loading state
        checkBtn.disabled = true;
        btnText.style.display = 'none';
        btnLoader.style.display = 'block';
        hideError();
        hideResults();

        try {
            const response = await fetch('api/check', {
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
            // Display user-friendly error message
            if (error.message.includes('Failed to fetch')) {
                showError('Unable to connect to the CDN checker service. Please check your internet connection and try again.');
            } else if (error.message.includes('Rate limit')) {
                showError('Too many requests. Please wait a moment and try again.');
            } else {
                showError(error.message || 'An error occurred while checking the CDN. Please try again.');
            }
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

        // Set CMS information
        if (data.cms) {
            let cmsText = data.cms;
            if (data.cms_version) {
                cmsText += ` ${data.cms_version}`;
            }
            document.getElementById('cms-info').textContent = cmsText;
            document.getElementById('cms-card').style.display = 'block';
        } else {
            document.getElementById('cms-card').style.display = 'none';
        }

        // Display Technology Stack
        if (data.server || data.language || data.frameworks || data.analytics) {
            let techHTML = '<div class="detail-value">';
            if (data.server) techHTML += `<div><strong>Server:</strong> ${escapeHtml(data.server)}</div>`;
            if (data.language && data.language.length > 0) techHTML += `<div><strong>Language:</strong> ${data.language.join(', ')}</div>`;
            if (data.frameworks && data.frameworks.length > 0) techHTML += `<div><strong>Frameworks:</strong> ${data.frameworks.join(', ')}</div>`;
            if (data.analytics && data.analytics.length > 0) techHTML += `<div><strong>Analytics:</strong> ${data.analytics.join(', ')}</div>`;
            if (data.hosting_provider) techHTML += `<div><strong>Hosting:</strong> ${data.hosting_provider}</div>`;
            techHTML += '</div>';
            document.getElementById('tech-card').innerHTML = techHTML;
            document.getElementById('tech-section').style.display = 'block';
        }

        // Display Security Analysis
        if (data.security) {
            let secHTML = '<div class="detail-value">';
            secHTML += `<div style="margin-bottom: 10px;"><strong>Security Grade:</strong> <span style="font-size: 1.5em; font-weight: bold; color: ${getGradeColor(data.security.grade)}">${data.security.grade}</span> (${data.security.score}/${data.security.max_score})</div>`;
            secHTML += '<div><strong>Security Headers:</strong></div><ul>';
            for (const [header, status] of Object.entries(data.security.headers)) {
                const icon = status.includes('✓') ? '✓' : '✗';
                const color = status.includes('✓') ? 'green' : 'red';
                secHTML += `<li style="color: ${color}">${icon} ${header}</li>`;
            }
            secHTML += '</ul></div>';
            document.getElementById('security-card').innerHTML = secHTML;
            document.getElementById('security-section').style.display = 'block';
        }

        // Display SSL Information
        if (data.ssl) {
            let sslHTML = '<div class="detail-value">';
            sslHTML += `<div><strong>Status:</strong> ${data.ssl.status}</div>`;
            sslHTML += `<div><strong>Issuer:</strong> ${data.ssl.issuer}</div>`;
            sslHTML += `<div><strong>Valid Until:</strong> ${data.ssl.valid_until} (${data.ssl.days_remaining} days)</div>`;
            sslHTML += `<div><strong>TLS Version:</strong> ${data.ssl.tls_version}</div>`;
            sslHTML += '</div>';
            document.getElementById('ssl-card').innerHTML = sslHTML;
            document.getElementById('ssl-section').style.display = 'block';
        }

        // Display Domain Information
        if (data.domain_info) {
            let domainHTML = '<div class="detail-value">';
            domainHTML += `<div><strong>Domain Age:</strong> ${data.domain_info.age_years} years (${data.domain_info.age_days} days)</div>`;
            domainHTML += `<div><strong>Created:</strong> ${data.domain_info.created}</div>`;
            domainHTML += `<div><strong>Expires:</strong> ${data.domain_info.expires}</div>`;
            domainHTML += `<div><strong>Registrar:</strong> ${data.domain_info.registrar}</div>`;
            domainHTML += '</div>';
            document.getElementById('domain-card').innerHTML = domainHTML;
            document.getElementById('domain-section').style.display = 'block';
        }

        // Display Email Security
        if (data.email_security) {
            let emailHTML = '<div class="detail-value">';
            emailHTML += `<div><strong>SPF:</strong> ${data.email_security.spf}</div>`;
            emailHTML += `<div><strong>DMARC:</strong> ${data.email_security.dmarc}</div>`;
            if (data.email_security.mx && data.email_security.mx.length > 0) {
                emailHTML += `<div><strong>Mail Servers:</strong> ${data.email_security.mx.join(', ')}</div>`;
            }
            emailHTML += '</div>';
            document.getElementById('email-card').innerHTML = emailHTML;
            document.getElementById('email-section').style.display = 'block';
        }

        // Display Performance
        if (data.performance) {
            let perfHTML = '<div class="detail-value">';
            perfHTML += `<div><strong>Response Time:</strong> ${data.performance.response_time_ms}ms</div>`;
            perfHTML += `<div><strong>Compression:</strong> ${data.performance.compression}</div>`;
            if (data.performance.page_size_kb) perfHTML += `<div><strong>Page Size:</strong> ${data.performance.page_size_kb} KB</div>`;
            perfHTML += '</div>';
            document.getElementById('performance-card').innerHTML = perfHTML;
            document.getElementById('performance-section').style.display = 'block';
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
            'SiteGround CDN': '🌐',
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

    function getGradeColor(grade) {
        const colors = {
            'A+': '#00a86b',
            'A': '#00c853',
            'B': '#64dd17',
            'C': '#ffd600',
            'D': '#ff6f00',
            'F': '#d50000'
        };
        return colors[grade] || '#666';
    }

    // Auto-focus on input
    urlInput.focus();
});
