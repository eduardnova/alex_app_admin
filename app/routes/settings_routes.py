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

@settings_bp.route('/perfil', methods=['POST'])
@login_required
def perfil():
    """Update user profile via AJAX"""
    try:
        data = request.get_json()
        if not data:
            return {"status": "error", "message": "No se recibieron datos"}, 400
            
        current_user.nombre = data.get('nombre')
        current_user.apellido = data.get('apellido')
        current_user.email = data.get('email')
        current_user.telefono = data.get('telefono')
        
        db.session.commit()
        return {"status": "success", "message": "Perfil actualizado exitosamente"}
    except Exception as e:
        db.session.rollback()
        return {"status": "error", "message": f"Error al actualizar: {str(e)}"}, 500

@settings_bp.route('/cambiar-password', methods=['POST'])
@login_required
def cambiar_password():
    """Change password via AJAX"""
    try:
        data = request.get_json()
        if not data:
            return {"status": "error", "message": "No se recibieron datos"}, 400

        password_actual = data.get('password_actual')
        password_nuevo = data.get('password_nuevo')
        password_confirmar = data.get('password_confirmar')
        
        if not current_user.check_password(password_actual):
            return {"status": "error", "message": "La contraseña actual es incorrecta"}, 400
        
        if password_nuevo != password_confirmar:
            return {"status": "error", "message": "Las contraseñas nuevas no coinciden"}, 400
        
        if len(password_nuevo) < 6:
            return {"status": "error", "message": "La nueva contraseña debe tener al menos 6 caracteres"}, 400
            
        current_user.set_password(password_nuevo)
        db.session.commit()
        
        return {"status": "success", "message": "Contraseña cambiada exitosamente"}
    except Exception as e:
        db.session.rollback()
        return {"status": "error", "message": f"Error al cambiar contraseña: {str(e)}"}, 500

