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
    
# Agregar al final de admin_routes.py

@admin_bp.route('/api/historial-usuario/<int:usuario_id>')
@login_required
@admin_required
def api_historial_usuario(usuario_id):
    """API endpoint for user access history"""
    registros = RegistroAcceso.query.filter_by(usuario_id=usuario_id)\
        .order_by(RegistroAcceso.fecha_hora.desc())\
        .limit(100).all()
    
    return jsonify([{
        'id': r.id,
        'accion': r.accion,
        'fecha_hora': r.fecha_hora.isoformat(),
        'ip_address': r.ip_address,
        'detalles': r.detalles
    } for r in registros])


@admin_bp.route('/api/analisis-semanal')
@login_required
@admin_required
def api_analisis_semanal():
    """API endpoint for weekly analytics"""
    from datetime import datetime, timedelta
    
    # Obtener fecha de inicio de la semana (lunes)
    hoy = datetime.now()
    inicio_semana = hoy - timedelta(days=hoy.weekday())
    inicio_semana = inicio_semana.replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Contar accesos por día
    dias_semana = [0] * 7
    dia_nombres = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
    
    for i in range(7):
        dia_inicio = inicio_semana + timedelta(days=i)
        dia_fin = dia_inicio + timedelta(days=1)
        
        count = RegistroAcceso.query.filter(
            RegistroAcceso.fecha_hora >= dia_inicio,
            RegistroAcceso.fecha_hora < dia_fin
        ).count()
        
        dias_semana[i] = count
    
    # Calcular estadísticas
    total = sum(dias_semana)
    promedio = total / 7 if total > 0 else 0
    
    # Encontrar día más activo
    max_accesos = max(dias_semana)
    dia_mas_activo = dia_nombres[dias_semana.index(max_accesos)] if max_accesos > 0 else 'N/A'
    
    return jsonify({
        'dias': dias_semana,
        'total': total,
        'promedio': promedio,
        'diaMasActivo': dia_mas_activo
    })


@admin_bp.route('/api/estadisticas-accesos')
@login_required
@admin_required
def api_estadisticas_accesos():
    """API endpoint for access statistics"""
    from datetime import datetime, timedelta
    
    hoy = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    ayer = hoy - timedelta(days=1)
    hace_24h = datetime.now() - timedelta(hours=24)
    
    # Accesos de hoy
    accesos_hoy = RegistroAcceso.query.filter(
        RegistroAcceso.fecha_hora >= hoy
    ).count()
    
    # Accesos de ayer
    accesos_ayer = RegistroAcceso.query.filter(
        RegistroAcceso.fecha_hora >= ayer,
        RegistroAcceso.fecha_hora < hoy
    ).count()
    
    # Calcular cambio porcentual
    if accesos_ayer > 0:
        cambio_hoy = ((accesos_hoy - accesos_ayer) / accesos_ayer) * 100
    else:
        cambio_hoy = 100 if accesos_hoy > 0 else 0
    
    # Accesos exitosos (login sin failed)
    exitosos = RegistroAcceso.query.filter(
        RegistroAcceso.fecha_hora >= hoy,
        RegistroAcceso.accion.like('%login%'),
        ~RegistroAcceso.accion.like('%failed%')
    ).count()
    
    # Accesos fallidos
    fallidos = RegistroAcceso.query.filter(
        RegistroAcceso.fecha_hora >= hoy,
        db.or_(
            RegistroAcceso.accion.like('%failed%'),
            RegistroAcceso.accion.like('%error%')
        )
    ).count()
    
    # Tasas
    total_intentos = exitosos + fallidos
    tasa_exito = (exitosos / total_intentos * 100) if total_intentos > 0 else 0
    tasa_fallo = (fallidos / total_intentos * 100) if total_intentos > 0 else 0
    
    # Usuarios activos en últimas 24h
    usuarios_activos = db.session.query(RegistroAcceso.usuario_id)\
        .filter(RegistroAcceso.fecha_hora >= hace_24h)\
        .distinct().count()
    
    return jsonify({
        'hoy': accesos_hoy,
        'exitosos': exitosos,
        'fallidos': fallidos,
        'usuarios_activos': usuarios_activos,
        'cambio_hoy': round(cambio_hoy, 1),
        'tasa_exito': round(tasa_exito, 1),
        'tasa_fallo': round(tasa_fallo, 1)
    })


@admin_bp.route('/api/exportar-accesos')
@login_required
@admin_required
def api_exportar_accesos():
    """Export access logs to CSV"""
    import csv
    from io import StringIO
    from flask import make_response
    
    registros = RegistroAcceso.query.order_by(
        RegistroAcceso.fecha_hora.desc()
    ).all()
    
    # Crear CSV
    si = StringIO()
    writer = csv.writer(si)
    
    # Headers
    writer.writerow(['ID', 'Usuario', 'Acción', 'Fecha', 'Hora', 'IP', 'Detalles'])
    
    # Datos
    for r in registros:
        writer.writerow([
            r.id,
            f"{r.usuario.nombre} {r.usuario.apellido}",
            r.accion,
            r.fecha_hora.strftime('%Y-%m-%d'),
            r.fecha_hora.strftime('%H:%M:%S'),
            r.ip_address or 'N/A',
            r.detalles or ''
        ])
    
    # Crear respuesta
    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = f"attachment; filename=registro_accesos_{datetime.now().strftime('%Y%m%d')}.csv"
    output.headers["Content-type"] = "text/csv"
    
    return output