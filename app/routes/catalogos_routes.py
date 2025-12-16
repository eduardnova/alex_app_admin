"""
Admin Routes - User management, access logs, system configuration
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from functools import wraps
from app import db
from app.models import (
    Usuario, RegistroAcceso,HistoricoVehiculoMarcaModelo,HistoricoBanco,HistoricoParentesco, VehiculoMarcaModelo, EstadoAlquiler,
    MetodoPago, TipoCuenta, Banco, Parentesco
)
from datetime import datetime
import os
from werkzeug.utils import secure_filename

catalogo_bp = Blueprint('catalogo', __name__, url_prefix='/catalogo')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
UPLOAD_FOLDER = 'app/static/uploads/logos'

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

# ==================== MARCAS Y MODELOS ====================

@catalogo_bp.route('/marcas_modelos')
@login_required
@admin_required
def marcas_modelos():
    """List vehicle brands and models"""
    # Se cambia el ordenamiento: fecha_hora_registro descendente (del más nuevo al más viejo)
    marcas = VehiculoMarcaModelo.query.order_by(VehiculoMarcaModelo.fecha_hora_registro.desc()).all()
    
    return render_template('catalogos/vehiculo_marca_modelo.html', marcas=marcas)

@catalogo_bp.route('/marcas_modelos/crear', methods=['POST'])
@login_required
@admin_required
def crear_marca_modelo():
    """Create new vehicle brand/model"""
    try:
        marca = request.form.get('marca', '').strip()
        modelo = request.form.get('modelo', '').strip()
        tipo = request.form.get('tipo', '').strip()
        descripcion = request.form.get('descripcion', '').strip()
        
        # Validate required fields
        if not marca or not modelo or not tipo:
            flash('Marca, modelo y tipo son campos requeridos.', 'warning')
            return redirect(url_for('catalogo.marcas_modelos'))
        
        # Check if combination already exists
        exists = VehiculoMarcaModelo.query.filter_by(
            marca=marca, 
            modelo=modelo
        ).first()
        
        if exists:
            flash(f'Ya existe una marca/modelo con el nombre {marca} {modelo}.', 'warning')
            return redirect(url_for('catalogo.marcas_modelos'))
        
        # Handle logo upload
        logo_path = None
        if 'logo' in request.files:
            file = request.files['logo']
            if file and file.filename and allowed_file(file.filename):
                # Create unique filename
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = secure_filename(file.filename)
                name, ext = os.path.splitext(filename)
                unique_filename = f"{name}_{timestamp}{ext}"
                
                filepath = os.path.join(UPLOAD_FOLDER, unique_filename)
                file.save(filepath)
                logo_path = f'uploads/logos/{unique_filename}'
        
        # Create new record
        nueva_marca = VehiculoMarcaModelo(
            marca=marca,
            modelo=modelo,
            tipo=tipo,
            descripcion=descripcion if descripcion else None,
            logo_path=logo_path,
            usuario_registro_id=current_user.id,
            usuario_actualizo_id=current_user.id,
            # ✅ Nombres de columnas corregidos
            fecha_hora_registro=datetime.now(),       
            fecha_hora_actualizo=datetime.now()
        )
        
        db.session.add(nueva_marca)
        db.session.flush()  # Get the ID before commit
        
        # Register in history
        #registrar_historico(nueva_marca, 'INSERT')
        
        db.session.commit()
        
        flash(f'Marca/Modelo {marca} {modelo} creado exitosamente.', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error al crear marca/modelo: {str(e)}', 'danger')
    
    return redirect(url_for('catalogo.marcas_modelos'))

@catalogo_bp.route('/marcas_modelos/<int:id>/editar', methods=['POST'])
@login_required
@admin_required
def editar_marca_modelo(id):
    """Edit vehicle brand/model"""
    marca = VehiculoMarcaModelo.query.get_or_404(id)
    
    try:
        # Update basic fields
        new_marca = request.form.get('marca', '').strip()
        new_modelo = request.form.get('modelo', '').strip()
        new_tipo = request.form.get('tipo', '').strip()
        new_descripcion = request.form.get('descripcion', '').strip()
        
        # Validate required fields
        if not new_marca or not new_modelo or not new_tipo:
            flash('Marca, modelo y tipo son campos requeridos.', 'warning')
            return redirect(url_for('catalogo.marcas_modelos'))
        
        # Check if new combination already exists (excluding current record)
        exists = VehiculoMarcaModelo.query.filter(
            VehiculoMarcaModelo.id != id,
            VehiculoMarcaModelo.marca == new_marca,
            VehiculoMarcaModelo.modelo == new_modelo
        ).first()
        
        if exists:
            flash(f'Ya existe otra marca/modelo con el nombre {new_marca} {new_modelo}.', 'warning')
            return redirect(url_for('catalogo.marcas_modelos'))
        
        marca.marca = new_marca
        marca.modelo = new_modelo
        marca.tipo = new_tipo
        marca.descripcion = new_descripcion if new_descripcion else None
        marca.usuario_actualizo_id = current_user.id
        marca.fecha_hora_actualizo = datetime.now()
        
        # Handle logo upload
        if 'logo' in request.files:
            file = request.files['logo']
            if file and file.filename and allowed_file(file.filename):
                # Delete old logo if exists
                if marca.logo_path:
                    old_logo = os.path.join('app/static', marca.logo_path)
                    if os.path.exists(old_logo):
                        try:
                            os.remove(old_logo)
                        except Exception as e:
                            print(f"Error deleting old logo: {e}")
                
                # Save new logo
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = secure_filename(file.filename)
                name, ext = os.path.splitext(filename)
                unique_filename = f"{name}_{timestamp}{ext}"
                
                filepath = os.path.join(UPLOAD_FOLDER, unique_filename)
                file.save(filepath)
                marca.logo_path = f'uploads/logos/{unique_filename}'
        
        # Register in history
        #registrar_historico(marca, 'UPDATE')
        
        db.session.commit()
        flash(f'Marca/Modelo {marca.marca} {marca.modelo} actualizado exitosamente.', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error al actualizar marca/modelo: {str(e)}', 'danger')
    
    return redirect(url_for('catalogo.marcas_modelos'))

@catalogo_bp.route('/marcas_modelos/<int:id>/eliminar', methods=['POST'])
@login_required
@admin_required
def eliminar_marca_modelo(id):
    """Delete vehicle brand/model"""
    marca = VehiculoMarcaModelo.query.get_or_404(id)
    
    try:
        # Register in history before deletion
        #registrar_historico(marca, 'DELETE')
        
        # Delete logo file if exists
        if marca.logo_path:
            logo_file = os.path.join('app/static', marca.logo_path)
            if os.path.exists(logo_file):
                try:
                    os.remove(logo_file)
                except Exception as e:
                    print(f"Error deleting logo file: {e}")
        
        marca_nombre = f"{marca.marca} {marca.modelo}"
        db.session.delete(marca)
        db.session.commit()
        
        flash(f'Marca/Modelo {marca_nombre} eliminado exitosamente.', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar marca/modelo: {str(e)}', 'danger')
    
    return redirect(url_for('catalogo.marcas_modelos'))

@catalogo_bp.route('/marcas_modelos/<int:id>')
@login_required
@admin_required
def ver_marca_modelo(id):
    """View vehicle brand/model details"""
    marca = VehiculoMarcaModelo.query.get_or_404(id)
    return jsonify({
        'id': marca.id,
        'marca': marca.marca,
        'modelo': marca.modelo,
        'tipo': marca.tipo,
        'descripcion': marca.descripcion,
        'logo_path': marca.logo_path,
        'fecha_registro': marca.fecha_registro.strftime('%d/%m/%Y %H:%M') if marca.fecha_registro else None,
        'fecha_actualizacion': marca.fecha_actualizacion.strftime('%d/%m/%Y %H:%M') if marca.fecha_actualizacion else None
    })

@catalogo_bp.route('/marcas_modelos/<int:id>/historial')
@login_required
@admin_required
def historial_marca_modelo(id):
    """Get history for a specific marca/modelo"""
    try:
        # Get marca info
        marca = VehiculoMarcaModelo.query.get_or_404(id)
        marca_nombre = f"{marca.marca} {marca.modelo}"
        
        # Get all history records for this marca/modelo
        historico = HistoricoVehiculoMarcaModelo.query.filter_by(id=id).order_by(
            HistoricoVehiculoMarcaModelo.fecha_hora_operacion.desc()
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
                previous = HistoricoVehiculoMarcaModelo.query.filter(
                    HistoricoVehiculoMarcaModelo.id == id,
                    HistoricoVehiculoMarcaModelo.fecha_hora_operacion < record.fecha_hora_operacion
                ).order_by(HistoricoVehiculoMarcaModelo.fecha_hora_operacion.desc()).first()
                
                if previous:
                    # Compare fields
                    fields_to_check = [
                        ('marca', 'Marca'),
                        ('modelo', 'Modelo'),
                        ('tipo', 'Tipo'),
                        ('descripcion', 'Descripción'),
                        ('logo_path', 'Logo')
                    ]
                    
                    for field, label in fields_to_check:
                        old_value = getattr(previous, field)
                        new_value = getattr(record, field)
                        
                        if old_value != new_value:
                            cambios.append({
                                'campo': label,
                                'valor_anterior': old_value or 'N/A',
                                'valor_nuevo': new_value or 'N/A'
                            })
            
            historial_data.append({
                'id_historico': record.id_historico,
                'tipo_operacion': record.tipo_operacion,
                'fecha_hora': record.fecha_hora_operacion.strftime('%d/%m/%Y %H:%M:%S'),
                'usuario_nombre': usuario_nombre,
                'usuario_iniciales': usuario_iniciales,
                'marca': record.marca,
                'modelo': record.modelo,
                'tipo': record.tipo,
                'descripcion': record.descripcion,
                'logo_path': record.logo_path,
                'cambios': cambios
            })
        
        return jsonify({
            'success': True,
            'marca_nombre': marca_nombre,
            'historial': historial_data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al cargar historial: {str(e)}'
        }), 500

# ==================== ESTADOS DE ALQUILER ====================

@catalogo_bp.route('/estados_alquiler')
@login_required
@admin_required
def estados_alquiler():
    """List rental states"""
    estados = EstadoAlquiler.query.all()
    return render_template('catalogos/estados_alquiler.html', estados=estados)

@catalogo_bp.route('/estados_alquiler/crear', methods=['GET', 'POST'])
@login_required
@admin_required
def crear_estado_alquiler():
    """Create new rental state"""
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        descripcion = request.form.get('descripcion')
        
        nuevo_estado = EstadoAlquiler(
            nombre=nombre,
            descripcion=descripcion,
            usuario_registro_id=current_user.id,
            usuario_actualizo_id=current_user.id
        )
        
        try:
            db.session.add(nuevo_estado)
            db.session.commit()
            flash('Estado de alquiler creado exitosamente.', 'success')
            return redirect(url_for('catalogo.estados_alquiler'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear estado: {str(e)}', 'danger')
    
    return render_template('catalogos/crear_estado_alquiler.html')

@catalogo_bp.route('/estados_alquiler/<int:id>')
@login_required
@admin_required
def ver_estado_alquiler(id):
    """View rental state details"""
    estado = EstadoAlquiler.query.get_or_404(id)
    return render_template('catalogos/ver_estado_alquiler.html', estado=estado)

@catalogo_bp.route('/estados_alquiler/<int:id>/editar', methods=['GET', 'POST'])
@login_required
@admin_required
def editar_estado_alquiler(id):
    """Edit rental state"""
    estado = EstadoAlquiler.query.get_or_404(id)
    
    if request.method == 'POST':
        estado.nombre = request.form.get('nombre')
        estado.descripcion = request.form.get('descripcion')
        estado.usuario_actualizo_id = current_user.id
        
        try:
            db.session.commit()
            flash('Estado de alquiler actualizado exitosamente.', 'success')
            return redirect(url_for('catalogo.estados_alquiler'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar estado: {str(e)}', 'danger')
    
    return render_template('catalogos/editar_estado_alquiler.html', estado=estado)

@catalogo_bp.route('/estados_alquiler/<int:id>/eliminar', methods=['POST'])
@login_required
@admin_required
def eliminar_estado_alquiler(id):
    """Delete rental state"""
    estado = EstadoAlquiler.query.get_or_404(id)
    
    try:
        db.session.delete(estado)
        db.session.commit()
        flash('Estado de alquiler eliminado exitosamente.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar estado: {str(e)}', 'danger')
    
    return redirect(url_for('catalogo.estados_alquiler'))

@catalogo_bp.route('/estados-alquiler/<int:id>/json')
@login_required
@admin_required
def ver_estado_alquiler_json(id):
    estado = EstadoAlquiler.query.get_or_404(id)
    return jsonify({
        'success': True,
        'data': {
            'id': estado.id,
            'nombre': estado.nombre,
            'descripcion': estado.descripcion
        }
    })
# ==================== MÉTODOS DE PAGO ====================

@catalogo_bp.route('/metodos_pago')
@login_required
@admin_required
def metodos_pago():
    """List payment methods"""
    metodos = MetodoPago.query.all()
    return render_template('catalogos/metodos_pago.html', metodos=metodos)

@catalogo_bp.route('/metodos_pago/crear', methods=['GET', 'POST'])
@login_required
@admin_required
def crear_metodo_pago():
    """Create new payment method"""
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        descripcion = request.form.get('descripcion')
        
        nuevo_metodo = MetodoPago(
            nombre=nombre,
            descripcion=descripcion,
            usuario_registro_id=current_user.id,
            usuario_actualizo_id=current_user.id
        )
        
        try:
            db.session.add(nuevo_metodo)
            db.session.commit()
            flash('Método de pago creado exitosamente.', 'success')
            return redirect(url_for('catalogo.metodos_pago'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear método de pago: {str(e)}', 'danger')
    
    return render_template('catalogos/crear_metodo_pago.html')

@catalogo_bp.route('/metodos_pago/<int:id>')
@login_required
@admin_required
def ver_metodo_pago(id):
    """View payment method details"""
    metodo = MetodoPago.query.get_or_404(id)
    return render_template('catalogos/ver_metodo_pago.html', metodo=metodo)

@catalogo_bp.route('/metodos_pago/<int:id>/editar', methods=['GET', 'POST'])
@login_required
@admin_required
def editar_metodo_pago(id):
    """Edit payment method"""
    metodo = MetodoPago.query.get_or_404(id)
    
    if request.method == 'POST':
        metodo.nombre = request.form.get('nombre')
        metodo.descripcion = request.form.get('descripcion')
        metodo.usuario_actualizo_id = current_user.id
        
        try:
            db.session.commit()
            flash('Método de pago actualizado exitosamente.', 'success')
            return redirect(url_for('catalogo.metodos_pago'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar método de pago: {str(e)}', 'danger')
    
    return render_template('catalogos/editar_metodo_pago.html', metodo=metodo)

@catalogo_bp.route('/metodos_pago/<int:id>/eliminar', methods=['POST'])
@login_required
@admin_required
def eliminar_metodo_pago(id):
    """Delete payment method"""
    metodo = MetodoPago.query.get_or_404(id)
    
    try:
        db.session.delete(metodo)
        db.session.commit()
        flash('Método de pago eliminado exitosamente.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar método de pago: {str(e)}', 'danger')
    
    return redirect(url_for('catalogo.metodos_pago'))

# ==================== TIPOS DE CUENTA ====================

@catalogo_bp.route('/catalogos/tipo-cuentas')
@login_required
@admin_required
def tipo_cuentas():
    """List account types"""
    tipos = TipoCuenta.query.all()
    return render_template('catalogos/tipo_cuentas.html', tipos=tipos)

@catalogo_bp.route('/catalogos/tipo-cuentas/crear', methods=['GET', 'POST'])
@login_required
@admin_required
def crear_tipo_cuenta():
    """Create new account type"""
    if request.method == 'POST':
        tipo_cuenta = request.form.get('tipo_cuenta')
        descripcion = request.form.get('descripcion')
        
        nuevo_tipo = TipoCuenta(
            tipo_cuenta=tipo_cuenta,
            descripcion=descripcion,
            usuario_registro_id=current_user.id,
            usuario_actualizo_id=current_user.id
        )
        
        try:
            db.session.add(nuevo_tipo)
            db.session.commit()
            flash('Tipo de cuenta creado exitosamente.', 'success')
            return redirect(url_for('catalogo.tipo_cuentas'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear tipo de cuenta: {str(e)}', 'danger')
    
    return render_template('catalogos/crear_tipo_cuenta.html')

@catalogo_bp.route('/catalogos/tipo-cuentas/<int:id>')
@login_required
@admin_required
def ver_tipo_cuenta(id):
    """View account type details"""
    tipo = TipoCuenta.query.get_or_404(id)
    return render_template('catalogos/ver_tipo_cuenta.html', tipo=tipo)

@catalogo_bp.route('/catalogos/tipo-cuentas/<int:id>/editar', methods=['GET', 'POST'])
@login_required
@admin_required
def editar_tipo_cuenta(id):
    """Edit account type"""
    tipo = TipoCuenta.query.get_or_404(id)
    
    if request.method == 'POST':
        tipo.tipo_cuenta = request.form.get('tipo_cuenta')
        tipo.descripcion = request.form.get('descripcion')
        tipo.usuario_actualizo_id = current_user.id
        
        try:
            db.session.commit()
            flash('Tipo de cuenta actualizado exitosamente.', 'success')
            return redirect(url_for('catalogo.tipo_cuentas'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar tipo de cuenta: {str(e)}', 'danger')
    
    return render_template('catalogos/editar_tipo_cuenta.html', tipo=tipo)

@catalogo_bp.route('/catalogos/tipo-cuentas/<int:id>/eliminar', methods=['POST'])
@login_required
@admin_required
def eliminar_tipo_cuenta(id):
    """Delete account type"""
    tipo = TipoCuenta.query.get_or_404(id)
    
    try:
        db.session.delete(tipo)
        db.session.commit()
        flash('Tipo de cuenta eliminado exitosamente.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar tipo de cuenta: {str(e)}', 'danger')
    
    return redirect(url_for('catalogo.tipo_cuentas'))

@catalogo_bp.route('/tipo-cuentas/<int:id>/json')
@login_required
@admin_required
def ver_tipo_cuenta_json(id):
    tipo = TipoCuenta.query.get_or_404(id)
    return jsonify({
        'success': True,
        'data': {
            'id': tipo.id,
            'tipo_cuenta': tipo.tipo_cuenta,
            'descripcion': tipo.descripcion
        }
    })
# ==================== BANCOS ====================


@catalogo_bp.route('/catalogos/bancos')
@login_required
@admin_required
def bancos():
    """List banks"""

    # Ordenar por la columna real (encriptada), NO por la property
    bancos = Banco.query.order_by(Banco.banco, Banco.cuenta).all()

    # Convertir a JSON serializable
    bancos_json = [{
        "id": b.id,
        "banco": b.banco,
        "cuenta": b.cuenta or "",  # <-- evita None
        "cedula": b.cedula or "",
        "tipo_cuenta": b.tipo_cuenta.tipo_cuenta if b.tipo_cuenta else None,
        "administrador": b.administrador,
        "logo_path": b.logo_path,
        "descripcion": b.descripcion,
        "fecha_registro": b.fecha_hora_registro,
        "fecha_actualizacion": b.fecha_hora_actualizo
    } for b in bancos]

    tipos_cuenta = TipoCuenta.query.all()
    return render_template('catalogos/bancos.html', bancos=bancos_json, tipos_cuenta=tipos_cuenta)

@catalogo_bp.route('/catalogos/bancos/crear', methods=['POST'])
@login_required
@admin_required
def crear_banco():
    """Create new bank"""
    try:
        banco_nombre = request.form.get('banco', '').strip()
        cuenta = request.form.get('cuenta', '').strip()
        tipo_cuenta_id = request.form.get('tipo_cuenta_id')
        cedula = request.form.get('cedula', '').strip()
        administrador = request.form.get('administrador', '').strip()
        descripcion = request.form.get('descripcion', '').strip()
        
        # Validate required fields
        if not banco_nombre or not cuenta or not tipo_cuenta_id or not cedula or not administrador:
            flash('Todos los campos requeridos deben completarse.', 'warning')
            return redirect(url_for('catalogo.bancos'))
        
        # Check if account already exists
        exists = Banco.query.filter_by(cuenta=cuenta).first()
        if exists:
            flash(f'Ya existe una cuenta con el número {cuenta}.', 'warning')
            return redirect(url_for('catalogo.bancos'))
        
        # Handle logo upload
        logo_path = None
        if 'logo' in request.files:
            file = request.files['logo']
            if file and file.filename and allowed_file(file.filename):
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = secure_filename(file.filename)
                name, ext = os.path.splitext(filename)
                unique_filename = f"{name}_{timestamp}{ext}"
                
                filepath = os.path.join(UPLOAD_FOLDER, unique_filename)
                file.save(filepath)
                logo_path = f'uploads/logos/{unique_filename}'
        
        # Create new bank
        nuevo_banco = Banco(
            banco=banco_nombre,
            cuenta=cuenta,  # Will be encrypted automatically
            tipo_cuenta_id=tipo_cuenta_id,
            cedula=cedula,  # Will be encrypted automatically
            administrador=administrador,
            descripcion=descripcion if descripcion else None,
            logo_path=logo_path,
            usuario_registro_id=current_user.id,
            usuario_actualizo_id=current_user.id,
            fecha_hora_registro=datetime.now(),
            fecha_hora_actualizo=datetime.now()
        )
        
        db.session.add(nuevo_banco)
        db.session.flush()
        
        # Register in history
        registrar_historico_banco(nuevo_banco, 'INSERT')
        
        db.session.commit()
        flash(f'Cuenta bancaria {banco_nombre} creada exitosamente.', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error al crear cuenta bancaria: {str(e)}', 'danger')
    
    return redirect(url_for('catalogo.bancos'))

@catalogo_bp.route('/catalogos/bancos/<int:id>/editar', methods=['POST'])
@login_required
@admin_required
def editar_banco(id):
    """Edit bank"""
    banco = Banco.query.get_or_404(id)
    
    try:
        new_banco_nombre = request.form.get('banco', '').strip()
        new_cuenta = request.form.get('cuenta', '').strip()
        new_tipo_cuenta_id = request.form.get('tipo_cuenta_id')
        new_cedula = request.form.get('cedula', '').strip()
        new_administrador = request.form.get('administrador', '').strip()
        new_descripcion = request.form.get('descripcion', '').strip()
        
        # Validate required fields
        if not new_banco_nombre or not new_cuenta or not new_tipo_cuenta_id or not new_cedula or not new_administrador:
            flash('Todos los campos requeridos deben completarse.', 'warning')
            return redirect(url_for('catalogo.bancos'))
        
        # Check if new account number already exists (excluding current record)
        exists = Banco.query.filter(
            Banco.id != id,
            Banco.cuenta == new_cuenta
        ).first()
        
        if exists:
            flash(f'Ya existe otra cuenta con el número {new_cuenta}.', 'warning')
            return redirect(url_for('catalogo.bancos'))
        
        # Update fields
        banco.banco = new_banco_nombre
        banco.cuenta = new_cuenta
        banco.tipo_cuenta_id = new_tipo_cuenta_id
        banco.cedula = new_cedula
        banco.administrador = new_administrador
        banco.descripcion = new_descripcion if new_descripcion else None
        banco.usuario_actualizo_id = current_user.id
        banco.fecha_hora_actualizo = datetime.now()
        
        # Handle logo upload
        if 'logo' in request.files:
            file = request.files['logo']
            if file and file.filename and allowed_file(file.filename):
                # Delete old logo if exists
                if banco.logo_path:
                    old_logo = os.path.join('app/static', banco.logo_path)
                    if os.path.exists(old_logo):
                        try:
                            os.remove(old_logo)
                        except Exception as e:
                            print(f"Error deleting old logo: {e}")
                
                # Save new logo
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = secure_filename(file.filename)
                name, ext = os.path.splitext(filename)
                unique_filename = f"{name}_{timestamp}{ext}"
                
                filepath = os.path.join(UPLOAD_FOLDER, unique_filename)
                file.save(filepath)
                banco.logo_path = f'uploads/logos/{unique_filename}'
        
        # Register in history
        registrar_historico_banco(banco, 'UPDATE')
        
        db.session.commit()
        flash(f'Cuenta bancaria {banco.banco} actualizada exitosamente.', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error al actualizar cuenta bancaria: {str(e)}', 'danger')
    
    return redirect(url_for('catalogo.bancos'))

@catalogo_bp.route('/catalogos/bancos/<int:id>/eliminar', methods=['POST'])
@login_required
@admin_required
def eliminar_banco(id):
    """Delete bank"""
    banco = Banco.query.get_or_404(id)
    
    try:
        # Register in history before deletion
        registrar_historico_banco(banco, 'DELETE')
        
        # Delete logo file if exists
        if banco.logo_path:
            logo_file = os.path.join('app/static', banco.logo_path)
            if os.path.exists(logo_file):
                try:
                    os.remove(logo_file)
                except Exception as e:
                    print(f"Error deleting logo file: {e}")
        
        banco_nombre = f"{banco.banco} - {banco.cuenta}"
        db.session.delete(banco)
        db.session.commit()
        
        flash(f'Cuenta bancaria {banco_nombre} eliminada exitosamente.', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar cuenta bancaria: {str(e)}', 'danger')
    
    return redirect(url_for('catalogo.bancos'))

@catalogo_bp.route('/catalogos/bancos/<int:id>')
@login_required
@admin_required
def ver_banco(id):
    """View bank details"""
    banco = Banco.query.get_or_404(id)
    return jsonify({
        'id': banco.id,
        'banco': banco.banco,
        'cuenta': banco.cuenta,
        'tipo_cuenta_id': banco.tipo_cuenta_id,
        'cedula': banco.cedula,
        'administrador': banco.administrador,
        'descripcion': banco.descripcion,
        'logo_path': banco.logo_path,
        'fecha_registro': banco.fecha_hora_registro.strftime('%d/%m/%Y %H:%M') if banco.fecha_hora_registro else None,
        'fecha_actualizacion': banco.fecha_hora_actualizo.strftime('%d/%m/%Y %H:%M') if banco.fecha_hora_actualizo else None
    })

@catalogo_bp.route('/catalogos/bancos/<int:id>/historial')
@login_required
@admin_required
def historial_banco(id):
    """Get history for a specific bank account"""
    try:
        # Get banco info
        banco = Banco.query.get_or_404(id)
        banco_nombre = f"{banco.banco} - {banco.cuenta}"
        
        # Get all history records for this banco
        historico = HistoricoBanco.query.filter_by(id=id).order_by(
            HistoricoBanco.fecha_hora_operacion.desc()
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
                previous = HistoricoBanco.query.filter(
                    HistoricoBanco.id == id,
                    HistoricoBanco.fecha_hora_operacion < record.fecha_hora_operacion
                ).order_by(HistoricoBanco.fecha_hora_operacion.desc()).first()
                
                if previous:
                    # Compare fields
                    fields_to_check = [
                        ('banco', 'Banco'),
                        ('cuenta', 'Cuenta'),
                        ('cedula', 'Cédula'),
                        ('administrador', 'Administrador'),
                        ('descripcion', 'Descripción'),
                        ('logo_path', 'Logo')
                    ]
                    
                    for field, label in fields_to_check:
                        old_value = getattr(previous, field)
                        new_value = getattr(record, field)
                        
                        if old_value != new_value:
                            cambios.append({
                                'campo': label,
                                'valor_anterior': old_value or 'N/A',
                                'valor_nuevo': new_value or 'N/A'
                            })
            
            historial_data.append({
                'id_historico': record.id_historico,
                'tipo_operacion': record.tipo_operacion,
                'fecha_hora': record.fecha_hora_operacion.strftime('%d/%m/%Y %H:%M:%S'),
                'usuario_nombre': usuario_nombre,
                'usuario_iniciales': usuario_iniciales,
                'banco': record.banco,
                'cuenta': record.cuenta,
                'cedula': record.cedula,
                'administrador': record.administrador,
                'descripcion': record.descripcion,
                'logo_path': record.logo_path,
                'cambios': cambios
            })
        
        return jsonify({
            'success': True,
            'banco_nombre': banco_nombre,
            'historial': historial_data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al cargar historial: {str(e)}'
        }), 500

@catalogo_bp.route('/catalogos/bancos/<int:id>/json')
@login_required
@admin_required
def ver_banco_json(id):
    banco = Banco.query.get_or_404(id)
    return jsonify({
        'success': True,
        'data': {
            'id': banco.id,
            'banco': banco.banco,
            'cuenta': banco.cuenta,
            'tipo_cuenta_id': banco.tipo_cuenta_id,
            'cedula': banco.cedula,
            'administrador': banco.administrador,
            'descripcion': banco.descripcion,
            'logo_path': banco.logo_path
        }
    })

# Helper function to register history
def registrar_historico_banco(banco, tipo_operacion):
    """Register banco operation in history"""
    historico = HistoricoBanco(
        tipo_operacion=tipo_operacion,
        fecha_hora_operacion=datetime.now(),
        usuario_operacion_id=current_user.id if current_user.is_authenticated else None,
        id=banco.id,
        banco=banco.banco,
        cuenta=banco.cuenta,  # Already decrypted by property
        tipo_cuenta_id=banco.tipo_cuenta_id,
        cedula=banco.cedula,  # Already decrypted by property
        administrador=banco.administrador,
        logo_path=banco.logo_path,
        descripcion=banco.descripcion,
        usuario_registro_id=banco.usuario_registro_id,
        fecha_hora_registro=banco.fecha_hora_registro,
        usuario_actualizo_id=banco.usuario_actualizo_id,
        fecha_hora_actualizo=banco.fecha_hora_actualizo
    )
    db.session.add(historico)
# ==================== PARENTESCOS ====================

@catalogo_bp.route('/parentescos')
@login_required
@admin_required
def parentescos():
    """List relationships"""
    parentescos = Parentesco.query.order_by(Parentesco.parentesco).all()
    return render_template('catalogos/parentescos.html', parentescos=parentescos)

@catalogo_bp.route('/parentescos/crear', methods=['POST'])
@login_required
@admin_required
def crear_parentesco():
    """Create new relationship"""
    try:
        parentesco = request.form.get('parentesco', '').strip()
        
        # Validate required field
        if not parentesco:
            flash('El tipo de parentesco es requerido.', 'warning')
            return redirect(url_for('catalogo.parentescos'))
        
        # Check if already exists
        exists = Parentesco.query.filter_by(parentesco=parentesco).first()
        if exists:
            flash(f'Ya existe un parentesco con el nombre {parentesco}.', 'warning')
            return redirect(url_for('catalogo.parentescos'))
        
        # Create new record
        nuevo_parentesco = Parentesco(
            parentesco=parentesco,
            usuario_registro_id=current_user.id,
            usuario_actualizo_id=current_user.id,
            fecha_hora_registro=datetime.now(),
            fecha_hora_actualizo=datetime.now()
        )
        
        db.session.add(nuevo_parentesco)
        db.session.flush()  # Get the ID before commit
        
        # Register in history
        registrar_historico_parentesco(nuevo_parentesco, 'INSERT')
        
        db.session.commit()
        flash(f'Parentesco {parentesco} creado exitosamente.', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error al crear parentesco: {str(e)}', 'danger')
    
    return redirect(url_for('catalogo.parentescos'))

@catalogo_bp.route('/parentescos/<int:id>')
@login_required
@admin_required
def ver_parentesco(id):
    """View relationship details"""
    parentesco = Parentesco.query.get_or_404(id)
    return jsonify({
        'id': parentesco.id,
        'parentesco': parentesco.parentesco,
        'fecha_registro': parentesco.fecha_hora_registro.strftime('%d/%m/%Y %H:%M') if parentesco.fecha_hora_registro else None,
        'fecha_actualizacion': parentesco.fecha_hora_actualizo.strftime('%d/%m/%Y %H:%M') if parentesco.fecha_hora_actualizo else None
    })

@catalogo_bp.route('/parentescos/<int:id>/editar', methods=['POST'])
@login_required
@admin_required
def editar_parentesco(id):
    """Edit relationship"""
    parentesco = Parentesco.query.get_or_404(id)
    
    try:
        new_parentesco = request.form.get('parentesco', '').strip()
        
        # Validate required field
        if not new_parentesco:
            flash('El tipo de parentesco es requerido.', 'warning')
            return redirect(url_for('catalogo.parentescos'))
        
        # Check if new name already exists (excluding current record)
        exists = Parentesco.query.filter(
            Parentesco.id != id,
            Parentesco.parentesco == new_parentesco
        ).first()
        
        if exists:
            flash(f'Ya existe otro parentesco con el nombre {new_parentesco}.', 'warning')
            return redirect(url_for('catalogo.parentescos'))
        
        # Update fields
        parentesco.parentesco = new_parentesco
        parentesco.usuario_actualizo_id = current_user.id
        parentesco.fecha_hora_actualizo = datetime.now()
        
        # Register in history
        registrar_historico_parentesco(parentesco, 'UPDATE')
        
        db.session.commit()
        flash(f'Parentesco {parentesco.parentesco} actualizado exitosamente.', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error al actualizar parentesco: {str(e)}', 'danger')
    
    return redirect(url_for('catalogo.parentescos'))

@catalogo_bp.route('/parentescos/<int:id>/eliminar', methods=['POST'])
@login_required
@admin_required
def eliminar_parentesco(id):
    """Delete relationship"""
    parentesco = Parentesco.query.get_or_404(id)
    
    try:
        # Register in history before deletion
        registrar_historico_parentesco(parentesco, 'DELETE')
        
        parentesco_nombre = parentesco.parentesco
        db.session.delete(parentesco)
        db.session.commit()
        
        flash(f'Parentesco {parentesco_nombre} eliminado exitosamente.', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar parentesco: {str(e)}', 'danger')
    
    return redirect(url_for('catalogo.parentescos'))

@catalogo_bp.route('/parentescos/<int:id>/historial')
@login_required
@admin_required
def historial_parentesco(id):
    """Get history for a specific parentesco"""
    try:
        # Get parentesco info
        parentesco = Parentesco.query.get_or_404(id)
        parentesco_nombre = parentesco.parentesco
        
        # Get all history records for this parentesco
        historico = HistoricoParentesco.query.filter_by(id=id).order_by(
            HistoricoParentesco.fecha_hora_operacion.desc()
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
                previous = HistoricoParentesco.query.filter(
                    HistoricoParentesco.id == id,
                    HistoricoParentesco.fecha_hora_operacion < record.fecha_hora_operacion
                ).order_by(HistoricoParentesco.fecha_hora_operacion.desc()).first()
                
                if previous:
                    # Compare parentesco field
                    if previous.parentesco != record.parentesco:
                        cambios.append({
                            'campo': 'Parentesco',
                            'valor_anterior': previous.parentesco or 'N/A',
                            'valor_nuevo': record.parentesco or 'N/A'
                        })
            
            historial_data.append({
                'id_historico': record.id_historico,
                'tipo_operacion': record.tipo_operacion,
                'fecha_hora': record.fecha_hora_operacion.strftime('%d/%m/%Y %H:%M:%S'),
                'usuario_nombre': usuario_nombre,
                'usuario_iniciales': usuario_iniciales,
                'parentesco': record.parentesco,
                'cambios': cambios
            })
        
        return jsonify({
            'success': True,
            'parentesco_nombre': parentesco_nombre,
            'historial': historial_data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al cargar historial: {str(e)}'
        }), 500

# ==================== HELPER FUNCTION ====================

def registrar_historico_parentesco(parentesco, tipo_operacion):
    """Register parentesco operation in history table"""
    historico = HistoricoParentesco(
        tipo_operacion=tipo_operacion,
        fecha_hora_operacion=datetime.now(),
        usuario_operacion_id=current_user.id,
        id=parentesco.id,
        parentesco=parentesco.parentesco,
        usuario_registro_id=parentesco.usuario_registro_id,
        fecha_hora_registro=parentesco.fecha_hora_registro,
        usuario_actualizo_id=parentesco.usuario_actualizo_id,
        fecha_hora_actualizo=parentesco.fecha_hora_actualizo
    )
    
    db.session.add(historico)
# ==================== API ENDPOINTS ====================

@catalogo_bp.route('/api/usuarios')
@login_required
@admin_required
def api_usuarios():
    """API endpoint for users list"""
    usuarios = Usuario.query.all()
    return jsonify([{
        'id': u.id,
        'username': u.username,
        'nombre': u.nombre,
        'apellido': u.apellido,
        'email': u.email,
        'rol': u.rol,
        'activo': u.activo
    } for u in usuarios])