"""
Inquilinos Routes - CRUD operations for tenant management
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from functools import wraps
from app import db
from app.models import (
    Usuario, Inquilino, HistoricoInquilino
)
from datetime import datetime
import os
from werkzeug.utils import secure_filename

inquilino_bp = Blueprint('inquilino', __name__, url_prefix='/inquilino')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'pdf'}
UPLOAD_FOLDER = 'app/static/uploads/inquilinos'

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
        return f'uploads/inquilinos/{unique_filename}'
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


# ==================== INQUILINOS ====================

@inquilino_bp.route('/inquilinos')
@login_required
@admin_required
def inquilinos():
    """List all tenants"""
    inquilinos = Inquilino.query.order_by(Inquilino.fecha_hora_registro.desc()).all()
    return render_template('modulos/inquilinos.html', inquilinos=inquilinos)


@inquilino_bp.route('/inquilinos/crear', methods=['POST'])
@login_required
@admin_required
def crear_inquilino():
    """Create new tenant"""
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
            return redirect(url_for('inquilino.inquilinos'))
        
        # Check if cedula already exists
        # Note: Since cedula is encrypted, we need to check differently
        # For now, we'll create the record
        
        # Handle document uploads
        cedula_path = None
        licencia_path = None
        buena_conducta_path = None
        
        if 'cedula_doc' in request.files:
            cedula_path = save_document(request.files['cedula_doc'], f'cedula_{cedula}')
        
        if 'licencia_doc' in request.files:
            licencia_path = save_document(request.files['licencia_doc'], f'licencia_{licencia}')
        
        if 'buena_conducta_doc' in request.files:
            buena_conducta_path = save_document(request.files['buena_conducta_doc'], f'buena_conducta_{cedula}')
        
        # Create new record
        nuevo_inquilino = Inquilino(
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
        
        db.session.add(nuevo_inquilino)
        db.session.flush()  # Get the ID before commit
        
        # Register in history
        #registrar_historico_inquilino(nuevo_inquilino, 'INSERT')
        
        db.session.commit()
        
        flash(f'Inquilino {nombre_apellido} creado exitosamente.', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error al crear inquilino: {str(e)}', 'danger')
    
    return redirect(url_for('inquilino.inquilinos'))


@inquilino_bp.route('/inquilinos/<int:id>/editar', methods=['POST'])
@login_required
@admin_required
def editar_inquilino(id):
    """Edit tenant"""
    inquilino = Inquilino.query.get_or_404(id)
    
    try:
        # Get form data
        new_nombre = request.form.get('nombre_apellido', '').strip()
        new_cedula = request.form.get('cedula', '').strip()
        new_licencia = request.form.get('licencia', '').strip()
        new_direccion = request.form.get('direccion', '').strip()
        new_telefono = request.form.get('telefono', '').strip()
        new_email = request.form.get('email', '').strip()
        
        # Validate required fields
        if not new_nombre or not new_cedula or not new_licencia:
            flash('Nombre, cédula y licencia son campos requeridos.', 'warning')
            return redirect(url_for('inquilino.inquilinos'))
        
        # Update basic fields
        inquilino.nombre_apellido = new_nombre
        inquilino.cedula = new_cedula
        inquilino.licencia = new_licencia
        inquilino.direccion = new_direccion if new_direccion else None
        inquilino.telefono = new_telefono if new_telefono else None
        inquilino.email = new_email if new_email else None
        inquilino.usuario_actualizo_id = current_user.id
        inquilino.fecha_hora_actualizo = datetime.now()
        
        # Handle document uploads
        if 'cedula_doc' in request.files:
            file = request.files['cedula_doc']
            if file and file.filename:
                # Delete old document
                if inquilino.cedula_path:
                    delete_document(inquilino.cedula_path)
                # Save new document
                inquilino.cedula_path = save_document(file, f'cedula_{new_cedula}')
        
        if 'licencia_doc' in request.files:
            file = request.files['licencia_doc']
            if file and file.filename:
                if inquilino.licencia_path:
                    delete_document(inquilino.licencia_path)
                inquilino.licencia_path = save_document(file, f'licencia_{new_licencia}')
        
        if 'buena_conducta_doc' in request.files:
            file = request.files['buena_conducta_doc']
            if file and file.filename:
                if inquilino.documento_buena_conducta_path:
                    delete_document(inquilino.documento_buena_conducta_path)
                inquilino.documento_buena_conducta_path = save_document(file, f'buena_conducta_{new_cedula}')
        
        # Register in history
        #registrar_historico_inquilino(inquilino, 'UPDATE')
        
        db.session.commit()
        flash(f'Inquilino {new_nombre} actualizado exitosamente.', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error al actualizar inquilino: {str(e)}', 'danger')
    
    return redirect(url_for('inquilino.inquilinos'))


@inquilino_bp.route('/inquilinos/<int:id>/eliminar', methods=['POST'])
@login_required
@admin_required
def eliminar_inquilino(id):
    """Delete tenant"""
    inquilino = Inquilino.query.get_or_404(id)
    
    try:
        # Register in history before deletion
        #registrar_historico_inquilino(inquilino, 'DELETE')
        
        # Delete associated documents
        if inquilino.cedula_path:
            delete_document(inquilino.cedula_path)
        if inquilino.licencia_path:
            delete_document(inquilino.licencia_path)
        if inquilino.documento_buena_conducta_path:
            delete_document(inquilino.documento_buena_conducta_path)
        
        inquilino_nombre = inquilino.nombre_apellido
        db.session.delete(inquilino)
        db.session.commit()
        
        flash(f'Inquilino {inquilino_nombre} eliminado exitosamente.', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar inquilino: {str(e)}', 'danger')
    
    return redirect(url_for('inquilino.inquilinos'))


@inquilino_bp.route('/inquilinos/<int:id>')
@login_required
@admin_required
def ver_inquilino(id):
    """View tenant details"""
    inquilino = Inquilino.query.get_or_404(id)
    return jsonify({
        'id': inquilino.id,
        'nombre_apellido': inquilino.nombre_apellido,
        'cedula': inquilino.cedula,
        'licencia': inquilino.licencia,
        'direccion': inquilino.direccion,
        'telefono': inquilino.telefono,
        'email': inquilino.email,
        'cedula_path': inquilino.cedula_path,
        'licencia_path': inquilino.licencia_path,
        'documento_buena_conducta_path': inquilino.documento_buena_conducta_path,
        'fecha_registro': inquilino.fecha_hora_registro.strftime('%d/%m/%Y %H:%M') if inquilino.fecha_hora_registro else None,
        'fecha_actualizacion': inquilino.fecha_hora_actualizo.strftime('%d/%m/%Y %H:%M') if inquilino.fecha_hora_actualizo else None
    })


@inquilino_bp.route('/inquilinos/<int:id>/historial')
@login_required
@admin_required
def historial_inquilino(id):
    """Get history for a specific tenant"""
    try:
        # Get inquilino info
        inquilino = Inquilino.query.get_or_404(id)
        inquilino_nombre = inquilino.nombre_apellido
        
        # Get all history records for this inquilino
        historico = HistoricoInquilino.query.filter_by(id=id).order_by(
            HistoricoInquilino.fecha_hora_operacion.desc()
        ).all()
        
        # Format history records
        historial_data = []
        for record in historico:
            # Get user info
            usuario = Usuario.query.get(record.usuario_operacion_id) if record.usuario_operacion_id else None
            usuario_nombre = f"{usuario.nombre} {usuario.apellido}" if usuario else "Sistema"
            usuario_iniciales = f"{usuario.nombre[0]}{usuario.apellido[0]}" if usuario else "SY"
            
            # Detect changes for UPDATE operations
            cambios = []
            if record.tipo_operacion == 'UPDATE':
                # Get previous record to compare
                previous = HistoricoInquilino.query.filter(
                    HistoricoInquilino.id == id,
                    HistoricoInquilino.fecha_hora_operacion < record.fecha_hora_operacion
                ).order_by(HistoricoInquilino.fecha_hora_operacion.desc()).first()
                
                if previous:
                    # Compare fields
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
                            # For path fields, simplify display
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
            'inquilino_nombre': inquilino_nombre,
            'historial': historial_data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al cargar historial: {str(e)}'
        }), 500


# ==================== HELPER FUNCTION ====================

def registrar_historico_inquilino(inquilino, tipo_operacion):
    """Register inquilino operation in history table"""
    historico = HistoricoInquilino(
        tipo_operacion=tipo_operacion,
        fecha_hora_operacion=datetime.now(),
        usuario_operacion_id=current_user.id,
        id=inquilino.id,
        nombre_apellido=inquilino.nombre_apellido,
        cedula=inquilino.cedula,
        licencia=inquilino.licencia,
        direccion=inquilino.direccion,
        telefono=inquilino.telefono,
        email=inquilino.email,
        cedula_path=inquilino.cedula_path,
        licencia_path=inquilino.licencia_path,
        documento_buena_conducta_path=inquilino.documento_buena_conducta_path,
        usuario_registro_id=inquilino.usuario_registro_id,
        fecha_hora_registro=inquilino.fecha_hora_registro,
        usuario_actualizo_id=inquilino.usuario_actualizo_id,
        fecha_hora_actualizo=inquilino.fecha_hora_actualizo
    )
    
    db.session.add(historico)


# ==================== API ENDPOINTS ====================

@inquilino_bp.route('/api/inquilinos')
@login_required
@admin_required
def api_inquilinos():
    """API endpoint for tenants list"""
    inquilinos = Inquilino.query.all()
    return jsonify([{
        'id': i.id,
        'nombre_apellido': i.nombre_apellido,
        'cedula': i.cedula,
        'licencia': i.licencia,
        'telefono': i.telefono,
        'email': i.email,
        'tiene_cedula_doc': bool(i.cedula_path),
        'tiene_licencia_doc': bool(i.licencia_path),
        'tiene_buena_conducta_doc': bool(i.documento_buena_conducta_path)
    } for i in inquilinos])


@inquilino_bp.route('/api/inquilinos/buscar')
@login_required
def buscar_inquilinos():
    """Search tenants by name or cedula"""
    query = request.args.get('q', '').strip()
    if len(query) < 2:
        return jsonify([])
    
    # Note: Since fields are encrypted, this search might need to be done differently
    # For now, we return all and filter client-side, or implement a different approach
    inquilinos = Inquilino.query.all()
    
    results = []
    for i in inquilinos:
        nombre = i.nombre_apellido or ''
        cedula = i.cedula or ''
        if query.lower() in nombre.lower() or query in cedula:
            results.append({
                'id': i.id,
                'nombre_apellido': nombre,
                'cedula': cedula,
                'telefono': i.telefono
            })
    
    return jsonify(results[:10])  # Limit to 10 results
