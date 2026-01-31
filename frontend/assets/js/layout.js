/* ========================================
   Layout Manager - Joitex Fiber
   Handles dynamic Sidebar and Navbar generation
   ======================================== */

const PORTAL_CONFIG = {
    admin: {
        title: 'Admin Dashboard',
        icon: 'bi-router-fill',
        color: '#1976d2',
        menu: [
            {
                title: 'Main',
                items: [
                    { icon: 'bi-speedometer2', label: 'Dashboard', href: 'dashboard.html' },
                    { icon: 'bi-people', label: 'User Management', href: 'users.html' }
                ]
            },
            {
                title: 'Configuration',
                items: [
                    { icon: 'bi-card-list', label: 'Internet Plans', href: 'plans.html' },
                    { icon: 'bi-hdd-network', label: 'OLT Catalog', href: 'olts.html' },
                    { icon: 'bi-diagram-3', label: 'IP Pools', href: 'ip-pools.html' }
                ]
            },
            {
                title: 'Reports & Audit',
                items: [
                    { icon: 'bi-graph-up', label: 'Global Reports', href: 'reports.html' },
                    { icon: 'bi-clock-history', label: 'Audit Logs', href: 'audits.html' }
                ]
            },
            {
                title: 'System',
                items: [
                    { icon: 'bi-gear', label: 'System Settings', href: 'settings.html' }
                ]
            }
        ]
    },
    engineer: {
        title: 'Engineer Dashboard',
        icon: 'bi-router-fill',
        color: '#f97316',
        menu: [
            {
                title: 'Field Operations',
                items: [
                    { icon: 'bi-speedometer2', label: 'Dashboard', href: 'dashboard.html' },
                    { icon: 'bi-list-task', label: 'Assigned Jobs', href: 'assigned-jobs.html', badge: '5' },
                    { icon: 'bi-hdd-rack', label: 'Device Entry', href: 'device-entry.html' },
                    { icon: 'bi-check-circle', label: 'Completion Report', href: 'completion.html' }
                ]
            },
            {
                title: 'Maintenance',
                items: [
                    { icon: 'bi-wrench-adjustable', label: 'Service Requests', href: 'maintenance.html' },
                    { icon: 'bi-box-seam', label: 'Material Requests', href: 'stock-requests.html' }
                ]
            }
        ]
    },
    sales: {
        title: 'Sales Dashboard',
        icon: 'bi-router-fill',
        color: '#4f46e5',
        menu: [
            {
                title: 'Sales Operations',
                items: [
                    { icon: 'bi-speedometer2', label: 'Dashboard', href: 'dashboard.html' },
                    { icon: 'bi-funnel', label: 'Lead Management', href: 'leads.html' },
                    { icon: 'bi-check-circle', label: 'Feasibility Queue', href: 'feasibility.html' },
                    { icon: 'bi-tools', label: 'Installations', href: 'installations.html' },
                    { icon: 'bi-power', label: 'Activation & Billing', href: 'activation.html' }
                ]
            },
            {
                title: 'Reports & Analytics',
                items: [
                    { icon: 'bi-graph-up', label: 'Sales Reports', href: 'reports.html' }
                ]
            }
        ]
    },
    inventory: {
        title: 'Inventory Dashboard',
        icon: 'bi-router-fill',
        color: '#9333ea',
        menu: [
            {
                title: 'Main',
                items: [
                    { icon: 'bi-speedometer2', label: 'Dashboard', href: 'dashboard.html' },
                    { icon: 'bi-grid', label: 'Inventory Catalog', href: 'catalog.html' },
                    { icon: 'bi-box-arrow-in-down', label: 'Receive Stock', href: 'receive.html' },
                    { icon: 'bi-box-arrow-up', label: 'Issue to Engineer', href: 'issue.html', badge: '3' }
                ]
            },
            {
                title: 'Management',
                items: [
                    { icon: 'bi-arrow-left-right', label: 'Stock Movements', href: 'transactions.html' },
                    { icon: 'bi-building', label: 'Vendors', href: 'vendors.html' },
                    { icon: 'bi-graph-up', label: 'Reports', href: 'reports.html' }
                ]
            }
        ]
    },
    callcenter: {
        title: 'Call Center Dashboard',
        icon: 'bi-router-fill',
        color: '#0d9488',
        menu: [
            {
                title: 'Main',
                items: [
                    { icon: 'bi-speedometer2', label: 'Dashboard', href: 'dashboard.html' },
                    { icon: 'bi-plus-circle', label: 'Create Inquiry', href: 'create-inquiry.html' },
                    { icon: 'bi-list-ul', label: 'My Inquiries', href: 'my-inquiries.html', badge: '-' },
                    { icon: 'bi-kanban', label: 'Status Board', href: 'status-board.html' }
                ]
            }
        ]
    },
    network: {
        title: 'Network Admin Dashboard',
        icon: 'bi-router-fill',
        color: '#16a34a',
        menu: [
            {
                title: 'Main',
                items: [
                    { icon: 'bi-speedometer2', label: 'Dashboard', href: 'dashboard.html' },
                    { icon: 'bi-hdd-network', label: 'OLT Details', href: 'olt-details.html' },
                    { icon: 'bi-diagram-3', label: 'IP Management', href: 'ip-management.html' },
                    { icon: 'bi-exclamation-triangle', label: 'Downtime Logs', href: 'downtime.html' }
                ]
            }
        ]
    },
    finance: {
        title: 'Finance Dashboard',
        icon: 'bi-router-fill',
        color: '#f59e0b',
        menu: [
            {
                title: 'Main',
                items: [
                    { icon: 'bi-speedometer2', label: 'Dashboard', href: 'dashboard.html' },
                    { icon: 'bi-receipt', label: 'Invoices', href: 'invoices.html' },
                    { icon: 'bi-cash-coin', label: 'Payments', href: 'payments.html' }
                ]
            }
        ]
    },
    salesexec: {
        title: 'Sales Executive Dashboard',
        icon: 'bi-router-fill',
        color: '#6366f1',
        menu: [
            {
                title: 'Main',
                items: [
                    { icon: 'bi-speedometer2', label: 'Dashboard', href: 'dashboard.html' },
                    { icon: 'bi-person-plus', label: 'My Leads', href: 'my-leads.html' },
                    { icon: 'bi-trophy', label: 'Performance', href: 'performance.html' }
                ]
            }
        ]
    }
};

const Layout = {
    init() {
        // Wait for auth to be ready
        if (!window.auth) {
            console.error('Auth module not loaded');
            return;
        }

        const user = window.auth.getCurrentUser();
        // Fallback to role from URL if user not fully loaded (though auth.protectPage handles this)
        // or just rely on the script calling init()
    },

    render(role) {
        const config = PORTAL_CONFIG[role];
        if (!config) {
            console.error(`No configuration found for role: ${role}`);
            return;
        }

        this.renderSidebar(config);
        this.renderHeader(config);
        this.renderFloatingActions();

        // Re-initialize SidebarManager to handle toggles and active links
        if (window.SidebarManager) {
            window.SidebarManager.init();
        }
    },

    renderSidebar(config) {
        const sidebar = document.querySelector('.sidebar');
        if (!sidebar) return;

        const sidebarHeader = `
            <div class="sidebar-header">
                <a href="dashboard.html" class="sidebar-logo">
                    <i class="bi ${config.icon}" style="color: ${config.color};"></i>
                    <span>Joitex Fiber</span>
                </a>
                <button class="sidebar-toggle" id="sidebarToggle">
                    <i class="bi bi-chevron-left"></i>
                </button>
            </div>
        `;

        let navContent = '<nav class="sidebar-nav">';

        config.menu.forEach(section => {
            navContent += `
                <div class="nav-section">
                    <div class="nav-section-title">${section.title}</div>
                    <ul class="nav flex-column">
            `;

            section.items.forEach(item => {
                const badge = item.badge ? `<span class="nav-badge">${item.badge}</span>` : '';
                navContent += `
                    <li class="nav-item">
                        <a href="${item.href}" class="nav-link">
                            <i class="bi ${item.icon}"></i>
                            <span>${item.label}</span>
                            ${badge}
                        </a>
                    </li>
                `;
            });

            navContent += `
                    </ul>
                </div>
            `;
        });

        navContent += '</nav>';

        sidebar.innerHTML = sidebarHeader + navContent;
    },

    renderHeader(config) {
        const header = document.querySelector('.header');
        if (!header) return;

        const user = window.auth.getCurrentUser();
        const userName = user ? user.name : 'User';
        const userRole = user ? user.role.charAt(0).toUpperCase() + user.role.slice(1) : 'Role';
        const initials = userName.split(' ').map(n => n[0]).join('').toUpperCase().substring(0, 2);

        const breadcrumbTitle = config.title.split(' ')[0]; // First word usually

        header.innerHTML = `
            <div class="header-left">
                <button class="mobile-menu-toggle" id="mobileMenuToggle">
                    <i class="bi bi-list"></i>
                </button>

                <nav aria-label="breadcrumb" class="breadcrumb-container d-none d-md-block">
                    <ol class="breadcrumb mb-0">
                        <li class="breadcrumb-item"><a href="dashboard.html">${breadcrumbTitle}</a></li>
                        <li class="breadcrumb-item active" id="pageBreadcrumb">Dashboard</li>
                    </ol>
                </nav>
            </div>

            <div class="header-right" id="headerRightActions">
                <div class="header-search d-none d-lg-block">
                    <i class="bi bi-search"></i>
                    <input type="text" class="form-control" placeholder="Search...">
                </div>

                <button class="header-action" id="themeToggle" data-bs-toggle="tooltip" title="Toggle Theme">
                    <i class="bi bi-moon"></i>
                </button>

                <button class="header-action" data-bs-toggle="tooltip" title="Notifications">
                    <i class="bi bi-bell"></i>
                    <span class="notification-badge"></span>
                </button>

                <div class="dropdown">
                    <div class="user-menu" data-bs-toggle="dropdown">
                        <div class="user-avatar" style="background: linear-gradient(135deg, ${config.color} 0%, ${adjustColor(config.color, -20)} 100%);">
                            ${initials}
                        </div>
                        <div class="user-info d-none d-md-block">
                            <div class="user-name" id="userName">${userName}</div>
                            <div class="user-role">${userRole}</div>
                        </div>
                        <i class="bi bi-chevron-down ms-2"></i>
                    </div>
                    <ul class="dropdown-menu dropdown-menu-end">
                        <li><a class="dropdown-item" href="#"><i class="bi bi-person me-2"></i>Profile</a></li>
                        <li><a class="dropdown-item" href="#"><i class="bi bi-gear me-2"></i>Settings</a></li>
                        <li>
                            <hr class="dropdown-divider">
                        </li>
                        <li><a class="dropdown-item" href="#" id="logoutBtn"><i class="bi bi-box-arrow-right me-2"></i>Logout</a></li>
                    </ul>
                </div>
            </div>
        `;

        // Re-attach listeners
        document.getElementById('logoutBtn')?.addEventListener('click', (e) => {
            e.preventDefault();
            if (window.Modal) {
                window.Modal.confirm('Confirm Logout', 'Are you sure?', () => window.auth.logout());
            } else {
                window.auth.logout();
            }
        });

        const themeBtn = document.getElementById('themeToggle');
        themeBtn?.addEventListener('click', () => {
            if (window.ThemeManager) window.ThemeManager.toggle();
        });

        this.updateActiveBreadcrumb();
    },

    renderFloatingActions() {
        if (document.getElementById('floating-actions')) return;

        const container = document.createElement('div');
        container.id = 'floating-actions';
        container.className = 'fab-container';

        // Switch Portal Button
        const switchBtn = document.createElement('button');
        switchBtn.className = 'fab-btn fab-btn-primary';
        switchBtn.innerHTML = '<i class="bi bi-grid-fill"></i><span>Switch Portal</span>';
        switchBtn.onclick = () => {
            // Go up two levels from /portals/admin/
            window.location.href = '../../select-portal.html';
        };

        // Logout Button
        const logoutBtn = document.createElement('button');
        logoutBtn.className = 'fab-btn fab-btn-danger';
        logoutBtn.innerHTML = '<i class="bi bi-box-arrow-right"></i><span>Logout</span>';
        logoutBtn.onclick = () => {
            if (window.Modal) {
                window.Modal.confirm('Confirm Logout', 'Are you sure?', () => window.auth.logout());
            } else {
                window.auth.logout();
            }
        };

        container.appendChild(switchBtn);
        container.appendChild(logoutBtn);

        document.body.appendChild(container);
    },

    updateActiveBreadcrumb() {
        const path = window.location.pathname;
        const page = path.split('/').pop() || 'dashboard.html';
        const labelEl = document.getElementById('pageBreadcrumb');
        if (!labelEl) return;

        const simpleName = page.replace('.html', '').replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
        labelEl.textContent = simpleName;
    }
};

// Helper to darken color
function adjustColor(color, amount) {
    return color;
}

// Global Export
window.Layout = Layout;
