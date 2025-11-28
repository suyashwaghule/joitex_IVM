/* ========================================
   Common Utilities & Functions
   ======================================== */

// Theme Management
const ThemeManager = {
    init() {
        const savedTheme = localStorage.getItem('joitex_theme') || 'light';
        this.setTheme(savedTheme);
    },

    setTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('joitex_theme', theme);
        
        // Update toggle button icon if exists
        const themeToggle = document.getElementById('themeToggle');
        if (themeToggle) {
            const icon = themeToggle.querySelector('i');
            if (icon) {
                icon.className = theme === 'dark' ? 'bi bi-sun' : 'bi bi-moon';
            }
        }
    },

    toggle() {
        const currentTheme = document.documentElement.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        this.setTheme(newTheme);
    }
};

// Sidebar Management
const SidebarManager = {
    init() {
        const sidebar = document.querySelector('.sidebar');
        const sidebarToggle = document.getElementById('sidebarToggle');
        const mobileMenuToggle = document.getElementById('mobileMenuToggle');
        const sidebarOverlay = document.querySelector('.sidebar-overlay');

        // Load saved state
        const isCollapsed = localStorage.getItem('sidebar_collapsed') === 'true';
        if (isCollapsed && window.innerWidth > 1024) {
            sidebar?.classList.add('collapsed');
        }

        // Desktop toggle
        sidebarToggle?.addEventListener('click', () => {
            sidebar?.classList.toggle('collapsed');
            const collapsed = sidebar?.classList.contains('collapsed');
            localStorage.setItem('sidebar_collapsed', collapsed);
        });

        // Mobile toggle
        mobileMenuToggle?.addEventListener('click', () => {
            sidebar?.classList.toggle('show');
            sidebarOverlay?.classList.toggle('show');
        });

        // Close on overlay click
        sidebarOverlay?.addEventListener('click', () => {
            sidebar?.classList.remove('show');
            sidebarOverlay?.classList.remove('show');
        });

        // Close on nav link click (mobile)
        if (window.innerWidth <= 1024) {
            document.querySelectorAll('.nav-link').forEach(link => {
                link.addEventListener('click', () => {
                    sidebar?.classList.remove('show');
                    sidebarOverlay?.classList.remove('show');
                });
            });
        }
    }
};

// Toast Notifications
const Toast = {
    show(message, type = 'info', duration = 3000) {
        const toastContainer = this.getContainer();
        
        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-white bg-${type} border-0`;
        toast.setAttribute('role', 'alert');
        toast.setAttribute('aria-live', 'assertive');
        toast.setAttribute('aria-atomic', 'true');
        
        const icons = {
            success: 'bi-check-circle-fill',
            error: 'bi-exclamation-circle-fill',
            warning: 'bi-exclamation-triangle-fill',
            info: 'bi-info-circle-fill'
        };
        
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    <i class="bi ${icons[type]} me-2"></i>
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;
        
        toastContainer.appendChild(toast);
        
        const bsToast = new bootstrap.Toast(toast, { delay: duration });
        bsToast.show();
        
        toast.addEventListener('hidden.bs.toast', () => {
            toast.remove();
        });
    },

    getContainer() {
        let container = document.getElementById('toastContainer');
        if (!container) {
            container = document.createElement('div');
            container.id = 'toastContainer';
            container.className = 'toast-container position-fixed top-0 end-0 p-3';
            container.style.zIndex = '9999';
            document.body.appendChild(container);
        }
        return container;
    },

    success(message, duration) {
        this.show(message, 'success', duration);
    },

    error(message, duration) {
        this.show(message, 'error', duration);
    },

    warning(message, duration) {
        this.show(message, 'warning', duration);
    },

    info(message, duration) {
        this.show(message, 'info', duration);
    }
};

// Modal Helper
const Modal = {
    confirm(title, message, onConfirm, onCancel) {
        const modalId = 'confirmModal_' + Date.now();
        const modal = document.createElement('div');
        modal.className = 'modal fade';
        modal.id = modalId;
        modal.setAttribute('tabindex', '-1');
        
        modal.innerHTML = `
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">${title}</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        ${message}
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                        <button type="button" class="btn btn-primary" id="confirmBtn">Confirm</button>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        const bsModal = new bootstrap.Modal(modal);
        
        modal.querySelector('#confirmBtn').addEventListener('click', () => {
            if (onConfirm) onConfirm();
            bsModal.hide();
        });
        
        modal.addEventListener('hidden.bs.modal', () => {
            if (onCancel) onCancel();
            modal.remove();
        });
        
        bsModal.show();
    }
};

// Form Validation Helper
const FormValidator = {
    validate(formId) {
        const form = document.getElementById(formId);
        if (!form) return false;

        let isValid = true;
        const inputs = form.querySelectorAll('input[required], select[required], textarea[required]');

        inputs.forEach(input => {
            if (!input.value.trim()) {
                input.classList.add('is-invalid');
                isValid = false;
            } else {
                input.classList.remove('is-invalid');
                input.classList.add('is-valid');
            }
        });

        return isValid;
    },

    clearValidation(formId) {
        const form = document.getElementById(formId);
        if (!form) return;

        form.querySelectorAll('.is-invalid, .is-valid').forEach(input => {
            input.classList.remove('is-invalid', 'is-valid');
        });
    }
};

// Data Table Helper
const DataTable = {
    init(tableId, options = {}) {
        const table = document.getElementById(tableId);
        if (!table) return;

        // Add sorting
        const headers = table.querySelectorAll('thead th[data-sortable]');
        headers.forEach(header => {
            header.style.cursor = 'pointer';
            header.innerHTML += ' <i class="bi bi-arrow-down-up ms-1"></i>';
            
            header.addEventListener('click', () => {
                this.sort(table, header);
            });
        });

        // Add search if specified
        if (options.searchInputId) {
            const searchInput = document.getElementById(options.searchInputId);
            searchInput?.addEventListener('input', (e) => {
                this.search(table, e.target.value);
            });
        }
    },

    sort(table, header) {
        const tbody = table.querySelector('tbody');
        const rows = Array.from(tbody.querySelectorAll('tr'));
        const columnIndex = Array.from(header.parentElement.children).indexOf(header);
        const isAscending = header.classList.contains('sort-asc');

        rows.sort((a, b) => {
            const aValue = a.children[columnIndex].textContent.trim();
            const bValue = b.children[columnIndex].textContent.trim();

            if (isAscending) {
                return bValue.localeCompare(aValue, undefined, { numeric: true });
            } else {
                return aValue.localeCompare(bValue, undefined, { numeric: true });
            }
        });

        // Update header icons
        table.querySelectorAll('thead th').forEach(th => {
            th.classList.remove('sort-asc', 'sort-desc');
        });

        header.classList.add(isAscending ? 'sort-desc' : 'sort-asc');

        // Re-append rows
        rows.forEach(row => tbody.appendChild(row));
    },

    search(table, query) {
        const tbody = table.querySelector('tbody');
        const rows = tbody.querySelectorAll('tr');
        const searchTerm = query.toLowerCase();

        rows.forEach(row => {
            const text = row.textContent.toLowerCase();
            row.style.display = text.includes(searchTerm) ? '' : 'none';
        });
    }
};

// Date Formatter
const DateFormatter = {
    format(date, format = 'short') {
        const d = new Date(date);
        
        const formats = {
            short: { month: 'short', day: 'numeric', year: 'numeric' },
            long: { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' },
            time: { hour: '2-digit', minute: '2-digit' },
            datetime: { month: 'short', day: 'numeric', year: 'numeric', hour: '2-digit', minute: '2-digit' }
        };

        return d.toLocaleDateString('en-US', formats[format] || formats.short);
    },

    relative(date) {
        const d = new Date(date);
        const now = new Date();
        const diff = now - d;
        const seconds = Math.floor(diff / 1000);
        const minutes = Math.floor(seconds / 60);
        const hours = Math.floor(minutes / 60);
        const days = Math.floor(hours / 24);

        if (days > 7) return this.format(date);
        if (days > 0) return `${days} day${days > 1 ? 's' : ''} ago`;
        if (hours > 0) return `${hours} hour${hours > 1 ? 's' : ''} ago`;
        if (minutes > 0) return `${minutes} minute${minutes > 1 ? 's' : ''} ago`;
        return 'Just now';
    }
};

// Number Formatter
const NumberFormatter = {
    format(number, decimals = 0) {
        return new Intl.NumberFormat('en-US', {
            minimumFractionDigits: decimals,
            maximumFractionDigits: decimals
        }).format(number);
    },

    currency(amount, currency = 'INR') {
        return new Intl.NumberFormat('en-IN', {
            style: 'currency',
            currency: currency
        }).format(amount);
    },

    percentage(value, decimals = 1) {
        return `${(value * 100).toFixed(decimals)}%`;
    }
};

// Local Storage Helper
const Storage = {
    set(key, value) {
        try {
            localStorage.setItem(`joitex_${key}`, JSON.stringify(value));
            return true;
        } catch (e) {
            console.error('Storage error:', e);
            return false;
        }
    },

    get(key, defaultValue = null) {
        try {
            const item = localStorage.getItem(`joitex_${key}`);
            return item ? JSON.parse(item) : defaultValue;
        } catch (e) {
            console.error('Storage error:', e);
            return defaultValue;
        }
    },

    remove(key) {
        localStorage.removeItem(`joitex_${key}`);
    },

    clear() {
        Object.keys(localStorage).forEach(key => {
            if (key.startsWith('joitex_')) {
                localStorage.removeItem(key);
            }
        });
    }
};

// Initialize common features
document.addEventListener('DOMContentLoaded', function() {
    ThemeManager.init();
    SidebarManager.init();

    // Theme toggle handler
    const themeToggle = document.getElementById('themeToggle');
    themeToggle?.addEventListener('click', () => ThemeManager.toggle());

    // Logout handler
    const logoutBtn = document.getElementById('logoutBtn');
    logoutBtn?.addEventListener('click', (e) => {
        e.preventDefault();
        Modal.confirm(
            'Confirm Logout',
            'Are you sure you want to logout?',
            () => auth.logout()
        );
    });

    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
});
