/* ========================================
   Login Page JavaScript
   ======================================== */

document.addEventListener('DOMContentLoaded', function() {
    // Check if already logged in - redirect to portal selection
    if (auth.isAuthenticated()) {
        window.location.href = getNavigationPath('select-portal.html');
        return;
    }

    // Get form elements
    const loginForm = document.getElementById('loginForm');
    const emailInput = document.getElementById('email');
    const passwordInput = document.getElementById('password');
    const rememberMeCheckbox = document.getElementById('rememberMe');
    const togglePasswordBtn = document.getElementById('togglePassword');
    const loginError = document.getElementById('loginError');
    const errorMessage = document.getElementById('errorMessage');

    // Toggle password visibility
    togglePasswordBtn.addEventListener('click', function() {
        const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
        passwordInput.setAttribute('type', type);
        
        const icon = this.querySelector('i');
        icon.classList.toggle('bi-eye');
        icon.classList.toggle('bi-eye-slash');
    });

    // Handle form submission
    loginForm.addEventListener('submit', function(e) {
        e.preventDefault();

        // Clear previous errors
        loginError.classList.add('d-none');
        emailInput.classList.remove('is-invalid');
        passwordInput.classList.remove('is-invalid');

        // Get form values
        const email = emailInput.value.trim();
        const password = passwordInput.value;
        const remember = rememberMeCheckbox.checked;

        // Validate inputs
        if (!email) {
            showError('Please enter your email address');
            emailInput.classList.add('is-invalid');
            return;
        }

        if (!password) {
            showError('Please enter your password');
            passwordInput.classList.add('is-invalid');
            return;
        }

        // Show loading state
        const submitBtn = loginForm.querySelector('button[type="submit"]');
        const originalBtnText = submitBtn.innerHTML;
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Signing in...';

        // Simulate API delay
        setTimeout(() => {
            // Attempt login
            const result = auth.login(email, password, remember);

            if (result.success) {
                // Success - redirect to dashboard
                submitBtn.innerHTML = '<i class="bi bi-check-circle me-2"></i>Success!';
                submitBtn.classList.remove('btn-primary');
                submitBtn.classList.add('btn-success');

                setTimeout(() => {
                    window.location.href = result.redirectUrl;
                }, 500);
            } else {
                // Error - show message
                showError(result.message);
                submitBtn.disabled = false;
                submitBtn.innerHTML = originalBtnText;
                emailInput.classList.add('is-invalid');
                passwordInput.classList.add('is-invalid');
            }
        }, 800);
    });

    // Show error message
    function showError(message) {
        errorMessage.textContent = message;
        loginError.classList.remove('d-none');
        
        // Auto-hide after 5 seconds
        setTimeout(() => {
            loginError.classList.add('d-none');
        }, 5000);
    }

    // Clear error on input
    emailInput.addEventListener('input', function() {
        this.classList.remove('is-invalid');
        loginError.classList.add('d-none');
    });

    passwordInput.addEventListener('input', function() {
        this.classList.remove('is-invalid');
        loginError.classList.add('d-none');
    });
});

// Demo account quick fill
function fillDemo(role) {
    const demoCredentials = {
        admin: { email: 'admin@joitex.com', password: 'admin123' },
        callcenter: { email: 'callcenter@joitex.com', password: 'call123' },
        sales: { email: 'sales@joitex.com', password: 'sales123' },
        salesexec: { email: 'salesexec@joitex.com', password: 'exec123' },
        engineer: { email: 'engineer@joitex.com', password: 'eng123' },
        inventory: { email: 'inventory@joitex.com', password: 'inv123' },
        network: { email: 'network@joitex.com', password: 'net123' },
        finance: { email: 'finance@joitex.com', password: 'fin123' }
    };

    const credentials = demoCredentials[role];
    if (credentials) {
        document.getElementById('email').value = credentials.email;
        document.getElementById('password').value = credentials.password;
        
        // Add visual feedback
        const emailInput = document.getElementById('email');
        const passwordInput = document.getElementById('password');
        
        emailInput.classList.add('is-valid');
        passwordInput.classList.add('is-valid');
        
        setTimeout(() => {
            emailInput.classList.remove('is-valid');
            passwordInput.classList.remove('is-valid');
        }, 1000);
    }
}
