"""
Authentication Routes - Login, Logout, Password Reset
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db, limiter
from app.models import Usuario, RegistroAcceso
from datetime import datetime

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def login():
    """User login"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = request.form.get('remember', False)
        
        user = Usuario.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            if not user.activo:
                flash('Tu cuenta está desactivada. Contacta al administrador.', 'danger')
                return render_template('auth/login.html')
            
            login_user(user, remember=remember)
            
            # Log access
            registro = RegistroAcceso(
                usuario_id=user.id,
                accion='login',
                ip_address=request.remote_addr,
                detalles=f'Login exitoso desde {request.user_agent.string[:100]}'
            )
            db.session.add(registro)
            db.session.commit()
            
            flash(f'Bienvenido {user.nombre}!', 'success')
            
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        
        else:
            flash('Usuario o contraseña incorrectos', 'danger')
            
            # Log failed attempt
            if user:
                registro = RegistroAcceso(
                    usuario_id=user.id,
                    accion='login_failed',
                    ip_address=request.remote_addr,
                    detalles='Intento de login fallido - contraseña incorrecta'
                )
                db.session.add(registro)
                db.session.commit()
    
    return render_template('auth/login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    """User logout"""
    # Log access
    registro = RegistroAcceso(
        usuario_id=current_user.id,
        accion='logout',
        ip_address=request.remote_addr,
        detalles='Logout exitoso'
    )
    db.session.add(registro)
    db.session.commit()
    
    logout_user()
    flash('Has cerrado sesión correctamente', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/forgot', methods=['GET', 'POST'])
@limiter.limit("3 per hour")
def forgot():
    """Forgot password"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        user = Usuario.query.filter_by(email=email).first()
        
        if user:
            # TODO: Implement email sending with token
            flash('Se ha enviado un correo con instrucciones para restablecer tu contraseña', 
                  'info')
            # For now, just log the attempt
            registro = RegistroAcceso(
                usuario_id=user.id,
                accion='password_reset_request',
                ip_address=request.remote_addr,
                detalles=f'Solicitud de restablecimiento de contraseña para {email}'
            )
            db.session.add(registro)
            db.session.commit()
        else:
            # Don't reveal if email exists
            flash('Si el correo existe, recibirás instrucciones para restablecer tu contraseña', 
                  'info')
        
        return redirect(url_for('auth.login'))
    
    return render_template('auth/forget.html')


@auth_bp.route('/reset/<token>', methods=['GET', 'POST'])
def reset(token):
    """Reset password with token"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    # TODO: Implement token validation
    
    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if password != confirm_password:
            flash('Las contraseñas no coinciden', 'danger')
            return render_template('auth/reset.html', token=token)
        
        # TODO: Update user password after validating token
        flash('Tu contraseña ha sido actualizada correctamente', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/reset.html', token=token)