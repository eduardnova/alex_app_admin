"""
Módulos Routes - Propietarios, Inquilinos, Vehículos, Alquileres, Pagos, Deudas
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db, cache
from app.models import (
    Propietario, Inquilino, Vehiculo, Alquiler, Pago, Deuda,
    VehiculoMarcaModelo, EstadoAlquiler, MetodoPago,
    ReferenciaPropietario, ReferenciaInquilino, GaranteInquilino
)
from datetime import datetime

modulos_bp = Blueprint('modulos', __name__)


# ==================== PROPIETARIOS ====================

@modulos_bp.route('/propietarios')
@login_required
@cache.cached(timeout=60, query_string=True)
def propietarios():
    """List all owners"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    propietarios = Propietario.query.paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('modulos/propietarios.html', propietarios=propietarios)


@modulos_bp.route('/propietarios/crear', methods=['GET', 'POST'])
@login_required
def crear_propietario():
    """Create new owner"""
    if request.method == 'POST':
        propietario = Propietario(
            nombre_apellido=request.form.get('nombre_apellido'),
            direccion=request.form.get('direccion'),
            telefono=request.form.get('telefono'),
            email=request.form.get('email'),
            usuario_registro_id=current_user.id,
            usuario_actualizo_id=current_user.id
        )
        
        # Handle encrypted fields
        cedula = request.form.get('cedula')
        if cedula:
            propietario.cedula = cedula
        
        licencia = request.form.get('licencia')
        if licencia:
            propietario.licencia = licencia
        
        db.session.add(propietario)
        db.session.commit()
        cache.clear()
        
        flash('Propietario creado exitosamente', 'success')
        return redirect(url_for('modulos.propietarios'))
    
    return render_template('modulos/crear_propietario.html')


@modulos_bp.route('/propietarios/<int:propietario_id>')
@login_required
def ver_propietario(propietario_id):
    """View owner details"""
    propietario = Propietario.query.get_or_404(propietario_id)
    vehiculos = propietario.vehiculos.all()
    referencias = propietario.referencias.all()
    
    return render_template('modulos/ver_propietario.html',
                         propietario=propietario,
                         vehiculos=vehiculos,
                         referencias=referencias)


# ==================== INQUILINOS ====================

@modulos_bp.route('/inquilinos')
@login_required
@cache.cached(timeout=60, query_string=True)
def inquilinos():
    """List all tenants"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    inquilinos = Inquilino.query.paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('modulos/inquilinos.html', inquilinos=inquilinos)


@modulos_bp.route('/inquilinos/crear', methods=['GET', 'POST'])
@login_required
def crear_inquilino():
    """Create new tenant"""
    if request.method == 'POST':
        inquilino = Inquilino(
            nombre_apellido=request.form.get('nombre_apellido'),
            direccion=request.form.get('direccion'),
            telefono=request.form.get('telefono'),
            email=request.form.get('email'),
            usuario_registro_id=current_user.id,
            usuario_actualizo_id=current_user.id
        )
        
        # Handle encrypted fields
        cedula = request.form.get('cedula')
        if cedula:
            inquilino.cedula = cedula
        
        licencia = request.form.get('licencia')
        if licencia:
            inquilino.licencia = licencia
        
        db.session.add(inquilino)
        db.session.commit()
        cache.clear()
        
        flash('Inquilino creado exitosamente', 'success')
        return redirect(url_for('modulos.inquilinos'))
    
    return render_template('modulos/crear_inquilino.html')


@modulos_bp.route('/inquilinos/<int:inquilino_id>')
@login_required
def ver_inquilino(inquilino_id):
    """View tenant details"""
    inquilino = Inquilino.query.get_or_404(inquilino_id)
    alquileres = inquilino.alquileres.all()
    referencias = inquilino.referencias.all()
    garantes = inquilino.garantes.all()
    deudas = inquilino.deudas.filter_by(estado='pendiente').all()
    
    return render_template('modulos/ver_inquilino.html',
                         inquilino=inquilino,
                         alquileres=alquileres,
                         referencias=referencias,
                         garantes=garantes,
                         deudas=deudas)


# ==================== VEHÍCULOS ====================

@modulos_bp.route('/vehiculos')
@login_required
@cache.cached(timeout=60, query_string=True)
def vehiculos():
    """List all vehicles"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    disponible = request.args.get('disponible')
    
    query = Vehiculo.query
    
    if disponible:
        query = query.filter_by(disponible=(disponible == 'true'))
    
    vehiculos = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('modulos/vehiculos.html', vehiculos=vehiculos)


@modulos_bp.route('/vehiculos/crear', methods=['GET', 'POST'])
@login_required
def crear_vehiculo():
    """Create new vehicle"""
    if request.method == 'POST':
        vehiculo = Vehiculo(
            propietario_id=request.form.get('propietario_id'),
            placa=request.form.get('placa'),
            marca_modelo_vehiculo_id=request.form.get('marca_modelo_id'),
            ano=request.form.get('ano'),
            color=request.form.get('color'),
            descripcion=request.form.get('descripcion'),
            precio_semanal=request.form.get('precio_semanal'),
            condiciones=request.form.get('condiciones'),
            disponible=True,
            usuario_registro_id=current_user.id,
            usuario_actualizo_id=current_user.id
        )
        
        db.session.add(vehiculo)
        db.session.commit()
        cache.clear()
        
        flash('Vehículo creado exitosamente', 'success')
        return redirect(url_for('modulos.vehiculos'))
    
    propietarios = Propietario.query.all()
    marcas_modelos = VehiculoMarcaModelo.query.all()
    
    return render_template('modulos/crear_vehiculo.html',
                         propietarios=propietarios,
                         marcas_modelos=marcas_modelos)


@modulos_bp.route('/vehiculos/<int:vehiculo_id>')
@login_required
def ver_vehiculo(vehiculo_id):
    """View vehicle details"""
    vehiculo = Vehiculo.query.get_or_404(vehiculo_id)
    alquileres = vehiculo.alquileres.order_by(Alquiler.fecha_alquiler_inicio.desc()).all()
    trabajos = vehiculo.trabajos.order_by(db.desc('fecha_inicio')).all()
    
    return render_template('modulos/ver_vehiculo.html',
                         vehiculo=vehiculo,
                         alquileres=alquileres,
                         trabajos=trabajos)


# ==================== ALQUILERES ====================

@modulos_bp.route('/alquileres')
@login_required
@cache.cached(timeout=60, query_string=True)
def alquileres():
    """List all rentals"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    estado = request.args.get('estado')
    
    query = Alquiler.query
    
    if estado:
        query = query.filter_by(estado_id=estado)
    
    alquileres = query.order_by(
        Alquiler.fecha_alquiler_inicio.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)
    
    estados = EstadoAlquiler.query.all()
    
    return render_template('modulos/alquileres.html',
                         alquileres=alquileres,
                         estados=estados)


@modulos_bp.route('/alquileres/crear', methods=['GET', 'POST'])
@login_required
def crear_alquiler():
    """Create new rental"""
    if request.method == 'POST':
        alquiler = Alquiler(
            vehiculo_id=request.form.get('vehiculo_id'),
            inquilino_id=request.form.get('inquilino_id'),
            estado_id=request.form.get('estado_id'),
            fecha_alquiler_inicio=request.form.get('fecha_inicio'),
            fecha_alquiler_fin=request.form.get('fecha_fin'),
            semana=request.form.get('semana'),
            dia_trabajo=request.form.get('dia_trabajo'),
            ingreso=request.form.get('ingreso'),
            monto_descuento=request.form.get('monto_descuento', 0),
            concepto_descuento=request.form.get('concepto_descuento'),
            notas=request.form.get('notas'),
            usuario_registro_id=current_user.id,
            usuario_actualizo_id=current_user.id
        )
        
        db.session.add(alquiler)
        
        # Update vehicle availability
        vehiculo = Vehiculo.query.get(alquiler.vehiculo_id)
        vehiculo.disponible = False
        
        db.session.commit()
        cache.clear()
        
        flash('Alquiler creado exitosamente', 'success')
        return redirect(url_for('modulos.alquileres'))
    
    vehiculos = Vehiculo.query.filter_by(disponible=True).all()
    inquilinos = Inquilino.query.all()
    estados = EstadoAlquiler.query.all()
    
    return render_template('modulos/crear_alquiler.html',
                         vehiculos=vehiculos,
                         inquilinos=inquilinos,
                         estados=estados)


# ==================== PAGOS ====================

@modulos_bp.route('/pagos')
@login_required
@cache.cached(timeout=60, query_string=True)
def pagos():
    """List all payments"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    pagos = Pago.query.order_by(
        Pago.fecha_pago.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('modulos/pagos.html', pagos=pagos)


@modulos_bp.route('/pagos/crear', methods=['GET', 'POST'])
@login_required
def crear_pago():
    """Create new payment"""
    if request.method == 'POST':
        monto = float(request.form.get('monto'))
        deducciones = float(request.form.get('deducciones', 0))
        
        pago = Pago(
            alquiler_id=request.form.get('alquiler_id'),
            metodo_pago_id=request.form.get('metodo_pago_id'),
            monto=monto,
            fecha_pago=request.form.get('fecha_pago'),
            deducciones=deducciones,
            neto=monto - deducciones,
            comprobante=request.form.get('comprobante'),
            notas=request.form.get('notas'),
            usuario_registro_id=current_user.id,
            usuario_actualizo_id=current_user.id
        )
        
        db.session.add(pago)
        db.session.commit()
        cache.clear()
        
        flash('Pago registrado exitosamente', 'success')
        return redirect(url_for('modulos.pagos'))
    
    alquileres = Alquiler.query.filter(
        Alquiler.estado_id.in_([1, 2, 3])  # Pendiente, En curso, Validado
    ).all()
    metodos = MetodoPago.query.all()
    
    return render_template('modulos/crear_pago.html',
                         alquileres=alquileres,
                         metodos=metodos)


# ==================== DEUDAS ====================

@modulos_bp.route('/deudas')
@login_required
@cache.cached(timeout=60, query_string=True)
def deudas():
    """List all debts"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    estado = request.args.get('estado', 'pendiente')
    
    deudas = Deuda.query.filter_by(estado=estado).order_by(
        Deuda.fecha_vencimiento.asc()
    ).paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('modulos/deudas.html', deudas=deudas)