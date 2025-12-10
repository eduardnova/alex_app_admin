"""
Módulos Routes - Propietarios, Inquilinos, Vehículos, Alquileres, Pagos, Deudas
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db, cache
from app.models import (
    Propietario, 
    Inquilino, 
    Vehiculo, 
    Alquiler,
    Pago, 
    Deuda,
    VehiculoMarcaModelo, 
    EstadoAlquiler, 
    MetodoPago,
    Usuario,
    ReferenciaPropietario, 
    ReferenciaInquilino, 
    GaranteInquilino,
    Parentesco, 
    HistoricoPropietario,
    HistoricoReferenciaPropietario
)
from datetime import datetime
from werkzeug.utils import secure_filename
import os


modulos_bp = Blueprint('modulos', __name__)

# Configuración de archivos
UPLOAD_FOLDER = 'app/static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def handle_file_upload(file, folder):
    """Handle file upload and return path"""
    if not file or not file.filename:
        return None
    
    if allowed_file(file.filename):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = secure_filename(file.filename)
        name, ext = os.path.splitext(filename)
        unique_filename = f"{name}_{timestamp}{ext}"
        
        upload_path = os.path.join(UPLOAD_FOLDER, folder)
        os.makedirs(upload_path, exist_ok=True)
        
        filepath = os.path.join(upload_path, unique_filename)
        file.save(filepath)
        
        return f'uploads/{folder}/{unique_filename}'
    
    return None


# ==================== REFERENCIAS ENDPOINTS ====================

@modulos_bp.route('/referencias/crear', methods=['POST'])
@login_required
def crear_referencia():
    """Create new reference"""
    try:
        propietario_id = request.form.get('propietario_id')
        
        referencia = ReferenciaPropietario(
            propietario_id=propietario_id,
            nombre_apellido=request.form.get('nombre_apellido'),
            parentesco_id=request.form.get('parentesco_id'),
            telefono=request.form.get('telefono'),
            usuario_registro_id=current_user.id,
            usuario_actualizo_id=current_user.id,
            fecha_hora_registro=datetime.now(),
            fecha_hora_actualizo=datetime.now()
        )
        
        db.session.add(referencia)
        db.session.flush()
        
        # Register in history
        #registrar_historico_referencia(referencia, 'INSERT')
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Referencia guardada exitosamente'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Error al guardar referencia: {str(e)}'}), 400


@modulos_bp.route('/referencias/<int:id>/data')
@login_required
def referencia_data(id):
    """Get reference data"""
    referencia = ReferenciaPropietario.query.get_or_404(id)
    return jsonify({
        'id': referencia.id,
        'propietario_id': referencia.propietario_id,
        'nombre_apellido': referencia.nombre_apellido,
        'parentesco_id': referencia.parentesco_id,
        'telefono': referencia.telefono
    })


@modulos_bp.route('/referencias/<int:id>/editar', methods=['POST'])
@login_required
def editar_referencia(id):
    """Edit reference"""
    referencia = ReferenciaPropietario.query.get_or_404(id)
    
    try:
        referencia.nombre_apellido = request.form.get('nombre_apellido')
        referencia.parentesco_id = request.form.get('parentesco_id')
        referencia.telefono = request.form.get('telefono')
        referencia.usuario_actualizo_id = current_user.id
        referencia.fecha_hora_actualizo = datetime.now()
        
        # Register in history
        registrar_historico_referencia(referencia, 'UPDATE')
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Referencia actualizada exitosamente'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Error al actualizar referencia: {str(e)}'}), 400

@modulos_bp.route('/referencias/<int:id>/eliminar', methods=['POST'])
@login_required
def eliminar_referencia(id):
    """Delete reference"""
    referencia = ReferenciaPropietario.query.get_or_404(id)
    
    try:
        # Register in history before deletion
        registrar_historico_referencia(referencia, 'DELETE')
        
        db.session.delete(referencia)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Referencia eliminada exitosamente'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Error al eliminar referencia: {str(e)}'}), 400

@modulos_bp.route('/referencias/<int:id>/historial')
@login_required
def historial_referencia(id):
    """Get reference history"""
    try:
        referencia = ReferenciaPropietario.query.get_or_404(id)
        nombre = referencia.nombre_apellido
        
        historico = HistoricoReferenciaPropietario.query.filter_by(id=id).order_by(
            HistoricoReferenciaPropietario.fecha_hora_operacion.desc()
        ).all()
        
        historial_data = []
        for record in historico:
            usuario = Usuario.query.get(record.usuario_operacion_id) if record.usuario_operacion_id else None
            usuario_nombre = f"{usuario.nombre} {usuario.apellido}" if usuario else "Sistema"
            usuario_iniciales = f"{usuario.nombre[0]}{usuario.apellido[0]}" if usuario else "SY"
            
            cambios = []
            if record.tipo_operacion == 'UPDATE':
                previous = HistoricoReferenciaPropietario.query.filter(
                    HistoricoReferenciaPropietario.id == id,
                    HistoricoReferenciaPropietario.fecha_hora_operacion < record.fecha_hora_operacion
                ).order_by(HistoricoReferenciaPropietario.fecha_hora_operacion.desc()).first()
                
                if previous:
                    fields_to_check = [
                        ('nombre_apellido', 'Nombre'),
                        ('parentesco_id', 'Parentesco'),
                        ('telefono', 'Teléfono')
                    ]
                    
                    for field, label in fields_to_check:
                        old_value = getattr(previous, field)
                        new_value = getattr(record, field)
                        
                        if old_value != new_value:
                            cambios.append({
                                'campo': label,
                                'valor_anterior': str(old_value) if old_value else 'N/A',
                                'valor_nuevo': str(new_value) if new_value else 'N/A'
                            })
            
            historial_data.append({
                'tipo_operacion': record.tipo_operacion,
                'fecha_hora': record.fecha_hora_operacion.strftime('%d/%m/%Y %H:%M:%S'),
                'usuario_nombre': usuario_nombre,
                'usuario_iniciales': usuario_iniciales,
                'cambios': cambios
            })
        
        return jsonify({
            'success': True,
            'nombre': nombre,
            'historial': historial_data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al cargar historial: {str(e)}'
        }), 500
        
# ==================== VEHÍCULOS ENDPOINTS ====================

@modulos_bp.route('/vehiculos/crear', methods=['POST'])
@login_required
def crear_vehiculo():
    """Create new vehicle"""
    try:
        propietario_id = request.form.get('propietario_id')
        
        vehiculo = Vehiculo(
            propietario_id=propietario_id,
            placa=request.form.get('placa'),
            marca_modelo_vehiculo_id=request.form.get('marca_modelo_id'),
            ano=request.form.get('ano') if request.form.get('ano') else None,
            color=request.form.get('color'),
            descripcion=request.form.get('descripcion'),
            precio_semanal=request.form.get('precio_semanal'),
            condiciones=request.form.get('condiciones'),
            disponible=bool(int(request.form.get('disponible', 1))),
            usuario_registro_id=current_user.id,
            usuario_actualizo_id=current_user.id,
            fecha_hora_registro=datetime.now(),
            fecha_hora_actualizo=datetime.now()
        )
        
        db.session.add(vehiculo)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Vehículo guardado exitosamente'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Error al guardar vehículo: {str(e)}'}), 400

@modulos_bp.route('/vehiculos/<int:id>/data')
@login_required
def vehiculo_data(id):
    """Get vehicle data"""
    vehiculo = Vehiculo.query.get_or_404(id)
    return jsonify({
        'id': vehiculo.id,
        'propietario_id': vehiculo.propietario_id,
        'placa': vehiculo.placa,
        'marca_modelo_vehiculo_id': vehiculo.marca_modelo_vehiculo_id,
        'ano': vehiculo.ano,
        'color': vehiculo.color,
        'descripcion': vehiculo.descripcion,
        'precio_semanal': float(vehiculo.precio_semanal) if vehiculo.precio_semanal else 0,
        'condiciones': vehiculo.condiciones,
        'disponible': vehiculo.disponible
    })

@modulos_bp.route('/vehiculos/<int:id>/editar', methods=['POST'])
@login_required
def editar_vehiculo(id):
    """Edit vehicle"""
    vehiculo = Vehiculo.query.get_or_404(id)
    
    try:
        vehiculo.placa = request.form.get('placa')
        vehiculo.marca_modelo_vehiculo_id = request.form.get('marca_modelo_id')
        vehiculo.ano = request.form.get('ano') if request.form.get('ano') else None
        vehiculo.color = request.form.get('color')
        vehiculo.descripcion = request.form.get('descripcion')
        vehiculo.precio_semanal = request.form.get('precio_semanal')
        vehiculo.condiciones = request.form.get('condiciones')
        vehiculo.disponible = bool(int(request.form.get('disponible', 1)))
        vehiculo.usuario_actualizo_id = current_user.id
        vehiculo.fecha_hora_actualizo = datetime.now()
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Vehículo actualizado exitosamente'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Error al actualizar vehículo: {str(e)}'}), 400

@modulos_bp.route('/vehiculos/<int:id>/eliminar', methods=['POST'])
@login_required
def eliminar_vehiculo(id):
    """Delete vehicle"""
    vehiculo = Vehiculo.query.get_or_404(id)
    
    try:
        db.session.delete(vehiculo)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Vehículo eliminado exitosamente'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Error al eliminar vehículo: {str(e)}'}), 400
    
@modulos_bp.route('/vehiculos/<int:id>/historial')
@login_required
def historial_vehiculo(id):
    """Get vehicle history"""
    return jsonify({
        'success': True,
        'nombre': 'Vehículo',
        'historial': []
    })

# ==================== API ENDPOINTS FOR SELECTS ====================

@modulos_bp.route('/api/parentescos')
@login_required
def api_parentescos():
    """Get all parentescos for select"""
    parentescos = Parentesco.query.all()
    return jsonify([{
        'id': p.id,
        'parentesco': p.parentesco
    } for p in parentescos])

@modulos_bp.route('/api/marcas-modelos')
@login_required
def api_marcas_modelos():
    """Get all marcas modelos for select"""
    marcas = VehiculoMarcaModelo.query.all()
    return jsonify([{
        'id': m.id,
        'marca': m.marca,
        'modelo': m.modelo
    } for m in marcas])

# ==================== HELPER FUNCTIONS ====================

def registrar_historico_propietario(propietario, tipo_operacion):
    """Register propietario operation in history"""
    historico = HistoricoPropietario(
        tipo_operacion=tipo_operacion,
        fecha_hora_operacion=datetime.now(),
        usuario_operacion_id=current_user.id,
        id=propietario.id,
        usuario_id=propietario.usuario_id,
        nombre_apellido=propietario.nombre_apellido,
        documento_buena_conducta_path=propietario.documento_buena_conducta_path,
        cedula=propietario.cedula,
        cedula_path=propietario.cedula_path,
        licencia=propietario.licencia,
        licencia_path=propietario.licencia_path,
        direccion=propietario.direccion,
        telefono=propietario.telefono,
        email=propietario.email,
        usuario_registro_id=propietario.usuario_registro_id,
        fecha_hora_registro=propietario.fecha_hora_registro,
        usuario_actualizo_id=propietario.usuario_actualizo_id,
        fecha_hora_actualizo=propietario.fecha_hora_actualizo
    )
    
    db.session.add(historico)


def registrar_historico_referencia(referencia, tipo_operacion):
    """Register referencia operation in history"""
    historico = HistoricoReferenciaPropietario(
        tipo_operacion=tipo_operacion,
        fecha_hora_operacion=datetime.now(),
        usuario_operacion_id=current_user.id,
        id=referencia.id,
        propietario_id=referencia.propietario_id,
        nombre_apellido=referencia.nombre_apellido,
        parentesco_id=referencia.parentesco_id,
        telefono=referencia.telefono,
        usuario_registro_id=referencia.usuario_registro_id,
        fecha_hora_registro=referencia.fecha_hora_registro,
        usuario_actualizo_id=referencia.usuario_actualizo_id,
        fecha_hora_actualizo=referencia.fecha_hora_actualizo
    )
    
    db.session.add(historico)
# ==================== VEHÍCULOS ====================


# ==================== ALQUILERES ====================

@modulos_bp.route('/alquileres')
@login_required
@cache.cached(timeout=60, query_string=True)
def alquileres():
    """List all rentals"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    estado = request.args.get('estado')
    
    query = Alquiler.query
    
    if estado:
        query = query.filter_by(estado_id=estado)
    
    alquileres = query.order_by(
        Alquiler.fecha_alquiler_inicio.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)
    
    estados = EstadoAlquiler.query.all()
    
    return render_template('modulos/alquileres.html',
                         alquileres=alquileres,
                         estados=estados)


@modulos_bp.route('/alquileres/crear', methods=['GET', 'POST'])
@login_required
def crear_alquiler():
    """Create new rental"""
    if request.method == 'POST':
        alquiler = Alquiler(
            vehiculo_id=request.form.get('vehiculo_id'),
            inquilino_id=request.form.get('inquilino_id'),
            estado_id=request.form.get('estado_id'),
            fecha_alquiler_inicio=request.form.get('fecha_inicio'),
            fecha_alquiler_fin=request.form.get('fecha_fin'),
            semana=request.form.get('semana'),
            dia_trabajo=request.form.get('dia_trabajo'),
            ingreso=request.form.get('ingreso'),
            monto_descuento=request.form.get('monto_descuento', 0),
            concepto_descuento=request.form.get('concepto_descuento'),
            notas=request.form.get('notas'),
            usuario_registro_id=current_user.id,
            usuario_actualizo_id=current_user.id
        )
        
        db.session.add(alquiler)
        
        # Update vehicle availability
        vehiculo = Vehiculo.query.get(alquiler.vehiculo_id)
        vehiculo.disponible = False
        
        db.session.commit()
        cache.clear()
        
        flash('Alquiler creado exitosamente', 'success')
        return redirect(url_for('modulos.alquileres'))
    
    vehiculos = Vehiculo.query.filter_by(disponible=True).all()
    inquilinos = Inquilino.query.all()
    estados = EstadoAlquiler.query.all()
    
    return render_template('modulos/crear_alquiler.html',
                         vehiculos=vehiculos,
                         inquilinos=inquilinos,
                         estados=estados)


# ==================== PAGOS ====================

@modulos_bp.route('/pagos')
@login_required
@cache.cached(timeout=60, query_string=True)
def pagos():
    """List all payments"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    pagos = Pago.query.order_by(
        Pago.fecha_pago.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('modulos/pagos.html', pagos=pagos)


@modulos_bp.route('/pagos/crear', methods=['GET', 'POST'])
@login_required
def crear_pago():
    """Create new payment"""
    if request.method == 'POST':
        monto = float(request.form.get('monto'))
        deducciones = float(request.form.get('deducciones', 0))
        
        pago = Pago(
            alquiler_id=request.form.get('alquiler_id'),
            metodo_pago_id=request.form.get('metodo_pago_id'),
            monto=monto,
            fecha_pago=request.form.get('fecha_pago'),
            deducciones=deducciones,
            neto=monto - deducciones,
            comprobante=request.form.get('comprobante'),
            notas=request.form.get('notas'),
            usuario_registro_id=current_user.id,
            usuario_actualizo_id=current_user.id
        )
        
        db.session.add(pago)
        db.session.commit()
        cache.clear()
        
        flash('Pago registrado exitosamente', 'success')
        return redirect(url_for('modulos.pagos'))
    
    alquileres = Alquiler.query.filter(
        Alquiler.estado_id.in_([1, 2, 3])  # Pendiente, En curso, Validado
    ).all()
    metodos = MetodoPago.query.all()
    
    return render_template('modulos/crear_pago.html',
                         alquileres=alquileres,
                         metodos=metodos)


# ==================== DEUDAS ====================

@modulos_bp.route('/deudas')
@login_required
@cache.cached(timeout=60, query_string=True)
def deudas():
    """List all debts"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    estado = request.args.get('estado', 'pendiente')
    
    deudas = Deuda.query.filter_by(estado=estado).order_by(
        Deuda.fecha_vencimiento.asc()
    ).paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('modulos/deudas.html', deudas=deudas)