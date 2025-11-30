"""
=== app/routes/reportes_routes.py ===
"""
from flask import Blueprint, render_template, jsonify
from flask_login import login_required
from app import db, cache
from app.models import Alquiler, Pago, Deuda, Vehiculo, Propietario, Inquilino
from sqlalchemy import func, extract
from datetime import datetime, timedelta

reportes_bp = Blueprint('reportes', __name__)

@reportes_bp.route('/dashboard')
@login_required
@cache.cached(timeout=300)
def dashboard():
    """Main dashboard with statistics"""
    # Get statistics
    total_vehiculos = Vehiculo.query.count()
    vehiculos_disponibles = Vehiculo.query.filter_by(disponible=True).count()
    total_propietarios = Propietario.query.count()
    total_inquilinos = Inquilino.query.count()
    
    # Active rentals
    alquileres_activos = Alquiler.query.filter(
        Alquiler.estado_id.in_([2, 3])  # En curso, Validado
    ).count()
    
    # Pending debts
    deudas_pendientes = db.session.query(
        func.sum(Deuda.monto_deuda)
    ).filter_by(estado='pendiente').scalar() or 0
    
    # Monthly income
    mes_actual = datetime.now().month
    año_actual = datetime.now().year
    
    ingresos_mes = db.session.query(
        func.sum(Pago.neto)
    ).filter(
        extract('month', Pago.fecha_pago) == mes_actual,
        extract('year', Pago.fecha_pago) == año_actual
    ).scalar() or 0
    
    # Recent payments
    pagos_recientes = Pago.query.order_by(
        Pago.fecha_pago.desc()
    ).limit(10).all()
    
    return render_template('reportes/dashboard.html',
                         total_vehiculos=total_vehiculos,
                         vehiculos_disponibles=vehiculos_disponibles,
                         total_propietarios=total_propietarios,
                         total_inquilinos=total_inquilinos,
                         alquileres_activos=alquileres_activos,
                         deudas_pendientes=deudas_pendientes,
                         ingresos_mes=ingresos_mes,
                         pagos_recientes=pagos_recientes)


@reportes_bp.route('/propietarios')
@login_required
def reportes_propietarios():
    """Owners reports"""
    propietarios = db.session.query(
        Propietario,
        func.count(Vehiculo.id).label('total_vehiculos')
    ).outerjoin(Vehiculo).group_by(Propietario.id).all()
    
    return render_template('reportes/reportes_propietarios.html',
                         propietarios=propietarios)


@reportes_bp.route('/inquilinos')
@login_required
def reportes_inquilinos():
    """Tenants reports"""
    inquilinos = db.session.query(
        Inquilino,
        func.count(Alquiler.id).label('total_alquileres'),
        func.sum(Deuda.monto_deuda).label('total_deudas')
    ).outerjoin(Alquiler).outerjoin(Deuda).group_by(Inquilino.id).all()
    
    return render_template('reportes/reportes_inquilinos.html',
                         inquilinos=inquilinos)


@reportes_bp.route('/ganancias')
@login_required
def reportes_ganancias():
    """Earnings reports"""
    # Monthly earnings for current year
    año_actual = datetime.now().year
    
    ganancias_mensuales = db.session.query(
        extract('month', Pago.fecha_pago).label('mes'),
        func.sum(Pago.neto).label('total')
    ).filter(
        extract('year', Pago.fecha_pago) == año_actual
    ).group_by('mes').all()
    
    return render_template('reportes/reportes_ganancias.html',
                         ganancias_mensuales=ganancias_mensuales,
                         año=año_actual)


@reportes_bp.route('/api/ingresos-mensuales')
@login_required
def api_ingresos_mensuales():
    """API endpoint for monthly income chart"""
    año = request.args.get('año', datetime.now().year, type=int)
    
    datos = db.session.query(
        extract('month', Pago.fecha_pago).label('mes'),
        func.sum(Pago.neto).label('total')
    ).filter(
        extract('year', Pago.fecha_pago) == año
    ).group_by('mes').all()
    
    # Fill missing months with 0
    ingresos = {i: 0 for i in range(1, 13)}
    for mes, total in datos:
        ingresos[int(mes)] = float(total)
    
    return jsonify({
        'meses': list(range(1, 13)),
        'ingresos': [ingresos[i] for i in range(1, 13)]
    })

