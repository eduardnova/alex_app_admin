"""
Inquilinos Routes - CRUD completo para inquilinos, referencias y garantes
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from functools import wraps
from app import db
from app.models import (
    Inquilino, ReferenciaInquilino, GaranteInquilino, Parentesco,
    HistoricoInquilino, HistoricoReferenciaInquilino, HistoricoGaranteInquilino,
    Usuario
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
    """Save document and return path"""
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
    """Delete document from filesystem"""
    if path:
        full_path = os.path.join('app/static', path)
        if os.path.exists(full_path):
            os.remove(full_path)


def registrar_historico_inquilino(inquilino, tipo_operacion):
    """Register inquilino history"""
    historico = HistoricoInquilino(
        tipo_operacion=tipo_operacion,
        fecha_hora_operacion=datetime.now(),
        usuario_operacion_id=current_user.id if current_user.is_authenticated else None,
        id=inquilino.id,
        nombre_apellido=inquilino.nombre_apellido,
        direccion=inquilino.direccion,
        telefono=inquilino.telefono,
        email=inquilino.email,
        documento_buena_conducta_path=inquilino.documento_buena_conducta_path,
        cedula=inquilino.cedula,
        cedula_path=inquilino.cedula_path,
        licencia=inquilino.licencia,
        licencia_path=inquilino.licencia_path,
        usuario_registro_id=inquilino.usuario_registro_id,
        fecha_hora_registro=inquilino.fecha_hora_registro,
        usuario_actualizo_id=inquilino.usuario_actualizo_id,
        fecha_hora_actualizo=inquilino.fecha_hora_actualizo
    )
    db.session.add(historico)


def registrar_historico_referencia(referencia, tipo_operacion):
    """Register referencia history"""
    historico = HistoricoReferenciaInquilino(
        tipo_operacion=tipo_operacion,
        fecha_hora_operacion=datetime.now(),
        usuario_operacion_id=current_user.id if current_user.is_authenticated else None,
        id=referencia.id,
        inquilino_id=referencia.inquilino_id,
        nombre_apellido=referencia.nombre_apellido,
        telefono=referencia.telefono,
        parentesco_id=referencia.parentesco_id,
        usuario_registro_id=referencia.usuario_registro_id,
        fecha_hora_registro=referencia.fecha_hora_registro,
        usuario_actualizo_id=referencia.usuario_actualizo_id,
        fecha_hora_actualizo=referencia.fecha_hora_actualizo
    )
    db.session.add(historico)


def registrar_historico_garante(garante, tipo_operacion):
    """Register garante history"""
    historico = HistoricoGaranteInquilino(
        tipo_operacion=tipo_operacion,
        fecha_hora_operacion=datetime.now(),
        usuario_operacion_id=current_user.id if current_user.is_authenticated else None,
        id=garante.id,
        inquilino_id=garante.inquilino_id,
        nombre_apellido=garante.nombre_apellido,
        direccion=garante.direccion,
        telefono=garante.telefono,
        email=garante.email,
        parentesco_id=garante.parentesco_id,
        documento_referencia_laboral_path=garante.documento_referencia_laboral_path,
        usuario_registro_id=garante.usuario_registro_id,
        fecha_hora_registro=garante.fecha_hora_registro,
        usuario_actualizo_id=garante.usuario_actualizo_id,
        fecha_hora_actualizo=garante.fecha_hora_actualizo
    )
    db.session.add(historico)


# ==================== INQUILINOS ====================

@inquilino_bp.route('/inquilinos')
@login_required
@admin_required
def inquilinos():
    """List all inquilinos"""
    inquilinos = Inquilino.query.order_by(Inquilino.fecha_hora_registro.desc()).all()
    parentescos = Parentesco.parentesco.all()
    return render_template('modulos/inquilinos.html', inquilinos=inquilinos, parentescos=parentescos)


@inquilino_bp.route('/inquilinos/crear', methods=['POST'])
@login_required
@admin_required
def crear_inquilino():
    """Create new inquilino"""
    try:
        nombre_apellido = request.form.get('nombre_apellido', '').strip()
        cedula = request.form.get('cedula', '').strip()
        licencia = request.form.get('licencia', '').strip()
        telefono = request.form.get('telefono', '').strip()
        email = request.form.get('email', '').strip()
        direccion = request.form.get('direccion', '').strip()
        
        if not nombre_apellido or not cedula or not licencia:
            flash('Nombre, cédula y licencia son campos requeridos.', 'warning')
            return redirect(url_for('inquilino.inquilinos'))
        
        # Handle document uploads
        cedula_path = save_document(request.files.get('cedula_doc'), 'cedula')
        licencia_path = save_document(request.files.get('licencia_doc'), 'licencia')
        buena_conducta_path = save_document(request.files.get('buena_conducta_doc'), 'buena_conducta')
        
        nuevo_inquilino = Inquilino(
            nombre_apellido=nombre_apellido,
            cedula=cedula,
            licencia=licencia,
            telefono=telefono if telefono else None,
            email=email if email else None,
            direccion=direccion if direccion else None,
            cedula_path=cedula_path,
            licencia_path=licencia_path,
            documento_buena_conducta_path=buena_conducta_path,
            usuario_registro_id=current_user.id,
            usuario_actualizo_id=current_user.id,
            fecha_hora_registro=datetime.now(),
            fecha_hora_actualizo=datetime.now()
        )
        
        db.session.add(nuevo_inquilino)
        db.session.flush()
        
        registrar_historico_inquilino(nuevo_inquilino, 'INSERT')
        
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
    """Edit inquilino"""
    inquilino = Inquilino.query.get_or_404(id)
    
    try:
        inquilino.nombre_apellido = request.form.get('nombre_apellido', '').strip()
        inquilino.cedula = request.form.get('cedula', '').strip()
        inquilino.licencia = request.form.get('licencia', '').strip()
        inquilino.telefono = request.form.get('telefono', '').strip() or None
        inquilino.email = request.form.get('email', '').strip() or None
        inquilino.direccion = request.form.get('direccion', '').strip() or None
        
        if not inquilino.nombre_apellido or not inquilino.cedula or not inquilino.licencia:
            flash('Nombre, cédula y licencia son campos requeridos.', 'warning')
            return redirect(url_for('inquilino.inquilinos'))
        
        # Handle document updates
        # Cédula
        if request.files.get('cedula_doc') and request.files['cedula_doc'].filename:
            if inquilino.cedula_path:
                delete_document(inquilino.cedula_path)
            inquilino.cedula_path = save_document(request.files['cedula_doc'], 'cedula')
        elif not request.form.get('cedula_doc_existing'):
            if inquilino.cedula_path:
                delete_document(inquilino.cedula_path)
            inquilino.cedula_path = None
        
        # Licencia
        if request.files.get('licencia_doc') and request.files['licencia_doc'].filename:
            if inquilino.licencia_path:
                delete_document(inquilino.licencia_path)
            inquilino.licencia_path = save_document(request.files['licencia_doc'], 'licencia')
        elif not request.form.get('licencia_doc_existing'):
            if inquilino.licencia_path:
                delete_document(inquilino.licencia_path)
            inquilino.licencia_path = None
        
        # Buena conducta
        if request.files.get('buena_conducta_doc') and request.files['buena_conducta_doc'].filename:
            if inquilino.documento_buena_conducta_path:
                delete_document(inquilino.documento_buena_conducta_path)
            inquilino.documento_buena_conducta_path = save_document(request.files['buena_conducta_doc'], 'buena_conducta')
        elif not request.form.get('buena_conducta_doc_existing'):
            if inquilino.documento_buena_conducta_path:
                delete_document(inquilino.documento_buena_conducta_path)
            inquilino.documento_buena_conducta_path = None
        
        inquilino.usuario_actualizo_id = current_user.id
        inquilino.fecha_hora_actualizo = datetime.now()
        
        registrar_historico_inquilino(inquilino, 'UPDATE')
        
        db.session.commit()
        flash(f'Inquilino {inquilino.nombre_apellido} actualizado exitosamente.', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error al actualizar inquilino: {str(e)}', 'danger')
    
    return redirect(url_for('inquilino.inquilinos'))


@inquilino_bp.route('/inquilinos/<int:id>/eliminar', methods=['POST'])
@login_required
@admin_required
def eliminar_inquilino(id):
    """Delete inquilino"""
    inquilino = Inquilino.query.get_or_404(id)
    
    try:
        registrar_historico_inquilino(inquilino, 'DELETE')
        
        # Delete associated documents
        delete_document(inquilino.cedula_path)
        delete_document(inquilino.licencia_path)
        delete_document(inquilino.documento_buena_conducta_path)
        
        # Delete garante documents
        for garante in inquilino.garantes:
            delete_document(garante.documento_referencia_laboral_path)
        
        nombre = inquilino.nombre_apellido
        db.session.delete(inquilino)
        db.session.commit()
        
        flash(f'Inquilino {nombre} eliminado exitosamente.', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar inquilino: {str(e)}', 'danger')
    
    return redirect(url_for('inquilino.inquilinos'))


@inquilino_bp.route('/inquilinos/<int:id>')
@login_required
@admin_required
def ver_inquilino(id):
    """Get inquilino details"""
    inquilino = Inquilino.query.get_or_404(id)
    
    return jsonify({
        'success': True,
        'inquilino': {
            'id': inquilino.id,
            'nombre_apellido': inquilino.nombre_apellido,
            'cedula': inquilino.cedula,
            'licencia': inquilino.licencia,
            'telefono': inquilino.telefono,
            'email': inquilino.email,
            'direccion': inquilino.direccion,
            'cedula_path': inquilino.cedula_path,
            'licencia_path': inquilino.licencia_path,
            'documento_buena_conducta_path': inquilino.documento_buena_conducta_path
        }
    })


@inquilino_bp.route('/inquilinos/<int:id>/historial')
@login_required
@admin_required
def historial_inquilino(id):
    """Get inquilino history"""
    inquilino = Inquilino.query.get_or_404(id)
    
    historial = HistoricoInquilino.query.filter_by(id=id).order_by(
        HistoricoInquilino.fecha_hora_operacion.desc()
    ).all()
    
    result = []
    prev_record = None
    
    # Reverse to process chronologically for change detection
    for record in reversed(historial):
        usuario = Usuario.query.get(record.usuario_operacion_id) if record.usuario_operacion_id else None
        
        item = {
            'id_historico': record.id_historico,
            'tipo_operacion': record.tipo_operacion,
            'fecha_hora': record.fecha_hora_operacion.strftime('%d/%m/%Y %H:%M:%S') if record.fecha_hora_operacion else '',
            'usuario_nombre': f"{usuario.nombre} {usuario.apellido}" if usuario else 'Sistema',
            'usuario_iniciales': f"{usuario.nombre[0]}{usuario.apellido[0]}" if usuario else 'S',
            'nombre_apellido': record.nombre_apellido,
            'cedula': record.cedula,
            'licencia': record.licencia,
            'cambios': []
        }
        
        # Detect changes for UPDATE
        if record.tipo_operacion == 'UPDATE' and prev_record:
            campos = [
                ('nombre_apellido', 'Nombre'),
                ('cedula', 'Cédula'),
                ('licencia', 'Licencia'),
                ('telefono', 'Teléfono'),
                ('email', 'Email'),
                ('direccion', 'Dirección'),
                ('cedula_path', 'Doc. Cédula'),
                ('licencia_path', 'Doc. Licencia'),
                ('documento_buena_conducta_path', 'Doc. Buena Conducta')
            ]
            
            for campo, label in campos:
                old_val = getattr(prev_record, campo, None)
                new_val = getattr(record, campo, None)
                if old_val != new_val:
                    item['cambios'].append({
                        'campo': label,
                        'valor_anterior': old_val or 'N/A',
                        'valor_nuevo': new_val or 'N/A'
                    })
        
        result.append(item)
        prev_record = record
    
    # Reverse back to show newest first
    result.reverse()
    
    return jsonify({
        'success': True,
        'inquilino_nombre': inquilino.nombre_apellido,
        'historial': result
    })


# ==================== REFERENCIAS ====================

@inquilino_bp.route('/inquilinos/<int:inquilino_id>/referencias')
@login_required
@admin_required
def listar_referencias(inquilino_id):
    """List referencias for inquilino"""
    referencias = ReferenciaInquilino.query.filter_by(inquilino_id=inquilino_id).order_by(
        ReferenciaInquilino.fecha_hora_registro.desc()
    ).all()
    
    result = []
    for ref in referencias:
        result.append({
            'id': ref.id,
            'nombre_apellido': ref.nombre_apellido,
            'telefono': ref.telefono,
            'parentesco_id': ref.parentesco_id,
            'parentesco_nombre': ref.parentesco.parentesco if ref.parentesco else 'N/A',
            'fecha_registro': ref.fecha_hora_registro.strftime('%d/%m/%Y %H:%M') if ref.fecha_hora_registro else ''
        })
    
    return jsonify({'success': True, 'referencias': result})


@inquilino_bp.route('/inquilinos/<int:inquilino_id>/referencias/crear', methods=['POST'])
@login_required
@admin_required
def crear_referencia(inquilino_id):
    """Create new referencia"""
    try:
        data = request.get_json()
        
        nombre_apellido = data.get('nombre_apellido', '').strip()
        telefono = data.get('telefono', '').strip()
        parentesco_id = data.get('parentesco_id')
        
        if not nombre_apellido or not telefono or not parentesco_id:
            return jsonify({'success': False, 'message': 'Todos los campos son requeridos'})
        
        nueva_referencia = ReferenciaInquilino(
            inquilino_id=inquilino_id,
            nombre_apellido=nombre_apellido,
            telefono=telefono,
            parentesco_id=parentesco_id,
            usuario_registro_id=current_user.id,
            usuario_actualizo_id=current_user.id,
            fecha_hora_registro=datetime.now(),
            fecha_hora_actualizo=datetime.now()
        )
        
        db.session.add(nueva_referencia)
        db.session.flush()
        
        registrar_historico_referencia(nueva_referencia, 'INSERT')
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Referencia creada exitosamente'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})


@inquilino_bp.route('/referencias/<int:id>/editar', methods=['POST'])
@login_required
@admin_required
def editar_referencia(id):
    """Edit referencia"""
    referencia = ReferenciaInquilino.query.get_or_404(id)
    
    try:
        data = request.get_json()
        
        referencia.nombre_apellido = data.get('nombre_apellido', '').strip()
        referencia.telefono = data.get('telefono', '').strip()
        referencia.parentesco_id = data.get('parentesco_id')
        referencia.usuario_actualizo_id = current_user.id
        referencia.fecha_hora_actualizo = datetime.now()
        
        registrar_historico_referencia(referencia, 'UPDATE')
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Referencia actualizada exitosamente'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})


@inquilino_bp.route('/referencias/<int:id>/eliminar', methods=['POST'])
@login_required
@admin_required
def eliminar_referencia(id):
    """Delete referencia"""
    referencia = ReferenciaInquilino.query.get_or_404(id)
    
    try:
        registrar_historico_referencia(referencia, 'DELETE')
        
        db.session.delete(referencia)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Referencia eliminada exitosamente'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})


# ==================== GARANTES ====================

@inquilino_bp.route('/inquilinos/<int:inquilino_id>/garantes')
@login_required
@admin_required
def listar_garantes(inquilino_id):
    """List garantes for inquilino"""
    garantes = GaranteInquilino.query.filter_by(inquilino_id=inquilino_id).order_by(
        GaranteInquilino.fecha_hora_registro.desc()
    ).all()
    
    result = []
    for gar in garantes:
        result.append({
            'id': gar.id,
            'nombre_apellido': gar.nombre_apellido,
            'direccion': gar.direccion,
            'telefono': gar.telefono,
            'email': gar.email,
            'parentesco_id': gar.parentesco_id,
            'parentesco_nombre': gar.parentesco.parentesco if gar.parentesco else 'N/A',
            'documento_referencia_laboral_path': gar.documento_referencia_laboral_path,
            'fecha_registro': gar.fecha_hora_registro.strftime('%d/%m/%Y %H:%M') if gar.fecha_hora_registro else ''
        })
    
    return jsonify({'success': True, 'garantes': result})


@inquilino_bp.route('/inquilinos/<int:inquilino_id>/garantes/crear', methods=['POST'])
@login_required
@admin_required
def crear_garante(inquilino_id):
    """Create new garante"""
    try:
        nombre_apellido = request.form.get('nombre_apellido', '').strip()
        telefono = request.form.get('telefono', '').strip()
        email = request.form.get('email', '').strip()
        direccion = request.form.get('direccion', '').strip()
        parentesco_id = request.form.get('parentesco_id')
        
        if not nombre_apellido or not parentesco_id:
            return jsonify({'success': False, 'message': 'Nombre y parentesco son requeridos'})
        
        # Handle document upload
        documento_path = save_document(request.files.get('documento'), 'garante_ref')
        
        nuevo_garante = GaranteInquilino(
            inquilino_id=inquilino_id,
            nombre_apellido=nombre_apellido,
            telefono=telefono if telefono else None,
            email=email if email else None,
            direccion=direccion if direccion else None,
            parentesco_id=parentesco_id,
            documento_referencia_laboral_path=documento_path,
            usuario_registro_id=current_user.id,
            usuario_actualizo_id=current_user.id,
            fecha_hora_registro=datetime.now(),
            fecha_hora_actualizo=datetime.now()
        )
        
        db.session.add(nuevo_garante)
        db.session.flush()
        
        registrar_historico_garante(nuevo_garante, 'INSERT')
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Garante creado exitosamente'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})


@inquilino_bp.route('/garantes/<int:id>/editar', methods=['POST'])
@login_required
@admin_required
def editar_garante(id):
    """Edit garante"""
    garante = GaranteInquilino.query.get_or_404(id)
    
    try:
        garante.nombre_apellido = request.form.get('nombre_apellido', '').strip()
        garante.telefono = request.form.get('telefono', '').strip() or None
        garante.email = request.form.get('email', '').strip() or None
        garante.direccion = request.form.get('direccion', '').strip() or None
        garante.parentesco_id = request.form.get('parentesco_id')
        
        # Handle document update
        if request.files.get('documento') and request.files['documento'].filename:
            if garante.documento_referencia_laboral_path:
                delete_document(garante.documento_referencia_laboral_path)
            garante.documento_referencia_laboral_path = save_document(request.files['documento'], 'garante_ref')
        elif not request.form.get('documento_existing'):
            if garante.documento_referencia_laboral_path:
                delete_document(garante.documento_referencia_laboral_path)
            garante.documento_referencia_laboral_path = None
        
        garante.usuario_actualizo_id = current_user.id
        garante.fecha_hora_actualizo = datetime.now()
        
        registrar_historico_garante(garante, 'UPDATE')
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Garante actualizado exitosamente'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})


@inquilino_bp.route('/garantes/<int:id>/eliminar', methods=['POST'])
@login_required
@admin_required
def eliminar_garante(id):
    """Delete garante"""
    garante = GaranteInquilino.query.get_or_404(id)
    
    try:
        registrar_historico_garante(garante, 'DELETE')
        
        # Delete document
        delete_document(garante.documento_referencia_laboral_path)
        
        db.session.delete(garante)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Garante eliminado exitosamente'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})


# ==================== API ENDPOINTS ====================

@inquilino_bp.route('/api/inquilinos')
@login_required
def api_inquilinos():
    """API: List all inquilinos"""
    inquilinos = Inquilino.query.order_by(Inquilino.nombre_apellido).all()
    
    result = []
    for inq in inquilinos:
        result.append({
            'id': inq.id,
            'nombre_apellido': inq.nombre_apellido,
            'cedula': inq.cedula,
            'licencia': inq.licencia,
            'telefono': inq.telefono,
            'email': inq.email
        })
    
    return jsonify(result)


@inquilino_bp.route('/api/inquilinos/buscar')
@login_required
def api_buscar_inquilinos():
    """API: Search inquilinos"""
    query = request.args.get('q', '').strip().lower()
    
    inquilinos = Inquilino.query.all()
    
    result = []
    for inq in inquilinos:
        # Search in decrypted fields
        searchable = f"{inq.nombre_apellido} {inq.cedula} {inq.licencia} {inq.telefono} {inq.email}".lower()
        if query in searchable:
            result.append({
                'id': inq.id,
                'nombre_apellido': inq.nombre_apellido,
                'cedula': inq.cedula,
                'telefono': inq.telefono
            })
    
    return jsonify(result)
