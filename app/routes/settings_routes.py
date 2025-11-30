"""
=== app/routes/settings_routes.py ===
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db

settings_bp = Blueprint('settings', __name__)

@settings_bp.route('/')
@login_required
def settings():
    """User settings"""
    return render_template('settings/setting.html', user=current_user)

@settings_bp.route('/perfil', methods=['GET', 'POST'])
@login_required
def perfil():
    """Update user profile"""
    if request.method == 'POST':
        current_user.nombre = request.form.get('nombre')
        current_user.apellido = request.form.get('apellido')
        current_user.email = request.form.get('email')
        current_user.telefono = request.form.get('telefono')
        
        db.session.commit()
        flash('Perfil actualizado exitosamente', 'success')
        return redirect(url_for('settings.settings'))
    
    return render_template('settings/perfil.html', user=current_user)

@settings_bp.route('/cambiar-password', methods=['GET', 'POST'])
@login_required
def cambiar_password():
    """Change password"""
    if request.method == 'POST':
        password_actual = request.form.get('password_actual')
        password_nuevo = request.form.get('password_nuevo')
        password_confirmar = request.form.get('password_confirmar')
        
        if not current_user.check_password(password_actual):
            flash('La contraseña actual es incorrecta', 'danger')
            return render_template('settings/cambiar_password.html')
        
        if password_nuevo != password_confirmar:
            flash('Las contraseñas no coinciden', 'danger')
            return render_template('settings/cambiar_password.html')
        
        current_user.set_password(password_nuevo)
        db.session.commit()
        
        flash('Contraseña cambiada exitosamente', 'success')
        return redirect(url_for('settings.settings'))
    
    return render_template('settings/cambiar_password.html')

