// ==========================================
// ALQUILERES.JS - ACCORDION STYLE (EXCEL-LIKE)
// ==========================================

// Global variables
let semanasData = {};
let bancosGlobal = [];
let tiposTrabajo = [];
let mecanicos = [];
let currentEditingDetalleId = null;
let currentSemanaId = null;
let userRol = null;

// ==========================================
// INITIALIZATION
// ==========================================
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Alquileres Sistema Inicializado');
    
    // Get user rol from DOM
    userRol = document.body.dataset.userRol || 'user';
    console.log('👤 User rol:', userRol);
    
    // Load resources
    loadBancos();
    loadTiposTrabajo();
    loadMecanicos();
    
    // ✅ VALIDAR SEMANAS ACTIVAS AL CARGAR
    validarSemanasActivas();
    
    // Setup filters
    const filtroEstado = document.getElementById('filtroEstado');
    if (filtroEstado) {
        filtroEstado.addEventListener('change', filtrarSemanas);
    }
    
    // Setup forms
    setupForms();
    
    // ✅ OCULTAR BOTONES SI NO ES ADMIN
    if (userRol !== 'admin') {
        ocultarBotonesAdmin();
    }
});

/ ==========================================
// ✅ VALIDAR SEMANAS ACTIVAS (NUEVO)
// ==========================================
function validarSemanasActivas() {
    fetch('/alquiler/semanas/validar-activas')
        .then(response => response.json())
        .then(result => {
            if (result.success && result.tiene_problemas) {
                mostrarModalSemanasProblematicas(result);
            }
        })
        .catch(error => console.error('Error validando semanas:', error));
}

function mostrarModalSemanasProblematicas(data) {
    const problemas = data.problemas;
    
    let mensaje = `<div style="text-align: left;">
        <p><strong>⚠️ Se detectaron ${problemas.length} semanas activas con problemas:</strong></p>
        <ul style="margin-top: 10px;">`;
    
    problemas.forEach(p => {
        const tipo = p.tipo === 'pasada' ? '🔴 Pasada' : '🔵 Futura';
        mensaje += `<li>
            <strong>${tipo}</strong>: Semana #${p.numero_semana} 
            (${p.fecha_inicio} - ${p.fecha_fin})
            <br><span style="font-size: 12px; color: #666;">
            ${p.tipo === 'pasada' ? 
                `Venció hace ${p.dias_diferencia} días` : 
                `Inicia en ${p.dias_diferencia} días`}
            </span>
        </li>`;
    });
    
    mensaje += `</ul>
        <p style="margin-top: 15px; font-size: 13px; color: #856404; background: #fff3cd; padding: 10px; border-radius: 4px;">
            <strong>Recomendación:</strong> ${userRol === 'admin' ? 
                'Cierra las semanas completadas para mantener el sistema organizado.' : 
                'Contacta a un administrador para cerrar estas semanas.'}
        </p>
    </div>`;
    
    showAlert('Semanas Activas Detectadas', mensaje, 'warning');
}

// ==========================================
// ✅ OCULTAR BOTONES ADMIN (NUEVO)
// ==========================================
function ocultarBotonesAdmin() {
    // Ocultar botones de eliminar y cerrar semana
    document.querySelectorAll('[onclick^="cerrarSemana"], [onclick^="eliminarSemana"]').forEach(btn => {
        btn.style.display = 'none';
    });
}



// ==========================================
// LOAD RESOURCES
// ==========================================
function loadBancos() {
    fetch('/alquiler/bancos/json')
        .then(response => response.json())
        .then(result => {
            if (result.success) {
                bancosGlobal = result.bancos;
                console.log('✅ Bancos loaded:', bancosGlobal.length);
            }
        })
        .catch(error => console.error('❌ Error loading bancos:', error));
}

function loadTiposTrabajo() {
    // Tipos de trabajo con íconos
    tiposTrabajo = [
        { id: 1, nombre: 'Reparación Mecánica', icon: '🔧' },
        { id: 2, nombre: 'Cambio de Pieza', icon: '⚙️' },
        { id: 3, nombre: 'Mantenimiento Preventivo', icon: '🛠️' },
        { id: 4, nombre: 'Ajustes', icon: '🔩' },
        { id: 5, nombre: 'Sistema Eléctrico', icon: '⚡' },
        { id: 6, nombre: 'Sistema de Frenos', icon: '🛑' },
        { id: 7, nombre: 'Suspensión', icon: '🚗' },
        { id: 8, nombre: 'Transmisión', icon: '⚙️' },
        { id: 9, nombre: 'Otros', icon: '📋' }
    ];
}

function loadMecanicos() {
    // Los mecánicos se cargan desde el backend en el template
    const mecanicosEl = document.getElementById('mecanicosList');
    if (mecanicosEl && mecanicosEl.dataset.mecanicos) {
        mecanicos = JSON.parse(mecanicosEl.dataset.mecanicos);
    }
}


// ==========================================
// TOGGLE SEMANA
// ==========================================
function toggleSemana(semanaId) {
    const item = document.querySelector(`[data-semana-id="${semanaId}"]`);
    const details = document.getElementById(`details-${semanaId}`);
    
    if (!item || !details) return;
    
    const isActive = item.classList.contains('active');
    
    if (isActive) {
        item.classList.remove('active');
        details.style.display = 'none';
    } else {
        item.classList.add('active');
        details.style.display = 'block';
        
        // ✅ CARGAR DETALLES SOLO DE ESTA SEMANA
        if (!semanasData[semanaId]) {
            loadDetallesSemana(semanaId);
        }
    }
}



// ==========================================
// LOAD DETALLES SEMANA
// ==========================================
function loadDetallesSemana(semanaId) {
    console.log('📋 Loading detalles for semana:', semanaId);
    
    const loading = document.getElementById(`loading-${semanaId}`);
    const tableWrapper = document.getElementById(`table-wrapper-${semanaId}`);
    const empty = document.getElementById(`empty-${semanaId}`);
    
    loading.style.display = 'flex';
    tableWrapper.style.display = 'none';
    empty.style.display = 'none';
    
    fetch(`/alquiler/semanas/${semanaId}/detalles`)
        .then(response => response.json())
        .then(result => {
            loading.style.display = 'none';
            
            if (result.success) {
                // ✅ ALMACENAR DATOS POR SEMANA (SEPARADOS)
                semanasData[semanaId] = {
                    detalles: result.detalles,
                    modificados: new Set(),
                    semana: result.semana
                };
                
                if (result.detalles.length > 0) {
                    renderDetallesTable(semanaId, result.detalles, result.semana);
                    tableWrapper.style.display = 'block';
                } else {
                    empty.style.display = 'flex';
                }
                
                console.log('✅ Detalles loaded:', result.detalles.length);
            } else {
                showAlert('Error', result.message, 'error');
                empty.style.display = 'flex';
            }
        })
        .catch(error => {
            console.error('❌ Error loading detalles:', error);
            loading.style.display = 'none';
            empty.style.display = 'flex';
        });
}


// ==========================================
// RENDER DETALLES TABLE
// ==========================================
function renderDetallesTable(semanaId, detalles, semana) {
    const tbody = document.getElementById(`tbody-${semanaId}`);
    tbody.innerHTML = '';
    
    let totals = {
        semanal: 0,
        ingreso: 0,
        inversion: 0,
        descuento: 0,
        nomina: 0,
        porcentaje_empresa: 0,
        deuda: 0,
        nomina2: 0
    };
    
    detalles.forEach((detalle, index) => {
        const row = document.createElement('tr');
        row.dataset.detalleId = detalle.id;
        row.dataset.index = index;
        
        // ✅ CALCULAR INVERSIONES TOTALES
        const inversionTotal = detalle.inversiones_totales || detalle.inversion_mecanica || 0;
        
        // ✅ INDICADOR DE COLOR (amarillo si inversión >= semanal)
        const inversionAlert = inversionTotal >= detalle.precio_semanal;
        const inversionClass = inversionAlert ? 'inversion-alert' : '';
        
        // Calculate values
        const ingreso = detalle.precio_semanal * detalle.dias_trabajo;
        const nominaEmpresa = ingreso * (detalle.porcentaje_empresa / 100);
        const nomina2 = ingreso + detalle.monto_deuda;
        
        // Update totals
        totals.semanal += parseFloat(detalle.precio_semanal);
        totals.ingreso += ingreso;
        totals.inversion += parseFloat(inversionTotal);
        totals.descuento += parseFloat(detalle.monto_descuento || 0);
        totals.nomina += parseFloat(detalle.nomina_empresa);
        totals.porcentaje_empresa += nominaEmpresa;
        totals.deuda += parseFloat(detalle.monto_deuda || 0);
        totals.nomina2 += nomina2;
        
        row.innerHTML = `
            <td class="sticky-col">
                <div style="display: flex; align-items: center; gap: 8px;">
                    <div style="width: 32px; height: 32px; border-radius: 50%; background: var(--bg-primary); display: flex; align-items: center; justify-content: center; font-weight: 600; font-size: 12px; color: var(--primary);">
                        ${detalle.propietario_iniciales}
                    </div>
                    <span>${detalle.propietario_nombre}</span>
                </div>
            </td>
            <td><strong>${detalle.vehiculo_marca}</strong> ${detalle.vehiculo_modelo}</td>
            <td>
                <code style="background: var(--bg-primary); padding: 4px 8px; border-radius: 4px; font-size: 12px;">
                    ${detalle.vehiculo_placa}
                </code>
            </td>
            <td><strong>${detalle.inquilino_nombre}</strong></td>
            <td>
                <a href="tel:${detalle.inquilino_telefono}" style="color: var(--primary); font-size: 12px;">
                    📞 ${detalle.inquilino_telefono}
                </a>
            </td>
            <td>
                <input type="number" 
                       class="form-input" 
                       value="${detalle.precio_semanal}" 
                       step="0.01" 
                       min="0"
                       data-field="precio_semanal"
                       onchange="updateDetalle(${semanaId}, ${index}, 'precio_semanal', this.value)"
                       style="min-width: 90px;">
            </td>
            <td>
                <input type="number" 
                       class="form-input" 
                       value="${detalle.dias_trabajo}" 
                       min="1" 
                       max="7"
                       data-field="dias_trabajo"
                       onchange="updateDetalle(${semanaId}, ${index}, 'dias_trabajo', this.value)"
                       style="width: 60px;">
            </td>
            <td class="calculated-cell">
                <span class="currency-display" data-calculated="ingreso">
                    $${formatCurrency(ingreso)}
                </span>
            </td>
            <td class="${inversionClass}" style="position: relative;">
                <div style="display: flex; align-items: center; gap: 4px;">
                    <span class="currency-display" style="color: ${inversionAlert ? '#d32f2f' : '#0a8754'};">
                        $${formatCurrency(inversionTotal)}
                    </span>
                    <button class="btn btn-xs btn-info" 
                            onclick="abrirModalInversiones(${semanaId}, ${index})"
                            style="padding: 2px 6px; font-size: 11px;">
                        ➕
                    </button>
                </div>
                ${inversionAlert ? `
                    <div style="position: absolute; top: -8px; right: -8px; background: #ff5722; color: white; border-radius: 50%; width: 20px; height: 20px; display: flex; align-items: center; justify-content: center; font-size: 12px; font-weight: bold;">
                        ⚠️
                    </div>
                ` : ''}
            </td>
            <td>
                <input type="text" 
                       class="form-input" 
                       value="${detalle.concepto_descuento || ''}" 
                       placeholder="Concepto..."
                       data-field="concepto_descuento"
                       onchange="updateDetalle(${semanaId}, ${index}, 'concepto_descuento', this.value)"
                       style="min-width: 140px;">
            </td>
            <td class="calculated-cell">
                <span class="currency-display">
                    $${formatCurrency(detalle.nomina_empresa)}
                </span>
            </td>
            <td>
                <span class="badge badge-primary">${detalle.porcentaje_empresa}%</span>
            </td>
            <td>
                <input type="number" 
                       class="form-input" 
                       value="${detalle.monto_deuda || 0}" 
                       step="0.01" 
                       min="0"
                       data-field="monto_deuda"
                       onchange="updateDetalle(${semanaId}, ${index}, 'monto_deuda', this.value)"
                       style="min-width: 90px;">
                ${detalle.tiene_deuda ? '<div class="debt-badge">⚠️ MORA</div>' : ''}
            </td>
            <td class="calculated-cell">
                <span class="currency-display" data-calculated="nomina2">
                    $${formatCurrency(nomina2)}
                </span>
            </td>
            <td>
                <select class="form-select" 
                        data-field="banco_id"
                        onchange="updateDetalle(${semanaId}, ${index}, 'banco_id', this.value)"
                        style="min-width: 140px;">
                    <option value="">Seleccionar...</option>
                    ${bancosGlobal.map(banco => `
                        <option value="${banco.id}" ${banco.id == detalle.banco_id ? 'selected' : ''}>
                            ${banco.banco}
                        </option>
                    `).join('')}
                </select>
            </td>
            <td>
                <input type="date" 
                       class="form-input" 
                       value="${detalle.fecha_confirmacion_pago || ''}"
                       data-field="fecha_confirmacion_pago"
                       onchange="updateDetalle(${semanaId}, ${index}, 'fecha_confirmacion_pago', this.value)"
                       style="min-width: 120px;">
                ${detalle.pago_confirmado ? `
                    <span class="payment-status confirmed">✓ Confirmado</span>
                ` : `
                    <span class="payment-status pending">⏱️ Pendiente</span>
                `}
            </td>
            <td>${detalle.dias_trabajo}</td>
            <td>
                <div class="action-buttons">
                    <button class="btn btn-sm btn-primary" 
                            onclick="editarDetalleCompleto(${semanaId}, ${index})" 
                            data-tooltip="Editar completo">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>
                        </svg>
                    </button>
                    <button class="btn btn-sm btn-danger" 
                            onclick="eliminarDetalle(${semanaId}, ${detalle.id}, '${detalle.inquilino_nombre}')" 
                            data-tooltip="Eliminar">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
                        </svg>
                    </button>
                </div>
            </td>
        `;
        
        tbody.appendChild(row);
    });
    
    renderFooterTotals(semanaId, totals, detalles.length);
}

// ==========================================
// ✅ MODAL DE INVERSIONES (NUEVO)
// ==========================================
function abrirModalInversiones(semanaId, index) {
    const detalle = semanasData[semanaId].detalles[index];
    if (!detalle) return;
    
    currentSemanaId = semanaId;
    currentEditingDetalleId = detalle.id;
    
    // Cargar inversiones existentes
    fetch(`/alquiler/detalles/${detalle.id}/inversiones`)
        .then(response => response.json())
        .then(result => {
            if (result.success) {
                mostrarModalInversiones(detalle, result.inversiones, result.total);
            }
        })
        .catch(error => {
            console.error('Error cargando inversiones:', error);
            showAlert('Error', 'Error al cargar inversiones', 'error');
        });
}

function mostrarModalInversiones(detalle, inversiones, total) {
    // Crear modal dinámicamente
    const modalHTML = `
        <div class="modal-overlay" id="inversionesModal" style="display: flex;">
            <div class="modal modal-lg" style="max-width: 900px;">
                <div class="modal-header">
                    <h3 class="modal-title">
                        💰 Inversiones Mecánicas - ${detalle.vehiculo_placa}
                    </h3>
                    <button class="modal-close" onclick="cerrarModalInversiones()">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
                        </svg>
                    </button>
                </div>
                <div class="modal-body">
                    <div class="alert alert-info" style="margin-bottom: 20px;">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                            <circle cx="12" cy="12" r="10"/>
                            <path d="M12 16v-4"/>
                            <path d="M12 8h.01"/>
                        </svg>
                        <div>
                            <strong>Total Invertido:</strong> $${formatCurrency(total)}
                            <br><strong>Vehículo:</strong> ${detalle.vehiculo_marca} ${detalle.vehiculo_modelo}
                            <br><strong>Precio Semanal:</strong> $${formatCurrency(detalle.precio_semanal)}
                            ${total >= detalle.precio_semanal ? 
                                '<br><span style="color: #d32f2f; font-weight: 600;">⚠️ La inversión supera el valor semanal</span>' : 
                                ''}
                        </div>
                    </div>

                    <div style="margin-bottom: 20px;">
                        <h4 style="font-size: 14px; font-weight: 600; margin-bottom: 10px;">
                            📋 Inversiones Registradas
                        </h4>
                        <div class="inversiones-table-wrapper" style="max-height: 300px; overflow-y: auto;">
                            <table class="table" style="font-size: 13px;">
                                <thead>
                                    <tr>
                                        <th>Fecha</th>
                                        <th>Tipo</th>
                                        <th>Mecánico</th>
                                        <th>Descripción</th>
                                        <th>Tipo Inv.</th>
                                        <th>Costo</th>
                                    </tr>
                                </thead>
                                <tbody id="inversionesListBody">
                                    ${inversiones.length > 0 ? 
                                        inversiones.map(inv => `
                                            <tr>
                                                <td>${inv.fecha}</td>
                                                <td>${inv.tipo_trabajo}</td>
                                                <td>${inv.mecanico}</td>
                                                <td>${inv.descripcion}</td>
                                                <td><span class="badge badge-${inv.tipo_inversion === 'falla_mecanica' ? 'warning' : 'danger'}">${inv.tipo_inversion}</span></td>
                                                <td><strong>$${formatCurrency(inv.costo)}</strong></td>
                                            </tr>
                                        `).join('') : 
                                        '<tr><td colspan="6" style="text-align: center; padding: 20px; color: #999;">No hay inversiones registradas</td></tr>'
                                    }
                                </tbody>
                            </table>
                        </div>
                    </div>

                    <div style="border-top: 2px solid var(--border-color); padding-top: 20px;">
                        <h4 style="font-size: 14px; font-weight: 600; margin-bottom: 15px;">
                            ➕ Agregar Nueva Inversión
                        </h4>
                        <form id="nuevaInversionForm">
                            <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px;">
                                <div class="form-group">
                                    <label class="form-label required">Tipo de Trabajo</label>
                                    <select name="tipo_trabajo_id" class="form-select" required>
                                        <option value="">Seleccionar tipo...</option>
                                        ${tiposTrabajo.map(tipo => `
                                            <option value="${tipo.id}">${tipo.icon} ${tipo.nombre}</option>
                                        `).join('')}
                                    </select>
                                </div>

                                <div class="form-group">
                                    <label class="form-label required">Mecánico</label>
                                    <select name="mecanico_id" class="form-select" required>
                                        <option value="">Seleccionar mecánico...</option>
                                        ${mecanicos.map(mec => `
                                            <option value="${mec.id}">${mec.nombre}</option>
                                        `).join('')}
                                    </select>
                                </div>

                                <div class="form-group">
                                    <label class="form-label required">Tipo de Inversión</label>
                                    <select name="tipo_inversion" class="form-select" required>
                                        <option value="">Seleccionar...</option>
                                        <option value="falla_mecanica">🔧 Falla Mecánica</option>
                                        <option value="accidente">💥 Accidente</option>
                                    </select>
                                </div>

                                <div class="form-group">
                                    <label class="form-label required">Costo</label>
                                    <input type="number" name="costo" class="form-input" step="0.01" min="0" required placeholder="0.00">
                                </div>

                                <div class="form-group" style="grid-column: 1 / -1;">
                                    <label class="form-label required">Descripción/Concepto</label>
                                    <textarea name="descripcion" class="form-textarea" rows="2" required placeholder="Ej: Cambio de aceite y filtros"></textarea>
                                </div>
                            </div>
                        </form>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" onclick="cerrarModalInversiones()">Cerrar</button>
                    <button type="button" class="btn btn-primary" onclick="guardarNuevaInversion()">
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
                        </svg>
                        Guardar Inversión
                    </button>
                </div>
            </div>
        </div>
    `;
    
    // Insertar modal en el DOM
    document.body.insertAdjacentHTML('beforeend', modalHTML);
}

function cerrarModalInversiones() {
    const modal = document.getElementById('inversionesModal');
    if (modal) {
        modal.remove();
    }
}

function guardarNuevaInversion() {
    const form = document.getElementById('nuevaInversionForm');
    const formData = new FormData(form);
    
    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }
    
    const data = {
        detalle_id: currentEditingDetalleId,
        tipo_trabajo_id: formData.get('tipo_trabajo_id'),
        mecanico_id: formData.get('mecanico_id'),
        tipo_inversion: formData.get('tipo_inversion'),
        descripcion: formData.get('descripcion'),
        costo: formData.get('costo')
    };
    
    fetch('/alquiler/inversiones/crear', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(result => {
        if (result.success) {
            showAlert('Éxito', 'Inversión registrada correctamente', 'success');
            cerrarModalInversiones();
            
            // Recargar detalles
            delete semanasData[currentSemanaId];
            loadDetallesSemana(currentSemanaId);
        } else {
            showAlert('Error', result.message, 'error');
        }
    })
    .catch(error => {
        console.error('Error guardando inversión:', error);
        showAlert('Error', 'Error al guardar inversión', 'error');
    });
}


// ==========================================
// RENDER FOOTER TOTALS
// ==========================================
function renderFooterTotals(semanaId, totals, count) {
    const tfoot = document.getElementById(`tfoot-${semanaId}`);
    tfoot.innerHTML = `
        <tr>
            <td class="sticky-col"><strong>TOTALES (${count})</strong></td>
            <td colspan="4"></td>
            <td class="total-value">$${formatCurrency(totals.semanal)}</td>
            <td></td>
            <td class="total-value">$${formatCurrency(totals.ingreso)}</td>
            <td class="total-value">$${formatCurrency(totals.inversion)}</td>
            <td></td>
            <td class="total-value">$${formatCurrency(totals.nomina)}</td>
            <td class="total-value">$${formatCurrency(totals.porcentaje_empresa)}</td>
            <td class="total-value">$${formatCurrency(totals.deuda)}</td>
            <td class="total-value">$${formatCurrency(totals.nomina2)}</td>
            <td colspan="4"></td>
        </tr>
    `;
}

// ==========================================
// CERRAR SEMANA (CON VALIDACIÓN ADMIN)
// ==========================================
function cerrarSemana(semanaId) {
    if (userRol !== 'admin') {
        showAlert('Acceso Denegado', 'Solo los administradores pueden cerrar semanas', 'error');
        return;
    }
    
    showConfirm(
        '¿Cerrar Semana?',
        'Una vez cerrada, no podrás modificar los datos.',
        function() {
            fetch(`/alquiler/semanas/${semanaId}/cerrar`, {
                method: 'POST'
            })
            .then(response => response.json())
            .then(result => {
                if (result.success) {
                    showAlert('Éxito', 'Semana cerrada', 'success');
                    setTimeout(() => window.location.reload(), 1500);
                } else {
                    showAlert('Error', result.message, 'error');
                }
            })
            .catch(error => {
                console.error('❌ Error:', error);
                showAlert('Error', 'Error al cerrar semana', 'error');
            });
        }
    );
}

// ==========================================
// ELIMINAR SEMANA (CON VALIDACIÓN ADMIN)
// ==========================================
function eliminarSemana(semanaId, totalVehiculos) {
    if (userRol !== 'admin') {
        showAlert('Acceso Denegado', 'Solo los administradores pueden eliminar semanas', 'error');
        return;
    }
    
    let message = totalVehiculos > 0 
        ? `Esta semana tiene ${totalVehiculos} alquileres. ¿Deseas eliminarla?`
        : 'Esta semana está vacía. ¿Deseas eliminarla?';
    
    showConfirm(
        '¿Eliminar Semana?',
        message,
        function() {
            fetch(`/alquiler/semanas/${semanaId}/eliminar`, {
                method: 'POST'
            })
            .then(response => response.json())
            .then(result => {
                if (result.success) {
                    showAlert('Éxito', 'Semana eliminada', 'success');
                    setTimeout(() => window.location.reload(), 1500);
                } else {
                    showAlert('Error', result.message, 'error');
                }
            })
            .catch(error => {
                console.error('❌ Error:', error);
                showAlert('Error', 'Error al eliminar semana', 'error');
            });
        }
    );
}

// ==========================================
// UTILITY
// ==========================================
function formatCurrency(value) {
    return parseFloat(value || 0).toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',');
}

// ==========================================
// UPDATE DETALLE (INLINE EDIT)
// ==========================================
function updateDetalle(semanaId, index, field, value) {
    if (!semanasData[semanaId]) return;
    
    const detalles = semanasData[semanaId].detalles;
    if (!detalles[index]) return;
    
    // Update value
    detalles[index][field] = value;
    
    // Mark as modified
    semanasData[semanaId].modificados.add(detalles[index].id);
    
    // Mark row visually
    const row = document.querySelector(`[data-detalle-id="${detalles[index].id}"]`);
    if (row) row.classList.add('modified-row');
    
    // Recalculate if necessary
    if (field === 'precio_semanal' || field === 'dias_trabajo' || field === 'monto_deuda') {
        recalcularFila(semanaId, index);
    }
    
    console.log('✏️ Updated:', field, '=', value, 'for detalle', detalles[index].id);
}

// ==========================================
// RECALCULAR FILA
// ==========================================
function recalcularFila(semanaId, index) {
    const detalle = semanasData[semanaId].detalles[index];
    if (!detalle) return;
    
    const row = document.querySelector(`[data-detalle-id="${detalle.id}"]`);
    if (!row) return;
    
    // Calculate
    const ingreso = parseFloat(detalle.precio_semanal) * parseInt(detalle.dias_trabajo);
    const nominaEmpresa = ingreso * (parseFloat(detalle.porcentaje_empresa) / 100);
    const nomina2 = ingreso + parseFloat(detalle.monto_deuda || 0);
    
    // Update calculated cells
    const ingresoCell = row.querySelector('[data-calculated="ingreso"]');
    const nomina2Cell = row.querySelector('[data-calculated="nomina2"]');
    
    if (ingresoCell) ingresoCell.textContent = `$${formatCurrency(ingreso)}`;
    if (nomina2Cell) nomina2Cell.textContent = `$${formatCurrency(nomina2)}`;
    
    // Update data
    detalle.ingreso_calculado = ingreso;
    detalle.nomina_empresa = nominaEmpresa;
    detalle.nomina_final = nomina2;
    
    // Recalculate totals
    recalcularTotales(semanaId);
}

// ==========================================
// RECALCULAR TOTALES
// ==========================================
function recalcularTotales(semanaId) {
    const detalles = semanasData[semanaId].detalles;
    
    let totals = {
        semanal: 0,
        ingreso: 0,
        inversion: 0,
        descuento: 0,
        nomina: 0,
        porcentaje_empresa: 0,
        deuda: 0,
        nomina2: 0
    };
    
    detalles.forEach(detalle => {
        totals.semanal += parseFloat(detalle.precio_semanal);
        totals.ingreso += parseFloat(detalle.ingreso_calculado || 0);
        totals.inversion += parseFloat(detalle.inversion_mecanica || 0);
        totals.descuento += parseFloat(detalle.monto_descuento || 0);
        totals.nomina += parseFloat(detalle.nomina_empresa || 0);
        totals.deuda += parseFloat(detalle.monto_deuda || 0);
        totals.nomina2 += parseFloat(detalle.nomina_final || 0);
    });
    
    renderFooterTotals(semanaId, totals, detalles.length);
}

// ==========================================
// EDITAR DETALLE COMPLETO (MODAL)
// ==========================================
// ==========================================
// EDITAR DETALLE COMPLETO (VERSIÓN MEJORADA)
// ==========================================
function editarDetalleCompleto(semanaId, index) {
    const detalle = semanasData[semanaId].detalles[index];
    if (!detalle) return;
    
    currentSemanaId = semanaId;
    currentEditingDetalleId = detalle.id;
    
    // Store original values for comparison
    window.originalDetalleValues = {
        vehiculo_id: detalle.vehiculo_id,
        inquilino_id: detalle.inquilino_id
    };
    
    // Fill form
    const form = document.getElementById('editarDetalleForm');
    document.getElementById('editDetalleId').value = detalle.id;
    form.querySelector('[name="precio_semanal"]').value = detalle.precio_semanal;
    form.querySelector('[name="dias_trabajo"]').value = detalle.dias_trabajo;
    form.querySelector('[name="inversion_mecanica"]').value = detalle.inversion_mecanica || 0;
    form.querySelector('[name="concepto_inversion"]').value = detalle.concepto_inversion || '';
    form.querySelector('[name="monto_descuento"]').value = detalle.monto_descuento || 0;
    form.querySelector('[name="concepto_descuento"]').value = detalle.concepto_descuento || '';
    form.querySelector('[name="monto_deuda"]').value = detalle.monto_deuda || 0;
    form.querySelector('[name="banco_id"]').value = detalle.banco_id || '';
    form.querySelector('[name="fecha_confirmacion_pago"]').value = detalle.fecha_confirmacion_pago || '';
    form.querySelector('[name="pago_confirmado"]').checked = detalle.pago_confirmado || false;
    form.querySelector('[name="notas"]').value = detalle.notas || '';
    
    // Load vehículos and inquilinos disponibles (including current ones)
    loadEditVehiculosSelect(semanaId, detalle.vehiculo_id);
    loadEditInquilinosSelect(semanaId, detalle.inquilino_id);
    
    // Open modal
    window.AppUtils.openModal('editarDetalleModal');
    
    console.log('📝 Editing detalle completo:', detalle.id);
}

// ==========================================
// LOAD VEHÍCULOS FOR EDIT (including current)
// ==========================================
function loadEditVehiculosSelect(semanaId, currentVehiculoId) {
    const select = document.getElementById('editVehiculoSelect');
    select.innerHTML = '<option value="">Cargando...</option>';
    
    fetch(`/alquiler/semanas/${semanaId}/disponibles`)
        .then(response => response.json())
        .then(result => {
            if (result.success) {
                select.innerHTML = '<option value="">Seleccionar vehículo...</option>';
                
                // Add current vehicle first (if exists)
                const currentIndex = result.vehiculos.findIndex(v => v.id === currentVehiculoId);
                if (currentIndex === -1 && currentVehiculoId) {
                    // Current vehicle not in available list, fetch it separately
                    // For now, we'll trust it's in the DB
                }
                
                result.vehiculos.forEach(veh => {
                    const option = document.createElement('option');
                    option.value = veh.id;
                    option.textContent = `${veh.placa} - ${veh.marca} ${veh.modelo} ${veh.ano || ''} ${veh.color || ''} - $${formatCurrency(veh.precio_semanal)}`;
                    option.dataset.vehiculo = JSON.stringify(veh);
                    
                    if (veh.id === currentVehiculoId) {
                        option.selected = true;
                    }
                    
                    select.appendChild(option);
                });
                
                // If current vehicle ID provided but not in list, add it
                if (currentVehiculoId && !select.querySelector(`option[value="${currentVehiculoId}"]`)) {
                    // Fetch current vehicle data
                    const currentDetalle = semanasData[semanaId].detalles.find(d => d.vehiculo_id === currentVehiculoId);
                    if (currentDetalle) {
                        const option = document.createElement('option');
                        option.value = currentVehiculoId;
                        option.textContent = `${currentDetalle.vehiculo_placa} - ${currentDetalle.vehiculo_marca} ${currentDetalle.vehiculo_modelo} (Actual)`;
                        option.selected = true;
                        select.insertBefore(option, select.firstChild.nextSibling);
                    }
                }
                
                // Add change listener
                select.addEventListener('change', showEditPreview);
            }
        })
        .catch(error => {
            console.error('Error loading vehiculos:', error);
            select.innerHTML = '<option value="">Error al cargar</option>';
        });
}

// ==========================================
// LOAD INQUILINOS FOR EDIT (including current)
// ==========================================
function loadEditInquilinosSelect(semanaId, currentInquilinoId) {
    const select = document.getElementById('editInquilinoSelect');
    select.innerHTML = '<option value="">Cargando...</option>';
    
    fetch(`/alquiler/semanas/${semanaId}/disponibles`)
        .then(response => response.json())
        .then(result => {
            if (result.success) {
                select.innerHTML = '<option value="">Seleccionar inquilino...</option>';
                
                result.inquilinos.forEach(inq => {
                    const option = document.createElement('option');
                    option.value = inq.id;
                    option.textContent = `${inq.nombre_apellido}${inq.telefono ? ' - ' + inq.telefono : ''}`;
                    option.dataset.inquilino = JSON.stringify(inq);
                    
                    if (inq.id === currentInquilinoId) {
                        option.selected = true;
                    }
                    
                    select.appendChild(option);
                });
                
                // If current inquilino ID provided but not in list, add it
                if (currentInquilinoId && !select.querySelector(`option[value="${currentInquilinoId}"]`)) {
                    const currentDetalle = semanasData[semanaId].detalles.find(d => d.inquilino_id === currentInquilinoId);
                    if (currentDetalle) {
                        const option = document.createElement('option');
                        option.value = currentInquilinoId;
                        option.textContent = `${currentDetalle.inquilino_nombre} (Actual)`;
                        option.selected = true;
                        select.insertBefore(option, select.firstChild.nextSibling);
                    }
                }
                
                // Add change listener
                select.addEventListener('change', showEditPreview);
            }
        })
        .catch(error => {
            console.error('Error loading inquilinos:', error);
            select.innerHTML = '<option value="">Error al cargar</option>';
        });
}

// ==========================================
// SHOW EDIT PREVIEW
// ==========================================
function showEditPreview() {
    const vehiculoSelect = document.getElementById('editVehiculoSelect');
    const inquilinoSelect = document.getElementById('editInquilinoSelect');
    const preview = document.getElementById('editPreview');
    const previewList = document.getElementById('editPreviewList');
    
    const changes = [];
    
    // Check vehicle change
    if (vehiculoSelect.value && vehiculoSelect.value != window.originalDetalleValues.vehiculo_id) {
        const option = vehiculoSelect.selectedOptions[0];
        changes.push(`<li>Vehículo cambiado a: <strong>${option.textContent}</strong></li>`);
    }
    
    // Check inquilino change
    if (inquilinoSelect.value && inquilinoSelect.value != window.originalDetalleValues.inquilino_id) {
        const option = inquilinoSelect.selectedOptions[0];
        changes.push(`<li>Inquilino cambiado a: <strong>${option.textContent}</strong></li>`);
    }
    
    if (changes.length > 0) {
        previewList.innerHTML = changes.join('');
        preview.style.display = 'block';
    } else {
        preview.style.display = 'none';
    }
}

// ==========================================
// SETUP EDITAR DETALLE FORM (VERSIÓN MEJORADA)
// ==========================================
function setupEditarDetalleForm() {
    const form = document.getElementById('editarDetalleForm');
    if (!form) return;
    
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        if (!currentSemanaId || !currentEditingDetalleId) return;
        
        const formData = new FormData(this);
        const data = {
            vehiculo_id: formData.get('vehiculo_id'),
            inquilino_id: formData.get('inquilino_id'),
            precio_semanal: formData.get('precio_semanal'),
            dias_trabajo: formData.get('dias_trabajo'),
            inversion_mecanica: formData.get('inversion_mecanica'),
            concepto_inversion: formData.get('concepto_inversion'),
            monto_descuento: formData.get('monto_descuento'),
            concepto_descuento: formData.get('concepto_descuento'),
            monto_deuda: formData.get('monto_deuda'),
            banco_id: formData.get('banco_id'),
            fecha_confirmacion_pago: formData.get('fecha_confirmacion_pago'),
            pago_confirmado: this.querySelector('[name="pago_confirmado"]').checked,
            notas: formData.get('notas')
        };
        
        // Disable submit
        const submitBtn = form.querySelector('[type="submit"]');
        submitBtn.disabled = true;
        submitBtn.innerHTML = `
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" style="animation: spin 1s linear infinite;">
                <circle cx="12" cy="12" r="10" stroke-width="3" stroke-dasharray="32"/>
            </svg>
            Guardando...
        `;
        
        fetch(`/alquiler/detalles/${currentEditingDetalleId}/editar-completo`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(result => {
            if (result.success) {
                window.AppUtils.closeModal('editarDetalleModal');
                
                // Reload detalles
                delete semanasData[currentSemanaId];
                loadDetallesSemana(currentSemanaId);
                
                showAlert('Éxito', 'Detalle actualizado correctamente', 'success');
            } else {
                showAlert('Error', result.message, 'error');
            }
        })
        .catch(error => {
            console.error('❌ Error saving:', error);
            showAlert('Error', 'Error al guardar cambios', 'error');
        })
        .finally(() => {
            submitBtn.disabled = false;
            submitBtn.innerHTML = `
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
                </svg>
                Guardar Cambios
            `;
        });
    });
}
// ==========================================
// GUARDAR CAMBIOS SEMANA
// ==========================================
function guardarCambiosSemana(semanaId) {
    if (!semanasData[semanaId]) {
        showAlert('Error', 'No hay datos cargados para esta semana', 'error');
        return;
    }
    
    const modificados = semanasData[semanaId].modificados;
    
    if (modificados.size === 0) {
        showAlert('Sin cambios', 'No hay modificaciones para guardar', 'info');
        return;
    }
    
    console.log('💾 Saving', modificados.size, 'changes for semana', semanaId);
    
    // Prepare data
    const detalles = semanasData[semanaId].detalles;
    const cambios = detalles
        .filter(d => modificados.has(d.id))
        .map(d => ({
            id: d.id,
            precio_semanal: d.precio_semanal,
            dias_trabajo: d.dias_trabajo,
            inversion_mecanica: d.inversion_mecanica,
            concepto_inversion: d.concepto_inversion,
            monto_descuento: d.monto_descuento,
            concepto_descuento: d.concepto_descuento,
            monto_deuda: d.monto_deuda,
            banco_id: d.banco_id,
            fecha_confirmacion_pago: d.fecha_confirmacion_pago,
            pago_confirmado: d.pago_confirmado,
            notas: d.notas
        }));
    
    // Send to server
    fetch(`/alquiler/semanas/${semanaId}/guardar-cambios`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ cambios })
    })
    .then(response => response.json())
    .then(result => {
        if (result.success) {
            modificados.clear();
            
            // Remove modified class from rows
            document.querySelectorAll('.modified-row').forEach(row => {
                row.classList.remove('modified-row');
            });
            
            showAlert('Éxito', `${result.updated} detalles guardados`, 'success');
            console.log('✅ Changes saved');
        } else {
            showAlert('Error', result.message, 'error');
        }
    })
    .catch(error => {
        console.error('❌ Error saving:', error);
        showAlert('Error', 'Error al guardar cambios', 'error');
    });
}




// ==========================================
// ELIMINAR DETALLE
// ==========================================
function eliminarDetalle(semanaId, detalleId, inquilinoNombre) {
    showConfirm(
        '¿Eliminar Alquiler?',
        `El alquiler de "${inquilinoNombre}" será eliminado de esta semana.`,
        function() {
            fetch(`/alquiler/detalles/${detalleId}/eliminar`, {
                method: 'POST'
            })
            .then(response => response.json())
            .then(result => {
                if (result.success) {
                    // Reload detalles
                    delete semanasData[semanaId];
                    loadDetallesSemana(semanaId);
                    showAlert('Éxito', 'Alquiler eliminado', 'success');
                } else {
                    showAlert('Error', result.message, 'error');
                }
            })
            .catch(error => {
                console.error('❌ Error deleting:', error);
                showAlert('Error', 'Error al eliminar', 'error');
            });
        }
    );
}

// ==========================================
// CERRAR SEMANA
// ==========================================
function cerrarSemana(semanaId) {
    showConfirm(
        '¿Cerrar Semana?',
        'Una vez cerrada, no podrás modificar los datos.',
        function() {
            fetch(`/alquiler/semanas/${semanaId}/cerrar`, {
                method: 'POST'
            })
            .then(response => response.json())
            .then(result => {
                if (result.success) {
                    showAlert('Éxito', 'Semana cerrada', 'success');
                    setTimeout(() => window.location.reload(), 1500);
                } else {
                    showAlert('Error', result.message, 'error');
                }
            })
            .catch(error => {
                console.error('❌ Error:', error);
                showAlert('Error', 'Error al cerrar semana', 'error');
            });
        }
    );
}

// ==========================================
// EXPORTAR EXCEL
// ==========================================
function exportarExcelSemana(semanaId) {
    window.location.href = `/alquiler/semanas/${semanaId}/exportar-excel`;
    showAlert('Procesando', 'Generando archivo Excel...', 'info');
}

// ==========================================
// FILTRAR SEMANAS
// ==========================================
function filtrarSemanas() {
    const filtro = document.getElementById('filtroEstado').value;
    const items = document.querySelectorAll('.semana-accordion-item');
    
    items.forEach(item => {
        const estado = item.dataset.estado;
        item.style.display = (!filtro || estado === filtro) ? '' : 'none';
    });
    
    console.log('🔍 Filtered by:', filtro);
}

// ==========================================
// CREAR SEMANA MODAL
// ==========================================
function openCrearSemanaModal() {
    const today = new Date();
    const monday = new Date(today);
    monday.setDate(today.getDate() - today.getDay() + 1);
    
    const sunday = new Date(monday);
    sunday.setDate(monday.getDate() + 6);
    
    const fechaInicio = document.querySelector('[name="fecha_inicio"]');
    const fechaFin = document.querySelector('[name="fecha_fin"]');
    
    if (fechaInicio) fechaInicio.valueAsDate = monday;
    if (fechaFin) fechaFin.valueAsDate = sunday;
    
    window.AppUtils.openModal('crearSemanaModal');
}
// ==========================================
// AGREGAR ALQUILER (VERSION CORREGIDA CON DEBUG)
// ==========================================
function agregarAlquiler(semanaId) {
    console.log('📋 Opening agregar alquiler for semana:', semanaId);
    
    currentSemanaId = semanaId;
    document.getElementById('agregarAlquilerSemanaId').value = semanaId;
    
    // Reset form
    const vehiculoSelect = document.getElementById('vehiculoSelect');
    const inquilinoSelect = document.getElementById('inquilinoSelect');
    const preview = document.getElementById('alquilerPreview');
    
    if (!vehiculoSelect || !inquilinoSelect) {
        console.error('❌ ERROR: No se encontraron los selects en el DOM');
        showAlert('Error', 'Error en la interfaz del formulario', 'error');
        return;
    }
    
    vehiculoSelect.innerHTML = '<option value="">Cargando vehículos...</option>';
    inquilinoSelect.innerHTML = '<option value="">Cargando inquilinos...</option>';
    
    if (preview) {
        preview.style.display = 'none';
    }
    
    // Open modal
    window.AppUtils.openModal('agregarAlquilerModal');
    
    // Load available vehiculos and inquilinos
    const url = `/alquiler/semanas/${semanaId}/disponibles`;
    console.log('🌐 Fetching from:', url);
    
    fetch(url)
        .then(response => {
            console.log('📡 Response status:', response.status);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(result => {
            console.log('📦 Response data:', result);
            
            if (result.success) {
                console.log('✅ Success! Vehículos:', result.vehiculos.length, 'Inquilinos:', result.inquilinos.length);
                loadVehiculosSelect(result.vehiculos);
                loadInquilinosSelect(result.inquilinos);
            } else {
                console.error('❌ Server returned success=false:', result.message);
                showAlert('Error', result.message, 'error');
                vehiculoSelect.innerHTML = '<option value="">Error al cargar</option>';
                inquilinoSelect.innerHTML = '<option value="">Error al cargar</option>';
            }
        })
        .catch(error => {
            console.error('❌ Error loading disponibles:', error);
            showAlert('Error', `Error al cargar datos: ${error.message}`, 'error');
            vehiculoSelect.innerHTML = '<option value="">Error de conexión</option>';
            inquilinoSelect.innerHTML = '<option value="">Error de conexión</option>';
        });
}

// ==========================================
// LOAD VEHICULOS SELECT (CON DEBUG)
// ==========================================
function loadVehiculosSelect(vehiculos) {
    console.log('🚗 Loading vehículos select:', vehiculos);
    
    const select = document.getElementById('vehiculoSelect');
    
    if (!select) {
        console.error('❌ ERROR: vehiculoSelect not found in DOM!');
        return;
    }
    
    if (!vehiculos || vehiculos.length === 0) {
        console.warn('⚠️ No hay vehículos disponibles');
        select.innerHTML = '<option value="">No hay vehículos disponibles</option>';
        return;
    }
    
    select.innerHTML = '<option value="">Seleccionar vehículo...</option>';
    
    vehiculos.forEach((veh, index) => {
        try {
            const option = document.createElement('option');
            option.value = veh.id;
            
            // Build display text
            const displayText = `${veh.placa || 'N/A'} - ${veh.marca || ''} ${veh.modelo || ''} ${veh.ano || ''} ${veh.color || ''} - $${formatCurrency(veh.precio_semanal)}`.trim();
            
            option.textContent = displayText;
            option.dataset.vehiculo = JSON.stringify(veh);
            select.appendChild(option);
            
            console.log(`  ✓ Added vehicle ${index + 1}:`, displayText);
        } catch (error) {
            console.error(`❌ Error adding vehicle ${veh.id}:`, error);
        }
    });
    
    console.log(`✅ Total vehículos en select: ${select.options.length - 1}`);
    
    // Add change listener (remove previous ones first)
    const newSelect = select.cloneNode(true);
    select.parentNode.replaceChild(newSelect, select);
    newSelect.addEventListener('change', updatePreview);
}

// ==========================================
// LOAD INQUILINOS SELECT (CON DEBUG)
// ==========================================
function loadInquilinosSelect(inquilinos) {
    console.log('👥 Loading inquilinos select:', inquilinos);
    
    const select = document.getElementById('inquilinoSelect');
    
    if (!select) {
        console.error('❌ ERROR: inquilinoSelect not found in DOM!');
        return;
    }
    
    if (!inquilinos || inquilinos.length === 0) {
        console.warn('⚠️ No hay inquilinos disponibles');
        select.innerHTML = '<option value="">No hay inquilinos disponibles</option>';
        return;
    }
    
    select.innerHTML = '<option value="">Seleccionar inquilino...</option>';
    
    inquilinos.forEach((inq, index) => {
        try {
            const option = document.createElement('option');
            option.value = inq.id;
            
            const displayText = `${inq.nombre_apellido}${inq.telefono ? ' - ' + inq.telefono : ''}`;
            
            option.textContent = displayText;
            option.dataset.inquilino = JSON.stringify(inq);
            select.appendChild(option);
            
            console.log(`  ✓ Added inquilino ${index + 1}:`, displayText);
        } catch (error) {
            console.error(`❌ Error adding inquilino ${inq.id}:`, error);
        }
    });
    
    console.log(`✅ Total inquilinos en select: ${select.options.length - 1}`);
    
    // Add change listener (remove previous ones first)
    const newSelect = select.cloneNode(true);
    select.parentNode.replaceChild(newSelect, select);
    newSelect.addEventListener('change', updatePreview);
}

// ==========================================
// UPDATE PREVIEW (SIMPLIFICADO)
// ==========================================
function updatePreview() {
    const vehiculoSelect = document.getElementById('vehiculoSelect');
    const inquilinoSelect = document.getElementById('inquilinoSelect');
    const preview = document.getElementById('alquilerPreview');
    
    if (!vehiculoSelect || !inquilinoSelect || !preview) {
        return;
    }
    
    const vehiculoOption = vehiculoSelect.selectedOptions[0];
    const inquilinoOption = inquilinoSelect.selectedOptions[0];
    
    if (!vehiculoOption || !vehiculoOption.value || !inquilinoOption || !inquilinoOption.value) {
        preview.style.display = 'none';
        return;
    }
    
    try {
        const vehiculo = JSON.parse(vehiculoOption.dataset.vehiculo);
        const inquilino = JSON.parse(inquilinoOption.dataset.inquilino);
        
        document.getElementById('previewVehiculo').textContent = 
            `${vehiculo.placa} - ${vehiculo.marca} ${vehiculo.modelo}`;
        document.getElementById('previewPrecio').textContent = 
            `$${formatCurrency(vehiculo.precio_semanal)}`;
        document.getElementById('previewInquilino').textContent = 
            inquilino.nombre_apellido;
        document.getElementById('previewPropietario').textContent = 
            vehiculo.propietario_nombre || 'N/A';
        
        preview.style.display = 'block';
    } catch (error) {
        console.error('Error updating preview:', error);
        preview.style.display = 'none';
    }
}

// ==========================================
// RENDER ALQUILERES LIST (CARD STYLE)
// ==========================================
function renderAlquileresList(alquileres) {
    const container = document.getElementById('alquileresList');
    
    if (!alquileres || alquileres.length === 0) {
        showEmptyAlquileres('No hay alquileres disponibles para agregar a esta semana');
        return;
    }
    
    // Store alquileres for search
    window.alquileresData = alquileres;
    
    container.innerHTML = '';
    
    alquileres.forEach(alq => {
        const card = createAlquilerCard(alq);
        container.appendChild(card);
    });
}

// ==========================================
// CREATE ALQUILER CARD
// ==========================================
function createAlquilerCard(alquiler) {
    const card = document.createElement('div');
    card.className = 'alquiler-card';
    card.dataset.alquilerId = alquiler.id;
    card.dataset.searchText = `${alquiler.vehiculo_placa} ${alquiler.vehiculo_marca} ${alquiler.vehiculo_modelo} ${alquiler.inquilino_nombre}`.toLowerCase();
    
    card.innerHTML = `
        <div class="alquiler-icon">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="white">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4"/>
            </svg>
        </div>
        
        <div class="alquiler-info">
            <div class="alquiler-primary">
                <div class="alquiler-placa">${alquiler.vehiculo_placa}</div>
                <div class="alquiler-vehiculo">${alquiler.vehiculo_marca} ${alquiler.vehiculo_modelo}</div>
            </div>
            <div class="alquiler-secondary">
                <div class="alquiler-detail">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/>
                    </svg>
                    <span>${alquiler.inquilino_nombre}</span>
                </div>
                ${alquiler.propietario_nombre ? `
                <div class="alquiler-detail">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/>
                    </svg>
                    <span>${alquiler.propietario_nombre}</span>
                </div>
                ` : ''}
            </div>
        </div>
        
        <div class="alquiler-price">
            <div class="alquiler-price-value">$${formatCurrency(alquiler.precio_semanal)}</div>
            <div class="alquiler-price-label">Semanal</div>
        </div>
    `;
    
    // Click handler
    card.addEventListener('click', function() {
        selectAlquiler(alquiler.id);
    });
    
    return card;
}

// ==========================================
// SELECT ALQUILER
// ==========================================
function selectAlquiler(alquilerId) {
    // Remove previous selection
    document.querySelectorAll('.alquiler-card').forEach(card => {
        card.classList.remove('selected');
    });
    
    // Add selection to clicked card
    const card = document.querySelector(`[data-alquiler-id="${alquilerId}"]`);
    if (card) {
        card.classList.add('selected');
    }
    
    // Set hidden input
    document.getElementById('selectedAlquilerId').value = alquilerId;
    
    // Enable submit button
    document.getElementById('agregarAlquilerSubmit').disabled = false;
    
    console.log('✅ Alquiler selected:', alquilerId);
}

// ==========================================
// SEARCH ALQUILERES
// ==========================================
function setupAlquilerSearch() {
    const searchInput = document.getElementById('searchAlquilerInput');
    if (!searchInput) return;
    
    searchInput.addEventListener('input', function(e) {
        const searchTerm = e.target.value.toLowerCase().trim();
        const cards = document.querySelectorAll('.alquiler-card');
        
        if (!searchTerm) {
            // Show all cards
            cards.forEach(card => {
                card.style.display = '';
                // Remove highlights
                card.querySelectorAll('.search-highlight').forEach(el => {
                    el.outerHTML = el.textContent;
                });
            });
            return;
        }
        
        // Filter and highlight
        cards.forEach(card => {
            const searchText = card.dataset.searchText;
            
            if (searchText.includes(searchTerm)) {
                card.style.display = '';
                
                // Highlight matching text
                highlightSearchTerm(card, searchTerm);
            } else {
                card.style.display = 'none';
            }
        });
        
        // Check if any visible
        const visibleCards = Array.from(cards).filter(card => card.style.display !== 'none');
        if (visibleCards.length === 0) {
            showEmptyAlquileres('No se encontraron alquileres que coincidan con la búsqueda');
        }
    });
}

// ==========================================
// HIGHLIGHT SEARCH TERM
// ==========================================
function highlightSearchTerm(card, term) {
    // Reset previous highlights
    card.querySelectorAll('.search-highlight').forEach(el => {
        el.outerHTML = el.textContent;
    });
    
    // Highlight in placa
    const placaEl = card.querySelector('.alquiler-placa');
    if (placaEl) {
        highlightInElement(placaEl, term);
    }
    
    // Highlight in vehiculo
    const vehiculoEl = card.querySelector('.alquiler-vehiculo');
    if (vehiculoEl) {
        highlightInElement(vehiculoEl, term);
    }
    
    // Highlight in inquilino
    const inquilinoEl = card.querySelector('.alquiler-secondary span');
    if (inquilinoEl) {
        highlightInElement(inquilinoEl, term);
    }
}

function highlightInElement(element, term) {
    const text = element.textContent;
    const regex = new RegExp(`(${escapeRegex(term)})`, 'gi');
    const highlighted = text.replace(regex, '<span class="search-highlight">$1</span>');
    element.innerHTML = highlighted;
}

function escapeRegex(str) {
    return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

// ==========================================
// SHOW EMPTY STATE
// ==========================================
function showEmptyAlquileres(message) {
    const container = document.getElementById('alquileresList');
    container.innerHTML = `
        <div class="alquileres-empty">
            <svg width="60" height="60" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
            </svg>
            <p>${message}</p>
        </div>
    `;
}

// ==========================================
// UPDATE PREVIEW
// ==========================================
function updatePreview() {
    const vehiculoSelect = document.getElementById('vehiculoSelect');
    const inquilinoSelect = document.getElementById('inquilinoSelect');
    const preview = document.getElementById('alquilerPreview');
    
    const vehiculoOption = vehiculoSelect.selectedOptions[0];
    const inquilinoOption = inquilinoSelect.selectedOptions[0];
    
    if (!vehiculoOption || !vehiculoOption.value || !inquilinoOption || !inquilinoOption.value) {
        preview.style.display = 'none';
        return;
    }
    
    const vehiculo = JSON.parse(vehiculoOption.dataset.vehiculo);
    const inquilino = JSON.parse(inquilinoOption.dataset.inquilino);
    
    document.getElementById('previewVehiculo').textContent = 
        `${vehiculo.placa} - ${vehiculo.marca} ${vehiculo.modelo}`;
    document.getElementById('previewPrecio').textContent = 
        `$${formatCurrency(vehiculo.precio_semanal)}`;
    document.getElementById('previewInquilino').textContent = 
        inquilino.nombre_apellido;
    document.getElementById('previewPropietario').textContent = 
        vehiculo.propietario_nombre || 'N/A';
    
    preview.style.display = 'block';
}

// ==========================================
// SETUP AGREGAR ALQUILER FORM (CORREGIDO)
// ==========================================
function setupAgregarAlquilerForm() {
    const form = document.getElementById('agregarAlquilerForm');
    if (!form) return;
    
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const formData = new FormData(this);
        const data = {
            semana_id: formData.get('semana_id'),
            vehiculo_id: formData.get('vehiculo_id'),
            inquilino_id: formData.get('inquilino_id'),
            dias_trabajo: formData.get('dias_trabajo')
        };
        
        if (!data.vehiculo_id || !data.inquilino_id) {
            showAlert('Error', 'Debe seleccionar un vehículo y un inquilino', 'error');
            return;
        }
        
        // Disable submit button
        const submitBtn = document.getElementById('agregarAlquilerSubmit');
        submitBtn.disabled = true;
        submitBtn.innerHTML = `
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" style="animation: spin 1s linear infinite;">
                <circle cx="12" cy="12" r="10" stroke-width="3" stroke-dasharray="32"/>
            </svg>
            Agregando...
        `;
        
fetch('/alquiler/semanas/agregar_alquiler', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(data)
        })
        .then(response => {
            // ✅ Check HTTP status first
            if (!response.ok) {
                return response.json().then(err => {
                    throw new Error(err.message || 'Error en el servidor');
                });
            }
            return response.json();
        })
        .then(result => {
            if (result.success) {
                window.AppUtils.closeModal('agregarAlquilerModal');
                
                // Reload detalles
                delete semanasData[currentSemanaId];
                loadDetallesSemana(currentSemanaId);
                
                showAlert('Éxito', 'Alquiler agregado correctamente', 'success');
                console.log('✅ Alquiler added:', result.detalle_id);
            } else {
                showAlert('Error', result.message, 'error');
            }
        })
        .catch(error => {
            console.error('❌ Error adding alquiler:', error);
            showAlert('Error', error.message || 'Error al agregar alquiler', 'error');
        })
        .finally(() => {
            // Re-enable submit
            submitBtn.disabled = false;
            submitBtn.innerHTML = `
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/>
                </svg>
                Agregar Alquiler
            `;
        });
    });
}

// ==========================================
// ELIMINAR SEMANA
// ==========================================
function eliminarSemana(semanaId, totalVehiculos) {
    let message = totalVehiculos > 0 
        ? `Esta semana tiene ${totalVehiculos} alquileres. Solo los administradores pueden eliminarla. ¿Continuar?`
        : 'Esta semana está vacía. ¿Deseas eliminarla?';
    
    showConfirm(
        '¿Eliminar Semana?',
        message,
        function() {
            fetch(`/alquiler/semanas/${semanaId}/eliminar`, {
                method: 'POST'
            })
            .then(response => response.json())
            .then(result => {
                if (result.success) {
                    showAlert('Éxito', 'Semana eliminada', 'success');
                    setTimeout(() => window.location.reload(), 1500);
                } else {
                    showAlert('Error', result.message, 'error');
                }
            })
            .catch(error => {
                console.error('❌ Error:', error);
                showAlert('Error', 'Error al eliminar semana', 'error');
            });
        }
    );
}

// ==========================================
// UTILITY
// ==========================================
function formatCurrency(value) {
    return parseFloat(value || 0).toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',');
}
