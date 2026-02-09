// ==========================================
// ALQUILERES.JS - VERSIÓN CORREGIDA Y COMPLETA
// ==========================================

// ==========================================
// VARIABLES GLOBALES
// ==========================================
let semanaActualId = null;
let semanasAbiertas = new Map(); // Cache de datos por semana
let inversionesCache = new Map(); // Cache de inversiones

// ==========================================
// INICIALIZACIÓN
// ==========================================
document.addEventListener('DOMContentLoaded', function() {
    console.log('✅ Inicializando sistema de alquileres...');
    
    // Validar semanas activas al cargar
    validarSemanasActivas();
    
    // Setup filtros
    setupFiltros();
    
    // Setup fecha inicio para nueva semana
    setupFechaInicioSemana();
    
    // Setup modals
    setupModals();
    
    console.log('✅ Sistema inicializado correctamente');
});

// ==========================================
// VALIDACIÓN DE SEMANAS ACTIVAS
// ==========================================
function validarSemanasActivas() {
    fetch('/alquiler/semanas/validar-activas')
        .then(res => res.json())
        .then(data => {
            if (data.success && data.tiene_problemas) {
                mostrarAlertaSemanasActivas(data.problemas);
            }
        })
        .catch(err => console.error('Error validando semanas:', err));
}

function mostrarAlertaSemanasActivas(problemas) {
    const html = `
        <div class="alert alert-warning" style="margin: 20px; padding: 20px; border-radius: 8px;">
            <div style="display: flex; align-items: start; gap: 12px;">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" style="flex-shrink: 0;">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
                </svg>
                <div style="flex: 1;">
                    <h4 style="margin: 0 0 8px 0; font-weight: 600;">⚠️ Advertencia: Semanas Activas Fuera de Rango</h4>
                    <p style="margin: 0 0 12px 0;">Se detectaron las siguientes semanas activas que no corresponden a la semana actual:</p>
                    <ul style="margin: 0; padding-left: 20px;">
                        ${problemas.map(p => `
                            <li>
                                <strong>Semana ${p.numero_semana}:</strong> 
                                ${p.fecha_inicio} - ${p.fecha_fin}
                                <span style="color: #dc3545;">(${p.tipo === 'pasada' ? 'Pasada' : 'Futura'} - ${p.dias_diferencia} días)</span>
                            </li>
                        `).join('')}
                    </ul>
                    <p style="margin: 12px 0 0 0; font-size: 14px; color: #856404;">
                        <strong>Recomendación:</strong> Revisa y cierra las semanas que ya pasaron.
                    </p>
                </div>
            </div>
        </div>
    `;
    
    // Insertar al inicio de content-area
    const contentArea = document.querySelector('.content-area');
    contentArea.insertAdjacentHTML('afterbegin', html);
}

// ==========================================
// CONFIGURACIÓN DE FECHA INICIO SEMANA
// ==========================================
function setupFechaInicioSemana() {
    const fechaInicio = document.getElementById('fechaInicio');
    const fechaFin = document.getElementById('fechaFin');
    
    if (!fechaInicio || !fechaFin) return;
    
    // Al cambiar fecha inicio, calcular fecha fin automáticamente
    fechaInicio.addEventListener('change', function() {
        const fecha = new Date(this.value + 'T00:00:00');
        
        // Validar que sea miércoles
        const diaSemana = fecha.getDay();
        if (diaSemana !== 3) { // 3 = Miércoles
            alert('⚠️ La fecha de inicio debe ser un MIÉRCOLES');
            this.value = '';
            fechaFin.value = '';
            return;
        }
        
        // Calcular jueves de la siguiente semana (8 días después)
        const fechaFinCalculada = new Date(fecha);
        fechaFinCalculada.setDate(fechaFinCalculada.getDate() + 8);
        
        // Formatear a YYYY-MM-DD
        const year = fechaFinCalculada.getFullYear();
        const month = String(fechaFinCalculada.getMonth() + 1).padStart(2, '0');
        const day = String(fechaFinCalculada.getDate()).padStart(2, '0');
        
        fechaFin.value = `${year}-${month}-${day}`;
    });
}

// ==========================================
// TOGGLE SEMANA (ACCORDION)
// ==========================================
function toggleSemana(semanaId) {
    const details = document.getElementById(`details-${semanaId}`);
    const toggle = document.getElementById(`toggle-${semanaId}`);
    const loading = document.getElementById(`loading-${semanaId}`);
    
    if (details.style.display === 'none' || details.style.display === '') {
        // Abrir
        details.style.display = 'block';
        toggle.classList.add('open');
        
        // Si no hay datos cargados, cargar
        if (!semanasAbiertas.has(semanaId)) {
            loading.style.display = 'flex';
            cargarDetallesSemana(semanaId);
        }
    } else {
        // Cerrar
        details.style.display = 'none';
        toggle.classList.remove('open');
    }
}



// ==========================================
// CARGAR DETALLES DE SEMANA
// ==========================================
function cargarDetallesSemana(semanaId) {
    console.log(`📊 Cargando detalles de semana ${semanaId}...`);
    
    fetch(`/alquiler/semanas/${semanaId}/detalles`)
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                // Guardar en cache
                semanasAbiertas.set(semanaId, data.detalles);
                
                // Renderizar
                renderizarTablaSemana(semanaId, data.detalles);
                
                console.log(`✅ Semana ${semanaId} cargada: ${data.detalles.length} alquileres`);
            } else {
                mostrarError('Error al cargar detalles de la semana');
            }
        })
        .catch(err => {
            console.error('Error:', err);
            mostrarError('Error al cargar detalles de la semana');
        })
        .finally(() => {
            document.getElementById(`loading-${semanaId}`).style.display = 'none';
        });
}

// ==========================================
// RENDERIZAR TABLA SEMANA
// ==========================================
function renderizarTablaSemana(semanaId, detalles) {
    const tbody = document.getElementById(`tbody-${semanaId}`);
    const tfoot = document.getElementById(`tfoot-${semanaId}`);
    const tableWrapper = document.getElementById(`table-wrapper-${semanaId}`);
    const emptyState = document.getElementById(`empty-${semanaId}`);
    
    if (!tbody) {
        console.error(`❌ No se encontró tbody para semana ${semanaId}`);
        return;
    }
    
    // Limpiar
    tbody.innerHTML = '';
    tfoot.innerHTML = '';
    
    if (detalles.length === 0) {
        tableWrapper.style.display = 'none';
        emptyState.style.display = 'block';
        return;
    }
    
    tableWrapper.style.display = 'block';
    emptyState.style.display = 'none';
    
    // Totales
    let totalIngreso = 0;
    let totalInversion = 0;
    let totalNomina = 0;
    let totalDeuda = 0;
    let totalNominaFinal = 0;
    
    // Renderizar filas
    detalles.forEach(detalle => {
        const precioSemanal = parseFloat(detalle.precio_semanal || 0);
        const inversion = parseFloat(detalle.inversiones_totales || 0);
        const ingreso = parseFloat(detalle.ingreso_calculado || 0);
        
        // Determinar clase de inversión
        let inversionClass = '';
        if (inversion >= precioSemanal) {
            inversionClass = 'inversion-danger';
        } else if (inversion >= precioSemanal * 0.7) {
            inversionClass = 'inversion-warning';
        }
        
        const tr = document.createElement('tr');
        tr.dataset.detalleId = detalle.id;
        
        tr.innerHTML = `
            <td class="sticky-col">
                <div style="display: flex; align-items: center; gap: 8px;">
                    <div class="avatar-circle">${detalle.propietario_iniciales || '??'}</div>
                    <span>${detalle.propietario_nombre || 'Sin propietario'}</span>
                </div>
            </td>
            <td>${detalle.vehiculo_marca || ''} ${detalle.vehiculo_modelo || ''}</td>
            <td><span class="placa-badge">${detalle.vehiculo_placa || ''}</span></td>
            <td>${detalle.inquilino_nombre || ''}</td>
            <td>${detalle.inquilino_telefono || ''}</td>
            <td class="text-right">$${precioSemanal.toFixed(2)}</td>
            <td class="text-center">
                <input type="number" 
                       class="cell-input" 
                       value="${detalle.dias_trabajo || 0}" 
                       min="1" 
                       max="7"
                       data-field="dias_trabajo"
                       data-detalle-id="${detalle.id}">
            </td>
            <td class="text-right">$${ingreso.toFixed(2)}</td>
            <td class="text-right ${inversionClass}">
                <div style="display: flex; align-items: center; justify-content: space-between; gap: 8px;">
                    <span>$${inversion.toFixed(2)}</span>
                    <button class="btn-icon" onclick="gestionarInversiones(${detalle.id})" title="Gestionar inversiones">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                            <path d="M12 5v14m-7-7h14"/>
                        </svg>
                    </button>
                </div>
            </td>
            <td>
                <input type="text" 
                       class="cell-input" 
                       value="${detalle.concepto_descuento || ''}"
                       data-field="concepto_descuento"
                       data-detalle-id="${detalle.id}"
                       placeholder="Concepto...">
            </td>
            <td class="text-right">$${parseFloat(detalle.nomina_empresa || 0).toFixed(2)}</td>
            <td class="text-center">${parseFloat(detalle.porcentaje_empresa || 0).toFixed(2)}%</td>
            <td class="text-right">
                <input type="number" 
                       class="cell-input" 
                       value="${detalle.monto_deuda || 0}"
                       step="0.01"
                       min="0"
                       data-field="monto_deuda"
                       data-detalle-id="${detalle.id}">
            </td>
            <td class="text-right font-bold">$${parseFloat(detalle.nomina_final || 0).toFixed(2)}</td>
            <td>
                <select class="cell-select" data-field="banco_id" data-detalle-id="${detalle.id}">
                    <option value="">Sin banco</option>
                </select>
            </td>
            <td>
                <input type="date" 
                       class="cell-input" 
                       value="${detalle.fecha_confirmacion_pago || ''}"
                       data-field="fecha_confirmacion_pago"
                       data-detalle-id="${detalle.id}">
            </td>
            <td class="text-center">${detalle.dias_trabajo || 0}</td>
            <td class="text-center">
                <div style="display: flex; gap: 4px; justify-content: center;">
                    <button class="btn-icon btn-edit" onclick="editarDetalle(${detalle.id})" title="Editar">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                            <path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7"/>
                            <path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z"/>
                        </svg>
                    </button>
                    <button class="btn-icon btn-delete" onclick="eliminarDetalle(${detalle.id}, ${semanaId})" title="Eliminar">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                            <path d="M3 6h18m-2 0v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6m3 0V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"/>
                        </svg>
                    </button>
                </div>
            </td>
        `;
        
        tbody.appendChild(tr);
        
        // Acumular totales
        totalIngreso += ingreso;
        totalInversion += inversion;
        totalNomina += parseFloat(detalle.nomina_empresa || 0);
        totalDeuda += parseFloat(detalle.monto_deuda || 0);
        totalNominaFinal += parseFloat(detalle.nomina_final || 0);
    });
    
    // Renderizar totales
    tfoot.innerHTML = `
        <tr style="background: #f8f9fa; font-weight: 700;">
            <td colspan="7" class="text-right">TOTALES:</td>
            <td class="text-right">$${totalIngreso.toFixed(2)}</td>
            <td class="text-right">$${totalInversion.toFixed(2)}</td>
            <td></td>
            <td class="text-right">$${totalNomina.toFixed(2)}</td>
            <td></td>
            <td class="text-right">$${totalDeuda.toFixed(2)}</td>
            <td class="text-right">$${totalNominaFinal.toFixed(2)}</td>
            <td colspan="3"></td>
        </tr>
    `;
    
    // Cargar opciones de bancos
    cargarBancosEnSelect(semanaId);
}

// ==========================================
// CARGAR BANCOS EN SELECT
// ==========================================
function cargarBancosEnSelect(semanaId) {
    fetch('/alquiler/bancos/json')
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                const selects = document.querySelectorAll(`#tbody-${semanaId} select[data-field="banco_id"]`);
                selects.forEach(select => {
                    const detalleId = select.dataset.detalleId;
                    const detalle = semanasAbiertas.get(semanaId).find(d => d.id == detalleId);
                    
                    select.innerHTML = '<option value="">Sin banco</option>';
                    data.bancos.forEach(banco => {
                        const option = document.createElement('option');
                        option.value = banco.id;
                        option.textContent = `${banco.banco} - ${banco.cuenta}`;
                        if (detalle && detalle.banco_id == banco.id) {
                            option.selected = true;
                        }
                        select.appendChild(option);
                    });
                });
            }
        })
        .catch(err => console.error('Error cargando bancos:', err));
}

// ==========================================
// GUARDAR CAMBIOS SEMANA
// ==========================================
function guardarCambiosSemana(semanaId) {
    console.log(`💾 Guardando cambios de semana ${semanaId}...`);
    
    const tbody = document.getElementById(`tbody-${semanaId}`);
    if (!tbody) return;
    
    const cambios = [];
    const inputs = tbody.querySelectorAll('[data-detalle-id]');
    
    // Agrupar por detalle_id
    const detallesPorId = {};
    inputs.forEach(input => {
        const detalleId = input.dataset.detalleId;
        if (!detallesPorId[detalleId]) {
            detallesPorId[detalleId] = { id: parseInt(detalleId) };
        }
        
        const field = input.dataset.field;
        let value = input.value;
        
        // Convertir a número si es necesario
        if (['dias_trabajo', 'monto_deuda', 'precio_semanal', 'banco_id'].includes(field)) {
            value = value ? parseFloat(value) : null;
        }
        
        detallesPorId[detalleId][field] = value;
    });
    
    // Convertir a array
    Object.values(detallesPorId).forEach(detalle => {
        cambios.push(detalle);
    });
    
    // Enviar al servidor
    fetch(`/alquiler/semanas/${semanaId}/guardar-cambios`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ cambios })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            mostrarExito(`✅ ${data.updated} detalles actualizados`);
            // Recargar datos
            semanasAbiertas.delete(semanaId);
            cargarDetallesSemana(semanaId);
        } else {
            mostrarError(data.message || 'Error al guardar cambios');
        }
    })
    .catch(err => {
        console.error('Error:', err);
        mostrarError('Error al guardar cambios');
    });
}

// ==========================================
// AGREGAR ALQUILER
// ==========================================
function agregarAlquiler(semanaId) {
    console.log(`➕ Abriendo modal para agregar alquiler a semana ${semanaId}`);
    
    semanaActualId = semanaId;
    document.getElementById('agregarAlquilerSemanaId').value = semanaId;
    
    // Cargar vehículos e inquilinos disponibles
    fetch(`/alquiler/semanas/${semanaId}/disponibles`)
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                // Llenar select de vehículos
                const vehiculoSelect = document.getElementById('vehiculoSelect');
                vehiculoSelect.innerHTML = '<option value="">Seleccionar vehículo...</option>';
                data.vehiculos.forEach(v => {
                    const option = document.createElement('option');
                    option.value = v.id;
                    option.textContent = `${v.placa} - ${v.marca} ${v.modelo} (${v.propietario_nombre})`;
                    option.dataset.precio = v.precio_semanal;
                    option.dataset.propietario = v.propietario_nombre;
                    vehiculoSelect.appendChild(option);
                });
                
                // Llenar select de inquilinos
                const inquilinoSelect = document.getElementById('inquilinoSelect');
                inquilinoSelect.innerHTML = '<option value="">Seleccionar inquilino...</option>';
                data.inquilinos.forEach(i => {
                    const option = document.createElement('option');
                    option.value = i.id;
                    option.textContent = `${i.nombre_apellido} - ${i.cedula || 'Sin cédula'}`;
                    inquilinoSelect.appendChild(option);
                });
                
                // Setup preview
                vehiculoSelect.addEventListener('change', updateAlquilerPreview);
                inquilinoSelect.addEventListener('change', updateAlquilerPreview);
                
                // Abrir modal
                openModal('agregarAlquilerModal');
            }
        })
        .catch(err => {
            console.error('Error:', err);
            mostrarError('Error al cargar datos disponibles');
        });
}

function updateAlquilerPreview() {
    const vehiculoSelect = document.getElementById('vehiculoSelect');
    const inquilinoSelect = document.getElementById('inquilinoSelect');
    const preview = document.getElementById('alquilerPreview');
    
    if (vehiculoSelect.value && inquilinoSelect.value) {
        const vehiculoOption = vehiculoSelect.options[vehiculoSelect.selectedIndex];
        const precio = vehiculoOption.dataset.precio || '0';
        const propietario = vehiculoOption.dataset.propietario || '';
        
        document.getElementById('previewVehiculo').textContent = vehiculoSelect.options[vehiculoSelect.selectedIndex].text.split(' (')[0];
        document.getElementById('previewPrecio').textContent = `$${parseFloat(precio).toFixed(2)}`;
        document.getElementById('previewInquilino').textContent = inquilinoSelect.options[inquilinoSelect.selectedIndex].text;
        document.getElementById('previewPropietario').textContent = propietario;
        
        preview.style.display = 'block';
    } else {
        preview.style.display = 'none';
    }
}

// Submit agregar alquiler
document.getElementById('agregarAlquilerForm')?.addEventListener('submit', function(e) {
    e.preventDefault();
    
    const formData = {
        semana_id: document.getElementById('agregarAlquilerSemanaId').value,
        vehiculo_id: document.getElementById('vehiculoSelect').value,
        inquilino_id: document.getElementById('inquilinoSelect').value,
        dias_trabajo: document.querySelector('[name="dias_trabajo"]').value
    };
    
    fetch('/alquiler/semanas/agregar_alquiler', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData)
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            mostrarExito('✅ Alquiler agregado correctamente');
            closeModal('agregarAlquilerModal');
            
            // Recargar datos de la semana
            semanasAbiertas.delete(formData.semana_id);
            cargarDetallesSemana(parseInt(formData.semana_id));
        } else {
            mostrarError(data.message || 'Error al agregar alquiler');
        }
    })
    .catch(err => {
        console.error('Error:', err);
        mostrarError('Error al agregar alquiler');
    });
});

// ==========================================
// EDITAR DETALLE
// ==========================================
function editarDetalle(detalleId) {
    console.log(`✏️ Editando detalle ${detalleId}`);
    
    // Buscar detalle en cache
    let detalle = null;
    let semanaId = null;
    
    for (let [sId, detalles] of semanasAbiertas.entries()) {
        detalle = detalles.find(d => d.id === detalleId);
        if (detalle) {
            semanaId = sId;
            break;
        }
    }
    
    if (!detalle) {
        mostrarError('No se encontró el detalle');
        return;
    }
    
    // Llenar formulario
    document.getElementById('editDetalleId').value = detalleId;
    document.querySelector('#editarDetalleForm [name="precio_semanal"]').value = detalle.precio_semanal || '';
    document.querySelector('#editarDetalleForm [name="dias_trabajo"]').value = detalle.dias_trabajo || '';
    document.querySelector('#editarDetalleForm [name="inversion_mecanica"]').value = detalle.inversiones_totales || 0;
    document.querySelector('#editarDetalleForm [name="concepto_inversion"]').value = detalle.concepto_inversion || '';
    document.querySelector('#editarDetalleForm [name="monto_descuento"]').value = detalle.monto_descuento || '';
    document.querySelector('#editarDetalleForm [name="concepto_descuento"]').value = detalle.concepto_descuento || '';
    document.querySelector('#editarDetalleForm [name="monto_deuda"]').value = detalle.monto_deuda || '';
    document.querySelector('#editarDetalleForm [name="fecha_confirmacion_pago"]').value = detalle.fecha_confirmacion_pago || '';
    document.querySelector('#editarDetalleForm [name="pago_confirmado"]').checked = detalle.pago_confirmado || false;
    document.querySelector('#editarDetalleForm [name="notas"]').value = detalle.notas || '';
    
    // Cargar opciones de vehículos e inquilinos
    if (semanaId) {
        fetch(`/alquiler/semanas/${semanaId}/disponibles`)
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    // Vehículos
                    const editVehiculoSelect = document.getElementById('editVehiculoSelect');
                    editVehiculoSelect.innerHTML = '';
                    
                    // Agregar vehículo actual
                    const currentVOption = document.createElement('option');
                    currentVOption.value = detalle.vehiculo_id;
                    currentVOption.textContent = `${detalle.vehiculo_placa} - ${detalle.vehiculo_marca} ${detalle.vehiculo_modelo} (Actual)`;
                    currentVOption.selected = true;
                    editVehiculoSelect.appendChild(currentVOption);
                    
                    // Agregar disponibles
                    data.vehiculos.forEach(v => {
                        if (v.id !== detalle.vehiculo_id) {
                            const option = document.createElement('option');
                            option.value = v.id;
                            option.textContent = `${v.placa} - ${v.marca} ${v.modelo} (${v.propietario_nombre})`;
                            editVehiculoSelect.appendChild(option);
                        }
                    });
                    
                    // Inquilinos
                    const editInquilinoSelect = document.getElementById('editInquilinoSelect');
                    editInquilinoSelect.innerHTML = '';
                    
                    // Agregar inquilino actual
                    const currentIOption = document.createElement('option');
                    currentIOption.value = detalle.inquilino_id;
                    currentIOption.textContent = `${detalle.inquilino_nombre} (Actual)`;
                    currentIOption.selected = true;
                    editInquilinoSelect.appendChild(currentIOption);
                    
                    // Agregar disponibles
                    data.inquilinos.forEach(i => {
                        if (i.id !== detalle.inquilino_id) {
                            const option = document.createElement('option');
                            option.value = i.id;
                            option.textContent = `${i.nombre_apellido} - ${i.cedula || 'Sin cédula'}`;
                            editInquilinoSelect.appendChild(option);
                        }
                    });
                }
            });
    }
    
    // Abrir modal
    openModal('editarDetalleModal');
}

// Submit editar detalle
document.getElementById('editarDetalleForm')?.addEventListener('submit', function(e) {
    e.preventDefault();
    
    const detalleId = document.getElementById('editDetalleId').value;
    
    const formData = {
        detalle_id: detalleId,
        vehiculo_id: document.getElementById('editVehiculoSelect').value,
        inquilino_id: document.getElementById('editInquilinoSelect').value,
        precio_semanal: document.querySelector('#editarDetalleForm [name="precio_semanal"]').value,
        dias_trabajo: document.querySelector('#editarDetalleForm [name="dias_trabajo"]').value,
        inversion_mecanica: document.querySelector('#editarDetalleForm [name="inversion_mecanica"]').value,
        concepto_inversion: document.querySelector('#editarDetalleForm [name="concepto_inversion"]').value,
        monto_descuento: document.querySelector('#editarDetalleForm [name="monto_descuento"]').value,
        concepto_descuento: document.querySelector('#editarDetalleForm [name="concepto_descuento"]').value,
        monto_deuda: document.querySelector('#editarDetalleForm [name="monto_deuda"]').value,
        banco_id: document.querySelector('#editarDetalleForm [name="banco_id"]').value || null,
        fecha_confirmacion_pago: document.querySelector('#editarDetalleForm [name="fecha_confirmacion_pago"]').value,
        pago_confirmado: document.querySelector('#editarDetalleForm [name="pago_confirmado"]').checked,
        notas: document.querySelector('#editarDetalleForm [name="notas"]').value
    };
    
    fetch(`/alquiler/detalles/${detalleId}/editar_completo`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData)
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            mostrarExito('✅ Detalle actualizado correctamente');
            closeModal('editarDetalleModal');
            
            // Recargar todas las semanas abiertas (por si cambió el vehículo/inquilino)
            semanasAbiertas.forEach((_, semanaId) => {
                semanasAbiertas.delete(semanaId);
                if (document.getElementById(`details-${semanaId}`).style.display !== 'none') {
                    cargarDetallesSemana(semanaId);
                }
            });
        } else {
            mostrarError(data.message || 'Error al actualizar detalle');
        }
    })
    .catch(err => {
        console.error('Error:', err);
        mostrarError('Error al actualizar detalle');
    });
});

// ==========================================
// ELIMINAR DETALLE
// ==========================================
function eliminarDetalle(detalleId, semanaId) {
    if (!confirm('¿Estás seguro de eliminar este alquiler?')) return;
    
    fetch(`/alquiler/detalles/${detalleId}/eliminar`, {
        method: 'POST'
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            mostrarExito('✅ Alquiler eliminado');
            semanasAbiertas.delete(semanaId);
            cargarDetallesSemana(semanaId);
        } else {
            mostrarError(data.message);
        }
    })
    .catch(err => {
        console.error('Error:', err);
        mostrarError('Error al eliminar alquiler');
    });
}

// ==========================================
// CERRAR SEMANA (SOLO ADMIN)
// ==========================================
function cerrarSemana(semanaId) {
    if (window.APP_DATA.userRol !== 'admin') {
        mostrarError('⛔ Solo administradores pueden cerrar semanas');
        return;
    }
    
    if (!confirm('¿Cerrar esta semana? No podrás editarla después.')) return;
    
    fetch(`/alquiler/semanas/${semanaId}/cerrar`, {
        method: 'POST'
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            mostrarExito('✅ Semana cerrada correctamente');
            location.reload();
        } else {
            mostrarError(data.message);
        }
    })
    .catch(err => {
        console.error('Error:', err);
        mostrarError('Error al cerrar semana');
    });
}

// ==========================================
// ELIMINAR SEMANA (SOLO ADMIN)
// ==========================================
function eliminarSemana(semanaId, totalVehiculos) {
    if (window.APP_DATA.userRol !== 'admin') {
        mostrarError('⛔ Solo administradores pueden eliminar semanas');
        return;
    }
    
    const msg = totalVehiculos > 0 
        ? `¿Eliminar esta semana y sus ${totalVehiculos} alquileres? Esta acción NO se puede deshacer.`
        : '¿Eliminar esta semana vacía?';
        
    if (!confirm(msg)) return;
    
    fetch(`/alquiler/semanas/${semanaId}/eliminar`, {
        method: 'POST'
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            mostrarExito('✅ Semana eliminada');
            location.reload();
        } else {
            mostrarError(data.message);
        }
    })
    .catch(err => {
        console.error('Error:', err);
        mostrarError('Error al eliminar semana');
    });
}

// ==========================================
// GESTIONAR INVERSIONES
// ==========================================
function gestionarInversiones(detalleId) {
    console.log(`🔧 Gestionando inversiones del detalle ${detalleId}`);
    
    document.getElementById('inversionDetalleId').value = detalleId;
    
    // Cargar inversiones existentes
    cargarInversiones(detalleId);
    
    // Abrir modal
    openModal('inversionesModal');
}

function cargarInversiones(detalleId) {
    const lista = document.getElementById('listaInversiones');
    lista.innerHTML = '<p style="text-align: center; padding: 20px;">Cargando...</p>';
    
    fetch(`/alquiler/detalles/${detalleId}/inversiones`)
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                if (data.inversiones.length === 0) {
                    lista.innerHTML = '<p style="text-align: center; color: #6c757d; padding: 20px;">No hay inversiones registradas</p>';
                } else {
                    lista.innerHTML = data.inversiones.map(inv => `
                        <div style="padding: 12px; border: 1px solid #dee2e6; border-radius: 6px; margin-bottom: 8px; background: white;">
                            <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 8px;">
                                <div>
                                    <strong style="color: #2c3e50;">${inv.tipo_trabajo}</strong>
                                    <span style="margin-left: 8px; padding: 2px 8px; background: ${inv.tipo_inversion === 'falla_mecanica' ? '#ffc107' : '#dc3545'}; color: white; border-radius: 4px; font-size: 11px;">
                                        ${inv.tipo_inversion === 'falla_mecanica' ? '🔧 Falla Mecánica' : '🚗 Accidente'}
                                    </span>
                                </div>
                                <strong style="color: #28a745; font-size: 16px;">$${parseFloat(inv.costo).toFixed(2)}</strong>
                            </div>
                            <div style="font-size: 13px; color: #6c757d; margin-bottom: 4px;">
                                ${inv.descripcion}
                            </div>
                            <div style="font-size: 12px; color: #adb5bd;">
                                📅 ${inv.fecha} | 👨‍🔧 ${inv.mecanico}
                            </div>
                        </div>
                    `).join('');
                }
                
                document.getElementById('totalInversiones').textContent = `$${parseFloat(data.total).toFixed(2)}`;
                inversionesCache.set(detalleId, data);
            }
        })
        .catch(err => {
            console.error('Error:', err);
            lista.innerHTML = '<p style="text-align: center; color: #dc3545; padding: 20px;">Error al cargar inversiones</p>';
        });
}

// Submit nueva inversión
document.getElementById('nuevaInversionForm')?.addEventListener('submit', function(e) {
    e.preventDefault();
    
    const detalleId = document.getElementById('inversionDetalleId').value;
    
    const formData = {
        detalle_id: detalleId,
        tipo_trabajo_id: this.tipo_trabajo_id.value,
        mecanico_id: this.mecanico_id.value,
        tipo_inversion: this.tipo_inversion.value,
        descripcion: this.descripcion.value,
        costo: parseFloat(this.costo.value)
    };
    
    fetch('/alquiler/inversiones/crear', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData)
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            mostrarExito('✅ Inversión registrada');
            this.reset();
            cargarInversiones(detalleId);
            
            // Actualizar el valor en el formulario de edición si está abierto
            const inversionInput = document.querySelector('#editarDetalleForm [name="inversion_mecanica"]');
            if (inversionInput) {
                inversionInput.value = data.total_inversion;
            }
        } else {
            mostrarError(data.message || 'Error al crear inversión');
        }
    })
    .catch(err => {
        console.error('Error:', err);
        mostrarError('Error al crear inversión');
    });
});

// ==========================================
// EXPORTAR A EXCEL
// ==========================================
function exportarExcelSemana(semanaId) {
    window.location.href = `/alquiler/semanas/${semanaId}/exportar-excel`;
}

// ==========================================
// MODALS
// ==========================================
function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'flex';
        setTimeout(() => modal.classList.add('show'), 10);
    }
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove('show');
        setTimeout(() => modal.style.display = 'none', 300);
    }
}

function setupModals() {
    // Cerrar modal al hacer click en overlay
    document.querySelectorAll('.modal-overlay').forEach(overlay => {
        overlay.addEventListener('click', function(e) {
            if (e.target === this) {
                this.classList.remove('show');
                setTimeout(() => this.style.display = 'none', 300);
            }
        });
    });
    
    // Cerrar con botón X
    document.querySelectorAll('.modal-close').forEach(btn => {
        btn.addEventListener('click', function() {
            const modal = this.closest('.modal-overlay');
            if (modal) {
                modal.classList.remove('show');
                setTimeout(() => modal.style.display = 'none', 300);
            }
        });
    });
}

function openCrearSemanaModal() {
    // Calcular próximo miércoles
    const hoy = new Date();
    const diaSemana = hoy.getDay();
    const diasHastaMiercoles = (3 - diaSemana + 7) % 7;
    const proximoMiercoles = new Date(hoy);
    proximoMiercoles.setDate(hoy.getDate() + (diasHastaMiercoles === 0 ? 7 : diasHastaMiercoles));
    
    // Formatear
    const year = proximoMiercoles.getFullYear();
    const month = String(proximoMiercoles.getMonth() + 1).padStart(2, '0');
    const day = String(proximoMiercoles.getDate()).padStart(2, '0');
    
    document.getElementById('fechaInicio').value = `${year}-${month}-${day}`;
    
    // Trigger change para calcular fecha fin
    document.getElementById('fechaInicio').dispatchEvent(new Event('change'));
    
    openModal('crearSemanaModal');
}

// ==========================================
// FILTROS
// ==========================================
function setupFiltros() {
    const filtroEstado = document.getElementById('filtroEstado');
    if (filtroEstado) {
        filtroEstado.addEventListener('change', function() {
            const estado = this.value;
            document.querySelectorAll('.semana-accordion-item').forEach(item => {
                if (!estado || item.dataset.estado === estado) {
                    item.style.display = 'block';
                } else {
                    item.style.display = 'none';
                }
            });
        });
    }
}

// ==========================================
// NOTIFICACIONES
// ==========================================
function mostrarExito(mensaje) {
    // Implementar sistema de notificaciones toast
    alert(mensaje);
}

function mostrarError(mensaje) {
    alert('❌ ' + mensaje);
}

console.log('✅ alquileres.js cargado completamente');