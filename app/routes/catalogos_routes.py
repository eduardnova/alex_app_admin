"""
Admin Routes - User management, access logs, system configuration
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from functools import wraps
from app import db, cache
from app.models import (
    Usuario, RegistroAcceso, VehiculoMarcaModelo, EstadoAlquiler,
    MetodoPago, TipoCuenta, Banco, Parentesco
)
from datetime import datetime
import os
from werkzeug.utils import secure_filename

catalogo_bp = Blueprint('catalogo', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
UPLOAD_FOLDER = 'app/static/uploads/logos'

def allowed_file(filename):
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
    marcas = VehiculoMarcaModelo.query.all()
    return render_template('catalogos/vehiculo_marca_modelo.html', marcas=marcas)

@catalogo_bp.route('/marcas_modelos/crear', methods=['GET', 'POST'])
@login_required
@admin_required
def crear_marca_modelo():
    """Create new vehicle brand/model"""
    if request.method == 'POST':
        marca = request.form.get('marca')
        modelo = request.form.get('modelo')
        tipo = request.form.get('tipo')
        descripcion = request.form.get('descripcion')
        
        logo_path = None
        if 'logo' in request.files:
            file = request.files['logo']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                file.save(filepath)
                logo_path = f'uploads/logos/{filename}'
        
        nueva_marca = VehiculoMarcaModelo(
            marca=marca,
            modelo=modelo,
            tipo=tipo,
            descripcion=descripcion,
            logo_path=logo_path,
            usuario_registro_id=current_user.id,
            usuario_actualizo_id=current_user.id
        )
        
        try:
            db.session.add(nueva_marca)
            db.session.commit()
            flash('Marca/Modelo creado exitosamente.', 'success')
            return redirect(url_for('catalogo.marcas_modelos'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear marca/modelo: {str(e)}', 'danger')
    
    return render_template('catalogos/crear_marca_modelo.html')

@catalogo_bp.route('/marcas_modelos/<int:id>')
@login_required
@admin_required
def ver_marca_modelo(id):
    """View vehicle brand/model details"""
    marca = VehiculoMarcaModelo.query.get_or_404(id)
    return render_template('catalogos/ver_marca_modelo.html', marca=marca)

@catalogo_bp.route('/marcas_modelos/<int:id>/editar', methods=['GET', 'POST'])
@login_required
@admin_required
def editar_marca_modelo(id):
    """Edit vehicle brand/model"""
    marca = VehiculoMarcaModelo.query.get_or_404(id)
    
    if request.method == 'POST':
        marca.marca = request.form.get('marca')
        marca.modelo = request.form.get('modelo')
        marca.tipo = request.form.get('tipo')
        marca.descripcion = request.form.get('descripcion')
        marca.usuario_actualizo_id = current_user.id
        
        if 'logo' in request.files:
            file = request.files['logo']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                file.save(filepath)
                marca.logo_path = f'uploads/logos/{filename}'
        
        try:
            db.session.commit()
            flash('Marca/Modelo actualizado exitosamente.', 'success')
            return redirect(url_for('catalogo.marcas_modelos'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar marca/modelo: {str(e)}', 'danger')
    
    return render_template('catalogos/editar_marca_modelo.html', marca=marca)

@catalogo_bp.route('/marcas_modelos/<int:id>/eliminar', methods=['POST'])
@login_required
@admin_required
def eliminar_marca_modelo(id):
    """Delete vehicle brand/model"""
    marca = VehiculoMarcaModelo.query.get_or_404(id)
    
    try:
        db.session.delete(marca)
        db.session.commit()
        flash('Marca/Modelo eliminado exitosamente.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar marca/modelo: {str(e)}', 'danger')
    
    return redirect(url_for('catalogo.marcas_modelos'))

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

# ==================== BANCOS ====================

@catalogo_bp.route('/catalogos/bancos')
@login_required
@admin_required
def bancos():
    """List banks"""
    bancos = Banco.query.all()
    return render_template('catalogos/bancos.html', bancos=bancos)

@catalogo_bp.route('/catalogos/bancos/crear', methods=['GET', 'POST'])
@login_required
@admin_required
def crear_banco():
    """Create new bank"""
    if request.method == 'POST':
        banco = request.form.get('banco')
        cuenta = request.form.get('cuenta')
        tipo_cuenta_id = request.form.get('tipo_cuenta_id')
        cedula = request.form.get('cedula')
        administrador = request.form.get('administrador')
        descripcion = request.form.get('descripcion')
        
        logo_path = None
        if 'logo' in request.files:
            file = request.files['logo']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                file.save(filepath)
                logo_path = f'uploads/logos/{filename}'
        
        nuevo_banco = Banco(
            banco=banco,
            cuenta=cuenta,
            tipo_cuenta_id=tipo_cuenta_id,
            cedula=cedula,
            administrador=administrador,
            descripcion=descripcion,
            logo_path=logo_path,
            usuario_registro_id=current_user.id,
            usuario_actualizo_id=current_user.id
        )
        
        try:
            db.session.add(nuevo_banco)
            db.session.commit()
            flash('Banco creado exitosamente.', 'success')
            return redirect(url_for('catalogo.bancos'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear banco: {str(e)}', 'danger')
    
    tipos_cuenta = TipoCuenta.query.all()
    return render_template('catalogos/crear_banco.html', tipos_cuenta=tipos_cuenta)

@catalogo_bp.route('/catalogos/bancos/<int:id>')
@login_required
@admin_required
def ver_banco(id):
    """View bank details"""
    banco = Banco.query.get_or_404(id)
    return render_template('catalogos/ver_banco.html', banco=banco)

@catalogo_bp.route('/catalogos/bancos/<int:id>/editar', methods=['GET', 'POST'])
@login_required
@admin_required
def editar_banco(id):
    """Edit bank"""
    banco = Banco.query.get_or_404(id)
    
    if request.method == 'POST':
        banco.banco = request.form.get('banco')
        banco.cuenta = request.form.get('cuenta')
        banco.tipo_cuenta_id = request.form.get('tipo_cuenta_id')
        banco.cedula = request.form.get('cedula')
        banco.administrador = request.form.get('administrador')
        banco.descripcion = request.form.get('descripcion')
        banco.usuario_actualizo_id = current_user.id
        
        if 'logo' in request.files:
            file = request.files['logo']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                file.save(filepath)
                banco.logo_path = f'uploads/logos/{filename}'
        
        try:
            db.session.commit()
            flash('Banco actualizado exitosamente.', 'success')
            return redirect(url_for('catalogo.bancos'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar banco: {str(e)}', 'danger')
    
    tipos_cuenta = TipoCuenta.query.all()
    return render_template('catalogos/editar_banco.html', banco=banco, tipos_cuenta=tipos_cuenta)

@catalogo_bp.route('/catalogos/bancos/<int:id>/eliminar', methods=['POST'])
@login_required
@admin_required
def eliminar_banco(id):
    """Delete bank"""
    banco = Banco.query.get_or_404(id)
    
    try:
        db.session.delete(banco)
        db.session.commit()
        flash('Banco eliminado exitosamente.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar banco: {str(e)}', 'danger')
    
    return redirect(url_for('catalogo.bancos'))

# ==================== PARENTESCOS ====================

@catalogo_bp.route('/catalogos/parentescos')
@login_required
@admin_required
def parentescos():
    """List relationships"""
    parentescos = Parentesco.query.all()
    return render_template('catalogos/parentescos.html', parentescos=parentescos)

@catalogo_bp.route('/catalogos/parentescos/crear', methods=['GET', 'POST'])
@login_required
@admin_required
def crear_parentesco():
    """Create new relationship"""
    if request.method == 'POST':
        parentesco = request.form.get('parentesco')
        
        nuevo_parentesco = Parentesco(
            parentesco=parentesco,
            usuario_registro_id=current_user.id,
            usuario_actualizo_id=current_user.id
        )
        
        try:
            db.session.add(nuevo_parentesco)
            db.session.commit()
            flash('Parentesco creado exitosamente.', 'success')
            return redirect(url_for('catalogo.parentescos'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear parentesco: {str(e)}', 'danger')
    
    return render_template('catalogos/crear_parentesco.html')

@catalogo_bp.route('/catalogos/parentescos/<int:id>')
@login_required
@admin_required
def ver_parentesco(id):
    """View relationship details"""
    parentesco = Parentesco.query.get_or_404(id)
    return render_template('catalogos/ver_parentesco.html', parentesco=parentesco)

@catalogo_bp.route('/catalogos/parentescos/<int:id>/editar', methods=['GET', 'POST'])
@login_required
@admin_required
def editar_parentesco(id):
    """Edit relationship"""
    parentesco = Parentesco.query.get_or_404(id)
    
    if request.method == 'POST':
        parentesco.parentesco = request.form.get('parentesco')
        parentesco.usuario_actualizo_id = current_user.id
        
        try:
            db.session.commit()
            flash('Parentesco actualizado exitosamente.', 'success')
            return redirect(url_for('catalogo.parentescos'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar parentesco: {str(e)}', 'danger')
    
    return render_template('catalogos/editar_parentesco.html', parentesco=parentesco)

@catalogo_bp.route('/catalogos/parentescos/<int:id>/eliminar', methods=['POST'])
@login_required
@admin_required
def eliminar_parentesco(id):
    """Delete relationship"""
    parentesco = Parentesco.query.get_or_404(id)
    
    try:
        db.session.delete(parentesco)
        db.session.commit()
        flash('Parentesco eliminado exitosamente.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar parentesco: {str(e)}', 'danger')
    
    return redirect(url_for('catalogo.parentescos'))

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