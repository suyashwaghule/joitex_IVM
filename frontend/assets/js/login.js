/* ========================================
   Login Page JavaScript
   ======================================== */

document.addEventListener('DOMContentLoaded', function () {
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

    // Theme Toggling
    const themeToggle = document.getElementById('themeToggle');
    const htmlElement = document.documentElement;
    const icon = themeToggle.querySelector('i');

    // Check for saved theme preference
    const savedTheme = localStorage.getItem('theme') || 'dark';
    htmlElement.setAttribute('data-theme', savedTheme);
    updateThemeIcon(savedTheme);

    themeToggle.addEventListener('click', () => {
        const currentTheme = htmlElement.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        
        htmlElement.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
        updateThemeIcon(newTheme);
    });

    function updateThemeIcon(theme) {
        if (theme === 'dark') {
            icon.classList.remove('bi-sun-fill');
            icon.classList.add('bi-moon-stars-fill');
        } else {
            icon.classList.remove('bi-moon-stars-fill');
            icon.classList.add('bi-sun-fill');
        }
    }

    // Toggle password visibility
    togglePasswordBtn.addEventListener('click', function () {
        const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
        passwordInput.setAttribute('type', type);

        const icon = this.querySelector('i');
        icon.classList.toggle('bi-eye');
        icon.classList.toggle('bi-eye-slash');
    });

    // Handle form submission
    loginForm.addEventListener('submit', async function (e) {
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

        // Attempt login
        const result = await auth.login(email, password, remember);

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

            if (result.message.toLowerCase().includes('email')) {
                emailInput.classList.add('is-invalid');
            } else {
                passwordInput.classList.add('is-invalid');
            }
        }
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
    emailInput.addEventListener('input', function () {
        this.classList.remove('is-invalid');
        loginError.classList.add('d-none');
    });

    passwordInput.addEventListener('input', function () {
        this.classList.remove('is-invalid');
        loginError.classList.add('d-none');
    });
});


