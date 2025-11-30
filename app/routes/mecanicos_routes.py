
"""
=== app/routes/mecanicos_routes.py ===
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db, cache
from app.models import (
    Mecanico, TipoTrabajo, TrabajoVehiculo, Pieza, 
    PiezaUsada, Vehiculo
)

mecanicos_bp = Blueprint('mecanicos', __name__)

@mecanicos_bp.route('/mecanicos')
@login_required
@cache.cached(timeout=60, query_string=True)
def mecanicos():
    """List all mechanics"""
    mecanicos = Mecanico.query.filter_by(activo=True).all()
    return render_template('mecanicos/mecanicos.html', mecanicos=mecanicos)


@mecanicos_bp.route('/mecanicos/crear', methods=['GET', 'POST'])
@login_required
def crear_mecanico():
    """Create new mechanic"""
    if request.method == 'POST':
        mecanico = Mecanico(
            nombre=request.form.get('nombre'),
            direccion=request.form.get('direccion'),
            telefono=request.form.get('telefono'),
            email=request.form.get('email'),
            especialidad=request.form.get('especialidad'),
            activo=True,
            usuario_registro_id=current_user.id,
            usuario_actualizo_id=current_user.id
        )
        
        db.session.add(mecanico)
        db.session.commit()
        cache.clear()
        
        flash('Mecánico creado exitosamente', 'success')
        return redirect(url_for('mecanicos.mecanicos'))
    
    return render_template('mecanicos/crear_mecanico.html')


@mecanicos_bp.route('/tipos-trabajos')
@login_required
def tipos_trabajos():
    """List work types"""
    tipos = TipoTrabajo.query.all()
    return render_template('mecanicos/tipos_trabajos.html', tipos=tipos)


@mecanicos_bp.route('/trabajos-vehiculos')
@login_required
@cache.cached(timeout=60, query_string=True)
def trabajos_vehiculos():
    """List vehicle works"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    trabajos = TrabajoVehiculo.query.order_by(
        TrabajoVehiculo.fecha_inicio.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('mecanicos/trabajos_vehiculos.html', trabajos=trabajos)


@mecanicos_bp.route('/trabajos-vehiculos/crear', methods=['GET', 'POST'])
@login_required
def crear_trabajo():
    """Create new vehicle work"""
    if request.method == 'POST':
        trabajo = TrabajoVehiculo(
            vehiculo_id=request.form.get('vehiculo_id'),
            mecanico_id=request.form.get('mecanico_id'),
            tipo_trabajo_id=request.form.get('tipo_trabajo_id'),
            fecha_inicio=request.form.get('fecha_inicio'),
            fecha_fin=request.form.get('fecha_fin'),
            descripcion=request.form.get('descripcion'),
            costo=request.form.get('costo', 0),
            estado=request.form.get('estado', 'pendiente'),
            notas=request.form.get('notas'),
            usuario_registro_id=current_user.id,
            usuario_actualizo_id=current_user.id
        )
        
        db.session.add(trabajo)
        db.session.commit()
        cache.clear()
        
        flash('Trabajo creado exitosamente', 'success')
        return redirect(url_for('mecanicos.trabajos_vehiculos'))
    
    vehiculos = Vehiculo.query.all()
    mecanicos = Mecanico.query.filter_by(activo=True).all()
    tipos = TipoTrabajo.query.all()
    
    return render_template('mecanicos/crear_trabajo.html',
                         vehiculos=vehiculos,
                         mecanicos=mecanicos,
                         tipos=tipos)


@mecanicos_bp.route('/piezas')
@login_required
@cache.cached(timeout=60, query_string=True)
def piezas():
    """List parts"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    piezas = Pieza.query.paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('mecanicos/piezas.html', piezas=piezas)


@mecanicos_bp.route('/piezas/crear', methods=['GET', 'POST'])
@login_required
def crear_pieza():
    """Create new part"""
    if request.method == 'POST':
        pieza = Pieza(
            nombre=request.form.get('nombre'),
            marca=request.form.get('marca'),
            modelo=request.form.get('modelo'),
            estado=request.form.get('estado'),
            costo=request.form.get('costo'),
            descripcion=request.form.get('descripcion'),
            usuario_registro_id=current_user.id,
            usuario_actualizo_id=current_user.id
        )
        
        db.session.add(pieza)
        db.session.commit()
        cache.clear()
        
        flash('Pieza creada exitosamente', 'success')
        return redirect(url_for('mecanicos.piezas'))
    
    return render_template('mecanicos/crear_pieza.html')