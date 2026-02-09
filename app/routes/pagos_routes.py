from flask import Blueprint, render_template, request, jsonify, current_app
from flask_login import login_required, current_user
from sqlalchemy import func, and_, case, desc
from app import db
from app.models import (
    DetalleAlquilerSemanal, SemanaAlquiler, Vehiculo, Inquilino, 
    Banco, Contrato, Deposito, Pago
)
import traceback

pagos_bp = Blueprint('pagos', __name__, 
                    template_folder='templates',
                    url_prefix='/pagos')

@pagos_bp.route('/')
@login_required
def index():
    """Renderiza la página principal del módulo de pagos"""
    # Se obtienen los bancos para el selector del modal de edición
    bancos = Banco.query.all()
    return render_template('modulos/pagos.html', bancos=bancos)

@pagos_bp.route('/inquilinos/data')
@login_required
def get_pagos_inquilinos_data():
    """API para obtener los datos de la tabla de pagos de inquilinos"""
    try:
        # Consulta principal: Detalles de alquileres semanales
        # Se une con Semana, Vehículo, Inquilino, Banco (si existe pago confirmado)
        
        query = db.session.query(
            DetalleAlquilerSemanal,
            SemanaAlquiler,
            Vehiculo,
            Inquilino,
            Banco
        ).join(
            SemanaAlquiler, DetalleAlquilerSemanal.semana_alquiler_id == SemanaAlquiler.id
        ).outerjoin(
            Vehiculo, DetalleAlquilerSemanal.vehiculo_id == Vehiculo.id
        ).outerjoin(
            Inquilino, DetalleAlquilerSemanal.inquilino_id == Inquilino.id
        ).outerjoin(
            Banco, DetalleAlquilerSemanal.banco_id == Banco.id
        )

        results = query.all()
        print(f"💰 [PAGOS] Found {len(results)} rental details")
        
        data = []
        for detalle, semana, vehiculo, inquilino, banco in results:
            
            # 1. Verificar Deuda Contrato (Activo)
            contrato_activo = Contrato.query.filter_by(
                inquilino_id=inquilino.id, 
                vehiculo_id=vehiculo.id, 
                estado='activo'
            ).first()
            
            # Simple lógica: Si hay contrato activo, no hay "deuda de contrato" per se,
            # pero el usuario pidió "SI DEBE VALOR DE CONTRATO".
            # Asumiremos que se refiere a si el contrato está pagado/confirmado.
            deuda_contrato = False
            if contrato_activo:
                if not contrato_activo.confirmacion_pago:
                   deuda_contrato = True
            
            # 2. Verificar Deuda Depósito
            # Buscar depósitos asociados al contrato activo o al inquilino/vehículo
            deuda_deposito = False
            monto_deposito_pendiente = 0
            
            depositos = Deposito.query.filter_by(
                inquilino_id=inquilino.id,
                vehiculo_id=vehiculo.id
            ).filter(Deposito.estado != 'completado').all()
            
            if depositos:
                deuda_deposito = True
                for dep in depositos:
                    monto_deposito_pendiente += (dep.deposito_total - dep.monto_pagado)


            # Formatear datos para la tabla
            data.append({
                'detalle_id': detalle.id,
                'semana_id': semana.id,
                'semana_numero': semana.numero_semana,  # Asegurar que este campo exista en SemanaAlquiler
                'fecha_inicio': semana.fecha_inicio.strftime('%d/%m/%Y'),
                'fecha_fin': semana.fecha_fin.strftime('%d/%m/%Y'),
                'placa': vehiculo.placa,
                'inquilino_nombre': inquilino.nombre_apellido,
                'inquilino_telefono': inquilino.telefono or 'N/A',
                'inquilino_id': inquilino.id,
                'monto_semanal': float(detalle.precio_semanal),
                'dias_trabajo': detalle.dias_trabajo,
                'ingreso': float(detalle.ingreso_calculado),
                'deuda_contrato': 'PENDIENTE' if deuda_contrato else 'AL DÍA',
                'deuda_deposito': f"${monto_deposito_pendiente:,.2f}" if deuda_deposito else 'AL DÍA',
                'banco_nombre': banco.banco if banco else 'N/A',
                'fecha_confirmacion': detalle.fecha_confirmacion_pago.strftime('%d/%m/%Y') if detalle.fecha_confirmacion_pago else 'PENDIENTE',
                'comprobante_path': detalle.comprobante_pago_path, # Property que desencripta
                'pago_confirmado': detalle.pago_confirmado,
                # Datos raw para el modal de edición
                'raw_banco_id': detalle.banco_id,
                'raw_fecha_confirmacion': detalle.fecha_confirmacion_pago.strftime('%Y-%m-%d') if detalle.fecha_confirmacion_pago else ''
            })
            
        return jsonify({'data': data})
        
    except Exception as e:
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

from werkzeug.utils import secure_filename
import os

@pagos_bp.route('/inquilinos/editar', methods=['POST'])
@login_required
def editar_pago_inquilino():
    """API para editar los datos de confirmación de pago (incluyendo archivo)"""
    try:
        # Se usa request.form y request.files para multipart/form-data
        detalle_id = request.form.get('detalle_id')
        banco_id = request.form.get('banco_id')
        fecha_confirmacion = request.form.get('fecha_confirmacion')
        
        # Archivo
        file = request.files.get('comprobante_file')
        
        detalle = DetalleAlquilerSemanal.query.get(detalle_id)
        if not detalle:
            return jsonify({'success': False, 'message': 'Detalle no encontrado'}), 404
            
        # Actualizar Banco
        if banco_id:
            detalle.banco_id = banco_id
            
        # Actualizar Fecha
        if fecha_confirmacion:
            from datetime import datetime
            detalle.fecha_confirmacion_pago = datetime.strptime(fecha_confirmacion, '%Y-%m-%d').date()
            detalle.pago_confirmado = True
            
        # Actualizar Comprobante (Archivo)
        if file and file.filename != '':
            filename = secure_filename(f"pago_{detalle.id}_{file.filename}")
            upload_folder = os.path.join(current_app.root_path, 'static', 'uploads', 'comprobantes')
            
            # Crear directorio si no existe
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)
                
            file_path = os.path.join(upload_folder, filename)
            file.save(file_path)
            
            # Guardar ruta relativa para acceso web
            # Nota: El setter 'comprobante_pago_path' en el modelo se encarga de encriptar si es necesario
            # Se guarda la URL accesible: /static/uploads/comprobantes/filename
            web_path = f"/static/uploads/comprobantes/{filename}"
            detalle.comprobante_pago_path = web_path

        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Pago actualizado correctamente'})
        
    except Exception as e:
        db.session.rollback()
        print(traceback.format_exc())
        return jsonify({'success': False, 'message': str(e)}), 500
