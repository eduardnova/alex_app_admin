// ==========================================
// ALQUILERES.JS - VERSIÓN CORREGIDA COMPLETA
// Fecha: 28/12/2025
// Cambios: Corrección de 5 errores críticos
// ==========================================

// ==========================================
// VARIABLES GLOBALES
// ==========================================
let semanaActualId = null;
let semanasAbiertas = new Map();
let inversionesCache = new Map();

// ==========================================
// INICIALIZACIÓN
// ==========================================
document.addEventListener('DOMContentLoaded', function () {
    console.log('✅ Inicializando sistema de alquileres...');

    validarSemanasActivas();
    setupFiltros();
    setupFechaInicioSemana();
    setupModals();

    console.log('✅ Sistema inicializado correctamente');
});

// ==========================================
// HELPERS PARA CUSTOM SELECTS
// ==========================================
function toggleSelect(id) {
    const wrapper = document.getElementById(id);
    if (!wrapper) return;

    // Cerrar otros abiertos
    document.querySelectorAll('.custom-select-wrapper').forEach(el => {
        if (el.id !== id) el.classList.remove('open');
    });

    wrapper.classList.toggle('open');

    // Si se abre, enfocar el search input
    if (wrapper.classList.contains('open')) {
        const searchInput = wrapper.querySelector('.custom-select-search input');
        if (searchInput) {
            searchInput.value = '';
            searchInput.focus();
            filterOptions(id, ''); // Resetear filtros
        }
    }
}

// Cerrar selects si se hace click fuera
document.addEventListener('click', function (e) {
    if (!e.target.closest('.custom-select-wrapper')) {
        document.querySelectorAll('.custom-select-wrapper').forEach(el => {
            el.classList.remove('open');
        });
    }
});

function selectOption(wrapperId, value, text, callback = null) {
    const wrapper = document.getElementById(wrapperId);
    if (!wrapper) return;

    const textEl = wrapper.querySelector('.selected-value');
    const valueEl = wrapper.querySelector('input[type="hidden"]');

    if (valueEl) valueEl.value = value;
    if (textEl) {
        textEl.textContent = text;
        textEl.classList.remove('placeholder');
    }

    // Marcar como seleccionado en la lista
    wrapper.querySelectorAll('.custom-select-option').forEach(opt => {
        opt.classList.toggle('selected', opt.dataset.value == value);
    });

    wrapper.classList.remove('open');

    if (callback && typeof callback === 'function') {
        callback(value);
    }
}

function filterOptions(wrapperId, query) {
    const wrapper = document.getElementById(wrapperId);
    if (!wrapper) return;

    query = query.toLowerCase().trim();
    const options = wrapper.querySelectorAll('.custom-select-option:not(.no-results)');
    let visibleCount = 0;

    options.forEach(opt => {
        const text = opt.textContent.toLowerCase();
        if (text.includes(query)) {
            opt.style.display = 'block';
            visibleCount++;
        } else {
            opt.style.display = 'none';
        }
    });

    // Mostrar/ocultar mensaje de "sin resultados"
    let noResultsEl = wrapper.querySelector('.no-results');
    if (!noResultsEl && visibleCount === 0) {
        const optionsCont = wrapper.querySelector('.custom-select-options');
        noResultsEl = document.createElement('div');
        noResultsEl.className = 'custom-select-option no-results';
        noResultsEl.textContent = 'No se encontraron resultados';
        optionsCont.appendChild(noResultsEl);
    } else if (noResultsEl) {
        noResultsEl.style.display = visibleCount === 0 ? 'block' : 'none';
    }
}

// ==========================================
// VALIDACIÓN DE SEMANAS ACTIVAS
// ==========================================
function validarSemanasActivas() {
    fetch('/alquiler/semanas/validar-activas')
        .then(res => res.json())
        .then(data => {
            if (data.success && data.tiene_problemas) {
                // mostrarAlertaSemanasActivas(data.problemas);
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

    fechaInicio.addEventListener('change', function () {
        const fecha = new Date(this.value + 'T00:00:00');
        const diaSemana = fecha.getDay();

        if (diaSemana !== 3) {
            alert('⚠️ La fecha de inicio debe ser un MIÉRCOLES');
            this.value = '';
            fechaFin.value = '';
            return;
        }

        const fechaFinCalculada = new Date(fecha);
        fechaFinCalculada.setDate(fechaFinCalculada.getDate() + 8);

        const year = fechaFinCalculada.getFullYear();
        const month = String(fechaFinCalculada.getMonth() + 1).padStart(2, '0');
        const day = String(fechaFinCalculada.getDate()).padStart(2, '0');

        fechaFin.value = `${year}-${month}-${day}`;
    });
}

// ==========================================
// ✅ CORRECCIÓN 2: FUNCIONES DE MODAL CORREGIDAS
// ==========================================
function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        // Forzar display y remover clase show primero
        modal.classList.remove('show');
        modal.style.display = 'flex';

        // Agregar clase después de un frame para animación
        requestAnimationFrame(() => {
            requestAnimationFrame(() => {
                modal.classList.add('show');
            });
        });
    }
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove('show');

        setTimeout(() => {
            modal.style.display = 'none';

            // Resetear formularios
            const form = modal.querySelector('form');
            if (form) {
                form.reset();
            }

            // Limpiar estados específicos
            if (modalId === 'agregarAlquilerModal') {
                document.getElementById('alquilerPreview').style.display = 'none';
            }
        }, 300);
    }
}

function setupModals() {
    // Cerrar al hacer click en overlay
    document.querySelectorAll('.modal-overlay').forEach(overlay => {
        overlay.addEventListener('click', function (e) {
            if (e.target === this) {
                closeModal(this.id);
            }
        });
    });

    // Cerrar con botón X
    document.querySelectorAll('.modal-close').forEach(btn => {
        btn.addEventListener('click', function () {
            const modal = this.closest('.modal-overlay');
            if (modal) {
                closeModal(modal.id);
            }
        });
    });

    // Cerrar con ESC
    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape') {
            document.querySelectorAll('.modal-overlay.show').forEach(modal => {
                closeModal(modal.id);
            });
        }
    });
}

function openCrearSemanaModal() {
    // Calcular próximo miércoles
    const hoy = new Date();
    const diaSemana = hoy.getDay();
    const diasHastaMiercoles = (3 - diaSemana + 7) % 7;
    const proximoMiercoles = new Date(hoy);
    proximoMiercoles.setDate(hoy.getDate() + (diasHastaMiercoles === 0 ? 7 : diasHastaMiercoles));

    const year = proximoMiercoles.getFullYear();
    const month = String(proximoMiercoles.getMonth() + 1).padStart(2, '0');
    const day = String(proximoMiercoles.getDate()).padStart(2, '0');

    document.getElementById('fechaInicio').value = `${year}-${month}-${day}`;
    document.getElementById('fechaInicio').dispatchEvent(new Event('change'));

    openModal('crearSemanaModal');
}

// ==========================================
// TOGGLE SEMANA
// ==========================================
function toggleSemana(semanaId) {
    const details = document.getElementById(`details-${semanaId}`);
    const toggle = document.getElementById(`toggle-${semanaId}`);
    const loading = document.getElementById(`loading-${semanaId}`);

    if (details.style.display === 'none' || details.style.display === '') {
        details.style.display = 'block';
        toggle.classList.add('open');

        if (!semanasAbiertas.has(semanaId)) {
            loading.style.display = 'flex';
            cargarDetallesSemana(semanaId);
        }
    } else {
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
                semanasAbiertas.set(semanaId, data.detalles);
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

    tbody.innerHTML = '';
    tfoot.innerHTML = '';

    if (detalles.length === 0) {
        tableWrapper.style.display = 'none';
        emptyState.style.display = 'block';
        return;
    }

    tableWrapper.style.display = 'block';
    emptyState.style.display = 'none';

    let totalIngreso = 0;
    let totalInversion = 0;
    let totalNomina = 0;
    let totalPorcentajeEmpresa = 0;
    let totalDeuda = 0;
    let totalNominaFinal = 0;

    detalles.forEach(detalle => {
        const precioSemanal = parseFloat(detalle.precio_semanal || 0);
        const inversion = parseFloat(detalle.inversiones_totales || 0);
        const ingreso = parseFloat(detalle.ingreso_calculado || 0);
        const porcentaje = parseFloat(detalle.porcentaje_empresa || 0);
        const montoPorcentaje = ingreso * (porcentaje / 100);

        let inversionClass = '';
        if (inversion >= precioSemanal) {
            inversionClass = 'inversion-danger';
        } else if (inversion >= precioSemanal * 0.7) {
            inversionClass = 'inversion-warning';
        }

        const tr = document.createElement('tr');
        tr.dataset.detalleId = detalle.id;

        // Aplicar clase si está confirmado
        if (detalle.pago_confirmado) {
            tr.classList.add('fila-confirmada');
        }

        const statusBadge = detalle.pago_confirmado
            ? `<span class="status-badge confirmed">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M20 6L9 17l-5-5" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/></svg>
                Confirmado
               </span>`
            : `<span class="status-badge unconfirmed">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
                Sin confirmar
               </span>`;

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
            <td class="text-right">
                ${detalle.contrato_deuda > 0
                ? `<span style="color: #e67e22; font-weight: bold;">No Pagado</span><div style="font-size: 0.85em; color: #e67e22;">$${detalle.contrato_deuda.toFixed(2)}</div>`
                : '<span style="color: #27ae60; font-weight: bold;">Pagado</span>'}
            </td>
            <td class="text-right">
                ${detalle.depositos_deuda > 0
                ? `<span style="color: #d35400; font-weight: bold; display: block; font-size: 0.8em;">Pendiente</span><span style="color: #d35400; font-weight: bold;">$${detalle.depositos_deuda.toFixed(2)}</span>`
                : `<span style="color: #27ae60; font-weight: bold;">Pagado</span>`}
            </td>
            <td class="text-right">$${precioSemanal.toFixed(2)}</td>
            <td class="text-center">
                ${detalle.dias_trabajo || 0}
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
            <td class="text-right">$${(ingreso - montoPorcentaje).toFixed(0)}</td> <!-- Corrected: Owner Share -->
            <td class="text-right" title="Porcentaje: ${porcentaje.toFixed(2)}%">
                $${montoPorcentaje.toFixed(0)}
            </td>
            <td class="text-right">
                $${parseFloat(detalle.monto_deuda || 0).toFixed(2)}
            </td>
            <td class="text-right font-bold">$${parseFloat(detalle.nomina_final || 0).toFixed(2)}</td>
            <td>
                <div style="display: flex; align-items: center; justify-content: space-between; gap: 4px;">
                    ${statusBadge}
                    <button class="btn-icon" onclick="abrirModalConfirmarPago(${detalle.id})" title="Confirmar Pago">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                            <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                        </svg>
                    </button>
                </div>
                ${detalle.banco_nombre ? `<div style="font-size: 10px; color: #6c757d; margin-top: 2px;">${detalle.banco_nombre}</div>` : ''}
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

        totalIngreso += ingreso;
        totalInversion += inversion;
        totalNomina += parseFloat(detalle.nomina_empresa || 0);
        totalPorcentajeEmpresa += montoPorcentaje;
        totalDeuda += parseFloat(detalle.monto_deuda || 0);
        totalNominaFinal += parseFloat(detalle.nomina_final || 0);
    });

    tfoot.innerHTML = `
        <tr style="background: #f8f9fa; font-weight: 700;">
            <td colspan="9" class="text-right">TOTALES:</td> <!-- Corrected colspan -->
            <td class="text-right">$${totalIngreso.toFixed(2)}</td>
            <td class="text-right">$${totalInversion.toFixed(2)}</td>
            <td class="text-right">$${(totalIngreso - totalPorcentajeEmpresa).toFixed(0)}</td> <!-- Corrected: Owner Share -->
            <td class="text-right">$${totalPorcentajeEmpresa.toFixed(0)}</td>
            <td class="text-right">$${totalDeuda.toFixed(2)}</td>
            <td class="text-right">$${totalNominaFinal.toFixed(2)}</td>
            <td colspan="2"></td>
        </tr>
    `;

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

    const detallesPorId = {};
    inputs.forEach(input => {
        const detalleId = input.dataset.detalleId;
        if (!detallesPorId[detalleId]) {
            detallesPorId[detalleId] = { id: parseInt(detalleId) };
        }

        const field = input.dataset.field;
        let value = input.value;

        if (['dias_trabajo', 'monto_deuda', 'precio_semanal', 'banco_id'].includes(field)) {
            value = value ? parseFloat(value) : null;
        }

        detallesPorId[detalleId][field] = value;
    });

    Object.values(detallesPorId).forEach(detalle => {
        cambios.push(detalle);
    });

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

    fetch(`/alquiler/semanas/${semanaId}/disponibles`)
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                // Configurar Vehículos
                const vehiculoOptions = document.getElementById('vehiculoSelectOptions');
                const vehiculoText = document.getElementById('vehiculoSelectText');
                const vehiculoValue = document.getElementById('vehiculoSelectValue');

                vehiculoOptions.innerHTML = '';
                vehiculoText.textContent = 'Seleccionar vehículo...';
                vehiculoText.classList.add('placeholder');
                vehiculoValue.value = '';

                data.vehiculos.forEach(v => {
                    const opt = document.createElement('div');
                    opt.className = 'custom-select-option';
                    opt.dataset.value = v.id;
                    opt.dataset.precio = v.precio_semanal;
                    opt.dataset.propietario = v.propietario_nombre;
                    opt.dataset.inquilinoId = v.inquilino_asociado_id || ''; // Store associated tenant ID

                    const inquilinoText = v.inquilino_nombre ? ` - [${v.inquilino_nombre}]` : '';
                    opt.textContent = `${v.placa} - ${v.marca} ${v.modelo} (${v.propietario_nombre})${inquilinoText}`;

                    opt.onclick = () => {
                        selectOption('vehiculoSelectWrapper', v.id, opt.textContent, () => {
                            // ✅ Auto-seleccionar inquilino asociado
                            if (v.inquilino_asociado_id) {
                                const inquilinoId = v.inquilino_asociado_id;
                                const inquilinoOpt = document.querySelector(`#inquilinoSelectOptions .custom-select-option[data-value="${inquilinoId}"]`);

                                if (inquilinoOpt) {
                                    console.log(`🔄 Auto-seleccionando inquilino ${inquilinoId}`);
                                    inquilinoOpt.click();
                                } else {
                                    console.warn(`⚠️ Inquilino asociado ${inquilinoId} no encontrado en lista`);
                                }
                            }
                            updateAlquilerPreview();
                        });
                    };
                    vehiculoOptions.appendChild(opt);
                });

                // Configurar Inquilinos
                const inquilinoOptions = document.getElementById('inquilinoSelectOptions');
                const inquilinoText = document.getElementById('inquilinoSelectText');
                const inquilinoValue = document.getElementById('inquilinoSelectValue');

                inquilinoOptions.innerHTML = '';
                inquilinoText.textContent = 'Seleccionar inquilino...';
                inquilinoText.classList.add('placeholder');
                inquilinoValue.value = '';

                data.inquilinos.forEach(i => {
                    const opt = document.createElement('div');
                    opt.className = 'custom-select-option';
                    opt.dataset.value = i.id;
                    opt.textContent = `${i.nombre_apellido} - ${i.cedula || 'Sin cédula'}`;

                    opt.onclick = () => {
                        selectOption('inquilinoSelectWrapper', i.id, opt.textContent, () => {
                            updateAlquilerPreview();
                        });
                    };
                    inquilinoOptions.appendChild(opt);
                });

                openModal('agregarAlquilerModal');
            }
        })
        .catch(err => {
            console.error('Error:', err);
            mostrarError('Error al cargar datos disponibles');
        });
}

function updateAlquilerPreview() {
    const vehiculoId = document.getElementById('vehiculoSelectValue')?.value;
    const inquilinoId = document.getElementById('inquilinoSelectValue')?.value;
    const preview = document.getElementById('alquilerPreview');

    if (vehiculoId && inquilinoId) {
        const vehiculoOpt = document.querySelector(`#vehiculoSelectOptions .custom-select-option[data-value="${vehiculoId}"]`);
        const inquilinoText = document.getElementById('inquilinoSelectText').textContent;

        if (vehiculoOpt) {
            const precio = vehiculoOpt.dataset.precio || '0';
            const propietario = vehiculoOpt.dataset.propietario || '';

            document.getElementById('previewVehiculo').textContent = vehiculoOpt.textContent.split(' (')[0];
            document.getElementById('previewPrecio').textContent = `$${parseFloat(precio).toFixed(2)}`;
            document.getElementById('previewInquilino').textContent = inquilinoText;
            document.getElementById('previewPropietario').textContent = propietario;

            preview.style.display = 'block';
        }
    } else {
        preview.style.display = 'none';
    }
}

document.getElementById('agregarAlquilerForm')?.addEventListener('submit', function (e) {
    e.preventDefault();

    const formData = {
        semana_id: document.getElementById('agregarAlquilerSemanaId').value,
        vehiculo_id: document.getElementById('vehiculoSelectValue').value,
        inquilino_id: document.getElementById('inquilinoSelectValue').value,
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

                semanasAbiertas.delete(parseInt(formData.semana_id));
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

    document.getElementById('editDetalleId').value = detalleId;
    document.querySelector('#editarDetalleForm [name="precio_semanal"]').value = detalle.precio_semanal || '';
    document.querySelector('#editarDetalleForm [name="dias_trabajo"]').value = detalle.dias_trabajo || '';
    document.querySelector('#editarDetalleForm [name="inversion_mecanica"]').value = detalle.inversiones_totales || 0;
    document.querySelector('#editarDetalleForm [name="concepto_inversion"]').value = detalle.concepto_inversion || '';
    document.querySelector('#editarDetalleForm [name="monto_descuento"]').value = detalle.monto_descuento || '';
    document.querySelector('#editarDetalleForm [name="concepto_descuento"]').value = detalle.concepto_descuento || '';
    document.querySelector('#editarDetalleForm [name="monto_deuda"]').value = detalle.monto_deuda || '';
    document.querySelector('#editarDetalleForm [name="notas"]').value = detalle.notas || '';

    // Poblar campos de pago
    const bancoSelect = document.querySelector('#editarDetalleForm [name="banco_id"]');
    const fechaPagoInput = document.querySelector('#editarDetalleForm [name="fecha_confirmacion_pago"]');
    const pagoConfirmadoCheck = document.querySelector('#editarDetalleForm [name="pago_confirmado"]');

    if (fechaPagoInput) fechaPagoInput.value = detalle.fecha_confirmacion_pago || '';
    if (pagoConfirmadoCheck) pagoConfirmadoCheck.checked = !!detalle.pago_confirmado;

    // Cargar bancos y seleccionar el actual
    if (bancoSelect) {
        fetch('/alquiler/bancos/json')
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    bancoSelect.innerHTML = '<option value="">Seleccionar banco...</option>';

                    // Opción efectivo
                    const optEfectivo = document.createElement('option');
                    optEfectivo.value = '0';
                    optEfectivo.textContent = 'EFECTIVO';
                    bancoSelect.appendChild(optEfectivo);

                    data.bancos.forEach(b => {
                        const opt = document.createElement('option');
                        opt.value = b.id;
                        opt.textContent = `${b.banco} - ${b.cuenta}`;
                        bancoSelect.appendChild(opt);
                    });

                    // Seleccionar valor actual
                    bancoSelect.value = detalle.banco_id || (detalle.pago_confirmado && !detalle.banco_id ? '0' : '');
                }
            });
    }

    if (semanaId) {
        fetch(`/alquiler/semanas/${semanaId}/disponibles`)
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    // Configurar Vehículo
                    const vehiculoOptions = document.getElementById('editVehiculoSelectOptions');
                    vehiculoOptions.innerHTML = '';

                    // Opción actual
                    const currentV = {
                        id: detalle.vehiculo_id,
                        text: `${detalle.vehiculo_placa} - ${detalle.vehiculo_marca} ${detalle.vehiculo_modelo} (Actual)`
                    };

                    const addOption = (v, isCurrent = false) => {
                        const opt = document.createElement('div');
                        opt.className = 'custom-select-option' + (isCurrent ? ' selected' : '');
                        opt.dataset.value = v.id;
                        opt.textContent = isCurrent ? v.text : `${v.placa} - ${v.marca} ${v.modelo} (${v.propietario_nombre})`;
                        opt.onclick = () => selectOption('editVehiculoSelectWrapper', v.id, opt.textContent);
                        vehiculoOptions.appendChild(opt);
                    };

                    addOption(currentV, true);
                    selectOption('editVehiculoSelectWrapper', currentV.id, currentV.text);

                    data.vehiculos.forEach(v => {
                        if (v.id !== detalle.vehiculo_id) {
                            addOption(v);
                        }
                    });

                    // Configurar Inquilino
                    const inquilinoOptions = document.getElementById('editInquilinoSelectOptions');
                    inquilinoOptions.innerHTML = '';

                    const currentI = {
                        id: detalle.inquilino_id,
                        text: `${detalle.inquilino_nombre} (Actual)`
                    };

                    const addIOption = (i, isCurrent = false) => {
                        const opt = document.createElement('div');
                        opt.className = 'custom-select-option' + (isCurrent ? ' selected' : '');
                        opt.dataset.value = i.id;
                        opt.textContent = isCurrent ? i.text : `${i.nombre_apellido} - ${i.cedula || 'Sin cédula'}`;
                        opt.onclick = () => selectOption('editInquilinoSelectWrapper', i.id, opt.textContent);
                        inquilinoOptions.appendChild(opt);
                    };

                    addIOption(currentI, true);
                    selectOption('editInquilinoSelectWrapper', currentI.id, currentI.text);

                    data.inquilinos.forEach(i => {
                        if (i.id !== detalle.inquilino_id) {
                            addIOption(i);
                        }
                    });
                }
            });
    }

    openModal('editarDetalleModal');
}

document.getElementById('editarDetalleForm')?.addEventListener('submit', function (e) {
    e.preventDefault();

    const detalleId = document.getElementById('editDetalleId').value;

    const formData = {
        detalle_id: detalleId,
        vehiculo_id: document.getElementById('editVehiculoSelectValue')?.value,
        inquilino_id: document.getElementById('editInquilinoSelectValue')?.value,
        precio_semanal: document.querySelector('#editarDetalleForm [name="precio_semanal"]')?.value,
        dias_trabajo: document.querySelector('#editarDetalleForm [name="dias_trabajo"]')?.value,
        inversion_mecanica: document.querySelector('#editarDetalleForm [name="inversion_mecanica"]')?.value,
        concepto_inversion: document.querySelector('#editarDetalleForm [name="concepto_inversion"]')?.value,
        monto_descuento: document.querySelector('#editarDetalleForm [name="monto_descuento"]')?.value,
        concepto_descuento: document.querySelector('#editarDetalleForm [name="concepto_descuento"]')?.value,
        monto_deuda: document.querySelector('#editarDetalleForm [name="monto_deuda"]')?.value,
        banco_id: document.querySelector('#editarDetalleForm [name="banco_id"]')?.value || null,
        fecha_confirmacion_pago: document.querySelector('#editarDetalleForm [name="fecha_confirmacion_pago"]')?.value,
        pago_confirmado: document.querySelector('#editarDetalleForm [name="pago_confirmado"]')?.checked || false,
        notas: document.querySelector('#editarDetalleForm [name="notas"]')?.value
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
// CORRECCIÓN 3: ELIMINAR CON MODAL DE CONFIRMACIÓN
// ==========================================
// Modificar función eliminarDetalle para usar modal
function eliminarDetalle(detalleId, semanaId) {
    // Guardar IDs en campos ocultos
    document.getElementById('eliminarDetalleId').value = detalleId;
    document.getElementById('eliminarSemanaId').value = semanaId;

    // Abrir modal de confirmación
    openModal('confirmarEliminarModal');
}
// Nueva función para ejecutar la eliminación
function confirmarEliminacionDetalle() {
    const detalleId = document.getElementById('eliminarDetalleId').value;
    const semanaId = document.getElementById('eliminarSemanaId').value;

    if (!detalleId || !semanaId) {
        mostrarError('Error: datos de eliminación no válidos');
        return;
    }

    // Cerrar modal
    closeModal('confirmarEliminarModal');

    // Ejecutar eliminación
    fetch(`/alquiler/detalles/${detalleId}/eliminar`, {
        method: 'POST'
    })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                mostrarExito('✅ Alquiler eliminado correctamente');
                semanasAbiertas.delete(parseInt(semanaId));
                cargarDetallesSemana(parseInt(semanaId));
            } else {
                mostrarError(data.message || 'Error al eliminar');
            }
        })
        .catch(err => {
            console.error('Error:', err);
            mostrarError('Error al eliminar alquiler');
        });
}

// ==========================================
// CERRAR SEMANA
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
// ELIMINAR SEMANA
// ==========================================
function eliminarSemana_(semanaId, totalVehiculos) {
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

// Función para abrir el modal con información de la semana
function abrirModalEliminarSemana(semanaId) {
    console.log(`🗑️ Abriendo modal para eliminar semana ${semanaId}`);

    // Verificar permisos
    if (window.APP_DATA.userRol !== 'admin') {
        mostrarError('⛔ Solo administradores pueden eliminar semanas');
        return;
    }

    // Buscar información de la semana en el DOM
    const semanaItem = document.querySelector(`[data-semana-id="${semanaId}"]`);
    if (!semanaItem) {
        mostrarError('No se encontró información de la semana');
        return;
    }

    // Extraer datos del DOM
    const semanaHeader = semanaItem.querySelector('.semana-header');
    const semanaTitle = semanaItem.querySelector('.semana-title').textContent.trim();
    const semanaMeta = semanaItem.querySelector('.semana-meta').textContent;

    // Parsear meta info (formato: "Semana #X • Y Vehículos • Z Socios • W Inquilinos • $XXX")
    const metaParts = semanaMeta.split('•').map(s => s.trim());
    const totalVehiculos = parseInt(metaParts[1]) || 0;
    const totalSocios = parseInt(metaParts[2]) || 0;
    const totalInquilinos = parseInt(metaParts[3]) || 0;
    const ingresoTotal = metaParts[4] || '$0.00';

    // Llenar modal
    document.getElementById('eliminarSemanaCompleta_id').value = semanaId;
    document.getElementById('eliminarSemanaCompleta_vehiculos').value = totalVehiculos;

    document.getElementById('eliminarSemanaModal_fecha').textContent = semanaTitle.replace('Semana: ', '');
    document.getElementById('eliminarSemanaModal_totalVehiculos').textContent = `${totalVehiculos} vehículos`;
    document.getElementById('eliminarSemanaModal_totalSocios').textContent = `${totalSocios} socios`;
    document.getElementById('eliminarSemanaModal_totalInquilinos').textContent = `${totalInquilinos} inquilinos`;
    document.getElementById('eliminarSemanaModal_ingresoTotal').textContent = ingresoTotal;

    // Mensaje según cantidad de vehículos
    const mensajeElement = document.getElementById('eliminarSemanaModal_mensaje');
    if (totalVehiculos > 0) {
        mensajeElement.innerHTML = `
            ⚠️ Esta semana contiene <strong>${totalVehiculos} alquiler${totalVehiculos !== 1 ? 'es' : ''}</strong> que 
            ${totalVehiculos !== 1 ? 'serán eliminados' : 'será eliminado'} permanentemente. 
            Los vehículos quedarán disponibles nuevamente.
        `;
        document.getElementById('eliminarSemanaModal_adminWarning').style.display = 'block';
    } else {
        mensajeElement.innerHTML = '¿Está seguro de eliminar esta semana vacía?';
        document.getElementById('eliminarSemanaModal_adminWarning').style.display = 'none';
    }

    // Resetear checkbox
    document.getElementById('confirmarEliminacionSemanaCheck').checked = false;
    document.getElementById('btnConfirmarEliminarSemana').disabled = true;

    // Abrir modal
    openModal('confirmarEliminarSemanaModal');
}

// Habilitar botón cuando se marca el checkbox
document.getElementById('confirmarEliminacionSemanaCheck')?.addEventListener('change', function () {
    document.getElementById('btnConfirmarEliminarSemana').disabled = !this.checked;
});

// Función para ejecutar la eliminación
function ejecutarEliminacionSemana() {
    const semanaId = document.getElementById('eliminarSemanaCompleta_id').value;
    const totalVehiculos = document.getElementById('eliminarSemanaCompleta_vehiculos').value;

    if (!semanaId) {
        mostrarError('Error: ID de semana no válido');
        return;
    }

    if (window.APP_DATA.userRol !== 'admin') {
        mostrarError('⛔ Solo administradores pueden eliminar semanas');
        return;
    }

    // Deshabilitar botón
    const btnEliminar = document.getElementById('btnConfirmarEliminarSemana');
    btnEliminar.disabled = true;
    btnEliminar.innerHTML = `
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" style="animation: spin 1s linear infinite;">
            <circle cx="12" cy="12" r="10" stroke-width="3" stroke-dasharray="32"/>
        </svg>
        Eliminando...
    `;

    console.log(`🗑️ Eliminando semana ${semanaId} con ${totalVehiculos} vehículos...`);

    // Ejecutar eliminación
    fetch(`/alquiler/semanas/${semanaId}/eliminar`, {
        method: 'POST'
    })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                mostrarExito(`✅ Semana eliminada correctamente (${totalVehiculos} alquileres liberados)`);
                closeModal('confirmarEliminarSemanaModal');

                // Recargar página después de 1 segundo
                setTimeout(() => {
                    location.reload();
                }, 1000);
            } else {
                mostrarError(data.message || 'Error al eliminar semana');
                btnEliminar.disabled = false;
                btnEliminar.innerHTML = `
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
                </svg>
                Sí, Eliminar Semana Completa
            `;
            }
        })
        .catch(err => {
            console.error('❌ Error:', err);
            mostrarError('Error al eliminar semana');
            btnEliminar.disabled = false;
            btnEliminar.innerHTML = `
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
            </svg>
            Sí, Eliminar Semana Completa
        `;
        });
}

// Actualizar función eliminarSemana original para usar el modal
function eliminarSemana(semanaId, totalVehiculos) {
    // Redirigir a la nueva función del modal
    abrirModalEliminarSemana(semanaId);
}


// ==========================================
// GESTIONAR INVERSIONES
function gestionarInversiones(detalleId) {
    try {
        console.log(`🔧 Gestionando inversiones del detalle ${detalleId}`);

        const modalId = 'inversionesModal';
        const modalEl = document.getElementById(modalId);

        if (!modalEl) {
            console.error('No existe modal id="inversionesModal"');
            return;
        }

        // 🚀 CRÍTICO: Mover el modal al body para evitar problemas de stacking context o transformaciones en padres
        if (modalEl.parentNode !== document.body) {
            document.body.appendChild(modalEl);
        }

        const inputId = document.getElementById('inversionDetalleId');
        if (inputId) inputId.value = detalleId;

        cargarInversiones(detalleId);

        // Estilos base del overlay
        modalEl.style.cssText = `
            display: flex !important;
            position: fixed !important;
            top: 0 !important;
            left: 0 !important;
            width: 100vw !important;
            height: 100vh !important;
            background-color: rgba(0, 0, 0, 0.5) !important;
            z-index: 100000 !important;
            align-items: center !important;
            justify-content: center !important;
            opacity: 1 !important;
            visibility: visible !important;
        `;

        // Estilos del contenido interno
        const modalContent = modalEl.querySelector('.modal');
        if (modalContent) {
            modalContent.style.cssText = `
                display: block !important;
                position: relative !important;
                z-index: 100001 !important;
                opacity: 1 !important;
                visibility: visible !important;
                transform: none !important;
                max-height: 90vh !important;
                overflow-y: auto !important;
            `;
        }

        // Handler para cerrar
        modalEl.onclick = function (e) {
            if (e.target === modalEl) {
                modalEl.style.display = 'none';
                document.body.style.overflow = '';
            }
        };

    } catch (e) {
        console.error(e);
        alert('Error: ' + e.message);
    }
}

function cargarInversiones(detalleId) {
    const lista = document.getElementById('listaInversiones');
    const totalElement = document.getElementById('totalInversiones');

    lista.innerHTML = '<p style="text-align: center; padding: 20px;"><svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" style="animation: spin 1s linear infinite;"><circle cx="12" cy="12" r="10" stroke-width="3" stroke-dasharray="32"/></svg></p>';

    fetch(`/alquiler/detalles/${detalleId}/inversiones`)
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                if (data.inversiones.length === 0) {
                    lista.innerHTML = `
                        <div style="text-align: center; padding: 30px; color: #6c757d;">
                            <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" style="opacity: 0.3; margin-bottom: 12px;">
                                <circle cx="12" cy="12" r="10"/>
                                <path d="M12 8v4m0 4h.01"/>
                            </svg>
                            <p style="margin: 0; font-size: 14px;">No hay inversiones registradas en esta semana</p>
                        </div>
                    `;
                } else {
                    // Ordenar por fecha descendente (más reciente primero) y luego por ID descendente
                    const inversionesOrdenadas = data.inversiones.sort((a, b) => {
                        const fechaA = new Date(a.fecha.split('/').reverse().join('-'));
                        const fechaB = new Date(b.fecha.split('/').reverse().join('-'));
                        if (fechaB - fechaA !== 0) {
                            return fechaB - fechaA;
                        }
                        return b.id - a.id; // Desempate por ID (Mayor ID = más reciente)
                    });

                    lista.innerHTML = inversionesOrdenadas.map((inv, index) => `
                        <div style="padding: 14px; border: 2px solid ${index === 0 ? '#28a745' : '#dee2e6'}; border-radius: 8px; margin-bottom: 10px; background: ${index === 0 ? '#f1f9f4' : 'white'}; transition: all 0.3s;" ${index === 0 ? 'class="nueva-inversion"' : ''}>
                            <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 10px;">
                                <div style="flex: 1;">
                                    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 6px;">
                                        <strong style="color: #2c3e50; font-size: 15px;">${inv.tipo_trabajo}</strong>
                                        ${inv.tipo_trabajo === 'Lavado'
                            ? `<span style="padding: 3px 10px; background: #17a2b8; color: white; border-radius: 12px; font-size: 11px; font-weight: 600;">Lavado de salida</span>`
                            : `<span style="padding: 3px 10px; background: ${inv.tipo_inversion === 'falla_mecanica' ? '#0724FFFF' : '#dc3545'}; color: white; border-radius: 12px; font-size: 11px; font-weight: 600;">
                                                ${inv.tipo_inversion === 'falla_mecanica' ? 'Falla Mecánica' : ' Accidente'}
                                               </span>`
                        }
                                        ${index === 0 ? '<span style="padding: 3px 10px; background: #28a745; color: white; border-radius: 12px; font-size: 11px; font-weight: 600; animation: pulse 1s infinite;"> NUEVO</span>' : ''}
                                    </div>
                                    <div style="font-size: 13px; color: #495057; margin-bottom: 8px; line-height: 1.4;">
                                        ${inv.descripcion}
                                    </div>
                                    <div style="font-size: 12px; color: #6c757d; display: flex; gap: 16px;">
                                        <span> ${inv.fecha}</span>
                                        ${inv.tipo_trabajo !== 'Lavado' ? `<span> ${inv.mecanico}</span>` : ''}
                                    </div>
                                </div>
                                <div style="text-align: right; margin-left: 16px;">
                                    <div style="font-size: 12px; color: #6c757d; margin-bottom: 4px;">Costo</div>
                                    <strong style="color: #28a745; font-size: 18px; font-weight: 700;">$${parseFloat(inv.costo).toFixed(2)}</strong>
                                </div>
                            </div>
                        </div>
                    `).join('');

                    // ✅ Highlight animado para el item nuevo
                    setTimeout(() => {
                        const nuevoItem = lista.querySelector('.nueva-inversion');
                        if (nuevoItem) {
                            nuevoItem.style.transform = 'scale(1.02)';
                            setTimeout(() => {
                                nuevoItem.style.transform = 'scale(1)';
                            }, 300);
                        }
                    }, 100);
                }

                // ✅ Actualizar total con animación
                const totalAnterior = parseFloat(totalElement.textContent.replace('$', '').replace(',', ''));
                const totalNuevo = parseFloat(data.total);

                if (totalNuevo !== totalAnterior) {
                    totalElement.style.transition = 'all 0.3s';
                    totalElement.style.transform = 'scale(1.1)';
                    totalElement.style.color = '#28a745';

                    setTimeout(() => {
                        totalElement.textContent = `$${totalNuevo.toFixed(2)}`;

                        setTimeout(() => {
                            totalElement.style.transform = 'scale(1)';
                            totalElement.style.color = 'inherit';
                        }, 200);
                    }, 150);
                } else {
                    totalElement.textContent = `$${totalNuevo.toFixed(2)}`;
                }

                inversionesCache.set(detalleId, data);

                console.log(`✅ ${data.inversiones.length} inversiones cargadas. Total: $${data.total}`);
            }
        })
        .catch(err => {
            console.error('Error:', err);
            lista.innerHTML = '<p style="text-align: center; color: #dc3545; padding: 20px;">❌ Error al cargar inversiones</p>';
        });
}

document.getElementById('nuevaInversionForm')?.addEventListener('submit', function (e) {
    e.preventDefault();

    const detalleId = document.getElementById('inversionDetalleId').value;
    const submitBtn = this.querySelector('button[type="submit"]');
    const originalBtnText = submitBtn.innerHTML;

    // Deshabilitar botón durante envío
    submitBtn.disabled = true;
    submitBtn.innerHTML = `
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" style="animation: spin 1s linear infinite;">
            <circle cx="12" cy="12" r="10" stroke-width="3" stroke-dasharray="32"/>
        </svg>
        Guardando...
    `;

    const formData = {
        detalle_id: detalleId,
        tipo_trabajo_id: this.tipo_trabajo_id.value,
        mecanico_id: this.mecanico_id.value,
        tipo_inversion: this.tipo_inversion.value,
        descripcion: this.descripcion.value,
        costo: parseFloat(this.costo.value)
    };

    console.log('📤 Enviando nueva inversión:', formData);

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
                console.log(`✅ Inversión creada. Total acumulado: $${data.total_inversion}`);

                // ✅ SIN ALERT - Feedback visual directo
                submitBtn.innerHTML = `
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
                </svg>
                ¡Inversión Agregada!
            `;
                submitBtn.style.background = '#28a745';

                // Resetear formulario
                this.reset();

                // ✅ RECARGAR LISTA AUTOMÁTICAMENTE
                setTimeout(() => {
                    cargarInversiones(detalleId);
                }, 300);

                // ✅ Actualizar el input de inversión en el modal de edición (si está abierto)
                const inversionInput = document.querySelector('#editarDetalleForm [name="inversion_mecanica"]');
                if (inversionInput) {
                    inversionInput.value = data.total_inversion;
                    inversionInput.style.background = '#d4edda';
                    setTimeout(() => {
                        inversionInput.style.background = '';
                    }, 1500);
                }

                // ✅ Actualizar la tabla principal si está visible
                const currentSemanaId = Array.from(semanasAbiertas.keys()).find(id => {
                    const detalles = semanasAbiertas.get(id);
                    return detalles && detalles.some(d => d.id == detalleId);
                });

                if (currentSemanaId) {
                    // Refrescar la fila específica en la tabla
                    actualizarFilaInversion(detalleId, data.total_inversion);
                }

                // Restaurar botón después de 2 segundos
                setTimeout(() => {
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = originalBtnText;
                    submitBtn.style.background = '';
                }, 2000);

            } else {
                console.error('❌ Error:', data.message);

                submitBtn.disabled = false;
                submitBtn.innerHTML = originalBtnText;

                // Mostrar error sin alert - usar notificación visual
                mostrarNotificacion('Error al crear inversión: ' + data.message, 'error');
            }
        })
        .catch(err => {
            console.error('❌ Error:', err);

            submitBtn.disabled = false;
            submitBtn.innerHTML = originalBtnText;

            mostrarNotificacion('Error de conexión al crear inversión', 'error');
        });
});

// ==========================================
// NUEVA FUNCIÓN: ACTUALIZAR FILA DE INVERSIÓN
// ==========================================

function actualizarFilaInversion(detalleId, nuevoTotal) {
    const fila = document.querySelector(`tr[data-detalle-id="${detalleId}"]`);
    if (!fila) return;

    // Buscar la celda de inversión (columna 9)
    const celdas = fila.querySelectorAll('td');
    if (celdas.length < 9) return;

    const celdaInversion = celdas[8]; // Índice 8 = columna "Inversión"
    const spanMonto = celdaInversion.querySelector('span');

    if (spanMonto) {
        // Animación de actualización
        celdaInversion.style.transition = 'all 0.3s';
        celdaInversion.style.background = '#d4edda';
        celdaInversion.style.transform = 'scale(1.05)';

        spanMonto.textContent = `$${parseFloat(nuevoTotal).toFixed(2)}`;

        setTimeout(() => {
            celdaInversion.style.transform = 'scale(1)';
            setTimeout(() => {
                celdaInversion.style.background = '';
            }, 500);
        }, 300);

        console.log(`✅ Fila actualizada: Detalle ${detalleId} -> $${nuevoTotal}`);
    }
}

function mostrarNotificacion(mensaje, tipo = 'success') {
    // Crear elemento de notificación
    const notif = document.createElement('div');
    notif.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${tipo === 'success' ? '#28a745' : '#dc3545'};
        color: white;
        padding: 16px 24px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        z-index: 10000;
        font-size: 14px;
        font-weight: 500;
        display: flex;
        align-items: center;
        gap: 12px;
        animation: slideInRight 0.3s ease;
        max-width: 400px;
    `;

    const icono = tipo === 'success'
        ? '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>'
        : '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>';

    notif.innerHTML = `${icono}<span>${mensaje}</span>`;

    document.body.appendChild(notif);

    // Auto-remover después de 3 segundos
    setTimeout(() => {
        notif.style.animation = 'slideOutRight 0.3s ease';
        setTimeout(() => {
            notif.remove();
        }, 300);
    }, 3000);
}


// ==========================================
// EXPORTAR A EXCEL
// ==========================================
function exportarExcelSemana(semanaId) {
    window.location.href = `/alquiler/semanas/${semanaId}/exportar-excel`;
}

// ==========================================
// FILTROS
// ==========================================
function setupFiltros() {
    const filtroEstado = document.getElementById('filtroEstado');
    if (filtroEstado) {
        filtroEstado.addEventListener('change', function () {
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
    alert(mensaje);
}

function mostrarError(mensaje) {
    alert('❌ ' + mensaje);
}

console.log('✅ alquileres.js cargado completamente (v4.0 - DEBUG ALERTS)');

// ==========================================
// CONFIRMAR PAGO (MODAL)
// ==========================================
function abrirModalConfirmarPago(detalleId) {
    console.log(`💰 Abriendo confirmación de pago para detalle ${detalleId}`);

    try {
        const modalId = 'confirmarPagoModal';
        const modalEl = document.getElementById(modalId);

        if (!modalEl) {
            throw new Error('No existe el elemento HTML con id="' + modalId + '"');
        }

        // Reset form
        const form = document.getElementById('confirmarPagoForm');
        if (form) form.reset();

        // Set ID
        const detalleIdInput = document.getElementById('pagoDetalleId');
        if (detalleIdInput) detalleIdInput.value = detalleId;

        // Load banks
        cargarBancosModal();

        // 🚀 CRÍTICO: Mover el modal al body para evitar problemas de stacking context
        if (modalEl.parentNode !== document.body) {
            document.body.appendChild(modalEl);
        }

        if (typeof openModal === 'function') {
            openModal(modalId);
        } else {
            modalEl.classList.add('active');
            document.body.style.overflow = 'hidden';
        }

        // Estilos base del overlay
        modalEl.style.cssText = `
        display: flex !important;
        position: fixed !important;
        top: 0 !important;
        left: 0 !important;
        width: 100vw !important;
        height: 100vh !important;
        background-color: rgba(0, 0, 0, 0.5) !important;
        z-index: 100000 !important;
        align-items: center !important;
        justify-content: center !important;
        opacity: 1 !important;
        visibility: visible !important;
    `;

        // Estilos del contenido interno
        const modalContent = modalEl.querySelector('.modal');
        if (modalContent) {
            modalContent.style.cssText = `
            display: block !important;
            position: relative !important;
            z-index: 100001 !important;
            opacity: 1 !important;
            visibility: visible !important;
            transform: none !important;
            max-height: 90vh !important;
            overflow-y: auto !important;
        `;
        }

        // Handler para cerrar
        modalEl.onclick = function (e) {
            if (e.target === modalEl) {
                modalEl.style.display = 'none';
                document.body.style.overflow = '';
            }
        };

    } catch (e) {
        console.error(e);
        alert('❌ ERROR CRÍTICO EN JS: ' + e.message);
    }


    // Reset form (ya realizado arriba)

    // Limpiar previews y flag de eliminación
    const previewContainer = document.getElementById('pagoPreviewContainer');
    const fileInfo = document.getElementById('fileInfo');
    const deleteFlag = document.getElementById('eliminarComprobanteFlag');

    if (previewContainer) previewContainer.innerHTML = '';
    if (fileInfo) {
        fileInfo.style.display = 'none';
        fileInfo.innerHTML = '';
    }
    if (deleteFlag) deleteFlag.value = 'false';

    // Buscar el detalle en nuestras semanas abiertas
    let detalle = null;
    semanasAbiertas.forEach((detalles) => {
        const found = detalles.find(d => d.id == detalleId);
        if (found) detalle = found;
    });

    if (!detalle) {
        console.error(`❌ No se encontró el detalle ${detalleId} en semanasAbiertas`, semanasAbiertas);
        mostrarError('No se encontró la información del alquiler');
        return;
    }

    // Llenar datos del modal
    // document.getElementById('confirmarPagoDetalleId').value = detalleId; // REDUNDANTE Y ERRONEO

    // Asegurar que tenemos strings válidos
    const marca = detalle.vehiculo_marca || 'S/M';
    const modelo = detalle.vehiculo_modelo || 'S/M';
    const placa = detalle.vehiculo_placa || 'S/P';
    const inquilino = detalle.inquilino_nombre || 'Sin Inquilino';
    const monto = parseFloat(detalle.nomina_final || 0).toFixed(2);

    document.getElementById('confirmarPagoInfo').textContent = `${marca} ${modelo} (${placa}) / ${inquilino}`;
    document.getElementById('confirmarPagoMonto').textContent = `$${monto}`;

    // Fecha por defecto hoy
    const hoy = new Date().toISOString().split('T')[0];
    document.getElementById('pagoFecha').value = detalle.fecha_confirmacion_pago || hoy;

    const checkbox = document.getElementById('pagoConfirmadoCheck');
    if (checkbox) {
        checkbox.checked = detalle.pago_confirmado !== false;
    }

    // Mostrar comprobante existente si hay
    if (detalle.comprobante_pago_path && previewContainer) {
        const path = `/static/${detalle.comprobante_pago_path}`;
        const isImage = detalle.comprobante_pago_path.match(/\.(jpg|jpeg|png|gif|webp)$/i);

        const card = document.createElement('div');
        card.className = 'current-image-item';
        card.innerHTML = `
            ${isImage ? `<img src="${path}" alt="Comprobante">` :
                `<div style="display: flex; align-items: center; justify-content: center; height: 100%; color: #6c757d; font-size: 24px;">📄</div>`}
            <div class="preview-badge">EXISTENTE</div>
            <button type="button" class="btn-delete-preview" onclick="eliminarComprobante(true)" title="Eliminar comprobante actual">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3">
                    <path d="M18 6L6 18M6 6l12 12"></path>
                </svg>
            </button>
        `;
        previewContainer.appendChild(card);

        if (fileInfo) {
            fileInfo.innerHTML = `<a href="${path}" target="_blank" class="text-primary" style="text-decoration: underline; font-weight: 500;">Ver archivo original</a>`;
            fileInfo.style.display = 'block';
        }
    }

    // Cargar bancos en el select del modal
    // Si está confirmado pero no tiene banco_id, es EFECTIVO ('0')
    const initialBancoId = (detalle.pago_confirmado && !detalle.banco_id) ? '0' : detalle.banco_id;
    cargarBancosModal(initialBancoId);

    openModal('confirmarPagoModal');
}

function cargarBancosModal(selectedBancoId = null) {
    const optionsContainer = document.getElementById('pagoBancoSelectOptions');
    const triggerText = document.getElementById('pagoBancoSelectText');
    const hiddenInput = document.getElementById('pagoBancoSelectValue');

    optionsContainer.innerHTML = '<div class="custom-select-option no-results">Cargando bancos...</div>';

    fetch('/alquiler/bancos/json')
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                optionsContainer.innerHTML = '';

                // OPCIÓN EFECTIVO
                const cashOption = document.createElement('div');
                cashOption.className = 'custom-select-option';
                cashOption.innerHTML = '<span style="font-weight: 600; color: #2ecc71;">💵 EFECTIVO</span>';
                cashOption.onclick = () => {
                    selectOption('pagoBancoSelectWrapper', '0', 'EFECTIVO');
                };

                if (selectedBancoId === 0 || selectedBancoId === '0' || (selectedBancoId === null && triggerText.textContent === 'EFECTIVO')) {
                    selectOption('pagoBancoSelectWrapper', '0', 'EFECTIVO');
                }
                optionsContainer.appendChild(cashOption);

                data.bancos.forEach(banco => {
                    const option = document.createElement('div');
                    option.className = 'custom-select-option';
                    option.textContent = `${banco.banco} - ${banco.cuenta}`;
                    option.onclick = () => {
                        selectOption('pagoBancoSelectWrapper', banco.id, banco.banco);
                    };

                    if (selectedBancoId && banco.id == selectedBancoId) {
                        selectOption('pagoBancoSelectWrapper', banco.id, banco.banco);
                    }

                    optionsContainer.appendChild(option);
                });

                if (data.bancos.length === 0 && !cashOption) {
                    optionsContainer.innerHTML = '<div class="custom-select-option no-results">No hay bancos registrados</div>';
                }
            }
        })
        .catch(err => {
            console.error('Error al cargar bancos:', err);
            optionsContainer.innerHTML = '<div class="custom-select-option no-results text-danger">Error al cargar bancos</div>';
        });
}

function previewPaymentProof(input) {
    const container = document.getElementById('pagoPreviewContainer');
    const fileInfo = document.getElementById('fileInfo');

    // Al seleccionar nuevo, cancelamos la eliminación del anterior si existía
    document.getElementById('eliminarComprobanteFlag').value = 'false';

    if (input.files && input.files[0]) {
        const file = input.files[0];
        container.innerHTML = ''; // Limpiar anteriores (incluyendo el "Existente")

        fileInfo.textContent = `Seleccionado: ${file.name} (${(file.size / 1024).toFixed(1)} KB)`;
        fileInfo.style.display = 'block';

        const card = document.createElement('div');
        card.className = 'current-image-item';

        if (file.type.startsWith('image/')) {
            const reader = new FileReader();
            reader.onload = function (e) {
                card.innerHTML = `
                    <img src="${e.target.result}" alt="Preview">
                    <div class="preview-badge">NUEVO</div>
                    <button type="button" class="btn-delete-preview" onclick="eliminarComprobante(false)" title="Quitar archivo">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3">
                            <path d="M18 6L6 18M6 6l12 12"></path>
                        </svg>
                    </button>
                `;
                container.appendChild(card);
            };
            reader.readAsDataURL(file);
        } else {
            card.innerHTML = `
                <div style="display: flex; align-items: center; justify-content: center; height: 100%; color: #6c757d; font-size: 24px;">📄</div>
                <div class="preview-badge">PDF</div>
                <button type="button" class="btn-delete-preview" onclick="eliminarComprobante(false)" title="Quitar archivo">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3">
                        <path d="M18 6L6 18M6 6l12 12"></path>
                    </svg>
                </button>
            `;
            container.appendChild(card);
        }
    }
}

function eliminarComprobante(existente = false) {
    const container = document.getElementById('pagoPreviewContainer');
    const fileInfo = document.getElementById('fileInfo');
    const input = document.getElementById('pagoComprobante');

    if (existente) {
        document.getElementById('eliminarComprobanteFlag').value = 'true';
    }

    // Reset inputs y UI
    input.value = '';
    container.innerHTML = '';
    fileInfo.style.display = 'none';
    fileInfo.innerHTML = '';

    console.log(`🗑️ Comprobante quitado${existente ? ' (marcado para eliminar del servidor)' : ''}`);
}

// Handler para el form de confirmación
document.getElementById('confirmarPagoForm').addEventListener('submit', function (e) {
    e.preventDefault();

    const formData = new FormData(this);
    const detalleId = document.getElementById('confirmarPagoDetalleId').value;
    const btn = document.getElementById('btnConfirmarPagoSubmit');

    // Agregar el valor del checkbox manualmente si es necesario
    formData.append('pago_confirmado', document.getElementById('pagoConfirmadoCheck').checked);

    btn.disabled = true;
    btn.innerHTML = '<span class="loading-spinner"></span> Confirmando...';

    fetch(`/alquiler/detalles/${detalleId}/confirmar_pago`, {
        method: 'POST',
        body: formData
    })
        .then(async res => {
            const isJson = res.headers.get('content-type')?.includes('application/json');
            const data = isJson ? await res.json() : null;

            if (!res.ok) {
                console.error('Error response:', res.status, data);
                throw new Error(data?.message || `Error del servidor (${res.status})`);
            }
            return data;
        })
        .then(data => {
            if (data.success) {
                mostrarExito(data.message);
                closeModal('confirmarPagoModal');

                // Recargar la semana para ver los cambios
                // Necesitamos encontrar el ID de la semana
                let semanaId = null;
                semanasAbiertas.forEach((detalles, sId) => {
                    if (detalles.find(d => d.id == detalleId)) semanaId = sId;
                });

                if (semanaId) {
                    document.getElementById(`loading-${semanaId}`).style.display = 'flex';
                    cargarDetallesSemana(semanaId);
                }
            } else {
                mostrarError(data.message || 'Error al confirmar el pago');
            }
        })
        .catch(err => {
            console.error('Error en confirmación:', err);
            mostrarError(`Error al confirmar pago: ${err.message}`);
        })
        .finally(() => {
            btn.disabled = false;
            btn.innerHTML = `
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
            </svg>
            Confirmar Pago
        `;
        });
});
// ==========================================
// EXPORTAR FUNCIONES GLOBALES
// ==========================================
window.gestionarInversiones = gestionarInversiones;
window.abrirModalConfirmarPago = abrirModalConfirmarPago;
window.editarDetalle = editarDetalle;
window.eliminarDetalle = eliminarDetalle;
window.eliminarSemana = eliminarSemana;
window.toggleSemana = toggleSemana;
window.agregarAlquiler = agregarAlquiler;
window.confirmarEliminacionDetalle = confirmarEliminacionDetalle;
window.ejecutarEliminacionSemana = ejecutarEliminacionSemana;
window.exportarExcelSemana = exportarExcelSemana;
window.previewPaymentProof = previewPaymentProof;

// ==========================================
// UTILITIES
// ==========================================

// Override global closeModal to handle our specific modals
window.closeModal = function (modalId) {
    const modal = document.getElementById(modalId);
    if (!modal) return;

    // 1. Remove active class
    modal.classList.remove('active');

    // 2. Hide with forced styles (counteracting the open logic)
    modal.style.setProperty('display', 'none', 'important');
    modal.style.setProperty('visibility', 'hidden', 'important');
    modal.style.setProperty('opacity', '0', 'important');

    // 3. Clean up body scroll
    document.body.style.overflow = '';

    console.log(`🔒 Cerrando modal ${modalId} (Forced cleanup)`);
};

// Specific close handlers to guarantee execution
function cerrarModalInversiones() {
    window.closeModal('inversionesModal');
}

function cerrarModalPago() {
    window.closeModal('confirmarPagoModal');
}

// Exportar globalmente
window.toggleSemana = toggleSemana;
window.gestionarInversiones = gestionarInversiones;
window.abrirModalConfirmarPago = abrirModalConfirmarPago;
window.eliminarComprobante = eliminarComprobante;
window.cerrarModalInversiones = cerrarModalInversiones;
window.cerrarModalPago = cerrarModalPago;
