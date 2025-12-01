/**
 * ALEX RENTACAR - MAIN JAVASCRIPT
 * Complete functionality for all UI components
 */

// ============== INITIALIZATION ============== //
document.addEventListener('DOMContentLoaded', function() {
    // Hide loader after page load
    setTimeout(() => {
        const loader = document.getElementById('loader');
        if (loader) {
            loader.classList.add('hidden');
        }
    }, 500);

    // Initialize all components
    initSidebar();
    initMobileMenu();
    initTheme();
    initUserMenu();
    initNotifications();
    initAlerts();
    initModals();
    initOffcanvas();
    initDropdowns();
    initTabs();
    initAccordions();
    initSwitches();
    initForms();
    initTooltips();
});

// ============== SIDEBAR ============== //
function initSidebar() {
    const sidebar = document.getElementById('sidebar');
    const sidebarToggle = document.getElementById('sidebarToggle');
    
    if (!sidebar || !sidebarToggle) return;

    // Load saved state
    const sidebarState = localStorage.getItem('sidebarState');
    if (sidebarState === 'collapsed') {
        sidebar.classList.add('collapsed');
    }

    // Toggle sidebar
    sidebarToggle.addEventListener('click', () => {
        sidebar.classList.toggle('collapsed');
        
        // Save state
        const isCollapsed = sidebar.classList.contains('collapsed');
        localStorage.setItem('sidebarState', isCollapsed ? 'collapsed' : 'expanded');
        
        // Dispatch event for other components
        window.dispatchEvent(new CustomEvent('sidebarToggle', {
            detail: { collapsed: isCollapsed }
        }));
    });

    // Add active class to current page
    const currentPath = window.location.pathname;
    const navItems = sidebar.querySelectorAll('.nav-item');
    
    navItems.forEach(item => {
        const href = item.getAttribute('href');
        if (href && currentPath.includes(href) && href !== '/') {
            item.classList.add('active');
        }
    });
}

// ============== MOBILE MENU ============== //
function initMobileMenu() {
    const mobileMenuBtn = document.getElementById('mobileMenuBtn');
    const sidebar = document.getElementById('sidebar');
    const mobileOverlay = document.getElementById('mobileOverlay');
    
    if (!mobileMenuBtn || !sidebar || !mobileOverlay) return;

    // Open mobile menu
    mobileMenuBtn.addEventListener('click', () => {
        sidebar.classList.add('mobile-open');
        mobileOverlay.classList.add('active');
        document.body.style.overflow = 'hidden';
    });

    // Close mobile menu
    mobileOverlay.addEventListener('click', () => {
        closeMobileMenu();
    });

    // Close on nav item click
    const navItems = sidebar.querySelectorAll('.nav-item');
    navItems.forEach(item => {
        item.addEventListener('click', () => {
            if (window.innerWidth <= 768) {
                closeMobileMenu();
            }
        });
    });

    function closeMobileMenu() {
        sidebar.classList.remove('mobile-open');
        mobileOverlay.classList.remove('active');
        document.body.style.overflow = '';
    }
}

// ============== THEME SWITCHER ============== //
function initTheme() {
    const themeToggle = document.getElementById('themeToggle');
    if (!themeToggle) return;

    // Load saved theme
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.body.setAttribute('data-theme', savedTheme);

    // Toggle theme
    themeToggle.addEventListener('click', () => {
        const currentTheme = document.body.getAttribute('data-theme');
        const newTheme = currentTheme === 'light' ? 'dark' : 'light';
        
        document.body.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
        
        // Animate transition
        document.body.style.transition = 'background-color 0.3s ease, color 0.3s ease';
    });
}

// ============== USER MENU ============== //
function initUserMenu() {
    const userMenu = document.getElementById('userMenu');
    const userMenuBtn = document.getElementById('userMenuBtn');
    
    if (!userMenu || !userMenuBtn) return;

    // Toggle user menu
    userMenuBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        userMenu.classList.toggle('active');
        closeOtherDropdowns(userMenu);
    });

    // Close on outside click
    document.addEventListener('click', (e) => {
        if (!userMenu.contains(e.target)) {
            userMenu.classList.remove('active');
        }
    });

    // Close on escape
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            userMenu.classList.remove('active');
        }
    });
}

// ============== NOTIFICATIONS ============== //
function initNotifications() {
    const notificationBtn = document.getElementById('notificationBtn');
    const notificationPanel = document.getElementById('notificationPanel');
    const markAllRead = document.getElementById('markAllRead');
    
    if (!notificationBtn || !notificationPanel) return;

    // Toggle notification panel
    notificationBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        notificationPanel.classList.toggle('active');
        closeOtherDropdowns(notificationPanel);
    });

    // Mark all as read
    if (markAllRead) {
        markAllRead.addEventListener('click', () => {
            const unreadItems = notificationPanel.querySelectorAll('.notification-item.unread');
            unreadItems.forEach(item => {
                item.classList.remove('unread');
            });
            
            // Update badge
            const badge = notificationBtn.querySelector('.badge');
            if (badge) {
                badge.textContent = '0';
                badge.style.display = 'none';
            }
        });
    }

    // Mark individual notification as read
    const notificationItems = notificationPanel.querySelectorAll('.notification-item');
    notificationItems.forEach(item => {
        item.addEventListener('click', () => {
            item.classList.remove('unread');
            updateNotificationCount();
        });
    });

    // Close on outside click
    document.addEventListener('click', (e) => {
        if (!notificationPanel.contains(e.target) && !notificationBtn.contains(e.target)) {
            notificationPanel.classList.remove('active');
        }
    });

    function updateNotificationCount() {
        const unreadCount = notificationPanel.querySelectorAll('.notification-item.unread').length;
        const badge = notificationBtn.querySelector('.badge');
        if (badge) {
            badge.textContent = unreadCount;
            badge.style.display = unreadCount > 0 ? 'flex' : 'none';
        }
    }
}

// ============== ALERTS ============== //
function initAlerts() {
    const alerts = document.querySelectorAll('.alert');
    
    alerts.forEach(alert => {
        const closeBtn = alert.querySelector('.alert-close');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => {
                alert.style.animation = 'slideOutUp 0.3s ease';
                setTimeout(() => {
                    alert.remove();
                }, 300);
            });
        }

        // Auto dismiss after 5 seconds
        setTimeout(() => {
            if (alert.parentElement) {
                alert.style.animation = 'slideOutUp 0.3s ease';
                setTimeout(() => {
                    alert.remove();
                }, 300);
            }
        }, 5000);
    });
}

// ============== MODALS ============== //
function initModals() {
    // Open modal
    document.querySelectorAll('[data-modal]').forEach(trigger => {
        trigger.addEventListener('click', () => {
            const modalId = trigger.getAttribute('data-modal');
            openModal(modalId);
        });
    });

    // Close modal
    document.querySelectorAll('.modal-close, [data-modal-close]').forEach(closeBtn => {
        closeBtn.addEventListener('click', () => {
            const modal = closeBtn.closest('.modal-overlay');
            if (modal) {
                closeModal(modal);
            }
        });
    });

    // Close on overlay click
    document.querySelectorAll('.modal-overlay').forEach(overlay => {
        overlay.addEventListener('click', (e) => {
            if (e.target === overlay) {
                closeModal(overlay);
            }
        });
    });

    // Close on escape
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            const activeModal = document.querySelector('.modal-overlay.active');
            if (activeModal) {
                closeModal(activeModal);
            }
        }
    });
}

function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (!modal) return;
    
    modal.classList.add('active');
    document.body.style.overflow = 'hidden';
    
    // Focus first input
    const firstInput = modal.querySelector('input, textarea, select');
    if (firstInput) {
        setTimeout(() => firstInput.focus(), 100);
    }
    
    // Dispatch event
    modal.dispatchEvent(new CustomEvent('modalOpened'));
}

function closeModal(modal) {
    if (!modal) return;
    
    modal.classList.remove('active');
    document.body.style.overflow = '';
    
    // Dispatch event
    modal.dispatchEvent(new CustomEvent('modalClosed'));
}

// ============== OFFCANVAS ============== //
function initOffcanvas() {
    // Open offcanvas
    document.querySelectorAll('[data-offcanvas]').forEach(trigger => {
        trigger.addEventListener('click', () => {
            const offcanvasId = trigger.getAttribute('data-offcanvas');
            openOffcanvas(offcanvasId);
        });
    });

    // Close offcanvas
    document.querySelectorAll('.offcanvas-close, [data-offcanvas-close]').forEach(closeBtn => {
        closeBtn.addEventListener('click', () => {
            const offcanvas = closeBtn.closest('.offcanvas');
            if (offcanvas) {
                closeOffcanvas(offcanvas);
            }
        });
    });

    // Close on overlay click
    document.querySelectorAll('.offcanvas-overlay').forEach(overlay => {
        overlay.addEventListener('click', () => {
            const offcanvas = overlay.nextElementSibling;
            if (offcanvas && offcanvas.classList.contains('offcanvas')) {
                closeOffcanvas(offcanvas);
            }
        });
    });

    // Close on escape
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            const activeOffcanvas = document.querySelector('.offcanvas.active');
            if (activeOffcanvas) {
                closeOffcanvas(activeOffcanvas);
            }
        }
    });
}

function openOffcanvas(offcanvasId) {
    const offcanvas = document.getElementById(offcanvasId);
    if (!offcanvas) return;
    
    const overlay = offcanvas.previousElementSibling;
    
    offcanvas.classList.add('active');
    if (overlay && overlay.classList.contains('offcanvas-overlay')) {
        overlay.classList.add('active');
    }
    document.body.style.overflow = 'hidden';
    
    // Dispatch event
    offcanvas.dispatchEvent(new CustomEvent('offcanvasOpened'));
}

function closeOffcanvas(offcanvas) {
    if (!offcanvas) return;
    
    const overlay = offcanvas.previousElementSibling;
    
    offcanvas.classList.remove('active');
    if (overlay && overlay.classList.contains('offcanvas-overlay')) {
        overlay.classList.remove('active');
    }
    document.body.style.overflow = '';
    
    // Dispatch event
    offcanvas.dispatchEvent(new CustomEvent('offcanvasClosed'));
}

// ============== DROPDOWNS ============== //
function initDropdowns() {
    document.querySelectorAll('.dropdown-trigger').forEach(trigger => {
        trigger.addEventListener('click', (e) => {
            e.stopPropagation();
            const dropdown = trigger.closest('.dropdown');
            dropdown.classList.toggle('active');
            closeOtherDropdowns(dropdown);
        });
    });

    // Close on outside click
    document.addEventListener('click', (e) => {
        if (!e.target.closest('.dropdown')) {
            document.querySelectorAll('.dropdown.active').forEach(dropdown => {
                dropdown.classList.remove('active');
            });
        }
    });

    // Handle dropdown item clicks
    document.querySelectorAll('.dropdown-item').forEach(item => {
        item.addEventListener('click', () => {
            const dropdown = item.closest('.dropdown');
            if (dropdown) {
                dropdown.classList.remove('active');
            }
        });
    });
}

// ============== TABS ============== //
function initTabs() {
    document.querySelectorAll('.tab-item').forEach(tab => {
        tab.addEventListener('click', () => {
            const tabContainer = tab.closest('.tabs-container');
            if (!tabContainer) return;

            // Remove active class from all tabs
            tabContainer.querySelectorAll('.tab-item').forEach(t => {
                t.classList.remove('active');
            });

            // Add active class to clicked tab
            tab.classList.add('active');

            // Handle tab content if data-tab attribute exists
            const tabId = tab.getAttribute('data-tab');
            if (tabId) {
                showTabContent(tabId);
            }
        });
    });
}

function showTabContent(tabId) {
    // Hide all tab contents
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });

    // Show selected tab content
    const targetContent = document.getElementById(tabId);
    if (targetContent) {
        targetContent.classList.add('active');
    }
}

// ============== ACCORDIONS ============== //
function initAccordions() {
    document.querySelectorAll('.accordion-header').forEach(header => {
        header.addEventListener('click', () => {
            const accordionItem = header.closest('.accordion-item');
            const accordion = accordionItem.closest('.accordion');
            
            // Check if it's a single-open accordion
            const singleOpen = accordion.hasAttribute('data-single-open');
            
            if (singleOpen) {
                // Close all other items
                accordion.querySelectorAll('.accordion-item').forEach(item => {
                    if (item !== accordionItem) {
                        item.classList.remove('active');
                    }
                });
            }
            
            // Toggle current item
            accordionItem.classList.toggle('active');
        });
    });
}

// ============== SWITCHES ============== //
function initSwitches() {
    document.querySelectorAll('.switch').forEach(switchEl => {
        switchEl.addEventListener('click', () => {
            switchEl.classList.toggle('active');
            
            // Dispatch event
            const isActive = switchEl.classList.contains('active');
            switchEl.dispatchEvent(new CustomEvent('switchChange', {
                detail: { active: isActive }
            }));
        });
    });
}

// ============== FORMS ============== //
function initForms() {
    // Form validation
    document.querySelectorAll('form[data-validate]').forEach(form => {
        form.addEventListener('submit', (e) => {
            if (!validateForm(form)) {
                e.preventDefault();
            }
        });
    });

    // Clear error on input
    document.querySelectorAll('.form-input, .form-select, .form-textarea').forEach(input => {
        input.addEventListener('input', () => {
            clearError(input);
        });
    });

    // File input display
    document.querySelectorAll('.file-input').forEach(input => {
        input.addEventListener('change', (e) => {
            const label = input.nextElementSibling;
            if (label && e.target.files.length > 0) {
                const fileName = e.target.files[0].name;
                const fileText = label.querySelector('.file-text');
                if (fileText) {
                    fileText.textContent = fileName;
                }
            }
        });
    });
}

function validateForm(form) {
    let isValid = true;
    const requiredInputs = form.querySelectorAll('[required]');
    
    requiredInputs.forEach(input => {
        if (!input.value.trim()) {
            showError(input, 'Este campo es requerido');
            isValid = false;
        } else {
            // Type-specific validation
            if (input.type === 'email' && !isValidEmail(input.value)) {
                showError(input, 'Email inválido');
                isValid = false;
            }
        }
    });
    
    return isValid;
}

function showError(input, message) {
    input.classList.add('error');
    
    // Remove existing error
    const existingError = input.parentElement.querySelector('.form-error');
    if (existingError) {
        existingError.remove();
    }
    
    // Add error message
    const error = document.createElement('div');
    error.className = 'form-error';
    error.innerHTML = `
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
        </svg>
        ${message}
    `;
    input.parentElement.appendChild(error);
}

function clearError(input) {
    input.classList.remove('error');
    const error = input.parentElement.querySelector('.form-error');
    if (error) {
        error.remove();
    }
}

function isValidEmail(email) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

// ============== TOOLTIPS ============== //
function initTooltips() {
    document.querySelectorAll('[data-tooltip]').forEach(element => {
        const tooltipText = element.getAttribute('data-tooltip');
        
        // Create tooltip element
        const tooltip = document.createElement('div');
        tooltip.className = 'tooltip-text';
        tooltip.textContent = tooltipText;
        element.appendChild(tooltip);
        element.classList.add('tooltip');
    });
}

// ============== UTILITY FUNCTIONS ============== //
function closeOtherDropdowns(currentElement) {
    document.querySelectorAll('.dropdown.active, .user-menu.active').forEach(el => {
        if (el !== currentElement && !currentElement.contains(el)) {
            el.classList.remove('active');
        }
    });
    
    document.querySelectorAll('.notification-panel.active').forEach(panel => {
        if (panel !== currentElement) {
            panel.classList.remove('active');
        }
    });
}

// Add slide out animation
const style = document.createElement('style');
style.textContent = `
    @keyframes slideOutUp {
        from {
            opacity: 1;
            transform: translateY(0);
        }
        to {
            opacity: 0;
            transform: translateY(-20px);
        }
    }
`;
document.head.appendChild(style);

// ============== GLOBAL FUNCTIONS ============== //
// Export functions to window for external use
window.AppUtils = {
    openModal,
    closeModal,
    openOffcanvas,
    closeOffcanvas,
    showError,
    clearError,
    validateForm
};

// ============== AUTO-SAVE FORM DATA ============== //
function initAutoSave() {
    const formsWithAutoSave = document.querySelectorAll('[data-autosave]');
    
    formsWithAutoSave.forEach(form => {
        const formId = form.getAttribute('data-autosave');
        
        // Load saved data
        const savedData = localStorage.getItem(`form_${formId}`);
        if (savedData) {
            try {
                const data = JSON.parse(savedData);
                Object.keys(data).forEach(key => {
                    const input = form.querySelector(`[name="${key}"]`);
                    if (input) {
                        input.value = data[key];
                    }
                });
            } catch (e) {
                console.error('Error loading saved form data:', e);
            }
        }
        
        // Save on input
        form.addEventListener('input', debounce(() => {
            const formData = new FormData(form);
            const data = {};
            formData.forEach((value, key) => {
                data[key] = value;
            });
            localStorage.setItem(`form_${formId}`, JSON.stringify(data));
        }, 1000));
    });
}

// Debounce function
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// ============== KEYBOARD SHORTCUTS ============== //
document.addEventListener('keydown', (e) => {
    // Ctrl/Cmd + B = Toggle sidebar
    if ((e.ctrlKey || e.metaKey) && e.key === 'b') {
        e.preventDefault();
        const toggleBtn = document.getElementById('sidebarToggle');
        if (toggleBtn) toggleBtn.click();
    }
    
    // Ctrl/Cmd + K = Focus search
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        const searchInput = document.querySelector('.search-input, input[type="search"]');
        if (searchInput) searchInput.focus();
    }
});

// ============== PRINT HANDLER ============== //
window.addEventListener('beforeprint', () => {
    const sidebar = document.getElementById('sidebar');
    if (sidebar) {
        sidebar.style.display = 'none';
    }
});

window.addEventListener('afterprint', () => {
    const sidebar = document.getElementById('sidebar');
    if (sidebar) {
        sidebar.style.display = '';
    }
});

console.log('🚗 AlexRentaCar - System loaded successfully!');