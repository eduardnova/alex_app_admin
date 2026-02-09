"""
Depósitos Routes - Gestión de depósitos de inquilinos
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from functools import wraps
from app import db
from app.models import (
    Deposito, Inquilino, Vehiculo, Contrato, TipoDeposito, 
    PagoDeposito, HistoricoDeposito, Usuario
)
from datetime import datetime
import os
from werkzeug.utils import secure_filename
from decimal import Decimal

deposito_bp = Blueprint('deposito', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'pdf'}
UPLOAD_FOLDER = 'app/static/uploads/depositos'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.rol != 'admin':
            flash('Acceso denegado. Se requieren permisos de administrador.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function


def save_comprobante(file, prefix):
    if file and file.filename and allowed_file(file.filename):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = secure_filename(file.filename)
        name, ext = os.path.splitext(filename)
        unique_filename = f"{prefix}_{name}_{timestamp}{ext}"
        filepath = os.path.join(UPLOAD_FOLDER, unique_filename)
        try:
            file.save(filepath)
            return f'uploads/depositos/{unique_filename}'
        except IOError as e:
            print(f"Error al guardar archivo: {str(e)}")
            return None
    return None


def delete_comprobante(path):
    if path:
        full_path = os.path.join('app/static', path)
        if os.path.exists(full_path):
            try:
                os.remove(full_path)
            except IOError as e:
                print(f"Error al eliminar archivo: {str(e)}")


def registrar_historico(deposito, tipo_operacion):
    historico = HistoricoDeposito(
        tipo_operacion=tipo_operacion,
        fecha_hora_operacion=datetime.now(),
        usuario_operacion_id=current_user.id if current_user.is_authenticated else None,
        id=deposito.id,
        contrato_id=deposito.contrato_id,
        inquilino_id=deposito.inquilino_id,
        vehiculo_id=deposito.vehiculo_id,
        tipo_vehiculo=deposito.tipo_vehiculo,
        deposito_total=deposito.deposito_total,
        cantidad_depositos=deposito.cantidad_depositos,
        monto_por_deposito=deposito.monto_por_deposito,
        depositos_pagados=deposito.depositos_pagados,
        depositos_pendientes=deposito.depositos_pendientes,
        estado=deposito.estado,
        notas=deposito.notas,
        usuario_registro_id=deposito.usuario_registro_id,
        fecha_hora_registro=deposito.fecha_hora_registro,
        usuario_actualizo_id=deposito.usuario_actualizo_id,
        fecha_hora_actualizo=deposito.fecha_hora_actualizo
    )
    db.session.add(historico)

@deposito_bp.route('/depositos/historial/<int:id>')
@login_required
@admin_required
def historial_deposito(id):
    historico = HistoricoDeposito.query.filter_by(id=id).order_by(
        HistoricoDeposito.fecha_hora_operacion.asc()
    ).all()
    
    result = []
    prev_record = None
    
    for record in historico:
        usuario = Usuario.query.get(record.usuario_operacion_id) if record.usuario_operacion_id else None
        
        cambios = []
        if record.tipo_operacion == 'UPDATE' and prev_record:
            # Campos a comparar
            campos = [
                ('deposito_total', 'Depósito Total'),
                ('cantidad_depositos', 'Cant. Depósitos'),
                ('monto_por_deposito', 'Monto por Depósito'),
                ('depositos_pagados', 'Depósitos Pagados'),
                ('depositos_pendientes', 'Depósitos Pendientes'),
                ('estado', 'Estado'),
                ('notas', 'Notas')
            ]
            
            for campo, label in campos:
                old_val = getattr(prev_record, campo)
                new_val = getattr(record, campo)
                
                if str(old_val) != str(new_val):
                    cambios.append({
                        'campo': label,
                        'valor_anterior': str(old_val) if old_val is not None else 'N/A',
                        'valor_nuevo': str(new_val) if new_val is not None else 'N/A'
                    })
        
        result.append({
            'tipo_operacion': record.tipo_operacion,
            'fecha_hora': record.fecha_hora_operacion.strftime('%d/%m/%Y %H:%M:%S'),
            'usuario_nombre': f"{usuario.nombre} {usuario.apellido}" if usuario else 'Sistema',
            'estado': record.estado,
            'cambios': cambios,
            # Data for INSERT/DELETE details
            'inquilino': Inquilino.query.get(record.inquilino_id).nombre_apellido if record.inquilino_id else 'N/A',
            'vehiculo': Vehiculo.query.get(record.vehiculo_id).placa if record.vehiculo_id else 'N/A',
            'monto_total': float(record.deposito_total) if record.deposito_total else 0
        })
        prev_record = record
    
    # Invertir para mostrar lo más reciente primero
    result.reverse()
    
    return jsonify({
        'success': True,
        'historial': result
    })



def actualizar_estado_deposito(deposito):
    """Actualiza el estado de un depósito basado en los montos pagado vs total"""
    monto_pagado = deposito.monto_pagado
    if monto_pagado >= deposito.deposito_total:
        deposito.estado = 'completado'
    elif monto_pagado > 0:
        deposito.estado = 'parcial'
    else:
        deposito.estado = 'pendiente'

# ==================== DEPÓSITOS ====================

@deposito_bp.route('/depositos')
@login_required
@admin_required
def listar_depositos():
    depositos = Deposito.query.order_by(Deposito.fecha_hora_registro.desc()).all()
    # Solo contratos activos que NO tengan un depósito registrado
    contratos = Contrato.query.filter_by(estado='activo').filter(~Contrato.depositos.any()).all()
    tipos_depositos = TipoDeposito.query.filter_by(activo=True).all()
    return render_template('modulos/depositos.html', 
                         depositos=depositos,
                         contratos=contratos,
                         tipos_depositos=tipos_depositos)


@deposito_bp.route('/depositos/crear', methods=['POST'])
@login_required
@admin_required
def crear_deposito():
    try:
        contrato_id = request.form.get('contrato_id')
        notas = request.form.get('notas', '').strip()
        
        if not contrato_id:
            flash('El contrato es requerido.', 'warning')
            return redirect(url_for('deposito.listar_depositos'))
        
        contrato = Contrato.query.get_or_404(contrato_id)
        
        # Verificar que no exista ya un depósito para este contrato
        if Deposito.query.filter_by(contrato_id=contrato_id).first():
            flash('Ya existe un depósito registrado para este contrato.', 'warning')
            return redirect(url_for('deposito.listar_depositos'))
        
        # Obtener tipo de vehículo
        tipo_vehiculo = contrato.vehiculo.marca_modelo.tipo
        
        # Buscar configuración de depósito
        tipo_deposito = TipoDeposito.query.filter_by(
            tipo_vehiculo=tipo_vehiculo,
            activo=True
        ).first()
        
        if not tipo_deposito:
            flash(f'No hay configuración de depósito para vehículos tipo {tipo_vehiculo}.', 'warning')
            return redirect(url_for('deposito.listar_depositos'))
        
        nuevo_deposito = Deposito(
            contrato_id=contrato_id,
            inquilino_id=contrato.inquilino_id,
            vehiculo_id=contrato.vehiculo_id,
            tipo_vehiculo=tipo_vehiculo,
            deposito_total=tipo_deposito.deposito_total,
            cantidad_depositos=tipo_deposito.cantidad_depositos,
            monto_por_deposito=tipo_deposito.monto_por_deposito,
            depositos_pagados=0,
            depositos_pendientes=tipo_deposito.cantidad_depositos,
            estado='pendiente',
            notas=notas,
            usuario_registro_id=current_user.id,
            usuario_actualizo_id=current_user.id
        )
        
        db.session.add(nuevo_deposito)
        db.session.flush()
        
        registrar_historico(nuevo_deposito, 'INSERT')
        db.session.commit()
        
        flash('Depósito creado exitosamente.', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error al crear depósito: {str(e)}', 'danger')
    
    return redirect(url_for('deposito.listar_depositos'))


@deposito_bp.route('/depositos/<int:id>')
@login_required
@admin_required
def ver_deposito(id):
    deposito = Deposito.query.get_or_404(id)
    
    return jsonify({
        'success': True,
        'deposito': {
            'id': deposito.id,
            'contrato_id': deposito.contrato_id,
            'inquilino_nombre': deposito.inquilino.nombre_apellido,
            'vehiculo_placa': deposito.vehiculo.placa,
            'tipo_vehiculo': deposito.tipo_vehiculo,
            'deposito_total': float(deposito.deposito_total),
            'cantidad_depositos': deposito.cantidad_depositos,
            'monto_por_deposito': float(deposito.monto_por_deposito),
            'depositos_pagados': deposito.depositos_pagados,
            'depositos_pendientes': deposito.depositos_pendientes,
            'porcentaje_completado': deposito.porcentaje_completado,
            'monto_pagado': float(deposito.monto_pagado),
            'monto_pendiente': float(deposito.monto_pendiente),
            'estado': deposito.estado,
            'notas': deposito.notas
        }
    })


@deposito_bp.route('/depositos/<int:id>/editar', methods=['POST'])
@login_required
@admin_required
def editar_deposito(id):
    deposito = Deposito.query.get_or_404(id)
    
    try:
        notas = request.form.get('notas', '').strip()
        
        deposito.notas = notas
        deposito.usuario_actualizo_id = current_user.id
        deposito.fecha_hora_actualizo = datetime.now()
        
        registrar_historico(deposito, 'UPDATE')
        db.session.commit()
        
        flash('Depósito actualizado exitosamente.', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error al actualizar depósito: {str(e)}', 'danger')
    
    return redirect(url_for('deposito.listar_depositos'))


@deposito_bp.route('/depositos/<int:id>/eliminar', methods=['POST'])
@login_required
@admin_required
def eliminar_deposito(id):
    deposito = Deposito.query.get_or_404(id)
    
    try:
        registrar_historico(deposito, 'DELETE')
        
        # Eliminar comprobantes de pagos
        for pago in deposito.pagos_deposito:
            delete_comprobante(pago.comprobante_path)
        
        db.session.delete(deposito)
        db.session.commit()
        
        flash('Depósito eliminado exitosamente.', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar depósito: {str(e)}', 'danger')
    
    return redirect(url_for('deposito.listar_depositos'))


# ==================== PAGOS DE DEPÓSITO ====================

@deposito_bp.route('/depositos/<int:deposito_id>/pagos')
@login_required
@admin_required
def listar_pagos(deposito_id):
    pagos = PagoDeposito.query.filter_by(deposito_id=deposito_id).order_by(
        PagoDeposito.numero_pago
    ).all()
    
    result = []
    for pago in pagos:
        result.append({
            'id': pago.id,
            'numero_pago': pago.numero_pago,
            'monto': float(pago.monto),
            'fecha_pago': pago.fecha_pago.strftime('%d/%m/%Y'),
            'tipo_pago': pago.tipo_pago,
            'comprobante_path': pago.comprobante_path,
            'confirmado': pago.confirmado,
            'notas': pago.notas
        })
    
    return jsonify({'success': True, 'pagos': result})


@deposito_bp.route('/depositos/<int:deposito_id>/pagos/crear', methods=['POST'])
@login_required
@admin_required
def crear_pago_deposito(deposito_id):
    try:
        deposito = Deposito.query.get_or_404(deposito_id)
        
        monto = request.form.get('monto')
        fecha_pago = request.form.get('fecha_pago')
        tipo_pago = request.form.get('tipo_pago')
        confirmado = request.form.get('confirmado') == 'true'
        notas = request.form.get('notas', '').strip()
        
        if not monto or not fecha_pago or not tipo_pago:
            return jsonify({
                'success': False,
                'message': 'Todos los campos son requeridos'
            })
        
        # Calcular número de pago
        ultimo_pago = PagoDeposito.query.filter_by(deposito_id=deposito_id).order_by(
            PagoDeposito.numero_pago.desc()
        ).first()
        numero_pago = (ultimo_pago.numero_pago + 1) if ultimo_pago else 1
        
        # Guardar comprobante
        comprobante_path = None
        if tipo_pago == 'transferencia':
            comprobante_path = save_comprobante(
                request.files.get('comprobante'),
                f'pago_dep_{deposito_id}'
            )
        
        nuevo_pago = PagoDeposito(
            deposito_id=deposito_id,
            numero_pago=numero_pago,
            monto=monto,
            fecha_pago=datetime.strptime(fecha_pago, '%Y-%m-%d').date(),
            tipo_pago=tipo_pago,
            comprobante_path=comprobante_path,
            confirmado=confirmado,
            notas=notas,
            usuario_registro_id=current_user.id
        )
        
        db.session.add(nuevo_pago)
        
        # Actualizar depósito usando la nueva lógica
        actualizar_estado_deposito(deposito)
        
        deposito.depositos_pagados += 1
        deposito.depositos_pendientes = max(0, deposito.depositos_pendientes - 1)
        
        deposito.usuario_actualizo_id = current_user.id
        deposito.fecha_hora_actualizo = datetime.now()
        
        db.session.commit()
        
        # Registrar historial del depósito tras el pago
        registrar_historico(deposito, 'UPDATE')
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Pago registrado exitosamente'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        })


@deposito_bp.route('/depositos/pagos/<int:id>/eliminar', methods=['POST'])
@login_required
@admin_required
def eliminar_pago_deposito(id):
    try:
        pago = PagoDeposito.query.get_or_404(id)
        deposito = pago.deposito
        
        # Eliminar comprobante
        delete_comprobante(pago.comprobante_path)
        
        db.session.delete(pago)
        
        # Actualizar depósito usando la nueva lógica
        actualizar_estado_deposito(deposito)
        
        deposito.depositos_pagados = max(0, deposito.depositos_pagados - 1)
        deposito.depositos_pendientes += 1
        
        deposito.usuario_actualizo_id = current_user.id
        deposito.fecha_hora_actualizo = datetime.now()
        
        db.session.commit()
        
        # Registrar historial del depósito tras eliminar pago
        registrar_historico(deposito, 'UPDATE')
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Pago eliminado exitosamente'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        })


@deposito_bp.route('/depositos/pagos/<int:id>', methods=['GET'])
@login_required
def get_pago_deposito(id):
    pago = PagoDeposito.query.get_or_404(id)
    return jsonify({
        'success': True,
        'pago': {
            'id': pago.id,
            'monto': float(pago.monto),
            'fecha_pago': pago.fecha_pago.strftime('%Y-%m-%d'),
            'tipo_pago': pago.tipo_pago,
            'confirmado': pago.confirmado,
            'notas': pago.notas,
            'comprobante_path': pago.comprobante_path
        }
    })


@deposito_bp.route('/depositos/pagos/<int:id>/editar', methods=['POST'])
@login_required
@admin_required
def editar_pago_deposito(id):
    try:
        pago = PagoDeposito.query.get_or_404(id)
        deposito = pago.deposito
        
        monto = request.form.get('monto')
        fecha_pago = request.form.get('fecha_pago')
        tipo_pago = request.form.get('tipo_pago')
        confirmado = request.form.get('confirmado') == 'true'
        notas = request.form.get('notas', '').strip()
        
        if not monto or not fecha_pago or not tipo_pago:
            return jsonify({
                'success': False,
                'message': 'Todos los campos son requeridos'
            })
            
        # Actualizar campos básicos
        pago.monto = Decimal(monto)
        pago.fecha_pago = datetime.strptime(fecha_pago, '%Y-%m-%d').date()
        pago.tipo_pago = tipo_pago
        pago.confirmado = confirmado
        pago.notas = notas
        
        # Manejar comprobante
        if 'comprobante' in request.files:
            file = request.files['comprobante']
            if file and file.filename:
                # Eliminar anterior si existe
                if pago.comprobante_path:
                    delete_comprobante(pago.comprobante_path)
                
                # Guardar nuevo
                pago.comprobante_path = save_comprobante(
                    file, 
                    f'pago_dep_{deposito.id}'
                )
        elif request.form.get('remove_comprobante') == 'true':
            if pago.comprobante_path:
                delete_comprobante(pago.comprobante_path)
            pago.comprobante_path = None

        db.session.commit()
        
        # Actualizar depósito usando la nueva lógica
        actualizar_estado_deposito(deposito)
        
        # Registrar historial del depósito tras editar pago
        registrar_historico(deposito, 'UPDATE')
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Pago actualizado exitosamente'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        })


# ==================== API ENDPOINTS ====================

@deposito_bp.route('/depositos/api/por-contrato/<int:contrato_id>')
@login_required
def api_deposito_por_contrato(contrato_id):
    deposito = Deposito.query.filter_by(contrato_id=contrato_id).first()
    
    if deposito:
        return jsonify({
            'success': True,
            'deposito': {
                'id': deposito.id,
                'deposito_total': float(deposito.deposito_total),
                'cantidad_depositos': deposito.cantidad_depositos,
                'depositos_pagados': deposito.depositos_pagados,
                'depositos_pendientes': deposito.depositos_pendientes,
                'estado': deposito.estado
            }
        })
    
    return jsonify({
        'success': False,
        'message': 'No se encontró depósito para este contrato'
    })