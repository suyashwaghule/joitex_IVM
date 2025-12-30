/* ========================================
   Authentication & Authorization Module
   ======================================== */

// Demo user credentials with portal access
const DEMO_USERS = {
    admin: {
        email: 'admin@joitex.com',
        password: 'admin123',
        role: 'admin',
        name: 'Admin User',
        permissions: ['all'],
        portals: ['admin', 'callcenter', 'sales', 'salesexec', 'engineer', 'inventory', 'network', 'finance']
    },
    callcenter: {
        email: 'callcenter@joitex.com',
        password: 'call123',
        role: 'callcenter',
        name: 'Call Center Agent',
        permissions: ['inquiries.create', 'inquiries.read', 'inquiries.update'],
        portals: ['callcenter', 'sales']
    },
    sales: {
        email: 'sales@joitex.com',
        password: 'sales123',
        role: 'sales',
        name: 'Sales Manager',
        permissions: ['inquiries.read', 'leads.all', 'activation.all'],
        portals: ['sales', 'callcenter']
    },
    salesexec: {
        email: 'salesexec@joitex.com',
        password: 'exec123',
        role: 'salesexec',
        name: 'Sales Executive',
        permissions: ['leads.create', 'leads.read', 'leads.update'],
        portals: ['salesexec', 'sales']
    },
    engineer: {
        email: 'engineer@joitex.com',
        password: 'eng123',
        role: 'engineer',
        name: 'Field Engineer',
        permissions: ['jobs.read', 'jobs.update', 'devices.all'],
        portals: ['engineer', 'inventory']
    },
    inventory: {
        email: 'inventory@joitex.com',
        password: 'inv123',
        role: 'inventory',
        name: 'Inventory Manager',
        permissions: ['inventory.all', 'vendors.all'],
        portals: ['inventory', 'engineer']
    },
    network: {
        email: 'network@joitex.com',
        password: 'net123',
        role: 'network',
        name: 'Network Admin',
        permissions: ['olts.all', 'ipam.all', 'monitoring.all'],
        portals: ['network', 'engineer']
    },
    finance: {
        email: 'finance@joitex.com',
        password: 'fin123',
        role: 'finance',
        name: 'Finance Manager',
        permissions: ['licenses.all', 'billing.read', 'reports.financial'],
        portals: ['finance', 'sales']
    }
};

// Get project base path (for subdirectory hosting support)
function getBasePath() {
    // Get the current location
    const pathname = window.location.pathname;
    const hostname = window.location.hostname;

    // For localhost/127.0.0.1, use relative paths
    if (hostname === 'localhost' || hostname === '127.0.0.1' || hostname === '') {
        return '';
    }

    // For production hosting, always use root-relative paths
    // This works for both root domain and subdirectory hosting
    return '';
}

// Get the correct path for navigation
function getNavigationPath(relativePath) {
    // Remove leading slash if present
    const cleanPath = relativePath.replace(/^\/+/, '');

    // Always return absolute path from origin to prevent appending to current URL
    return `${window.location.origin}/${cleanPath}`;
}

// Role configurations with relative paths
const ROLE_CONFIG = {
    admin: { name: 'Admin', color: '#1976d2', dashboard: 'portals/admin/dashboard.html' },
    callcenter: { name: 'Call Center', color: '#0d9488', dashboard: 'portals/callcenter/dashboard.html' },
    sales: { name: 'Sales Manager', color: '#4f46e5', dashboard: 'portals/sales/dashboard.html' },
    salesexec: { name: 'Sales Executive', color: '#6366f1', dashboard: 'portals/salesexec/dashboard.html' },
    engineer: { name: 'Engineer', color: '#f97316', dashboard: 'portals/engineer/dashboard.html' },
    inventory: { name: 'Inventory Manager', color: '#9333ea', dashboard: 'portals/inventory/dashboard.html' },
    network: { name: 'Network Admin', color: '#16a34a', dashboard: 'portals/network/dashboard.html' },
    finance: { name: 'Finance Manager', color: '#f59e0b', dashboard: 'portals/finance/dashboard.html' }
};

// Authentication class
class Auth {
    constructor() {
        this.currentUser = null;
        this.loadSession();
    }

    async login(email, password, remember = false) {
        try {
            const response = await fetch('http://127.0.0.1:5000/api/auth/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ email, password })
            });

            const data = await response.json();

            if (!response.ok) {
                return { success: false, message: data.message || 'Login failed' };
            }

            const user = data.user;
            const token = data.access_token;

            // Store session
            const session = {
                user,
                token,
                timestamp: new Date().toISOString(),
                remember
            };

            remember
                ? localStorage.setItem('joitex_session', JSON.stringify(session))
                : sessionStorage.setItem('joitex_session', JSON.stringify(session));

            this.currentUser = user;
            this.token = token;

            // Redirect to portal selection page after login
            const redirectUrl = getNavigationPath(data.redirectUrl || 'select-portal.html');
            return { success: true, user, redirectUrl };

        } catch (error) {
            console.error('Login error:', error);
            return { success: false, message: 'Network error. Could not connect to backend.' };
        }
    }

    logout() {
        localStorage.removeItem('joitex_session');
        sessionStorage.removeItem('joitex_session');
        this.currentUser = null;
        window.location.href = getNavigationPath('index.html');
    }

    loadSession() {
        const sessionData = localStorage.getItem('joitex_session') || sessionStorage.getItem('joitex_session');
        if (sessionData) {
            try {
                const session = JSON.parse(sessionData);
                this.currentUser = session.user;
                this.token = session.token;
            } catch {
                this.clearSession();
            }
        }
    }

    clearSession() {
        localStorage.removeItem('joitex_session');
        sessionStorage.removeItem('joitex_session');
    }

    isAuthenticated() {
        return !!this.currentUser;
    }

    protectPage(allowedRoles = []) {
        if (!this.isAuthenticated()) {
            window.location.href = getNavigationPath('index.html');
            return false;
        }

        // If no specific roles required, just check authentication
        if (!allowedRoles.length) {
            return true;
        }

        // Admin has access to everything
        if (Array.isArray(this.currentUser.permissions) && this.currentUser.permissions.includes('all')) {
            return true;
        }

        // Check if user's primary role is allowed
        if (allowedRoles.includes(this.currentUser.role)) {
            return true;
        }

        // Check if user has access to any of the allowed portals
        if (Array.isArray(this.currentUser.portals)) {
            for (const role of allowedRoles) {
                if (this.currentUser.portals.includes(role)) {
                    return true;
                }
            }
        }

        // Access denied
        window.location.href = getNavigationPath('403.html');
        return false;
    }

    getCurrentUser() {
        return this.currentUser;
    }

    async checkResponse(response) {
        if (response.status === 401) {
            console.warn('Unauthorized request detected. Logging out...');
            this.logout();
            return false;
        }
        return true;
    }
}

// Global auth instance and expose to window
const auth = new Auth();
window.auth = auth;
window.ROLE_CONFIG = ROLE_CONFIG;
if (typeof module !== 'undefined' && module.exports) module.exports = { auth, ROLE_CONFIG };
