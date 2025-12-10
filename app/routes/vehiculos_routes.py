"""
Vehiculos Routes - CRUD completo para vehiculos, historial alquileres y reparaciones
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from functools import wraps
from app import db
from app.models import (
    Vehiculo, Alquiler, VehiculoMarcaModelo, Propietario,
    HistoricoVehiculo, HistoricoAlquiler,
    Usuario
)
from datetime import datetime
import os
from werkzeug.utils import secure_filename
from app.models import encrypt_data, decrypt_data  # Para placa encriptada

# Intentar importar TrabajoVehiculo (el nombre correcto según tu modelo)
try:
    from app.models import TrabajoVehiculo, HistoricoTrabajoVehiculo
    TRABAJOS_ENABLED = True
except ImportError:
    TRABAJOS_ENABLED = False
    print("⚠️  Warning: TrabajoVehiculo model not found. Reparaciones features disabled.")

vehiculo_bp = Blueprint('vehiculo', __name__, url_prefix='/vehiculo')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'pdf'}
UPLOAD_FOLDER = 'app/static/uploads/vehiculos'

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def admin_required(f):
    """Decorator to require admin role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.rol != 'admin':
            flash('Acceso denegado. Se requieren permisos de administrador.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function


def save_document(file, prefix):
    """Save document and return path"""
    if file and file.filename and allowed_file(file.filename):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = secure_filename(file.filename)
        name, ext = os.path.splitext(filename)
        unique_filename = f"{prefix}_{name}_{timestamp}{ext}"
        filepath = os.path.join(UPLOAD_FOLDER, unique_filename)
        file.save(filepath)
        return f'uploads/vehiculos/{unique_filename}'
    return None


def delete_document(path):
    """Delete document from filesystem"""
    if path:
        full_path = os.path.join('app/static', path)
        if os.path.exists(full_path):
            os.remove(full_path)


def registrar_historico_vehiculo(vehiculo, tipo_operacion):
    """Register vehiculo history"""
    historico = HistoricoVehiculo(
        tipo_operacion=tipo_operacion,
        fecha_hora_operacion=datetime.now(),
        usuario_operacion_id=current_user.id if current_user.is_authenticated else None,
        id=vehiculo.id,
        propietario_id=vehiculo.propietario_id,
        placa=vehiculo.placa,
        marca_modelo_vehiculo_id=vehiculo.marca_modelo_vehiculo_id,
        ano=vehiculo.ano,
        color=vehiculo.color,
        descripcion=vehiculo.descripcion,
        precio_semanal=vehiculo.precio_semanal,
        condiciones=vehiculo.condiciones,
        disponible=vehiculo.disponible,
        usuario_registro_id=vehiculo.usuario_registro_id,
        fecha_hora_registro=vehiculo.fecha_hora_registro,
        usuario_actualizo_id=vehiculo.usuario_actualizo_id,
        fecha_hora_actualizo=vehiculo.fecha_hora_actualizo
    )
    db.session.add(historico)


# ==================== VEHICULOS ====================

@vehiculo_bp.route('/vehiculos')
@login_required
@admin_required
def vehiculos():
    """List all vehiculos"""
    vehiculos = Vehiculo.query.order_by(Vehiculo.fecha_hora_registro.desc()).all()
    marca_modelos = VehiculoMarcaModelo.query.order_by(VehiculoMarcaModelo.marca).all()
    
    # Si Propietario tiene columnas nombre y apellido separadas, ordenar por nombre
    # Si nombre_apellido es una propiedad híbrida, ordenar en Python después de traer todos
    try:
        # Intentar ordenar por columna nombre directamente en DB
        propietarios = Propietario.query.order_by(Propietario.nombre).all()
    except AttributeError:
        # Si no existe la columna nombre, traer todos y ordenar en Python
        propietarios = Propietario.query.all()
        try:
            propietarios = sorted(propietarios, key=lambda p: (p.nombre_apellido or '').lower())
        except:
            pass
    
    return render_template('modulos/vehiculos.html', vehiculos=vehiculos, marca_modelos=marca_modelos, propietarios=propietarios)


@vehiculo_bp.route('/vehiculos/crear', methods=['POST'])
@login_required
@admin_required
def crear_vehiculo():
    """Create new vehiculo"""
    
    #try:
    placa = request.form.get('placa', '').strip()
    ano = request.form.get('ano')
    color = request.form.get('color', '').strip()
    descripcion = request.form.get('descripcion', '').strip()
    precio_semanal = request.form.get('precio_semanal')
    condiciones = request.form.get('condiciones', '').strip()
    disponible = 'disponible' in request.form
    marca_modelo_id = request.form.get('marca_modelo_id')
    propietario_id = request.form.get('propietario_id')
    
    if not placa or not ano or not marca_modelo_id or not propietario_id:
        flash('Placa, año, marca/modelo y propietario son requeridos.', 'warning')
        return redirect(url_for('vehiculo.vehiculos'))
    
    placa_encrypted = encrypt_data(placa)
    
    nuevo_vehiculo = Vehiculo(
        placa=placa_encrypted,
        ano=ano,
        color=color if color else None,
        descripcion=descripcion if descripcion else None,
        precio_semanal=precio_semanal if precio_semanal else None,
        condiciones=condiciones if condiciones else None,
        disponible=disponible,
        marca_modelo_vehiculo_id=marca_modelo_id,
        propietario_id=propietario_id,
        usuario_registro_id=current_user.id,
        usuario_actualizo_id=current_user.id,
        fecha_hora_registro=datetime.now(),
        fecha_hora_actualizo=datetime.now()
    )
    
    db.session.add(nuevo_vehiculo)
    db.session.flush()
        
        #registrar_historico_vehiculo(nuevo_vehiculo, 'INSERT')
        
    db.session.commit()
    flash(f'Vehículo creado exitosamente.', 'success')
        
    #except Exception as e:
    #    db.session.rollback()
    #    flash(f'Error al crear vehículo: {str(e)}', 'danger')
    
    return redirect(url_for('vehiculo.vehiculos'))


@vehiculo_bp.route('/vehiculos/<int:id>/editar', methods=['POST'])
@login_required
@admin_required
def editar_vehiculo(id):
    """Edit vehiculo"""
    vehiculo = Vehiculo.query.get_or_404(id)
    
    try:
        placa = request.form.get('placa', '').strip()
        vehiculo.ano = request.form.get('ano')
        vehiculo.color = request.form.get('color', '').strip() or None
        vehiculo.descripcion = request.form.get('descripcion', '').strip() or None
        vehiculo.precio_semanal = request.form.get('precio_semanal')
        vehiculo.condiciones = request.form.get('condiciones', '').strip() or None
        vehiculo.disponible = 'disponible' in request.form
        vehiculo.marca_modelo_vehiculo_id = request.form.get('marca_modelo_id')
        vehiculo.propietario_id = request.form.get('propietario_id')
        
        if placa:
            vehiculo.placa = encrypt_data(placa)
        
        if not vehiculo.placa or not vehiculo.ano or not vehiculo.marca_modelo_vehiculo_id or not vehiculo.propietario_id:
            flash('Placa, año, marca/modelo y propietario son requeridos.', 'warning')
            return redirect(url_for('vehiculo.vehiculos'))
        
        vehiculo.usuario_actualizo_id = current_user.id
        vehiculo.fecha_hora_actualizo = datetime.now()
        
        registrar_historico_vehiculo(vehiculo, 'UPDATE')
        
        db.session.commit()
        flash(f'Vehículo actualizado exitosamente.', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error al actualizar vehículo: {str(e)}', 'danger')
    
    return redirect(url_for('vehiculo.vehiculos'))


@vehiculo_bp.route('/vehiculos/<int:id>/eliminar', methods=['POST'])
@login_required
@admin_required
def eliminar_vehiculo(id):
    """Delete vehiculo"""
    vehiculo = Vehiculo.query.get_or_404(id)
    
    try:
        registrar_historico_vehiculo(vehiculo, 'DELETE')
        
        db.session.delete(vehiculo)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Vehículo eliminado exitosamente'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})


@vehiculo_bp.route('/vehiculos/<int:id>')
@login_required
@admin_required
def get_vehiculo(id):
    """Get vehiculo details for edit"""
    try:
        vehiculo = Vehiculo.query.get_or_404(id)
        
        # Desencriptar placa para form - con manejo de errores
        placa_decrypted = None
        if vehiculo.placa:
            try:
                placa_decrypted = decrypt_data(vehiculo.placa)
            except Exception as decrypt_error:
                # Si falla la desencriptación, asumir que está en texto plano
                print(f"⚠️  Placa no encriptada o error de desencriptación: {decrypt_error}")
                placa_decrypted = vehiculo.placa
        
        return jsonify({
            'success': True, 
            'vehiculo': {
                'id': vehiculo.id,
                'placa': placa_decrypted,
                'marca_modelo_vehiculo_id': vehiculo.marca_modelo_vehiculo_id,
                'propietario_id': vehiculo.propietario_id,
                'ano': vehiculo.ano,
                'color': vehiculo.color,
                'descripcion': vehiculo.descripcion,
                'precio_semanal': float(vehiculo.precio_semanal) if vehiculo.precio_semanal else None,
                'condiciones': vehiculo.condiciones,
                'disponible': vehiculo.disponible
            }
        })
    except Exception as e:
        print(f"Error en get_vehiculo: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'Error al cargar vehículo: {str(e)}'
        }), 500


# ==================== ALQUILERES ====================

@vehiculo_bp.route('/vehiculos/<int:vehiculo_id>/alquileres')
@login_required
@admin_required
def listar_alquileres(vehiculo_id):
    """List alquileres for vehiculo (historial inquilinos)"""
    alquileres = Alquiler.query.filter_by(vehiculo_id=vehiculo_id).order_by(
        Alquiler.fecha_hora_registro.desc()
    ).all()
    
    result = []
    for alq in alquileres:
        result.append({
            'id': alq.id,
            'inquilino_nombre': alq.inquilino.nombre_apellido if alq.inquilino else 'N/A',
            'fecha_inicio': alq.fecha_alquiler_inicio.isoformat() if alq.fecha_alquiler_inicio else None,
            'fecha_fin': alq.fecha_alquiler_fin.isoformat() if alq.fecha_alquiler_fin else None,
            'ingreso': float(alq.ingreso) if alq.ingreso else None,
            'notas': alq.notas
        })
    
    return jsonify({'success': True, 'alquileres': result})


# ==================== REPARACIONES ====================

@vehiculo_bp.route('/vehiculos/<int:vehiculo_id>/reparaciones')
@login_required
@admin_required
def listar_reparaciones(vehiculo_id):
    """List reparaciones (trabajos) for vehiculo"""
    try:
        # Usar TrabajoVehiculo en lugar de TrabajosVehiculo
        from app.models import TrabajoVehiculo
        
        reparaciones = TrabajoVehiculo.query.filter_by(vehiculo_id=vehiculo_id).order_by(
            TrabajoVehiculo.fecha_hora_registro.desc()
        ).all()
        
        result = []
        for rep in reparaciones:
            result.append({
                'id': rep.id,
                'tipo_trabajo_nombre': rep.tipo_trabajo.nombre if hasattr(rep, 'tipo_trabajo') and rep.tipo_trabajo else 'N/A',
                'fecha_inicio': rep.fecha_inicio.isoformat() if rep.fecha_inicio else None,
                'fecha_fin': rep.fecha_fin.isoformat() if rep.fecha_fin else None,
                'costo': float(rep.costo) if rep.costo else None,
                'notas': rep.notas
            })
        
        return jsonify({'success': True, 'reparaciones': result})
    except ImportError:
        return jsonify({'success': True, 'reparaciones': []})


# ==================== HISTORIAL ====================

@vehiculo_bp.route('/vehiculos/<int:id>/historial')
@login_required
@admin_required
def historial_vehiculo(id):
    """Get vehiculo history"""
    try:
        # Verificar que el vehículo existe
        vehiculo = Vehiculo.query.get(id)
        if not vehiculo:
            return jsonify({
                'success': False,
                'message': 'Vehículo no encontrado'
            }), 404
        
        # Obtener historial - filtrar por el id del vehículo (no id_historico)
        historicos = HistoricoVehiculo.query.filter_by(id=id).order_by(
            HistoricoVehiculo.fecha_hora_operacion.desc()
        ).all()
        
        print(f"📊 Historial encontrado: {len(historicos)} registros para vehículo {id}")
        
        result = []
        for hist in historicos:
            # Obtener información del usuario
            usuario_nombre = 'Sistema'
            usuario_iniciales = 'SYS'
            if hist.usuario_operacion_id:
                usuario = Usuario.query.get(hist.usuario_operacion_id)
                if usuario:
                    usuario_nombre = f'{usuario.nombre} {usuario.apellido}'
                    usuario_iniciales = f'{usuario.nombre[0]}{usuario.apellido[0]}'.upper()
            
            # Obtener información de marca/modelo
            marca = None
            modelo = None
            if hist.marca_modelo_vehiculo_id:
                marca_modelo = VehiculoMarcaModelo.query.get(hist.marca_modelo_vehiculo_id)
                if marca_modelo:
                    marca = marca_modelo.marca
                    modelo = marca_modelo.modelo
            
            # Desencriptar placa con manejo de errores
            placa = 'N/A'
            if hist.placa:
                try:
                    placa = decrypt_data(hist.placa)
                except:
                    placa = hist.placa  # Si falla, usar texto plano
            
            cambios = []  # Lógica para diffs si needed (comparar con prev)
            result.append({
                'tipo_operacion': hist.tipo_operacion,
                'fecha_hora': hist.fecha_hora_operacion.strftime('%d/%m/%Y %H:%M'),
                'usuario_nombre': usuario_nombre,
                'usuario_iniciales': usuario_iniciales,
                'marca': marca,
                'modelo': modelo,
                'placa': placa,
                'cambios': cambios
            })
        
        vehiculo_nombre = 'Desconocido'
        if vehiculo and vehiculo.marca_modelo:
            vehiculo_nombre = f'{vehiculo.marca_modelo.marca} {vehiculo.marca_modelo.modelo}'
        
        print(f"✅ Retornando {len(result)} registros de historial")
        
        return jsonify({
            'success': True,
            'vehiculo_nombre': vehiculo_nombre,
            'historial': result
        })
    except Exception as e:
        print(f"❌ Error en historial_vehiculo: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500



# ==================== API ENDPOINTS ====================

@vehiculo_bp.route('/api/vehiculos')
@login_required
def api_vehiculos():
    """API: List all vehiculos"""
    vehiculos = Vehiculo.query.order_by(Vehiculo.marca_modelo_vehiculo_id).all()
    
    result = []
    for veh in vehiculos:
        # Desencriptar placa con manejo de errores
        placa = None
        if veh.placa:
            try:
                placa = decrypt_data(veh.placa)
            except:
                placa = veh.placa  # Si falla, usar texto plano
        
        result.append({
            'id': veh.id,
            'marca': veh.marca_modelo.marca,
            'modelo': veh.marca_modelo.modelo,
            'placa': placa,
            'ano': veh.ano,
            'color': veh.color,
            'precio_semanal': veh.precio_semanal
        })
    
    return jsonify(result)


@vehiculo_bp.route('/api/vehiculos/buscar')
@login_required
def api_buscar_vehiculos():
    """API: Search vehiculos"""
    query = request.args.get('q', '').strip().lower()
    
    vehiculos = Vehiculo.query.all()
    
    result = []
    for veh in vehiculos:
        # Desencriptar placa con manejo de errores
        placa_dec = ''
        if veh.placa:
            try:
                placa_dec = decrypt_data(veh.placa)
            except:
                placa_dec = veh.placa  # Si falla, usar texto plano
        
        searchable = f"{veh.marca_modelo.marca} {veh.marca_modelo.modelo} {placa_dec} {veh.ano} {veh.color}".lower()
        if query in searchable:
            result.append({
                'id': veh.id,
                'marca_modelo': f"{veh.marca_modelo.marca} {veh.marca_modelo.modelo}",
                'placa': placa_dec
            })
    
    return jsonify(result)