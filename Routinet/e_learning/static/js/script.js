// script.js - version consolidée pour Routinet
document.addEventListener('DOMContentLoaded', () => {
  initNavigation();
  initSearch();
  initLanguageSelector();
  initAnimations();
  initTabs();
  initForms();
  updateUserDisplay();
  initModals();
  initRoleDisplay();
  initDarkMode();
});

// Navigation + mobile menu
function initNavigation() {
  const mobileMenu = document.querySelector('.mobile-menu');
  const navLinks = document.querySelector('.nav-links');
  const mobileMenuContent = document.querySelector('.mobile-menu-content');

  if (mobileMenu && navLinks) {
    mobileMenu.addEventListener('click', (e) => {
      navLinks.style.display = navLinks.style.display === 'flex' ? 'none' : 'flex';
      if (mobileMenuContent) mobileMenuContent.classList.toggle('active');
    });
  }

  // smooth scroll for anchors
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
      const target = document.querySelector(this.getAttribute('href'));
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  });
}

// Search
function initSearch() {
  const searchInput = document.getElementById('global-search');
  if (!searchInput) return;
  let searchTimeout;
  searchInput.addEventListener('keypress', function(e) {
    if (e.key === 'Enter') performSearch(this.value);
  });
  searchInput.addEventListener('input', function() {
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(() => {
      if (this.value.length >= 3) suggestSearch(this.value);
    }, 500);
  });
}
function performSearch(query) {
  if (query && query.trim() !== '') window.location.href = `/cours/?search=${encodeURIComponent(query)}`;
}
function suggestSearch(q) { /* AJAX suggestion possible */ console.log('suggest:', q); }

// Language selector
function initLanguageSelector() {
  const select = document.getElementById('language-select');
  if (select) {
    const preferred = localStorage.getItem('preferredLanguage') || select.value;
    select.value = preferred;
    select.addEventListener('change', function() {
      localStorage.setItem('preferredLanguage', this.value);
      // submit language form if exists
      const form = document.getElementById('language-form');
      if (form) form.submit();
    });
  }
}

// Animations
function initAnimations() {
  const elements = document.querySelectorAll('.fade-in, .category-card, .course-card, .course-card-large, .assignment-card, .faq-item');
  const observer = new IntersectionObserver((entries, obs) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        obs.unobserve(entry.target);
      }
    });
  }, { threshold: 0.15, rootMargin: '0px 0px -50px 0px' });
  elements.forEach(el => observer.observe(el));
}

// Tabs
function initTabs() {
  const tabButtons = document.querySelectorAll('.tab-btn');
  const panes = document.querySelectorAll('.tab-content');
  tabButtons.forEach(btn => btn.addEventListener('click', function() {
    tabButtons.forEach(b => b.classList.remove('active'));
    panes.forEach(p => p.classList.remove('active'));
    btn.classList.add('active');
    const id = btn.dataset.tab;
    const pane = document.getElementById(id);
    if (pane) pane.classList.add('active');
  }));

  // profile nav items
  const profileNavItems = document.querySelectorAll('.profile-nav .nav-item[data-tab], .nav-item[data-tab]');
  const profilePanes = document.querySelectorAll('.tab-pane');
  profileNavItems.forEach(item => item.addEventListener('click', function(e) {
    e.preventDefault();
    profileNavItems.forEach(i => i.classList.remove('active'));
    profilePanes.forEach(p => p.classList.remove('active'));
    item.classList.add('active');
    const id = item.dataset.tab;
    const pane = document.getElementById(id);
    if (pane) pane.classList.add('active');
  }));
}

// Forms: simple validation
function initForms() {
  const forms = document.querySelectorAll('form');
  forms.forEach(form => {
    form.addEventListener('submit', function(e) {
      // simple required validation - you may expand
      const required = this.querySelectorAll('[required]');
      for (let el of required) {
        if (!el.value.trim()) {
          e.preventDefault();
          showFieldError(el, 'Ce champ est obligatoire');
          el.focus();
          return;
        }
      }
    });
  });
}

// simple field error functions
function showFieldError(field, message) {
  clearFieldError(field);
  field.style.borderColor = 'var(--danger-color)';
  const err = document.createElement('div');
  err.className = 'field-error';
  err.textContent = message;
  field.parentNode.appendChild(err);
}
function clearFieldError(field) {
  field.style.borderColor = '';
  const existing = field.parentNode.querySelector('.field-error');
  if (existing) existing.remove();
}

// Update avatar placeholder if provided as data-src
function updateUserDisplay() {
  const avatar = document.getElementById('user-avatar');
  if (avatar && avatar.dataset.src) avatar.src = avatar.dataset.src;
}

// Modales (connexion/inscription)
function initModals() {
  const modalLogin = document.getElementById('login-modal');
  const modalRegister = document.getElementById('register-modal');

  // open buttons
  document.getElementById('btn-login-modal')?.addEventListener('click', (e) => {
    e.preventDefault();
    if (modalLogin) { modalLogin.classList.remove('hidden'); modalRegister?.classList.add('hidden'); }
  });
  document.getElementById('btn-register-modal')?.addEventListener('click', (e) => {
    e.preventDefault();
    if (modalRegister) { modalRegister.classList.remove('hidden'); modalLogin?.classList.add('hidden'); }
  });

  // close handlers (common)
  document.querySelectorAll('.modal .close').forEach(btn => btn.addEventListener('click', () => {
    btn.closest('.modal')?.classList.add('hidden');
  }));
  // close on outside click
  document.querySelectorAll('.modal').forEach(m => m.addEventListener('click', function(e) {
    if (e.target === this) this.classList.add('hidden');
  }));

  // switch links inside modals
  document.getElementById('switch-to-register')?.addEventListener('click', (e) => {
    e.preventDefault();
    modalLogin?.classList.add('hidden');
    modalRegister?.classList.remove('hidden');
  });
  document.getElementById('switch-to-login')?.addEventListener('click', (e) => {
    e.preventDefault();
    modalRegister?.classList.add('hidden');
    modalLogin?.classList.remove('hidden');
  });
}

// Role display: hides elements with data-role="enseignant" from non-teachers
function initRoleDisplay() {
  const role = document.body.dataset.role || null;
  const teacherEls = document.querySelectorAll('[data-role="enseignant"]');
  teacherEls.forEach(el => {
    if (role === 'enseignant' || role === 'administrateur') {
      el.style.display = '';
    } else {
      el.style.display = 'none';
    }
  });
}

// Dark mode toggle
function initDarkMode() {
  const toggle = document.getElementById('toggle-dark-mode');
  if (!toggle) return;
  toggle.addEventListener('click', () => document.body.classList.toggle('dark-mode'));
}

// Notifications
function showNotification(message, type='info') {
  const notification = document.createElement('div');
  notification.className = `notification notification-${type}`;
  notification.textContent = message;
  document.body.appendChild(notification);
  setTimeout(() => notification.remove(), 4500);
}

// Export small API
window.Routinet = { performSearch, changeLanguage: (lang) => { localStorage.setItem('preferredLanguage', lang); const f=document.getElementById('language-form'); if(f){ let input=f.querySelector('input[name=language]'); if(!input){ input=document.createElement('input'); input.type='hidden'; input.name='language'; f.appendChild(input);} input.value=lang; f.submit(); } } };
