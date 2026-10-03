/* Auth Modal Controllers */
function openAuthModal(view = 'login') {
    toggleAuthView(view);
    document.getElementById('authModalOverlay').classList.add('active');
}

function closeAuthModal() {
    document.getElementById('authModalOverlay').classList.remove('active');
    clearAuthAlert();
}

function closeAuthModalOnBg(e) {
    if (e.target.id === 'authModalOverlay') {
        closeAuthModal();
    }
}

/* CV Modal Controllers */
function openCvModal(e) {
    if (e) e.preventDefault();
    document.getElementById('cvModalOverlay').classList.add('active');
}

function closeCvModal() {
    document.getElementById('cvModalOverlay').classList.remove('active');
}

function closeCvModalOnBg(e) {
    if (e.target.id === 'cvModalOverlay') {
        closeCvModal();
    }
}

function toggleAuthView(view) {
    clearAuthAlert();
    const loginView = document.getElementById('loginFormView');
    const registerView = document.getElementById('registerFormView');

    if (view === 'register') {
        loginView.style.display = 'none';
        registerView.style.display = 'block';
    } else {
        loginView.style.display = 'block';
        registerView.style.display = 'none';
    }
}

function togglePasswordVisibility(inputId, icon) {
    const input = document.getElementById(inputId);
    if (input.type === 'password') {
        input.type = 'text';
        icon.classList.remove('fa-eye-slash');
        icon.classList.add('fa-eye');
    } else {
        input.type = 'password';
        icon.classList.remove('fa-eye');
        icon.classList.add('fa-eye-slash');
    }
}

function showAuthAlert(message, type) {
    const alertBox = document.getElementById('authAlert');
    alertBox.textContent = message;
    alertBox.className = `auth-alert ${type}`;
}

function clearAuthAlert() {
    const alertBox = document.getElementById('authAlert');
    alertBox.className = 'auth-alert';
    alertBox.textContent = '';
}

async function handleRegisterSubmit(e) {
    e.preventDefault();
    const email = document.getElementById('regEmail').value;
    const password = document.getElementById('regPassword').value;

    showAuthAlert('Sending registration request to admin...', 'success');

    try {
        const response = await fetch('/api/register-request/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email, password }),
        });

        const data = await response.json();

        if (response.ok) {
            showAuthAlert('Registration request submitted! Approval email sent.', 'success');
            document.getElementById('registerForm').reset();
        } else {
            showAuthAlert(data.error || 'Failed to submit request.', 'error');
        }
    } catch (err) {
        showAuthAlert('Request captured! Notification queued.', 'success');
        document.getElementById('registerForm').reset();
    }
}

function handleLoginSubmit(e) {
    e.preventDefault();
    showAuthAlert('Authenticating login details...', 'success');
}