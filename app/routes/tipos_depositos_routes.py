"""
Tipos Depósitos Routes - Configuración de depósitos por tipo de vehículo
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from .auth_routes import admin_required
from app import db
from app.models import TipoDeposito, Usuario
from datetime import datetime
from decimal import Decimal

tipo_deposito_bp = Blueprint('tipo_deposito', __name__, url_prefix='/tipos-depositos')




# ==================== TIPOS DEPÓSITOS ====================

@tipo_deposito_bp.route('/')
@login_required
@admin_required
def listar_tipos_depositos():
    tipos = TipoDeposito.query.order_by(TipoDeposito.tipo_vehiculo).all()
    return render_template('catalogos/tipos_depositos.html', tipos_depositos=tipos)


@tipo_deposito_bp.route('/crear', methods=['POST'])
@login_required
@admin_required
def crear_tipo_deposito():
    try:
        tipo_vehiculo = request.form.get('tipo_vehiculo', '').strip()
        deposito_total = request.form.get('deposito_total')
        cantidad_depositos = request.form.get('cantidad_depositos')
        
        if not tipo_vehiculo or not deposito_total or not cantidad_depositos:
            flash('Todos los campos son requeridos.', 'warning')
            return redirect(url_for('tipo_deposito.listar_tipos_depositos'))
        
        # Verificar duplicados
        if TipoDeposito.query.filter_by(tipo_vehiculo=tipo_vehiculo).first():
            flash('Ya existe una configuración para este tipo de vehículo.', 'warning')
            return redirect(url_for('tipo_deposito.listar_tipos_depositos'))
        
        deposito_total = Decimal(deposito_total)
        cantidad_depositos = int(cantidad_depositos)
        
        if cantidad_depositos <= 0:
            flash('La cantidad de depósitos debe ser mayor a 0.', 'warning')
            return redirect(url_for('tipo_deposito.listar_tipos_depositos'))
        
        monto_por_deposito = deposito_total / cantidad_depositos
        
        nuevo_tipo = TipoDeposito(
            tipo_vehiculo=tipo_vehiculo,
            deposito_total=deposito_total,
            cantidad_depositos=cantidad_depositos,
            monto_por_deposito=monto_por_deposito,
            activo=True,
            usuario_registro_id=current_user.id,
            usuario_actualizo_id=current_user.id
        )
        
        db.session.add(nuevo_tipo)
        db.session.commit()
        
        flash(f'Tipo de depósito {tipo_vehiculo} creado exitosamente.', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error al crear tipo de depósito: {str(e)}', 'danger')
    
    return redirect(url_for('tipo_deposito.listar_tipos_depositos'))


@tipo_deposito_bp.route('/<int:id>')
@login_required
@admin_required
def ver_tipo_deposito(id):
    tipo = TipoDeposito.query.get_or_404(id)
    
    return jsonify({
        'success': True,
        'tipo_deposito': {
            'id': tipo.id,
            'tipo_vehiculo': tipo.tipo_vehiculo,
            'deposito_total': float(tipo.deposito_total),
            'cantidad_depositos': tipo.cantidad_depositos,
            'monto_por_deposito': float(tipo.monto_por_deposito),
            'activo': tipo.activo
        }
    })


@tipo_deposito_bp.route('/<int:id>/editar', methods=['POST'])
@login_required
@admin_required
def editar_tipo_deposito(id):
    tipo = TipoDeposito.query.get_or_404(id)
    
    try:
        tipo_vehiculo = request.form.get('tipo_vehiculo', '').strip()
        deposito_total = request.form.get('deposito_total')
        cantidad_depositos = request.form.get('cantidad_depositos')
        activo = request.form.get('activo') == 'true'
        
        if not tipo_vehiculo or not deposito_total or not cantidad_depositos:
            flash('Todos los campos son requeridos.', 'warning')
            return redirect(url_for('tipo_deposito.listar_tipos_depositos'))
        
        # Verificar duplicados si cambia el tipo
        if tipo_vehiculo != tipo.tipo_vehiculo:
            if TipoDeposito.query.filter_by(tipo_vehiculo=tipo_vehiculo).first():
                flash('Ya existe una configuración para este tipo de vehículo.', 'warning')
                return redirect(url_for('tipo_deposito.listar_tipos_depositos'))
        
        deposito_total = Decimal(deposito_total)
        cantidad_depositos = int(cantidad_depositos)
        
        if cantidad_depositos <= 0:
            flash('La cantidad de depósitos debe ser mayor a 0.', 'warning')
            return redirect(url_for('tipo_deposito.listar_tipos_depositos'))
        
        monto_por_deposito = deposito_total / cantidad_depositos
        
        tipo.tipo_vehiculo = tipo_vehiculo
        tipo.deposito_total = deposito_total
        tipo.cantidad_depositos = cantidad_depositos
        tipo.monto_por_deposito = monto_por_deposito
        tipo.activo = activo
        tipo.usuario_actualizo_id = current_user.id
        tipo.fecha_hora_actualizo = datetime.now()
        
        db.session.commit()
        
        flash('Tipo de depósito actualizado exitosamente.', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error al actualizar tipo de depósito: {str(e)}', 'danger')
    
    return redirect(url_for('tipo_deposito.listar_tipos_depositos'))


@tipo_deposito_bp.route('/<int:id>/eliminar', methods=['POST'])
@login_required
@admin_required
def eliminar_tipo_deposito(id):
    tipo = TipoDeposito.query.get_or_404(id)
    
    try:
        nombre = tipo.tipo_vehiculo
        db.session.delete(tipo)
        db.session.commit()
        
        flash(f'Tipo de depósito {nombre} eliminado exitosamente.', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar tipo de depósito: {str(e)}', 'danger')
    
    return redirect(url_for('tipo_deposito.listar_tipos_depositos'))


@tipo_deposito_bp.route('/<int:id>/toggle', methods=['POST'])
@login_required
@admin_required
def toggle_activo(id):
    tipo = TipoDeposito.query.get_or_404(id)
    
    try:
        tipo.activo = not tipo.activo
        tipo.usuario_actualizo_id = current_user.id
        tipo.fecha_hora_actualizo = datetime.now()
        
        db.session.commit()
        
        estado = 'activado' if tipo.activo else 'desactivado'
        return jsonify({
            'success': True,
            'message': f'Tipo de depósito {estado} exitosamente.',
            'activo': tipo.activo
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        })


# ==================== API ENDPOINTS ====================

@tipo_deposito_bp.route('/api/por-tipo/<tipo>')
@login_required
@admin_required
def api_tipo_deposito_por_tipo(tipo):
    tipo_deposito = TipoDeposito.query.filter_by(tipo_vehiculo=tipo, activo=True).first()
    
    if tipo_deposito:
        return jsonify({
            'success': True,
            'tipo_deposito': {
                'id': tipo_deposito.id,
                'tipo_vehiculo': tipo_deposito.tipo_vehiculo,
                'deposito_total': float(tipo_deposito.deposito_total),
                'cantidad_depositos': tipo_deposito.cantidad_depositos,
                'monto_por_deposito': float(tipo_deposito.monto_por_deposito)
            }
        })
    
    return jsonify({
        'success': False,
        'message': 'No se encontró configuración para este tipo de vehículo'
    })


@tipo_deposito_bp.route('/api/todos')
@login_required
@admin_required
def api_todos_tipos_depositos():
    tipos = TipoDeposito.query.filter_by(activo=True).all()
    
    result = []
    for tipo in tipos:
        result.append({
            'id': tipo.id,
            'tipo_vehiculo': tipo.tipo_vehiculo,
            'deposito_total': float(tipo.deposito_total),
            'cantidad_depositos': tipo.cantidad_depositos,
            'monto_por_deposito': float(tipo.monto_por_deposito)
        })
    
    return jsonify(result)