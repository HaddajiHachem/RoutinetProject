// Gestion des modales pour Routinet - Version corrigée
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Initialisation des modales Routinet...');
    initModals();
    initAuthForms();
});

function initModals() {
    // Éléments des modales
    const loginModal = document.getElementById('login-modal');
    const registerModal = document.getElementById('register-modal');
    const authModal = document.getElementById('auth-modal'); // Modale legacy
    
    // Boutons d'ouverture
    const loginBtn = document.getElementById('btn-login-modal');
    const registerBtn = document.getElementById('btn-register-modal');
    
    console.log('Boutons trouvés:', { loginBtn, registerBtn });

    // Gestionnaire pour le bouton de connexion
    if (loginBtn) {
        loginBtn.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            console.log('Clic sur connexion');
            if (loginModal) {
                openModal(loginModal);
            }
        });
    }

    // Gestionnaire pour le bouton d'inscription
    if (registerBtn) {
        registerBtn.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            console.log('Clic sur inscription');
            if (registerModal) {
                openModal(registerModal);
            }
        });
    }

    // Fermeture des modales
    initCloseModals();
    
    // Basculer entre connexion et inscription
    initAuthSwitching();
    
    // Gestion des clics externes et Échap
    initModalOverlay();
}

function initCloseModals() {
    // Fermer avec le bouton ×
    const closeButtons = document.querySelectorAll('.close-modal, .close');
    closeButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            console.log('Fermeture modale');
            closeAllModals();
        });
    });
}

function initAuthSwitching() {
    // Basculer vers l'inscription
    const switchToRegister = document.getElementById('switch-to-register');
    const showRegister = document.getElementById('show-register');
    
    [switchToRegister, showRegister].forEach(btn => {
        if (btn) {
            btn.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                const loginModal = document.getElementById('login-modal');
                const registerModal = document.getElementById('register-modal');
                if (loginModal) closeModal(loginModal);
                if (registerModal) openModal(registerModal);
            });
        }
    });

    // Basculer vers la connexion
    const switchToLogin = document.getElementById('switch-to-login');
    const showLogin = document.getElementById('show-login');
    
    [switchToLogin, showLogin].forEach(btn => {
        if (btn) {
            btn.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                const loginModal = document.getElementById('login-modal');
                const registerModal = document.getElementById('register-modal');
                if (registerModal) closeModal(registerModal);
                if (loginModal) openModal(loginModal);
            });
        }
    });
}

function initModalOverlay() {
    // Fermer en cliquant à l'extérieur
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('modal')) {
            console.log('Clic externe - fermeture');
            closeAllModals();
        }
    });

    // Fermer avec Échap
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            console.log('Échap - fermeture');
            closeAllModals();
        }
    });
}

function openModal(modal) {
    if (!modal) {
        console.error('Modale non trouvée');
        return;
    }
    
    // Fermer toutes les modales d'abord
    closeAllModals();
    
    // Ouvrir la modale demandée
    modal.style.display = 'block';
    modal.setAttribute('aria-hidden', 'false');
    document.body.style.overflow = 'hidden';
    document.body.classList.add('modal-open');
    
    console.log('Modale ouverte:', modal.id);
}

function closeModal(modal) {
    if (!modal) return;
    
    modal.style.display = 'none';
    modal.setAttribute('aria-hidden', 'true');
    document.body.style.overflow = '';
    document.body.classList.remove('modal-open');
    
    console.log('Modale fermée:', modal.id);
}

function closeAllModals() {
    const modals = document.querySelectorAll('.modal');
    modals.forEach(modal => {
        modal.style.display = 'none';
        modal.setAttribute('aria-hidden', 'true');
    });
    document.body.style.overflow = '';
    document.body.classList.remove('modal-open');
    
    console.log('Toutes les modales fermées');
}

// Gestion des formulaires d'authentification
function initAuthForms() {
    // Formulaire de connexion
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', function(e) {
            if (!validateLoginForm(this)) {
                e.preventDefault();
                console.log('Validation connexion échouée');
            } else {
                console.log('Soumission connexion');
                // La soumission normale Django se poursuit
            }
        });
    }

    // Formulaire d'inscription
    const registerForm = document.getElementById('register-form');
    if (registerForm) {
        registerForm.addEventListener('submit', function(e) {
            if (!validateRegisterForm(this)) {
                e.preventDefault();
                console.log('Validation inscription échouée');
            } else {
                console.log('Soumission inscription');
                // La soumission normale Django se poursuit
            }
        });
    }

    // Initialiser la visibilité des mots de passe
    initPasswordToggles();
}

function validateLoginForm(form) {
    const email = form.querySelector('input[type="email"]');
    const password = form.querySelector('input[type="password"]');
    
    clearFormErrors(form);
    
    let isValid = true;
    
    if (!email || !email.value.trim()) {
        showFieldError(email, 'L\'email est obligatoire');
        isValid = false;
    } else if (!isValidEmail(email.value)) {
        showFieldError(email, 'Format d\'email invalide');
        isValid = false;
    }
    
    if (!password || !password.value.trim()) {
        showFieldError(password, 'Le mot de passe est obligatoire');
        isValid = false;
    }
    
    return isValid;
}

function validateRegisterForm(form) {
    const firstname = form.querySelector('input[name="firstname"], input[name="first_name"]');
    const lastname = form.querySelector('input[name="lastname"], input[name="last_name"]');
    const email = form.querySelector('input[type="email"]');
    const password = form.querySelector('input[name="password"], input[name="password1"]');
    const confirmPassword = form.querySelector('input[name="confirm_password"], input[name="password2"]');
    const acceptTerms = form.querySelector('input[name="accept-terms"]');
    
    clearFormErrors(form);
    
    let isValid = true;
    
    // Validation des champs
    if (!firstname?.value.trim()) {
        showFieldError(firstname, 'Le prénom est obligatoire');
        isValid = false;
    }
    
    if (!lastname?.value.trim()) {
        showFieldError(lastname, 'Le nom est obligatoire');
        isValid = false;
    }
    
    if (!email?.value.trim()) {
        showFieldError(email, 'L\'email est obligatoire');
        isValid = false;
    } else if (!isValidEmail(email.value)) {
        showFieldError(email, 'Format d\'email invalide');
        isValid = false;
    }
    
    if (!password?.value.trim()) {
        showFieldError(password, 'Le mot de passe est obligatoire');
        isValid = false;
    } else if (password.value.length < 8) {
        showFieldError(password, 'Le mot de passe doit contenir au moins 8 caractères');
        isValid = false;
    }
    
    if (confirmPassword && !confirmPassword.value.trim()) {
        showFieldError(confirmPassword, 'Veuillez confirmer votre mot de passe');
        isValid = false;
    } else if (confirmPassword && password && password.value !== confirmPassword.value) {
        showFieldError(confirmPassword, 'Les mots de passe ne correspondent pas');
        isValid = false;
    }
    
    if (acceptTerms && !acceptTerms.checked) {
        showFieldError(acceptTerms, 'Vous devez accepter les conditions d\'utilisation');
        isValid = false;
    }
    
    return isValid;
}

function initPasswordToggles() {
    document.querySelectorAll('.password-toggle').forEach(toggle => {
        toggle.addEventListener('click', function() {
            const input = this.closest('.form-group').querySelector('input[type="password"]');
            if (input) {
                const type = input.type === 'password' ? 'text' : 'password';
                input.type = type;
                const icon = this.querySelector('i');
                if (icon) {
                    icon.classList.toggle('fa-eye');
                    icon.classList.toggle('fa-eye-slash');
                }
            }
        });
    });
}

function showFieldError(field, message) {
    if (!field) return;
    
    clearFieldError(field);
    field.classList.add('error');
    
    const errorElement = document.createElement('div');
    errorElement.className = 'field-error';
    errorElement.textContent = message;
    
    field.parentNode.appendChild(errorElement);
}

function clearFieldError(field) {
    if (!field) return;
    field.classList.remove('error');
    const existingError = field.parentNode.querySelector('.field-error');
    if (existingError) {
        existingError.remove();
    }
}

function clearFormErrors(form) {
    const errors = form.querySelectorAll('.field-error');
    errors.forEach(error => error.remove());
    const errorFields = form.querySelectorAll('.error');
    errorFields.forEach(field => field.classList.remove('error'));
}

function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

// Fonctions globales pour débogage
window.debugModals = {
    openLogin: () => {
        const modal = document.getElementById('login-modal');
        if (modal) openModal(modal);
    },
    openRegister: () => {
        const modal = document.getElementById('register-modal');
        if (modal) openModal(modal);
    },
    closeAll: closeAllModals,
    listModals: () => {
        return document.querySelectorAll('.modal');
    }
};