/**
 * CUSTOM ALERT SYSTEM
 * Reemplaza los alert() default del navegador con alertas personalizadas
 * Uso: showAlert('Título', 'Mensaje', 'tipo')
 * Tipos: success, error, warning, info
 */

// Create alert container if it doesn't exist
function createAlertContainer() {
    if (document.getElementById('customAlertContainer')) return;
    
    const container = document.createElement('div');
    container.id = 'customAlertContainer';
    container.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 99999;
        display: flex;
        flex-direction: column;
        gap: 12px;
        max-width: 400px;
    `;
    document.body.appendChild(container);
}

// Show custom alert
function showAlert(title, message, type = 'info', duration = 5000) {
    createAlertContainer();
    
    const alertId = 'alert_' + Date.now() + Math.random();
    const container = document.getElementById('customAlertContainer');
    
    // Icon and color based on type
    const configs = {
        success: {
            icon: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>',
            color: '#10b981',
            bg: 'rgba(16, 185, 129, 0.1)'
        },
        error: {
            icon: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z"/>',
            color: '#ef4444',
            bg: 'rgba(239, 68, 68, 0.1)'
        },
        warning: {
            icon: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>',
            color: '#f59e0b',
            bg: 'rgba(245, 158, 11, 0.1)'
        },
        info: {
            icon: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>',
            color: '#3b82f6',
            bg: 'rgba(59, 130, 246, 0.1)'
        }
    };
    
    const config = configs[type] || configs.info;
    
    const alertDiv = document.createElement('div');
    alertDiv.id = alertId;
    alertDiv.style.cssText = `
        background: white;
        border-radius: 12px;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15);
        padding: 16px 20px;
        display: flex;
        align-items: start;
        gap: 12px;
        animation: slideInRight 0.3s ease-out;
        border-left: 4px solid ${config.color};
        min-width: 320px;
        max-width: 400px;
    `;
    
    alertDiv.innerHTML = `
        <div style="
            width: 40px;
            height: 40px;
            border-radius: 50%;
            background: ${config.bg};
            display: flex;
            align-items: center;
            justify-content: center;
            flex-shrink: 0;
        ">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="${config.color}">
                ${config.icon}
            </svg>
        </div>
        <div style="flex: 1; padding-top: 2px;">
            <div style="font-weight: 600; font-size: 14px; color: #1f2937; margin-bottom: 4px;">
                ${title}
            </div>
            <div style="font-size: 13px; color: #6b7280; line-height: 1.5;">
                ${message}
            </div>
        </div>
        <button onclick="closeAlert('${alertId}')" style="
            background: none;
            border: none;
            cursor: pointer;
            padding: 4px;
            color: #9ca3af;
            flex-shrink: 0;
        ">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
            </svg>
        </button>
    `;
    
    container.appendChild(alertDiv);
    
    // Auto remove after duration
    if (duration > 0) {
        setTimeout(() => {
            closeAlert(alertId);
        }, duration);
    }
}

// Close alert
function closeAlert(alertId) {
    const alert = document.getElementById(alertId);
    if (alert) {
        alert.style.animation = 'slideOutRight 0.3s ease-out';
        setTimeout(() => {
            alert.remove();
        }, 300);
    }
}

// Show confirmation dialog (replaces confirm())
function showConfirm(title, message, onConfirm, onCancel = null) {
    const modalId = 'confirmModal_' + Date.now();
    
    const modalHTML = `
        <div class="modal-overlay" id="${modalId}" style="display: flex !important;">
            <div class="modal modal-sm">
                <div class="modal-header">
                    <h3 class="modal-title">${title}</h3>
                    <button class="modal-close" onclick="closeConfirmModal('${modalId}')">×</button>
                </div>
                <div class="modal-body">
                    <div style="text-align: center; margin-bottom: 20px;">
                        <div style="width: 64px; height: 64px; margin: 0 auto 16px; border-radius: 50%; background: rgba(245, 101, 101, 0.1); display: flex; align-items: center; justify-content: center;">
                            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="var(--danger)" stroke-width="2">
                                <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
                                <line x1="12" y1="9" x2="12" y2="13"></line>
                                <line x1="12" y1="17" x2="12.01" y2="17"></line>
                            </svg>
                        </div>
                        <p style="font-size: 15px; color: var(--text-primary); font-weight: 600; margin-bottom: 8px;">
                            ${title}
                        </p>
                        <p style="font-size: 14px; color: var(--text-secondary);">
                            ${message}
                        </p>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" onclick="closeConfirmModal('${modalId}')">Cancelar</button>
                    <button type="button" class="btn btn-danger" onclick="confirmAction('${modalId}')">Confirmar</button>
                </div>
            </div>
        </div>
    `;
    
    const modalDiv = document.createElement('div');
    modalDiv.innerHTML = modalHTML;
    document.body.appendChild(modalDiv.firstElementChild);
    
    // Store callbacks
    window.confirmCallbacks = window.confirmCallbacks || {};
    window.confirmCallbacks[modalId] = {
        onConfirm: onConfirm,
        onCancel: onCancel
    };
}

function closeConfirmModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        const callbacks = window.confirmCallbacks?.[modalId];
        if (callbacks?.onCancel) {
            callbacks.onCancel();
        }
        modal.remove();
        delete window.confirmCallbacks?.[modalId];
    }
}

function confirmAction(modalId) {
    const callbacks = window.confirmCallbacks?.[modalId];
    if (callbacks?.onConfirm) {
        callbacks.onConfirm();
    }
    closeConfirmModal(modalId);
}

// Add animations
if (!document.getElementById('customAlertStyles')) {
    const style = document.createElement('style');
    style.id = 'customAlertStyles';
    style.textContent = `
        @keyframes slideInRight {
            from {
                transform: translateX(400px);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }
        
        @keyframes slideOutRight {
            from {
                transform: translateX(0);
                opacity: 1;
            }
            to {
                transform: translateX(400px);
                opacity: 0;
            }
        }
    `;
    document.head.appendChild(style);
}
