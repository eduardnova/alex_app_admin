"""
Propietarios Routes - CRUD operations for owner management
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from functools import wraps
from app import db
from app.models import (
    Usuario, Propietario, HistoricoPropietario, ReferenciaPropietario
)
from datetime import datetime
import os
from werkzeug.utils import secure_filename

propietario_bp = Blueprint('propietario', __name__, url_prefix='/propietario')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'pdf'}
UPLOAD_FOLDER = 'app/static/uploads/propietarios'

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
    """Save uploaded document and return the path"""
    if file and file.filename and allowed_file(file.filename):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = secure_filename(file.filename)
        name, ext = os.path.splitext(filename)
        unique_filename = f"{prefix}_{name}_{timestamp}{ext}"
        
        filepath = os.path.join(UPLOAD_FOLDER, unique_filename)
        file.save(filepath)
        return f'uploads/propietarios/{unique_filename}'
    return None

def delete_document(path):
    """Delete a document file"""
    if path:
        full_path = os.path.join('app/static', path)
        if os.path.exists(full_path):
            try:
                os.remove(full_path)
                return True
            except Exception as e:
                print(f"Error deleting file: {e}")
    return False


# ==================== PROPIETARIOS ====================

@propietario_bp.route('/propietarios')
@login_required
@admin_required
def propietarios():
    """List all owners"""
    propietarios = Propietario.query.order_by(Propietario.fecha_hora_registro.desc()).all()
    return render_template('modulos/propietarios.html', propietarios=propietarios)


@propietario_bp.route('/propietarios/crear', methods=['POST'])
@login_required
@admin_required
def crear_propietario():
    """Create new owner"""
    try:
        nombre_apellido = request.form.get('nombre_apellido', '').strip()
        cedula = request.form.get('cedula', '').strip()
        licencia = request.form.get('licencia', '').strip()
        direccion = request.form.get('direccion', '').strip()
        telefono = request.form.get('telefono', '').strip()
        email = request.form.get('email', '').strip()
        
        # Validate required fields
        if not nombre_apellido or not cedula or not licencia:
            flash('Nombre, cédula y licencia son campos requeridos.', 'warning')
            return redirect(url_for('propietario.propietarios'))
        
        # Handle document uploads
        cedula_path = None
        licencia_path = None
        buena_conducta_path = None
        
        if 'cedula_doc' in request.files:
            cedula_path = save_document(request.files['cedula_doc'], f'cedula_{cedula.replace("-", "")}')
        
        if 'licencia_doc' in request.files:
            licencia_path = save_document(request.files['licencia_doc'], f'licencia_{licencia.replace("-", "")}')
        
        if 'buena_conducta_doc' in request.files:
            buena_conducta_path = save_document(request.files['buena_conducta_doc'], f'buena_conducta_{cedula.replace("-", "")}')
        
        # Create new record
        nuevo_propietario = Propietario(
            nombre_apellido=nombre_apellido,
            cedula=cedula,
            licencia=licencia,
            direccion=direccion if direccion else None,
            telefono=telefono if telefono else None,
            email=email if email else None,
            cedula_path=cedula_path,
            licencia_path=licencia_path,
            documento_buena_conducta_path=buena_conducta_path,
            usuario_registro_id=current_user.id,
            usuario_actualizo_id=current_user.id,
            fecha_hora_registro=datetime.now(),
            fecha_hora_actualizo=datetime.now()
        )
        
        db.session.add(nuevo_propietario)
        db.session.flush()
        
        # Register in history
        #registrar_historico_propietario(nuevo_propietario, 'INSERT')
        
        db.session.commit()
        
        flash(f'Propietario {nombre_apellido} creado exitosamente.', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error al crear propietario: {str(e)}', 'danger')
    
    return redirect(url_for('propietario.propietarios'))


@propietario_bp.route('/propietarios/<int:id>/editar', methods=['POST'])
@login_required
@admin_required
def editar_propietario(id):
    """Edit owner"""
    propietario = Propietario.query.get_or_404(id)
    
    #try:
    new_nombre = request.form.get('nombre_apellido', '').strip()
    new_cedula = request.form.get('cedula', '').strip()
    new_licencia = request.form.get('licencia', '').strip()
    new_direccion = request.form.get('direccion', '').strip()
    new_telefono = request.form.get('telefono', '').strip()
    new_email = request.form.get('email', '').strip()
    
    # Validate required fields
    if not new_nombre or not new_cedula or not new_licencia:
        flash('Nombre, cédula y licencia son campos requeridos.', 'warning')
        return redirect(url_for('propietario.propietarios'))
    
    # Update basic fields
    propietario.nombre_apellido = new_nombre
    propietario.cedula = new_cedula
    propietario.licencia = new_licencia
    propietario.direccion = new_direccion if new_direccion else None
    propietario.telefono = new_telefono if new_telefono else None
    propietario.email = new_email if new_email else None
    propietario.usuario_actualizo_id = current_user.id
    propietario.fecha_hora_actualizo = datetime.now()
    
    # Handle document uploads
    if 'cedula_doc' in request.files:
        file = request.files['cedula_doc']
        if file and file.filename:
            if propietario.cedula_path:
                delete_document(propietario.cedula_path)
            propietario.cedula_path = save_document(file, f'cedula_{new_cedula.replace("-", "")}')
    
    if 'licencia_doc' in request.files:
        file = request.files['licencia_doc']
        if file and file.filename:
            if propietario.licencia_path:
                delete_document(propietario.licencia_path)
            propietario.licencia_path = save_document(file, f'licencia_{new_licencia.replace("-", "")}')
    
    if 'buena_conducta_doc' in request.files:
        file = request.files['buena_conducta_doc']
        if file and file.filename:
            if propietario.documento_buena_conducta_path:
                delete_document(propietario.documento_buena_conducta_path)
            propietario.documento_buena_conducta_path = save_document(file, f'buena_conducta_{new_cedula.replace("-", "")}')
    
    # Register in history
    #registrar_historico_propietario(propietario, 'UPDATE')
    
    db.session.commit()
    flash(f'Propietario {new_nombre} actualizado exitosamente.', 'success')
        
    #except Exception as e:
    #    db.session.rollback()
    #    flash(f'Error al actualizar propietario: {str(e)}', 'danger')
    
    return redirect(url_for('propietario.propietarios'))


@propietario_bp.route('/propietarios/<int:id>/eliminar', methods=['POST'])
@login_required
@admin_required
def eliminar_propietario(id):
    """Delete owner"""
    propietario = Propietario.query.get_or_404(id)
    
    try:
        # Register in history before deletion
        #registrar_historico_propietario(propietario, 'DELETE')
        
        # Delete associated documents
        if propietario.cedula_path:
            delete_document(propietario.cedula_path)
        if propietario.licencia_path:
            delete_document(propietario.licencia_path)
        if propietario.documento_buena_conducta_path:
            delete_document(propietario.documento_buena_conducta_path)
        
        propietario_nombre = propietario.nombre_apellido
        db.session.delete(propietario)
        db.session.commit()
        
        flash(f'Propietario {propietario_nombre} eliminado exitosamente.', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar propietario: {str(e)}', 'danger')
    
    return redirect(url_for('propietario.propietarios'))


@propietario_bp.route('/propietarios/<int:id>')
@login_required
@admin_required
def ver_propietario(id):
    """View owner details"""
    propietario = Propietario.query.get_or_404(id)
    return jsonify({
        'id': propietario.id,
        'nombre_apellido': propietario.nombre_apellido,
        'cedula': propietario.cedula,
        'licencia': propietario.licencia,
        'direccion': propietario.direccion,
        'telefono': propietario.telefono,
        'email': propietario.email,
        'cedula_path': propietario.cedula_path,
        'licencia_path': propietario.licencia_path,
        'documento_buena_conducta_path': propietario.documento_buena_conducta_path,
        'vehiculos_count': propietario.vehiculos.count(),
        'referencias_count': propietario.referencias.count(),
        'fecha_registro': propietario.fecha_hora_registro.strftime('%d/%m/%Y %H:%M') if propietario.fecha_hora_registro else None,
        'fecha_actualizacion': propietario.fecha_hora_actualizo.strftime('%d/%m/%Y %H:%M') if propietario.fecha_hora_actualizo else None
    })


@propietario_bp.route('/propietarios/<int:id>/historial')
@login_required
@admin_required
def historial_propietario(id):
    """Get history for a specific owner"""
    try:
        propietario = Propietario.query.get_or_404(id)
        propietario_nombre = propietario.nombre_apellido
        
        # Get all history records
        historico = HistoricoPropietario.query.filter_by(id=id).order_by(
            HistoricoPropietario.fecha_hora_operacion.desc()
        ).all()
        
        historial_data = []
        for record in historico:
            usuario = Usuario.query.get(record.usuario_operacion_id) if record.usuario_operacion_id else None
            usuario_nombre = f"{usuario.nombre} {usuario.apellido}" if usuario else "Sistema"
            usuario_iniciales = f"{usuario.nombre[0]}{usuario.apellido[0]}" if usuario else "SY"
            
            cambios = []
            if record.tipo_operacion == 'UPDATE':
                previous = HistoricoPropietario.query.filter(
                    HistoricoPropietario.id == id,
                    HistoricoPropietario.fecha_hora_operacion < record.fecha_hora_operacion
                ).order_by(HistoricoPropietario.fecha_hora_operacion.desc()).first()
                
                if previous:
                    fields_to_check = [
                        ('nombre_apellido', 'Nombre'),
                        ('cedula', 'Cédula'),
                        ('licencia', 'Licencia'),
                        ('direccion', 'Dirección'),
                        ('telefono', 'Teléfono'),
                        ('email', 'Email'),
                        ('cedula_path', 'Doc. Cédula'),
                        ('licencia_path', 'Doc. Licencia'),
                        ('documento_buena_conducta_path', 'Doc. Buena Conducta')
                    ]
                    
                    for field, label in fields_to_check:
                        old_value = getattr(previous, field)
                        new_value = getattr(record, field)
                        
                        if old_value != new_value:
                            if '_path' in field:
                                old_display = 'Sí' if old_value else 'No'
                                new_display = 'Sí' if new_value else 'No'
                            else:
                                old_display = old_value or 'N/A'
                                new_display = new_value or 'N/A'
                            
                            cambios.append({
                                'campo': label,
                                'valor_anterior': old_display,
                                'valor_nuevo': new_display
                            })
            
            historial_data.append({
                'id_historico': record.id_historico,
                'tipo_operacion': record.tipo_operacion,
                'fecha_hora': record.fecha_hora_operacion.strftime('%d/%m/%Y %H:%M:%S'),
                'usuario_nombre': usuario_nombre,
                'usuario_iniciales': usuario_iniciales,
                'nombre_apellido': record.nombre_apellido,
                'cedula': record.cedula,
                'licencia': record.licencia,
                'direccion': record.direccion,
                'telefono': record.telefono,
                'email': record.email,
                'cambios': cambios
            })
        
        return jsonify({
            'success': True,
            'propietario_nombre': propietario_nombre,
            'historial': historial_data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al cargar historial: {str(e)}'
        }), 500


# ==================== HELPER FUNCTION ====================

def registrar_historico_propietario(propietario, tipo_operacion):
    """Register propietario operation in history table"""
    historico = HistoricoPropietario(
        tipo_operacion=tipo_operacion,
        fecha_hora_operacion=datetime.now(),
        usuario_operacion_id=current_user.id,
        id=propietario.id,
        usuario_id=propietario.usuario_id,
        nombre_apellido=propietario.nombre_apellido,
        cedula=propietario.cedula,
        licencia=propietario.licencia,
        direccion=propietario.direccion,
        telefono=propietario.telefono,
        email=propietario.email,
        cedula_path=propietario.cedula_path,
        licencia_path=propietario.licencia_path,
        documento_buena_conducta_path=propietario.documento_buena_conducta_path,
        usuario_registro_id=propietario.usuario_registro_id,
        fecha_hora_registro=propietario.fecha_hora_registro,
        usuario_actualizo_id=propietario.usuario_actualizo_id,
        fecha_hora_actualizo=propietario.fecha_hora_actualizo
    )
    
    db.session.add(historico)


# ==================== API ENDPOINTS ====================

@propietario_bp.route('/api/propietarios')
@login_required
@admin_required
def api_propietarios():
    """API endpoint for owners list"""
    propietarios = Propietario.query.all()
    return jsonify([{
        'id': p.id,
        'nombre_apellido': p.nombre_apellido,
        'cedula': p.cedula,
        'licencia': p.licencia,
        'telefono': p.telefono,
        'email': p.email,
        'vehiculos_count': p.vehiculos.count(),
        'referencias_count': p.referencias.count(),
        'tiene_cedula_doc': bool(p.cedula_path),
        'tiene_licencia_doc': bool(p.licencia_path),
        'tiene_buena_conducta_doc': bool(p.documento_buena_conducta_path)
    } for p in propietarios])


@propietario_bp.route('/api/propietarios/buscar')
@login_required
def buscar_propietarios():
    """Search owners by name or cedula"""
    query = request.args.get('q', '').strip()
    if len(query) < 2:
        return jsonify([])
    
    propietarios = Propietario.query.all()
    
    results = []
    for p in propietarios:
        nombre = p.nombre_apellido or ''
        cedula = p.cedula or ''
        if query.lower() in nombre.lower() or query in cedula:
            results.append({
                'id': p.id,
                'nombre_apellido': nombre,
                'cedula': cedula,
                'telefono': p.telefono,
                'vehiculos_count': p.vehiculos.count()
            })
    
    return jsonify(results[:10])
