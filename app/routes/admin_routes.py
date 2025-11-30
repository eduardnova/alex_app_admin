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

admin_bp = Blueprint('admin', __name__)


def admin_required(f):
    """Decorator to require admin role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.rol != 'admin':
            flash('Acceso denegado. Se requieren permisos de administrador.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function


@admin_bp.route('/')
@login_required
@admin_required
def admin():
    """Admin dashboard"""
    usuarios_count = Usuario.query.count()
    vehiculos_count = VehiculoMarcaModelo.query.count()
    accesos_recientes = RegistroAcceso.query.order_by(
        RegistroAcceso.fecha_hora.desc()
    ).limit(10).all()
    
    return render_template('admin/admin.html',
                         usuarios_count=usuarios_count,
                         vehiculos_count=vehiculos_count,
                         accesos_recientes=accesos_recientes)


@admin_bp.route('/usuarios')
@login_required
@admin_required
@cache.cached(timeout=60, query_string=True)
def usuarios():
    """List all users"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    usuarios = Usuario.query.paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('admin/usuarios.html', usuarios=usuarios)


@admin_bp.route('/usuarios/crear', methods=['GET', 'POST'])
@login_required
@admin_required
def crear_usuario():
    """Create new user"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')
        nombre = request.form.get('nombre')
        apellido = request.form.get('apellido')
        rol = request.form.get('rol', 'user')
        telefono = request.form.get('telefono')
        
        # Validate
        if Usuario.query.filter_by(username=username).first():
            flash('El nombre de usuario ya existe', 'danger')
            return render_template('admin/crear_usuario.html')
        
        if Usuario.query.filter_by(email=email).first():
            flash('El email ya está registrado', 'danger')
            return render_template('admin/crear_usuario.html')
        
        # Create user
        user = Usuario(
            username=username,
            nombre=nombre,
            apellido=apellido,
            email=email,
            telefono=telefono,
            rol=rol,
            activo=True
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        # Clear cache
        cache.clear()
        
        flash(f'Usuario {username} creado exitosamente', 'success')
        return redirect(url_for('admin.usuarios'))
    
    return render_template('admin/crear_usuario.html')


@admin_bp.route('/usuarios/<int:user_id>/editar', methods=['GET', 'POST'])
@login_required
@admin_required
def editar_usuario(user_id):
    """Edit user"""
    user = Usuario.query.get_or_404(user_id)
    
    if request.method == 'POST':
        user.nombre = request.form.get('nombre')
        user.apellido = request.form.get('apellido')
        user.email = request.form.get('email')
        user.telefono = request.form.get('telefono')
        user.rol = request.form.get('rol')
        user.activo = request.form.get('activo') == 'on'
        
        # Update password if provided
        new_password = request.form.get('new_password')
        if new_password:
            user.set_password(new_password)
        
        db.session.commit()
        cache.clear()
        
        flash(f'Usuario {user.username} actualizado exitosamente', 'success')
        return redirect(url_for('admin.usuarios'))
    
    return render_template('admin/editar_usuario.html', user=user)


@admin_bp.route('/usuarios/<int:user_id>/eliminar', methods=['POST'])
@login_required
@admin_required
def eliminar_usuario(user_id):
    """Delete user"""
    user = Usuario.query.get_or_404(user_id)
    
    if user.id == current_user.id:
        flash('No puedes eliminar tu propio usuario', 'danger')
        return redirect(url_for('admin.usuarios'))
    
    db.session.delete(user)
    db.session.commit()
    cache.clear()
    
    flash(f'Usuario {user.username} eliminado exitosamente', 'success')
    return redirect(url_for('admin.usuarios'))


@admin_bp.route('/registro-acceso')
@login_required
@admin_required
def registro_acceso():
    """View access logs"""
    page = request.args.get('page', 1, type=int)
    per_page = 50
    
    registros = RegistroAcceso.query.order_by(
        RegistroAcceso.fecha_hora.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('admin/registro_acceso.html', registros=registros)


# ==================== CATÁLOGOS ====================

@admin_bp.route('/catalogos/marcas-modelos')
@login_required
@admin_required
def marcas_modelos():
    """List vehicle brands and models"""
    marcas = VehiculoMarcaModelo.query.all()
    return render_template('catalogos/vehiculo_marca_modelo.html', marcas=marcas)


@admin_bp.route('/catalogos/estados-alquiler')
@login_required
@admin_required
def estados_alquiler():
    """List rental states"""
    estados = EstadoAlquiler.query.all()
    return render_template('catalogos/estados_alquiler.html', estados=estados)


@admin_bp.route('/catalogos/metodos-pago')
@login_required
@admin_required
def metodos_pago():
    """List payment methods"""
    metodos = MetodoPago.query.all()
    return render_template('catalogos/metodos_pago.html', metodos=metodos)


@admin_bp.route('/catalogos/tipo-cuentas')
@login_required
@admin_required
def tipo_cuentas():
    """List account types"""
    tipos = TipoCuenta.query.all()
    return render_template('catalogos/tipo_cuentas.html', tipos=tipos)


@admin_bp.route('/catalogos/bancos')
@login_required
@admin_required
def bancos():
    """List banks"""
    bancos = Banco.query.all()
    return render_template('catalogos/bancos.html', bancos=bancos)


@admin_bp.route('/catalogos/parentescos')
@login_required
@admin_required
def parentescos():
    """List relationships"""
    parentescos = Parentesco.query.all()
    return render_template('catalogos/parentescos.html', parentescos=parentescos)


# ==================== API ENDPOINTS ====================

@admin_bp.route('/api/usuarios')
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