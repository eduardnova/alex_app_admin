// ==========================================
// ALQUILERES.JS - SISTEMA COMPLETO v2.0.1
// Sistema de Gestión de Alquileres Semanales
// ==========================================

// ==========================================
// VARIABLES GLOBALES
// ==========================================
const semanasCacheIndependiente = {};
let currentSemanaId = null;
let currentDetalleId = null;

// ==========================================
// INICIALIZACIÓN PRINCIPAL
// ==========================================
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Inicializando sistema de alquileres...');
    
    // Inicializar componentes
    inicializarModales();
    inicializarFiltros();
    inicializarFormularios();
    
    // Cargar datos globales
    cargarBancos();
    cargarTiposTrabajo();
    
    // Validar semanas activas
    validarSemanasActivas();
    
    console.log('✅ Sistema inicializado correctamente');
});


// ==========================================
// INICIALIZAR MODALES
// ==========================================
function inicializarModales() {
    console.log('📦 Inicializando modales...');
    
    // Cerrar modales al hacer click en overlay
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('modal-overlay')) {
            cerrarModal(e.target.id);
        }
    });
    
    // Botones de cerrar modal
    const closeButtons = document.querySelectorAll('.modal-close, [data-modal-close]');
    closeButtons.forEach(function(btn) {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const modal = e.target.closest('.modal-overlay');
            if (modal) {
                cerrarModal(modal.id);
            }
        });
    });
    
    console.log('✅ Modales inicializados');
}


// ==========================================
// INICIALIZAR FORMULARIOS
// ==========================================
function inicializarFormularios() {
    console.log('📝 Inicializando formularios...');
    
    // Form Crear Semana
    const formCrearSemana = document.getElementById('crearSemanaForm');
    if (formCrearSemana) {
        formCrearSemana.addEventListener('submit', function(e) {
            // El form se envía normalmente (POST tradicional)
            console.log('📤 Enviando form crear semana...');
        });
    }
    
    // Form Agregar Alquiler
    const formAgregarAlquiler = document.getElementById('agregarAlquilerForm');
    if (formAgregarAlquiler) {
        formAgregarAlquiler.addEventListener('submit', function(e) {
            e.preventDefault();
            submitAgregarAlquiler();
        });
    }
    
    // Form Editar Detalle
    const formEditarDetalle = document.getElementById('editarDetalleForm');
    if (formEditarDetalle) {
        formEditarDetalle.addEventListener('submit', function(e) {
            e.preventDefault();
            submitEditarDetalle();
        });
    }
    
    console.log('✅ Formularios inicializados');
}


// ==========================================
// INICIALIZAR FILTROS
// ==========================================
function inicializarFiltros() {
    const filtroEstado = document.getElementById('filtroEstado');
    
    if (filtroEstado) {
        filtroEstado.addEventListener('change', function(e) {
            const estado = e.target.value;
            const semanas = document.querySelectorAll('.semana-accordion-item');
            
            semanas.forEach(function(semana) {
                const semanaEstado = semana.dataset.estado;
                
                if (estado === '' || semanaEstado === estado) {
                    semana.style.display = 'block';
                } else {
                    semana.style.display = 'none';
                }
            });
            
            console.log(`🔍 Filtrado por estado: ${estado || 'todos'}`);
        });
    }
}


// ==========================================
// ABRIR MODAL CREAR SEMANA
// ==========================================
function openCrearSemanaModal() {
    console.log('📅 Abriendo modal crear semana...');
    const modal = document.getElementById('crearSemanaModal');
    
    if (!modal) {
        console.error('❌ No se encontró el modal crearSemanaModal');
        mostrarError('Error: Modal no encontrado');
        return;
    }
    
    modal.style.display = 'flex';
    setTimeout(function() {
        modal.classList.add('show');
    }, 10);
}


// ==========================================
// CERRAR MODAL
// ==========================================
function cerrarModal(modalId) {
    const modal = document.getElementById(modalId);
    
    if (!modal) {
        console.warn('⚠️ Modal no encontrado:', modalId);
        return;
    }
    
    modal.classList.remove('show');
    
    setTimeout(function() {
        modal.style.display = 'none';
        
        // Limpiar formularios si existen
        const form = modal.querySelector('form');
        if (form) {
            form.reset();
        }
    }, 300);
}


// ==========================================
// TOGGLE SEMANA (EXPANDIR/CONTRAER) - CORREGIDO
// ==========================================
function toggleSemana(semanaId) {
    console.log(`🔽 Toggle semana ${semanaId}`);
    
    const item = document.querySelector(`.semana-accordion-item[data-semana-id="${semanaId}"]`);
    const details = document.getElementById(`details-${semanaId}`);
    const toggle = document.getElementById(`toggle-${semanaId}`);
    const loading = document.getElementById(`loading-${semanaId}`);
    
    if (!details || !toggle || !item) {
        console.error(`❌ Elementos no encontrados para semana ${semanaId}`);
        return;
    }
    
    const isExpanded = item.classList.contains('active');
    
    if (!isExpanded) {
        // EXPANDIR
        item.classList.add('active');
        details.style.display = 'block';
        toggle.classList.add('open');
        
        // Cargar datos si no están en cache
        if (!semanasCacheIndependiente[semanaId]) {
            if (loading) {
                loading.style.display = 'flex';
            }
            cargarDetallesSemana(semanaId);
        }
    } else {
        // CONTRAER
        item.classList.remove('active');
        details.style.display = 'none';
        toggle.classList.remove('open');
    }
}


// ==========================================
// CARGAR DETALLES DE SEMANA
// ==========================================
function cargarDetallesSemana(semanaId) {
    console.log(`📊 Cargando detalles de semana ${semanaId}...`);
    
    const loading = document.getElementById(`loading-${semanaId}`);
    const tableWrapper = document.getElementById(`table-wrapper-${semanaId}`);
    const emptyState = document.getElementById(`empty-${semanaId}`);
    
    fetch(`/alquiler/semanas/${semanaId}/detalles`)
        .then(response => response.json())
        .then(data => {
            if (loading) loading.style.display = 'none';
            
            if (data.success) {
                // Guardar en cache INDEPENDIENTE
                semanasCacheIndependiente[semanaId] = data.detalles;
                
                console.log(`✅ Cargados ${data.detalles.length} alquileres para semana ${semanaId}`);
                
                if (data.detalles.length === 0) {
                    if (emptyState) emptyState.style.display = 'flex';
                    if (tableWrapper) tableWrapper.style.display = 'none';
                } else {
                    if (emptyState) emptyState.style.display = 'none';
                    if (tableWrapper) tableWrapper.style.display = 'block';
                    renderizarTablaAlquileres(semanaId, data.detalles);
                }
            } else {
                mostrarError(data.message || 'Error al cargar alquileres');
            }
        })
        .catch(error => {
            if (loading) loading.style.display = 'none';
            console.error('❌ Error:', error);
            mostrarError('Error de conexión: ' + error.message);
        });
}


// ==========================================
// RENDERIZAR TABLA DE ALQUILERES
// ==========================================
function renderizarTablaAlquileres(semanaId, detalles) {
    const tbody = document.getElementById(`tbody-${semanaId}`);
    const tfoot = document.getElementById(`tfoot-${semanaId}`);
    
    if (!tbody) {
        console.error(`❌ No se encontró tbody para semana ${semanaId}`);
        return;
    }
    
    // LIMPIAR TABLA
    tbody.innerHTML = '';
    
    let totalIngresos = 0;
    let totalInversiones = 0;
    let totalDescuentos = 0;
    let totalNominas = 0;
    let totalDeudas = 0;
    let totalNominasFinal = 0;
    
    detalles.forEach(function(detalle) {
        const row = tbody.insertRow();
        row.dataset.detalleId = detalle.id;
        row.dataset.semanaId = semanaId;
        
        // 1. Avatar Propietario
        const avatarCell = row.insertCell();
        avatarCell.className = 'sticky-col';
        avatarCell.innerHTML = `
            <div class="propietario-cell">
                <div class="avatar">${detalle.propietario_iniciales || '??'}</div>
                <span class="propietario-nombre">${detalle.propietario_nombre || 'Sin propietario'}</span>
            </div>
        `;
        
        // 2. Vehículo
        row.insertCell().innerHTML = `
            <div class="vehiculo-info">
                <strong>${detalle.vehiculo_marca || 'N/A'} ${detalle.vehiculo_modelo || ''}</strong>
            </div>
        `;
        
        // 3. Placa
        row.insertCell().innerHTML = `<span class="badge badge-secondary">${detalle.vehiculo_placa || 'N/A'}</span>`;
        
        // 4. Inquilino
        row.insertCell().textContent = detalle.inquilino_nombre || 'Sin inquilino';
        
        // 5. Teléfono
        row.insertCell().textContent = detalle.inquilino_telefono || '-';
        
        // 6. Precio Semanal
        const precioCell = row.insertCell();
        precioCell.textContent = `$${detalle.precio_semanal.toFixed(2)}`;
        precioCell.className = 'text-right';
        
        // 7. DT (Días de Trabajo)
        const dtCell = row.insertCell();
        dtCell.innerHTML = `<input type="number" class="excel-input" value="${detalle.dias_trabajo}" min="1" max="7" data-field="dias_trabajo" onchange="marcarCambio(${detalle.id}, ${semanaId})">`;
        
        // 8. Ingreso
        const ingresoCell = row.insertCell();
        ingresoCell.textContent = `$${detalle.ingreso_calculado.toFixed(2)}`;
        ingresoCell.className = 'text-right font-weight-bold';
        totalIngresos += detalle.ingreso_calculado;
        
        // 9. INVERSIÓN (CON COLOR CONDICIONAL)
        const inversionTotal = detalle.inversion_mecanica || 0;
        const inversionCell = row.insertCell();
        inversionCell.className = 'text-right';
        
        // Colorear si inversión >= precio semanal
        if (inversionTotal >= detalle.precio_semanal) {
            inversionCell.classList.add('inversion-warning');
        }
        
        inversionCell.innerHTML = `
            <div style="display: flex; align-items: center; justify-content: flex-end; gap: 8px;">
                <span>$${inversionTotal.toFixed(2)}</span>
                <button class="btn-icon" onclick="gestionarInversiones(${detalle.id}, ${semanaId})" title="Gestionar inversiones">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                        <path d="M12 5v14m-7-7h14" stroke-width="2" stroke-linecap="round"/>
                    </svg>
                </button>
            </div>
        `;
        totalInversiones += inversionTotal;
        
        // 10. Concepto Descuento
        row.insertCell().innerHTML = `<input type="text" class="excel-input" value="${detalle.concepto_descuento || ''}" data-field="concepto_descuento" onchange="marcarCambio(${detalle.id}, ${semanaId})">`;
        totalDescuentos += detalle.monto_descuento || 0;
        
        // 11. Nómina Empresa
        const nominaCell = row.insertCell();
        nominaCell.textContent = `$${detalle.nomina_empresa.toFixed(2)}`;
        nominaCell.className = 'text-right';
        totalNominas += detalle.nomina_empresa;
        
        // 12. % Empresa
        row.insertCell().innerHTML = `<span class="badge badge-info">${detalle.porcentaje_empresa}%</span>`;
        
        // 13. Deuda
        row.insertCell().innerHTML = `<input type="number" class="excel-input" value="${detalle.monto_deuda || 0}" step="0.01" min="0" data-field="monto_deuda" onchange="marcarCambio(${detalle.id}, ${semanaId})">`;
        totalDeudas += detalle.monto_deuda || 0;
        
        // 14. Nómina Final
        const nominaFinalCell = row.insertCell();
        nominaFinalCell.textContent = `$${detalle.nomina_final.toFixed(2)}`;
        nominaFinalCell.className = 'text-right font-weight-bold text-success';
        totalNominasFinal += detalle.nomina_final;
        
        // 15. Banco
        row.insertCell().innerHTML = `
            <select class="excel-select" data-field="banco_id" onchange="marcarCambio(${detalle.id}, ${semanaId})">
                <option value="">Seleccionar...</option>
                ${window.bancosGlobal ? window.bancosGlobal.map(function(b) {
                    return `<option value="${b.id}" ${detalle.banco_id == b.id ? 'selected' : ''}>${b.banco}</option>`;
                }).join('') : ''}
            </select>
        `;
        
        // 16. Confirmación Pago
        row.insertCell().innerHTML = `<input type="date" class="excel-input" value="${detalle.fecha_confirmacion_pago || ''}" data-field="fecha_confirmacion_pago" onchange="marcarCambio(${detalle.id}, ${semanaId})">`;
        
        // 17. DT2
        row.insertCell().textContent = detalle.dias_trabajo;
        
        // 18. Acciones
        const actionsCell = row.insertCell();
        actionsCell.innerHTML = `
            <div class="action-buttons">
                <button class="btn-icon btn-edit" onclick="editarDetalleCompleto(${detalle.id}, ${semanaId})" title="Editar">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                        <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7" stroke-width="2"/>
                        <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z" stroke-width="2"/>
                    </svg>
                </button>
                <button class="btn-icon btn-delete" onclick="eliminarDetalle(${detalle.id}, ${semanaId})" title="Eliminar">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                        <path d="M3 6h18M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2m3 0v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6h14z" stroke-width="2"/>
                    </svg>
                </button>
            </div>
        `;
    });
    
    // FOOTER con totales
    if (tfoot) {
        tfoot.innerHTML = `
            <tr class="totals-row">
                <td colspan="7" class="text-right"><strong>TOTALES:</strong></td>
                <td class="text-right"><strong>$${totalIngresos.toFixed(2)}</strong></td>
                <td class="text-right"><strong>$${totalInversiones.toFixed(2)}</strong></td>
                <td></td>
                <td class="text-right"><strong>$${totalNominas.toFixed(2)}</strong></td>
                <td></td>
                <td class="text-right"><strong>$${totalDeudas.toFixed(2)}</strong></td>
                <td class="text-right"><strong>$${totalNominasFinal.toFixed(2)}</strong></td>
                <td colspan="4"></td>
            </tr>
        `;
    }
    
    console.log(`✅ Tabla renderizada: ${detalles.length} filas`);
}


// ==========================================
// MARCAR CAMBIO
// ==========================================
function marcarCambio(detalleId, semanaId) {
    const row = document.querySelector(`tr[data-detalle-id="${detalleId}"]`);
    if (row) {
        row.style.backgroundColor = '#fff3cd';
        setTimeout(function() {
            row.style.backgroundColor = '';
        }, 1000);
    }
}


// ==========================================
// GESTIONAR INVERSIONES - CORREGIDO
// ==========================================
function gestionarInversiones(detalleId, semanaId) {
    console.log(`🔧 Gestionando inversiones de detalle ${detalleId}`);
    currentDetalleId = detalleId;
    currentSemanaId = semanaId;
    
    // Buscar detalle en cache
    const detalle = semanasCacheIndependiente[semanaId]?.find(function(d) {
        return d.id === detalleId;
    });
    
    if (!detalle) {
        console.error('❌ Detalle no encontrado');
        mostrarError('No se encontró el detalle del alquiler');
        return;
    }
    
    console.log('📋 Creando modal de inversiones...');
    
    // Crear y mostrar modal
    const modal = crearModalInversiones(detalle, semanaId);
    document.body.appendChild(modal);
    
    // Forzar reflow para animación
    modal.offsetHeight;
    
    setTimeout(function() {
        modal.classList.add('show');
        console.log('✅ Modal inversiones abierto');
    }, 10);
}


// ==========================================
// CREAR MODAL DE INVERSIONES - OPTIMIZADO
// ==========================================
function crearModalInversiones(detalle, semanaId) {
    // HTML de inversiones
    const inversionesHTML = detalle.inversiones && detalle.inversiones.length > 0 
        ? detalle.inversiones.map(function(inv) {
            return `
                <tr>
                    <td><span class="badge badge-warning">${inv.tipo_trabajo || 'N/A'}</span></td>
                    <td>${inv.descripcion || '-'}</td>
                    <td class="text-right"><strong>$${(inv.costo || 0).toFixed(2)}</strong></td>
                    <td>${inv.fecha || '-'}</td>
                    <td class="text-center">
                        <button class="btn-icon btn-delete" onclick="eliminarInversion(${inv.id}, ${detalle.id}, ${semanaId})" title="Eliminar">
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                                <path d="M3 6h18M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2m3 0v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6h14z" stroke-width="2"/>
                            </svg>
                        </button>
                    </td>
                </tr>
            `;
        }).join('') 
        : '<tr><td colspan="5" class="text-center" style="padding: 20px; color: var(--text-tertiary);">No hay inversiones registradas</td></tr>';
    
    // Opciones de tipos de trabajo
    const tiposTrabajosOptions = window.tiposTrabajo ? window.tiposTrabajo.map(function(t) {
        return `<option value="${t.id}">${getIconoTipoTrabajo(t.nombre)} ${t.nombre}</option>`;
    }).join('') : '<option value="">No hay tipos de trabajo disponibles</option>';
    
    // Crear elemento modal
    const modalDiv = document.createElement('div');
    modalDiv.className = 'modal-overlay';
    modalDiv.id = 'inversionesModal';
    modalDiv.innerHTML = `
        <div class="modal modal-lg">
            <div class="modal-header">
                <h3 class="modal-title">
                    🔧 Inversiones Mecánicas - ${detalle.vehiculo_placa || 'N/A'}
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
                        <strong>Precio Semanal:</strong> $${(detalle.precio_semanal || 0).toFixed(2)}
                        ${(detalle.inversion_mecanica || 0) >= (detalle.precio_semanal || 0) ? 
                            '<br><strong style="color: #856404;">⚠️ La inversión iguala o supera el precio semanal</strong>' : ''}
                    </div>
                </div>
                
                <div style="background: var(--bg-primary); padding: 16px; border-radius: 8px; margin-bottom: 20px;">
                    <h4 style="font-size: 14px; font-weight: 600; margin-bottom: 12px;">➕ Nueva Inversión</h4>
                    <form id="formNuevaInversion" onsubmit="agregarInversion(event, ${detalle.id}, ${semanaId})">
                        <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px;">
                            <div class="form-group">
                                <label class="form-label required">Tipo de Trabajo</label>
                                <select name="tipo_trabajo_id" class="form-select" required>
                                    <option value="">Seleccionar...</option>
                                    ${tiposTrabajosOptions}
                                </select>
                            </div>
                            
                            <div class="form-group">
                                <label class="form-label required">Tipo de Falla</label>
                                <select name="tipo_falla" class="form-select" required>
                                    <option value="falla_mecanica">🔧 Falla Mecánica</option>
                                    <option value="accidente">🚗💥 Accidente</option>
                                    <option value="mantenimiento">🛠️ Mantenimiento</option>
                                    <option value="desgaste">⚙️ Desgaste Normal</option>
                                    <option value="otro">📋 Otro</option>
                                </select>
                            </div>
                            
                            <div class="form-group" style="grid-column: 1 / -1;">
                                <label class="form-label required">Concepto/Descripción</label>
                                <textarea name="descripcion" class="form-textarea" rows="2" required placeholder="Ej: Cambio de pastillas de freno delanteras"></textarea>
                            </div>
                            
                            <div class="form-group">
                                <label class="form-label required">Monto</label>
                                <div class="input-group">
                                    <span class="input-addon">$</span>
                                    <input type="number" name="costo" class="form-input" step="0.01" min="0.01" required>
                                </div>
                            </div>
                        </div>
                        
                        <button type="submit" class="btn btn-primary" style="margin-top: 12px;">
                            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/>
                            </svg>
                            Agregar Inversión
                        </button>
                    </form>
                </div>
                
                <div>
                    <h4 style="font-size: 14px; font-weight: 600; margin-bottom: 12px;">📋 Inversiones Registradas</h4>
                    <div class="table-responsive">
                        <table class="table" id="tablaInversiones">
                            <thead>
                                <tr>
                                    <th>Tipo</th>
                                    <th>Descripción</th>
                                    <th>Monto</th>
                                    <th>Fecha</th>
                                    <th style="width: 80px;">Acciones</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${inversionesHTML}
                            </tbody>
                            <tfoot>
                                <tr style="background: var(--bg-primary); font-weight: bold;">
                                    <td colspan="2" class="text-right">TOTAL INVERSIONES:</td>
                                    <td class="text-right" style="color: ${(detalle.inversion_mecanica || 0) >= (detalle.precio_semanal || 0) ? '#856404' : 'inherit'};">
                                        $${(detalle.inversion_mecanica || 0).toFixed(2)}
                                    </td>
                                    <td colspan="2"></td>
                                </tr>
                            </tfoot>
                        </table>
                    </div>
                </div>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-secondary" onclick="cerrarModalInversiones()">Cerrar</button>
            </div>
        </div>
    `;
    
    return modalDiv;
}

// ==========================================
// CERRAR MODAL INVERSIONES
// ==========================================
function cerrarModalInversiones() {
    const modal = document.getElementById('inversionesModal');
    if (modal) {
        modal.classList.remove('show');
        setTimeout(function() {
            modal.remove();
        }, 300);
    }
}


// ==========================================
// AGREGAR INVERSIÓN
// ==========================================
function agregarInversion(event, detalleId, semanaId) {
    event.preventDefault();
    
    const form = event.target;
    const formData = new FormData(form);
    
    const data = {
        tipo_trabajo_id: formData.get('tipo_trabajo_id'),
        descripcion: formData.get('descripcion'),
        costo: parseFloat(formData.get('costo')),
        tipo_falla: formData.get('tipo_falla')
    };
    
    if (!data.tipo_trabajo_id || !data.descripcion || !data.costo) {
        mostrarError('Todos los campos son requeridos');
        return;
    }
    
    if (data.costo <= 0) {
        mostrarError('El monto debe ser mayor a 0');
        return;
    }
    
    fetch(`/alquiler/detalles/${detalleId}/agregar_inversion`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(data)
    })
    .then(function(response) {
        return response.json();
    })
    .then(function(result) {
        if (result.success) {
            mostrarExito('Inversión agregada exitosamente');
            cerrarModalInversiones();
            semanasCacheIndependiente[semanaId] = null;
            cargarDetallesSemana(semanaId);
        } else {
            mostrarError(result.message || 'Error al agregar inversión');
        }
    })
    .catch(function(error) {
        console.error('❌ Error:', error);
        mostrarError('Error de conexión: ' + error.message);
    });
}


// ==========================================
// ELIMINAR INVERSIÓN
// ==========================================
function eliminarInversion(inversionId, detalleId, semanaId) {
    if (!confirm('¿Eliminar esta inversión?')) return;
    
    fetch(`/alquiler/inversiones/${inversionId}/eliminar`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'}
    })
    .then(function(response) {
        return response.json();
    })
    .then(function(result) {
        if (result.success) {
            mostrarExito('Inversión eliminada');
            cerrarModalInversiones();
            semanasCacheIndependiente[semanaId] = null;
            cargarDetallesSemana(semanaId);
        } else {
            mostrarError(result.message);
        }
    })
    .catch(function(error) {
        mostrarError('Error: ' + error.message);
    });
}


// ==========================================
// AGREGAR ALQUILER - CORREGIDO
// ==========================================
function agregarAlquiler(semanaId) {
    console.log(`➕ Abriendo modal agregar alquiler para semana ${semanaId}`);
    currentSemanaId = semanaId;
    
    // Verificar que el modal existe
    const modal = document.getElementById('agregarAlquilerModal');
    if (!modal) {
        console.error('❌ Modal agregarAlquilerModal no encontrado');
        mostrarError('Error: Modal no encontrado en el DOM');
        return;
    }
    
    // Cargar datos disponibles
    fetch(`/alquiler/semanas/${semanaId}/disponibles`)
        .then(function(response) {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(function(data) {
            if (data.success) {
                const vehiculoSelect = document.getElementById('vehiculoSelect');
                const inquilinoSelect = document.getElementById('inquilinoSelect');
                
                if (!vehiculoSelect || !inquilinoSelect) {
                    throw new Error('No se encontraron los select elements');
                }
                
                // Poblar vehículos
                vehiculoSelect.innerHTML = '<option value="">Seleccionar vehículo...</option>' +
                    data.vehiculos.map(function(v) {
                        return `<option value="${v.id}" data-precio="${v.precio_semanal}">
                            ${v.placa} - ${v.marca} ${v.modelo} - $${v.precio_semanal}
                        </option>`;
                    }).join('');
                
                // Poblar inquilinos
                inquilinoSelect.innerHTML = '<option value="">Seleccionar inquilino...</option>' +
                    data.inquilinos.map(function(i) {
                        return `<option value="${i.id}">
                            ${i.nombre_apellido} - ${i.telefono || 'Sin teléfono'}
                        </option>`;
                    }).join('');
                
                // Setear semana ID
                document.getElementById('agregarAlquilerSemanaId').value = semanaId;
                
                // ABRIR MODAL
                modal.style.display = 'flex';
                setTimeout(function() {
                    modal.classList.add('show');
                }, 10);
                
                console.log('✅ Modal abierto exitosamente');
            } else {
                mostrarError(data.message || 'Error al cargar datos disponibles');
            }
        })
        .catch(function(error) {
            console.error('❌ Error al cargar disponibles:', error);
            mostrarError('Error de conexión: ' + error.message);
        });
}



// ==========================================
// SUBMIT AGREGAR ALQUILER
// ==========================================
function submitAgregarAlquiler() {
    const form = document.getElementById('agregarAlquilerForm');
    const formData = new FormData(form);
    
    const data = {
        semana_id: formData.get('semana_id'),
        vehiculo_id: formData.get('vehiculo_id'),
        inquilino_id: formData.get('inquilino_id'),
        dias_trabajo: formData.get('dias_trabajo') || 7
    };
    
    fetch('/alquiler/semanas/agregar_alquiler', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(data)
    })
    .then(function(response) {
        return response.json();
    })
    .then(function(result) {
        if (result.success) {
            mostrarExito('Alquiler agregado exitosamente');
            cerrarModal('agregarAlquilerModal');
            semanasCacheIndependiente[data.semana_id] = null;
            cargarDetallesSemana(data.semana_id);
        } else {
            mostrarError(result.message || 'Error al agregar alquiler');
        }
    })
    .catch(function(error) {
        console.error('❌ Error:', error);
        mostrarError('Error de conexión: ' + error.message);
    });
}


// ==========================================
// EDITAR DETALLE COMPLETO - CORREGIDO
// ==========================================
function editarDetalleCompleto(detalleId, semanaId) {
    console.log(`✏️ Editando detalle ${detalleId} de semana ${semanaId}`);
    currentDetalleId = detalleId;
    currentSemanaId = semanaId;
    
    // Verificar modal
    const modal = document.getElementById('editarDetalleModal');
    if (!modal) {
        console.error('❌ Modal editarDetalleModal no encontrado');
        mostrarError('Error: Modal no encontrado');
        return;
    }
    
    // Buscar detalle en cache
    const detalle = semanasCacheIndependiente[semanaId]?.find(function(d) {
        return d.id === detalleId;
    });
    
    if (!detalle) {
        console.error('❌ Detalle no encontrado en cache');
        mostrarError('No se encontró el detalle del alquiler');
        return;
    }
    
    console.log('📋 Detalle encontrado:', detalle);
    
    // Cargar vehículos e inquilinos disponibles
    fetch(`/alquiler/semanas/${semanaId}/disponibles`)
        .then(function(response) {
            return response.json();
        })
        .then(function(data) {
            if (data.success) {
                // Preparar vehículo actual
                const vehiculoActual = {
                    id: detalle.vehiculo_id,
                    placa: detalle.vehiculo_placa,
                    marca: detalle.vehiculo_marca,
                    modelo: detalle.vehiculo_modelo,
                    precio_semanal: detalle.precio_semanal
                };
                
                // Preparar inquilino actual
                const inquilinoActual = {
                    id: detalle.inquilino_id,
                    nombre_apellido: detalle.inquilino_nombre,
                    telefono: detalle.inquilino_telefono
                };
                
                // Poblar select de vehículos
                const editVehiculoSelect = document.getElementById('editVehiculoSelect');
                if (editVehiculoSelect) {
                    editVehiculoSelect.innerHTML = 
                        `<option value="${vehiculoActual.id}" selected>
                            ${vehiculoActual.placa} - ${vehiculoActual.marca} ${vehiculoActual.modelo}
                        </option>` +
                        data.vehiculos.map(function(v) {
                            return `<option value="${v.id}">
                                ${v.placa} - ${v.marca} ${v.modelo} - $${v.precio_semanal}
                            </option>`;
                        }).join('');
                }
                
                // Poblar select de inquilinos
                const editInquilinoSelect = document.getElementById('editInquilinoSelect');
                if (editInquilinoSelect) {
                    editInquilinoSelect.innerHTML = 
                        `<option value="${inquilinoActual.id}" selected>
                            ${inquilinoActual.nombre_apellido}
                        </option>` +
                        data.inquilinos.map(function(i) {
                            return `<option value="${i.id}">
                                ${i.nombre_apellido} - ${i.telefono || 'Sin teléfono'}
                            </option>`;
                        }).join('');
                }
                
                // Poblar todos los campos del formulario
                document.getElementById('editDetalleId').value = detalleId;
                
                const form = document.getElementById('editarDetalleForm');
                if (form) {
                    form.querySelector('[name="precio_semanal"]').value = detalle.precio_semanal || 0;
                    form.querySelector('[name="dias_trabajo"]').value = detalle.dias_trabajo || 7;
                    form.querySelector('[name="inversion_mecanica"]').value = detalle.inversion_mecanica || 0;
                    form.querySelector('[name="concepto_inversion"]').value = detalle.concepto_inversion || '';
                    form.querySelector('[name="monto_descuento"]').value = detalle.monto_descuento || 0;
                    form.querySelector('[name="concepto_descuento"]').value = detalle.concepto_descuento || '';
                    form.querySelector('[name="monto_deuda"]').value = detalle.monto_deuda || 0;
                    form.querySelector('[name="banco_id"]').value = detalle.banco_id || '';
                    form.querySelector('[name="fecha_confirmacion_pago"]').value = detalle.fecha_confirmacion_pago || '';
                    form.querySelector('[name="notas"]').value = detalle.notas || '';
                    
                    const pagoCheck = document.getElementById('pagoConfirmadoCheck');
                    if (pagoCheck) {
                        pagoCheck.checked = detalle.pago_confirmado || false;
                    }
                }
                
                // ABRIR MODAL
                modal.style.display = 'flex';
                setTimeout(function() {
                    modal.classList.add('show');
                }, 10);
                
                console.log('✅ Modal editar abierto exitosamente');
            } else {
                mostrarError(data.message || 'Error al cargar datos');
            }
        })
        .catch(function(error) {
            console.error('❌ Error:', error);
            mostrarError('Error de conexión: ' + error.message);
        });
}


// ==========================================
// SUBMIT EDITAR DETALLE
// ==========================================
function submitEditarDetalle() {
    const form = document.getElementById('editarDetalleForm');
    const formData = new FormData(form);
    const detalleId = document.getElementById('editDetalleId').value;
    
    const data = {
        vehiculo_id: formData.get('vehiculo_id'),
        inquilino_id: formData.get('inquilino_id'),
        precio_semanal: formData.get('precio_semanal'),
        dias_trabajo: formData.get('dias_trabajo'),
        inversion_mecanica: formData.get('inversion_mecanica') || 0,
        concepto_inversion: formData.get('concepto_inversion'),
        monto_descuento: formData.get('monto_descuento') || 0,
        concepto_descuento: formData.get('concepto_descuento'),
        monto_deuda: formData.get('monto_deuda') || 0,
        banco_id: formData.get('banco_id') || null,
        fecha_confirmacion_pago: formData.get('fecha_confirmacion_pago'),
        pago_confirmado: document.getElementById('pagoConfirmadoCheck').checked,
        notas: formData.get('notas')
    };
    
    fetch(`/alquiler/detalles/${detalleId}/editar_completo`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(data)
    })
    .then(function(response) {
        return response.json();
    })
    .then(function(result) {
        if (result.success) {
            mostrarExito('Detalle actualizado exitosamente');
            cerrarModal('editarDetalleModal');
            semanasCacheIndependiente[currentSemanaId] = null;
            cargarDetallesSemana(currentSemanaId);
        } else {
            mostrarError(result.message || 'Error al actualizar');
        }
    })
    .catch(function(error) {
        console.error('❌ Error:', error);
        mostrarError('Error de conexión: ' + error.message);
    });
}


// ==========================================
// ELIMINAR DETALLE
// ==========================================
function eliminarDetalle(detalleId, semanaId) {
    if (!confirm('¿Estás seguro de eliminar este alquiler de la semana?')) return;
    
    fetch(`/alquiler/detalles/${detalleId}/eliminar`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'}
    })
    .then(function(response) {
        return response.json();
    })
    .then(function(result) {
        if (result.success) {
            mostrarExito('Alquiler eliminado exitosamente');
            semanasCacheIndependiente[semanaId] = null;
            cargarDetallesSemana(semanaId);
        } else {
            mostrarError(result.message || 'Error al eliminar');
        }
    })
    .catch(function(error) {
        console.error('❌ Error:', error);
        mostrarError('Error de conexión: ' + error.message);
    });
}


// ==========================================
// CERRAR SEMANA
// ==========================================
function cerrarSemana(semanaId) {
    if (!confirm('¿Cerrar esta semana? No podrás editarla después.')) return;
    
    fetch(`/alquiler/semanas/${semanaId}/cerrar`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'}
    })
    .then(function(response) {
        return response.json();
    })
    .then(function(result) {
        if (result.success) {
            mostrarExito('Semana cerrada exitosamente');
            setTimeout(function() {
                location.reload();
            }, 1000);
        } else {
            mostrarError(result.message || 'Error al cerrar semana');
        }
    })
    .catch(function(error) {
        console.error('❌ Error:', error);
        mostrarError('Error de conexión: ' + error.message);
    });
}


// ==========================================
// ELIMINAR SEMANA
// ==========================================
function eliminarSemana(semanaId, totalVehiculos) {
    const mensaje = totalVehiculos > 0 
        ? `¿Eliminar esta semana y sus ${totalVehiculos} alquileres?\n\n⚠️ ESTA ACCIÓN NO SE PUEDE DESHACER.`
        : '¿Eliminar esta semana vacía?';
    
    if (!confirm(mensaje)) return;
    
    if (totalVehiculos > 0) {
        const confirmar = prompt('Escribe "ELIMINAR" para confirmar:');
        if (confirmar !== 'ELIMINAR') {
            mostrarError('Eliminación cancelada');
            return;
        }
    }
    
    fetch(`/alquiler/semanas/${semanaId}/eliminar`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'}
    })
    .then(function(response) {
        return response.json();
    })
    .then(function(result) {
        if (result.success) {
            mostrarExito('Semana eliminada exitosamente');
            setTimeout(function() {
                location.reload();
            }, 1000);
        } else {
            mostrarError(result.message || 'Error al eliminar semana');
        }
    })
    .catch(function(error) {
        console.error('❌ Error:', error);
        mostrarError('Error de conexión: ' + error.message);
    });
}


// ==========================================
// GUARDAR CAMBIOS SEMANA
// ==========================================
function guardarCambiosSemana(semanaId) {
    const tbody = document.getElementById(`tbody-${semanaId}`);
    
    if (!tbody) {
        mostrarError('No se encontró la tabla');
        return;
    }
    
    const cambios = [];
    const rows = tbody.querySelectorAll('tr');
    
    rows.forEach(function(row) {
        const detalleId = row.dataset.detalleId;
        
        if (!detalleId) return;
        
        const inputs = row.querySelectorAll('[data-field]');
        const cambio = { id: parseInt(detalleId) };
        
        inputs.forEach(function(input) {
            const field = input.dataset.field;
            let value = input.value;
            
            if (input.type === 'number') {
                value = parseFloat(value) || 0;
            }
            
            cambio[field] = value;
        });
        
        cambios.push(cambio);
    });
    
    if (cambios.length === 0) {
        mostrarError('No hay cambios para guardar');
        return;
    }
    
    fetch(`/alquiler/semanas/${semanaId}/guardar-cambios`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ cambios: cambios })
    })
    .then(function(response) {
        return response.json();
    })
    .then(function(result) {
        if (result.success) {
            mostrarExito(`${result.updated} cambios guardados`);
            semanasCacheIndependiente[semanaId] = null;
            cargarDetallesSemana(semanaId);
        } else {
            mostrarError(result.message || 'Error al guardar');
        }
    })
    .catch(function(error) {
        console.error('❌ Error:', error);
        mostrarError('Error de conexión: ' + error.message);
    });
}


// ==========================================
// EXPORTAR EXCEL
// ==========================================
function exportarExcelSemana(semanaId) {
    window.location.href = `/alquiler/semanas/${semanaId}/exportar-excel`;
}


// ==========================================
// VALIDAR SEMANAS ACTIVAS
// ==========================================
function validarSemanasActivas() {
    fetch('/alquiler/semanas/validar_activas')
        .then(function(response) {
            return response.json();
        })
        .then(function(data) {
            if (data.success && data.warning) {
                mostrarAdvertenciaSemanas(data);
            }
        })
        .catch(function(error) {
            console.error('Error validando semanas:', error);
        });
}

function mostrarAdvertenciaSemanas(data) {
    const alertHTML = `
        <div class="alert alert-warning" id="alertSemanasActivas" style="margin-bottom: 20px;">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
                <line x1="12" y1="9" x2="12" y2="13"/>
                <line x1="12" y1="17" x2="12.01" y2="17"/>
            </svg>
            <div>
                <strong>⚠️ Advertencia:</strong> Hay ${data.total_activas} semanas activas. 
                Las siguientes semanas están fuera del rango actual:
                <ul style="margin-top: 8px; margin-bottom: 8px;">
                    ${data.semanas_fuera_rango.map(function(s) {
                        return `<li>Semana #${s.numero_semana}: ${s.fecha_inicio} - ${s.fecha_fin}</li>`;
                    }).join('')}
                </ul>
                <p style="margin-top: 8px; margin-bottom: 0;"><strong>Recomendación:</strong> Cierra las semanas completadas para evitar confusiones.</p>
            </div>
        </div>
    `;
    
    const contentArea = document.querySelector('.content-area');
    if (contentArea) {
        contentArea.insertAdjacentHTML('afterbegin', alertHTML);
    }
}


// ==========================================
// CARGAR BANCOS
// ==========================================
function cargarBancos() {
    fetch('/alquiler/bancos/json')
        .then(function(response) {
            return response.json();
        })
        .then(function(data) {
            if (data.success) {
                window.bancosGlobal = data.bancos;
                console.log(`✅ Cargados ${data.bancos.length} bancos`);
            }
        })
        .catch(function(error) {
            console.error('Error cargando bancos:', error);
        });
}


// ==========================================
// CARGAR TIPOS DE TRABAJO
// ==========================================
function cargarTiposTrabajo() {
    if (window.tiposTrabajo) {
        console.log(`✅ Disponibles ${window.tiposTrabajo.length} tipos de trabajo`);
    }
}


// ==========================================
// ICONO TIPO TRABAJO
// ==========================================
function getIconoTipoTrabajo(nombre) {
    const iconos = {
        'Reparación Mecánica': '🔧',
        'Cambio de Pieza': '⚙️',
        'Mantenimiento': '🛠️',
        'Cambio de Aceite': '🛢️',
        'Frenos': '🚙',
        'Motor': '⚡',
        'Transmisión': '⚙️',
        'Suspensión': '🔩',
        'Eléctrico': '💡',
        'Carrocería': '🚗',
        'Pintura': '🎨',
        'Otro': '📋'
    };
    
    return iconos[nombre] || '🔧';
}


// ==========================================
// NOTIFICACIONES
// ==========================================
function mostrarExito(mensaje) {
    if (typeof Swal !== 'undefined') {
        Swal.fire({
            icon: 'success',
            title: '¡Éxito!',
            text: mensaje,
            timer: 3000,
            showConfirmButton: false
        });
    } else {
        alert('✅ ' + mensaje);
    }
}

function mostrarError(mensaje) {
    if (typeof Swal !== 'undefined') {
        Swal.fire({
            icon: 'error',
            title: 'Error',
            text: mensaje,
            confirmButtonText: 'Entendido'
        });
    } else {
        alert('❌ ' + mensaje);
    }
}

function mostrarAdvertencia(mensaje) {
    if (typeof Swal !== 'undefined') {
        Swal.fire({
            icon: 'warning',
            title: 'Advertencia',
            text: mensaje,
            confirmButtonText: 'Entendido'
        });
    } else {
        alert('⚠️ ' + mensaje);
    }
}


// ==========================================
// UTILIDADES
// ==========================================
function formatearMoneda(valor) {
    return new Intl.NumberFormat('es-DO', {
        style: 'currency',
        currency: 'DOP'
    }).format(valor);
}

function formatearFecha(fecha) {
    if (!fecha) return '-';
    return new Date(fecha).toLocaleDateString('es-DO');
}


// ==========================================
// DEBUGGING
// ==========================================
if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
    window.debugAlquileres = {
        verCache: function() {
            console.log('📦 Cache de semanas:', semanasCacheIndependiente);
        },
        limpiarCache: function() {
            Object.keys(semanasCacheIndependiente).forEach(function(key) {
                delete semanasCacheIndependiente[key];
            });
            console.log('🧹 Cache limpiado');
        },
        recargarSemana: function(semanaId) {
            semanasCacheIndependiente[semanaId] = null;
            cargarDetallesSemana(semanaId);
            console.log(`🔄 Recargando semana ${semanaId}`);
        },
        verGlobales: function() {
            console.log('🌍 Variables globales:');
            console.log('- bancosGlobal:', window.bancosGlobal);
            console.log('- tiposTrabajo:', window.tiposTrabajo);
            console.log('- userRole:', window.userRole);
        }
    };
    
    console.log('🐛 Modo debug activado. Usa window.debugAlquileres para herramientas.');
}


// ==========================================
// EXPORTAR FUNCIONES GLOBALES
// ==========================================
window.toggleSemana = toggleSemana;
window.cargarDetallesSemana = cargarDetallesSemana;
window.gestionarInversiones = gestionarInversiones;
window.agregarInversion = agregarInversion;
window.eliminarInversion = eliminarInversion;
window.cerrarModalInversiones = cerrarModalInversiones;
window.eliminarDetalle = eliminarDetalle;
window.cerrarSemana = cerrarSemana;
window.eliminarSemana = eliminarSemana;
window.openCrearSemanaModal = openCrearSemanaModal;
window.agregarAlquiler = agregarAlquiler;
window.editarDetalleCompleto = editarDetalleCompleto;
window.guardarCambiosSemana = guardarCambiosSemana;
window.exportarExcelSemana = exportarExcelSemana;
window.marcarCambio = marcarCambio;
window.cerrarModal = cerrarModal;
window.getIconoTipoTrabajo = getIconoTipoTrabajo;
window.mostrarExito = mostrarExito;
window.mostrarError = mostrarError;
window.mostrarAdvertencia = mostrarAdvertencia;

console.log('✅ alquileres.js cargado completamente');
console.log('📊 Sistema de Alquileres v2.0.1 - Listo para usar');