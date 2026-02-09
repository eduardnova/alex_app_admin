// pagos.js - Gestión de Pagos

document.addEventListener('DOMContentLoaded', function () {
    console.log('💰 Módulo Pagos cargado');

    // Inicializar DataTables
    initTablaInquilinos();

    // Handler para modal editar
    const editForm = document.getElementById('editarPagoForm');
    if (editForm) {
        editForm.addEventListener('submit', handleEditarPagoSubmit);
    }
});

let tablaInquilinos;

function initTablaInquilinos() {
    tablaInquilinos = $('#tablaPagosInquilinos').DataTable({
        ajax: {
            url: '/pagos/inquilinos/data',
            dataSrc: 'data'
        },
        dom: 't', // Only show table. Custom footer handles the rest.
        pageLength: 10, // Match default select
        columns: [
            { data: 'semana_numero', render: (data, type, row) => `<strong>#${data}</strong>` },
            {
                data: null,
                render: function (data, type, row) {
                    return `<small>${row.fecha_inicio} <br> ${row.fecha_fin}</small>`;
                }
            },
            { data: 'placa' },
            { data: 'inquilino_nombre' },
            {
                data: 'inquilino_id',
                render: function (data) {
                    return `<span class="badge badge-info">${data}</span>`;
                }
            },
            { data: 'inquilino_telefono' },
            {
                data: 'monto_semanal',
                render: $.fn.dataTable.render.number(',', '.', 2, '$')
            },
            { data: 'dias_trabajo' },
            {
                data: 'ingreso',
                render: function (data, type, row) {
                    return `<strong class="text-success">$${parseFloat(data).toFixed(2)}</strong>`;
                }
            },
            {
                data: 'deuda_contrato',
                render: function (data) {
                    if (data === 'AL DÍA') return '<span class="badge badge-success">AL DÍA</span>';
                    return '<span class="badge badge-danger">PENDIENTE</span>';
                }
            },
            {
                data: 'deuda_deposito',
                render: function (data) {
                    if (data === 'AL DÍA') return '<span class="badge badge-success">AL DÍA</span>';
                    return `<span class="badge badge-danger">${data}</span>`;
                }
            },
            { data: 'banco_nombre' },
            { data: 'fecha_confirmacion' },
            {
                data: 'comprobante_path',
                render: function (data) {
                    if (data) return `<a href="${data}" target="_blank" class="btn btn-xs btn-outline-secondary">Ver</a>`;
                    return '<small class="text-muted">Sin archivo</small>';
                }
            },
            {
                data: 'pago_confirmado',
                render: function (data) {
                    return data
                        ? '<span class="badge badge-success">Confirmado</span>'
                        : '<span class="badge badge-warning">Pendiente</span>';
                }
            },
            {
                data: null,
                render: function (data, type, row) {
                    return `
                        <button class="btn btn-sm btn-action btn-primary" onclick='window.abrirModalEditarPago(${JSON.stringify(row)})' title="Editar">
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                                <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
                            </svg>
                        </button>
                    `;
                }
            }
        ],
        drawCallback: function (settings) {
            updateCustomFooter(this.api());
        },
        language: {
            url: "//cdn.datatables.net/plug-ins/1.13.4/i18n/es-ES.json"
        },
        order: [[0, 'desc']] // Ordenar por # Semana descendente
    });

    // Custom Search Integration
    $('#searchPagosInput').on('keyup', function () {
        tablaInquilinos.search(this.value).draw();
    });

    // Custom Items Per Page
    $('#itemsPerPage').on('change', function () {
        tablaInquilinos.page.len(this.value).draw();
    });

    // Helper to update footer
    function updateCustomFooter(api) {
        var pageInfo = api.page.info();

        // Update Counts
        $('#showingStart').text(pageInfo.recordsTotal > 0 ? pageInfo.start + 1 : 0);
        $('#showingEnd').text(pageInfo.end);
        $('#totalRecords').text(pageInfo.recordsTotal); // Or recordsDisplay if filtered

        // Update Pagination Buttons
        var container = $('#paginationContainer');
        container.empty();

        // Previous Button
        var prevBtn = $('<button class="pagination-item"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/></svg></button>');
        if (pageInfo.page === 0) prevBtn.prop('disabled', true);
        else prevBtn.on('click', function () { api.page('previous').draw('page'); });
        container.append(prevBtn);

        // Number Buttons (Simplified: show all or max 5 for now)
        // For simplicity reusing basic logic: show current, prev, next
        var totalPages = pageInfo.pages;
        var currentPage = pageInfo.page;

        // Logic to show limited window of pages
        let startPage = Math.max(0, currentPage - 2);
        let endPage = Math.min(totalPages - 1, currentPage + 2);

        if (totalPages > 1) {
            for (let i = startPage; i <= endPage; i++) {
                let btn = $('<button class="pagination-item">' + (i + 1) + '</button>');
                if (i === currentPage) btn.addClass('active');
                btn.on('click', function () { api.page(i).draw('page'); });
                container.append(btn);
            }
        }

        // Next Button
        var nextBtn = $('<button class="pagination-item"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/></svg></button>');
        if (pageInfo.page >= totalPages - 1) nextBtn.prop('disabled', true);
        else nextBtn.on('click', function () { api.page('next').draw('page'); });
        container.append(nextBtn);
    }
}

// Abrir Modal Edición
window.abrirModalEditarPago = function (data) {
    if (typeof data === 'string') data = JSON.parse(data);

    console.log('Editando pago:', data);

    document.getElementById('pagoDetalleId').value = data.detalle_id;

    // Set Monto (Cantidad Depositada = Ingreso Calculado)
    document.getElementById('editPagoMonto').value = parseFloat(data.ingreso).toFixed(2);

    // Set Display Banco
    document.getElementById('displayPagoBanco').value = data.banco_nombre || 'N/A';

    // Set Fecha -- Readonly view
    const fechaInput = document.getElementById('editPagoFecha');
    if (data.raw_fecha_confirmacion) {
        fechaInput.value = data.raw_fecha_confirmacion;
    } else {
        fechaInput.value = "";
    }

    // Set Preview (Ensure element exists)
    const previewContainer = document.getElementById('comprobantePreview');
    if (previewContainer) {
        if (data.comprobante_path && data.comprobante_path !== "" && data.comprobante_path !== "null") {
            const fileExt = data.comprobante_path.split('.').pop().toLowerCase();

            // Ensure path starts with / if it's a relative path (e.g. static/...)
            let displayPath = data.comprobante_path;
            if (!displayPath.startsWith('http') && !displayPath.startsWith('/')) {
                displayPath = '/' + displayPath;
            }

            if (['jpg', 'jpeg', 'png', 'gif', 'webp'].includes(fileExt)) {
                // Use object-fit contain to see full image
                previewContainer.innerHTML = `<img src="${displayPath}" style="max-width: 100%; max-height: 200px; object-fit: contain; border-radius: 4px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">`;
            } else if (fileExt === 'pdf') {
                previewContainer.innerHTML = `<a href="${displayPath}" target="_blank" class="btn btn-sm btn-outline-primary" style="text-decoration: none;">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" style="margin-right:5px; vertical-align:middle;"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>
                    Ver Documento PDF
                 </a>`;
            } else {
                previewContainer.innerHTML = `<a href="${displayPath}" target="_blank" class="btn btn-sm btn-outline-secondary" style="text-decoration: none;">Ver Archivo Adjunto</a>`;
            }
        } else {
            previewContainer.innerHTML = '<span class="text-muted" style="font-size: 13px; color: #a0aec0;">Vista previa del comprobante</span>';
        }
    }

    // Show Modal
    const modal = document.getElementById('editarPagoModal');
    if (modal) {
        document.body.appendChild(modal);
        modal.style.display = 'flex';
        modal.classList.add('active');
    }
}

// Handle File Select for Preview
document.addEventListener('DOMContentLoaded', function () {
    const fileInput = document.getElementById('editPagoFile');
    if (fileInput) {
        fileInput.addEventListener('change', function (e) {
            const file = e.target.files[0];
            const previewContainer = document.getElementById('comprobantePreview');

            if (file) {
                if (file.type.startsWith('image/')) {
                    const reader = new FileReader();
                    reader.onload = function (e) {
                        previewContainer.innerHTML = `<img src="${e.target.result}" style="max-width: 100%; max-height: 200px; border-radius: 4px;">`;
                    }
                    reader.readAsDataURL(file);
                } else {
                    previewContainer.innerHTML = `<span class="badge badge-info">${file.name}</span>`;
                }
            }
        });
    }
});

// Cerrar Modal (Global override check)
window.closeModal = window.closeModal || function (id) {
    const modal = document.getElementById(id);
    if (modal) modal.style.display = 'none';
}

// Handle Submit
function handleEditarPagoSubmit(e) {
    e.preventDefault();

    const formData = new FormData();
    formData.append('detalle_id', document.getElementById('pagoDetalleId').value);
    formData.append('banco_id', document.getElementById('editPagoBanco').value);
    formData.append('fecha_confirmacion', document.getElementById('editPagoFecha').value);

    // File
    const fileInput = document.getElementById('editPagoFile');
    if (fileInput.files.length > 0) {
        formData.append('comprobante_file', fileInput.files[0]);
    }

    fetch('/pagos/inquilinos/editar', {
        method: 'POST',
        body: formData
        // No headers content-type specifically, fetch adds multipart boundary automatically
    })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                alert('Pago actualizado correctamente');
                closeModal('editarPagoModal');
                // Recargar tabla
                tablaInquilinos.ajax.reload(null, false);
            } else {
                alert('Error: ' + data.message);
            }
        })
        .catch(err => {
            console.error(err);
            alert('Error al actualizar pago');
        });
}
