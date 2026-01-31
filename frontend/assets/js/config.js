/**
 * Application Configuration
 * 
 * This file allows you to configure the frontend for different environments.
 * Include this script BEFORE auth.js in your HTML files.
 * 
 * Usage in HTML:
 * <script src="assets/js/config.js"></script>
 * <script src="assets/js/auth.js"></script>
 */

(function () {
    // Auto-detect environment
    const hostname = window.location.hostname;
    const isLocalhost = hostname === 'localhost' || hostname === '127.0.0.1' || hostname === '';

    // Determine API URL based on environment
    let apiBaseUrl;
    if (isLocalhost) {
        apiBaseUrl = 'http://127.0.0.1:5000';
    } else if (hostname.includes('appspot.com') || hostname.includes('joitex')) {
        // Google App Engine - backend is on 'api' service
        apiBaseUrl = 'https://api-dot-joitex.el.r.appspot.com';
    } else {
        // Custom domain
        apiBaseUrl = 'https://api.' + hostname.replace('www.', '');
    }

    // Configuration object
    window.config = {
        // API Base URL
        apiBaseUrl: apiBaseUrl,

        // Application Settings
        appName: 'Joitex Fiber',
        appVersion: '1.0.0',

        // Feature Flags
        features: {
            enableDemoCredentials: isLocalhost,
            enableDebugMode: isLocalhost,
            enableAnalytics: !isLocalhost
        },

        // Session Settings
        session: {
            tokenExpiry: 24 * 60 * 60 * 1000, // 24 hours in ms
            refreshThreshold: 30 * 60 * 1000   // Refresh if less than 30 mins left
        }
    };

    // Log configuration in development
    if (window.config.features.enableDebugMode) {
        console.log('🔧 App Config:', window.config);
    }
})();
