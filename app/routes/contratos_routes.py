"""
Contratos Routes - CRUD completo para contratos de alquiler
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from functools import wraps
from app import db
from app.models import (
    Contrato, Inquilino, Vehiculo, Usuario, VehiculoMarcaModelo,
    HistoricoContrato, Deposito, TipoDeposito, Alquiler, DetalleAlquilerSemanal
)
from datetime import datetime
import os
from werkzeug.utils import secure_filename

contrato_bp = Blueprint('contrato', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'pdf'}
UPLOAD_FOLDER = 'app/static/uploads/contratos'

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
            return f'uploads/contratos/{unique_filename}'
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


def registrar_historico(contrato, tipo_operacion):
    historico = HistoricoContrato(
        tipo_operacion=tipo_operacion,
        fecha_hora_operacion=datetime.now(),
        usuario_operacion_id=current_user.id if current_user.is_authenticated else None,
        id=contrato.id,
        inquilino_id=contrato.inquilino_id,
        vehiculo_id=contrato.vehiculo_id,
        monto_contrato=contrato.monto_contrato,
        fecha_inicio=contrato.fecha_inicio,
        fecha_fin=contrato.fecha_fin,
        es_indefinido=contrato.es_indefinido,
        tipo_pago=contrato.tipo_pago,
        comprobante_pago_path=contrato.comprobante_pago_path,
        archivo_contrato_path=contrato.archivo_contrato_path,
        confirmacion_pago=contrato.confirmacion_pago,
        estado=contrato.estado,
        notas=contrato.notas,
        usuario_registro_id=contrato.usuario_registro_id,
        fecha_hora_registro=contrato.fecha_hora_registro,
        usuario_actualizo_id=contrato.usuario_actualizo_id,
        fecha_hora_actualizo=contrato.fecha_hora_actualizo
    )
    db.session.add(historico)


# ==================== CONTRATOS ====================

@contrato_bp.route('/contrato')
@login_required
@admin_required
def contratos():
    contratos = Contrato.query.order_by(Contrato.fecha_hora_registro.desc()).all()
    inquilinos = sorted(Inquilino.query.all(), key=lambda x: x.nombre_apellido or '')
    
    # Obtener IDs de vehículos con contratos activos
    vehiculos_ocupados_ids = [c.vehiculo_id for c in Contrato.query.filter_by(estado='activo').all()]
    
    # Filtrar vehículos: disponibles y no ocupados
    todos_vehiculos = Vehiculo.query.all()
    vehiculos = [v for v in todos_vehiculos if v.disponible and v.id not in vehiculos_ocupados_ids]
    vehiculos = sorted(vehiculos, key=lambda x: x.placa or '')
    
    return render_template('modulos/contratos.html', 
                         contratos=contratos, 
                         inquilinos=inquilinos,
                         vehiculos=vehiculos)


@contrato_bp.route('/contrato/crear', methods=['POST'])
@login_required
@admin_required
def crear_contrato():
    try:
        inquilino_id = request.form.get('inquilino_id')
        vehiculo_id = request.form.get('vehiculo_id')
        monto_contrato = request.form.get('monto_contrato', 1000.00)
        fecha_inicio = request.form.get('fecha_inicio')
        duracion_contrato = request.form.get('duracion_contrato')
        fecha_fin = request.form.get('fecha_fin') if duracion_contrato == 'definido' else None
        tipo_pago = request.form.get('tipo_pago')
        confirmacion_pago = request.form.get('confirmacion_pago') == 'true'
        notas = request.form.get('notas', '').strip()
        
        if not inquilino_id or not vehiculo_id or not fecha_inicio or not tipo_pago:
            flash('Inquilino, vehículo, fecha de inicio y tipo de pago son requeridos.', 'warning')
            return redirect(url_for('contrato.contratos'))
        
        # Verificar que el vehículo esté disponible
        vehiculo = Vehiculo.query.get(vehiculo_id)
        if not vehiculo or not vehiculo.disponible:
            flash('El vehículo seleccionado no está disponible.', 'warning')
            return redirect(url_for('contrato.contratos'))
        
        # Guardar comprobante si existe
        comprobante_path = None
        if tipo_pago == 'transferencia':
            comprobante_path = save_comprobante(request.files.get('comprobante_pago'), 'comprobante')
        
        # Guardar archivo de contrato si existe
        archivo_contrato_path = save_comprobante(request.files.get('archivo_contrato'), 'contrato')
        
        nuevo_contrato = Contrato(
            inquilino_id=inquilino_id,
            vehiculo_id=vehiculo_id,
            monto_contrato=monto_contrato,
            fecha_inicio=datetime.strptime(fecha_inicio, '%Y-%m-%d').date(),
            fecha_fin=datetime.strptime(fecha_fin, '%Y-%m-%d').date() if fecha_fin else None,
            es_indefinido=(duracion_contrato == 'indefinido'),
            tipo_pago=tipo_pago,
            comprobante_pago_path=comprobante_path,
            archivo_contrato_path=archivo_contrato_path,
            confirmacion_pago=confirmacion_pago,
            estado='activo',
            notas=notas,
            usuario_registro_id=current_user.id,
            usuario_actualizo_id=current_user.id
        )
        
        db.session.add(nuevo_contrato)
        db.session.flush()
        
        # Marcar vehículo como no disponible
        vehiculo.disponible = False
        
        registrar_historico(nuevo_contrato, 'INSERT')
        db.session.commit()
        
        flash('Contrato creado exitosamente.', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error al crear contrato: {str(e)}', 'danger')
    
    return redirect(url_for('contrato.contratos'))


@contrato_bp.route('/contrato/<int:id>')
@login_required
@admin_required
def ver_contrato(id):
    contrato = Contrato.query.get_or_404(id)
    
    # Build vehiculo info string
    vehiculo_info = f"{contrato.vehiculo.placa}"
    if contrato.vehiculo.marca_modelo:
        vehiculo_info += f" - {contrato.vehiculo.marca_modelo.marca} {contrato.vehiculo.marca_modelo.modelo}"
    
    return jsonify({
        'success': True,
        'contrato': {
            'id': contrato.id,
            'inquilino_id': contrato.inquilino_id,
            'inquilino_nombre': contrato.inquilino.nombre_apellido,
            'vehiculo_id': contrato.vehiculo_id,
            'vehiculo_placa': contrato.vehiculo.placa,
            'vehiculo_info': vehiculo_info,
            'monto_contrato': float(contrato.monto_contrato),
            'fecha_inicio': contrato.fecha_inicio.strftime('%Y-%m-%d'),
            'fecha_fin': contrato.fecha_fin.strftime('%Y-%m-%d') if contrato.fecha_fin else None,
            'es_indefinido': contrato.es_indefinido,
            'tipo_pago': contrato.tipo_pago,
            'comprobante_pago_path': contrato.comprobante_pago_path,
            'archivo_contrato_path': contrato.archivo_contrato_path,
            'confirmacion_pago': contrato.confirmacion_pago,
            'estado': contrato.estado,
            'notas': contrato.notas
        }
    })


@contrato_bp.route('/contrato/<int:id>/editar', methods=['POST'])
@login_required
@admin_required
def editar_contrato(id):
    contrato = Contrato.query.get_or_404(id)
    
    try:
        monto_contrato = request.form.get('monto_contrato')
        fecha_inicio = request.form.get('fecha_inicio')
        duracion_contrato = request.form.get('duracion_contrato')
        fecha_fin = request.form.get('fecha_fin') if duracion_contrato == 'definido' else None
        tipo_pago = request.form.get('tipo_pago')
        confirmacion_pago = request.form.get('confirmacion_pago') == 'true'
        estado = request.form.get('estado')
        notas = request.form.get('notas', '').strip()
        
        # Actualizar Inquilino
        inquilino_id = request.form.get('inquilino_id')
        if inquilino_id and int(inquilino_id) != contrato.inquilino_id:
            contrato.inquilino_id = inquilino_id
            
            # 🔴 Actualizar también el inquilino en los depósitos asociados (si existen)
            depositos_asociados = Deposito.query.filter_by(contrato_id=contrato.id).all()
            for dep in depositos_asociados:
                dep.inquilino_id = inquilino_id
            
            print(f"   ⚠️ Actualizado inquilino en {len(depositos_asociados)} depósitos asociados.")

            # 🔴 Actualizar también el inquilino en los ALQUILERES asociados (por vehículo y fecha)
            # Buscar alquileres de este vehículo que hayan iniciado en o después de la fecha de inicio del contrato
            alquileres_asociados = Alquiler.query.filter(
                Alquiler.vehiculo_id == contrato.vehiculo_id,
                Alquiler.fecha_alquiler_inicio >= contrato.fecha_inicio
            ).all()

            # Filtrar si hay fecha fin de contrato, para no tocar futuros contratos
            if contrato.fecha_fin:
                alquileres_asociados = [a for a in alquileres_asociados if a.fecha_alquiler_inicio <= contrato.fecha_fin]
            
            for alq in alquileres_asociados:
                alq.inquilino_id = inquilino_id
                
                # 🔴 Actualizar también los DETALLES SEMANALES asociados a este alquiler
                detalles_asociados = DetalleAlquilerSemanal.query.filter_by(alquiler_id=alq.id).all()
                for det in detalles_asociados:
                    det.inquilino_id = inquilino_id
                
                print(f"      - Sincronizados {len(detalles_asociados)} detalles semanales para alquiler {alq.id}")
            
            print(f"   ⚠️ Actualizado inquilino en {len(alquileres_asociados)} alquileres asociados.")

        # Actualizar Vehículo
        vehiculo_id = request.form.get('vehiculo_id')
        if vehiculo_id and int(vehiculo_id) != contrato.vehiculo_id:
            # Verificar disponibilidad del nuevo vehículo
            nuevo_vehiculo = Vehiculo.query.get(vehiculo_id)
            if not nuevo_vehiculo:
                flash('El vehículo seleccionado no existe.', 'warning')
                return redirect(url_for('contrato.contratos'))
            
            if not nuevo_vehiculo.disponible:
                flash(f'El vehículo {nuevo_vehiculo.placa} no está disponible.', 'warning')
                return redirect(url_for('contrato.contratos'))
            
            # Liberar vehículo anterior
            if contrato.vehiculo:
                contrato.vehiculo.disponible = True
            
            # Asignar nuevo vehículo y marcar como ocupado
            contrato.vehiculo_id = vehiculo_id
            nuevo_vehiculo.disponible = False

        
        contrato.monto_contrato = monto_contrato
        contrato.fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
        contrato.fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d').date() if fecha_fin else None
        contrato.es_indefinido = (duracion_contrato == 'indefinido')
        contrato.tipo_pago = tipo_pago
        contrato.confirmacion_pago = confirmacion_pago
        contrato.estado = estado
        contrato.notas = notas
        
        # Manejar comprobante
        if request.files.get('comprobante_pago') and request.files['comprobante_pago'].filename:
            if contrato.comprobante_pago_path:
                delete_comprobante(contrato.comprobante_pago_path)
            contrato.comprobante_pago_path = save_comprobante(request.files['comprobante_pago'], 'comprobante')
        elif not request.form.get('comprobante_existing'):
            if contrato.comprobante_pago_path:
                delete_comprobante(contrato.comprobante_pago_path)
            contrato.comprobante_pago_path = None
        
        # Manejar archivo de contrato
        if request.files.get('archivo_contrato') and request.files['archivo_contrato'].filename:
            if contrato.archivo_contrato_path:
                delete_comprobante(contrato.archivo_contrato_path)
            contrato.archivo_contrato_path = save_comprobante(request.files['archivo_contrato'], 'contrato')
        elif request.form.get('archivo_contrato_delete') == 'true':
            if contrato.archivo_contrato_path:
                delete_comprobante(contrato.archivo_contrato_path)
            contrato.archivo_contrato_path = None
        
        # Si el contrato cambia a finalizado, liberar vehículo
        if estado in ['finalizado', 'cancelado']:
            contrato.vehiculo.disponible = True
        
        contrato.usuario_actualizo_id = current_user.id
        contrato.fecha_hora_actualizo = datetime.now()
        
        registrar_historico(contrato, 'UPDATE')
        db.session.commit()
        
        flash('Contrato actualizado exitosamente.', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error al actualizar contrato: {str(e)}', 'danger')
    
    return redirect(url_for('contrato.contratos'))


@contrato_bp.route('/contrato/<int:id>/eliminar', methods=['POST'])
@login_required
@admin_required
def eliminar_contrato(id):
    contrato = Contrato.query.get_or_404(id)
    
    try:
        # Liberar vehículo
        contrato.vehiculo.disponible = True
        
        registrar_historico(contrato, 'DELETE')
        
        # Eliminar comprobante y archivo de contrato
        delete_comprobante(contrato.comprobante_pago_path)
        delete_comprobante(contrato.archivo_contrato_path)
        
        db.session.delete(contrato)
        db.session.commit()
        
        flash('Contrato eliminado exitosamente.', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar contrato: {str(e)}', 'danger')
    
    return redirect(url_for('contrato.contratos'))


@contrato_bp.route('/contrato/<int:id>/historial')
@login_required
@admin_required
def historial_contrato(id):
    contrato = Contrato.query.get_or_404(id)
    
    # Obtener historial ordenado del más antiguo al más nuevo para detectar cambios
    historial = HistoricoContrato.query.filter_by(id=id).order_by(
        HistoricoContrato.fecha_hora_operacion.asc()
    ).all()
    
    result = []
    prev_record = None
    
    for record in historial:
        usuario = Usuario.query.get(record.usuario_operacion_id) if record.usuario_operacion_id else None
        
        cambios = []
        if record.tipo_operacion == 'UPDATE' and prev_record:
            # Campos a comparar
            campos = [
                ('monto_contrato', 'Monto'),
                ('fecha_inicio', 'Fecha Inicio'),
                ('fecha_fin', 'Fecha Fin'),
                ('es_indefinido', 'Es Indefinido'),
                ('tipo_pago', 'Tipo Pago'),
                ('comprobante_pago_path', 'Comprobante Pago'),
                ('archivo_contrato_path', 'Archivo Contrato'),
                ('confirmacion_pago', 'Confirmación Pago'),
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
            
            # Comparar Inquilino
            if prev_record.inquilino_id != record.inquilino_id:
                old_inq = Inquilino.query.get(prev_record.inquilino_id)
                new_inq = Inquilino.query.get(record.inquilino_id)
                cambios.append({
                    'campo': 'Inquilino',
                    'valor_anterior': old_inq.nombre_apellido if old_inq else 'N/A',
                    'valor_nuevo': new_inq.nombre_apellido if new_inq else 'N/A'
                })
                
            # Comparar Vehículo
            if prev_record.vehiculo_id != record.vehiculo_id:
                old_veh = Vehiculo.query.get(prev_record.vehiculo_id)
                new_veh = Vehiculo.query.get(record.vehiculo_id)
                cambios.append({
                    'campo': 'Vehículo',
                    'valor_anterior': old_veh.placa if old_veh else 'N/A',
                    'valor_nuevo': new_veh.placa if new_veh else 'N/A'
                })

        result.append({
            'tipo_operacion': record.tipo_operacion,
            'fecha_hora': record.fecha_hora_operacion.strftime('%d/%m/%Y %H:%M:%S'),
            'usuario_nombre': f"{usuario.nombre} {usuario.apellido}" if usuario else 'Sistema',
            'estado': record.estado,
            'monto_contrato': float(record.monto_contrato) if record.monto_contrato else 0,
            'cambios': cambios,
            # Data for INSERT/DELETE details
            'inquilino': Inquilino.query.get(record.inquilino_id).nombre_apellido if record.inquilino_id else 'N/A',
            'vehiculo': Vehiculo.query.get(record.vehiculo_id).placa if record.vehiculo_id else 'N/A'
        })
        prev_record = record
    
    # Invertir para mostrar lo más reciente primero
    result.reverse()
    
    return jsonify({
        'success': True,
        'historial': result
    })


# ==================== API ENDPOINTS ====================

@contrato_bp.route('/contrato/api/vehiculos-disponibles')
@login_required
def api_vehiculos_disponibles():
    # Obtener IDs de vehículos con contratos activos
    vehiculos_ocupados_ids = [c.vehiculo_id for c in Contrato.query.filter_by(estado='activo').all()]
    
    # Filtrar vehículos: disponibles (encriptado) y no ocupados
    todos_vehiculos = Vehiculo.query.all()
    vehiculos = [v for v in todos_vehiculos if v.disponible and v.id not in vehiculos_ocupados_ids]
    
    result = []
    for v in vehiculos:
        result.append({
            'id': v.id,
            'placa': v.placa,
            'marca_modelo': f"{v.marca_modelo.marca} {v.marca_modelo.modelo}" if v.marca_modelo else 'Sin Marca/Modelo',
            'tipo': v.marca_modelo.tipo if v.marca_modelo else 'N/A',
            'precio_semanal': float(v.precio_semanal) if v.precio_semanal else 0.0
        })
    
    return jsonify(result)