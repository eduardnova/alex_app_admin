# ==========================================
# RUTAS FLASK PARA SISTEMA DE ALQUILERES
# ==========================================

"""
AGREGAR ESTAS RUTAS A TU APLICACIÓN FLASK
Crear archivo: app/routes/alquileres_routes.py
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from datetime import datetime, date, timedelta
from sqlalchemy import func, and_
from app import db
from app.models import (
    PorcentajeGanancia, SemanaAlquiler, DetalleAlquilerSemanal,
    Alquiler, Vehiculo, Inquilino, Propietario, Banco, Usuario,EstadoAlquiler
)

alquileres_bp = Blueprint('alquiler', __name__)


# ==========================================
# PANTALLA PRINCIPAL - ALQUILERES
# ==========================================
@alquileres_bp.route('/')
@login_required
def index():
    """Pantalla principal de gestión de alquileres semanales"""
    
    # Get semanas con paginación
    page = request.args.get('page', 1, type=int)
    semanas = SemanaAlquiler.query.order_by(
        SemanaAlquiler.fecha_inicio.desc()
    ).paginate(page=page, per_page=20, error_out=False)
    
    # Get porcentajes activos para el modal
    porcentajes_activos = PorcentajeGanancia.query.filter_by(activo=True).all()
    
    # Get bancos para los selects
    bancos = Banco.query.all()
    
    # Calculate stats
    total_semanas = SemanaAlquiler.query.count()
    semanas_activas = SemanaAlquiler.query.filter_by(estado='abierta').count()
    
    # Pagos pendientes
    pagos_pendientes = DetalleAlquilerSemanal.query.filter_by(
        pago_confirmado=False
    ).count()
    
    # Ingreso del mes actual
    mes_actual = date.today().month
    anio_actual = date.today().year
    ingreso_total_mes = db.session.query(
        func.sum(SemanaAlquiler.ingreso_total)
    ).filter(
        and_(
            func.extract('month', SemanaAlquiler.fecha_inicio) == mes_actual,
            func.extract('year', SemanaAlquiler.fecha_inicio) == anio_actual
        )
    ).scalar() or 0
    
    return render_template(
        'modulos/alquileres.html',
        semanas=semanas.items,
        porcentajes_activos=porcentajes_activos,
        bancos=bancos,
        total_semanas=total_semanas,
        semanas_activas=semanas_activas,
        pagos_pendientes=pagos_pendientes,
        ingreso_total_mes=ingreso_total_mes
    )


# ==========================================
# CREAR SEMANA
# ==========================================
@alquileres_bp.route('/alquiler/semanas/crear', methods=['POST'])
@login_required
def crear_semana():
    """Crea una nueva semana de trabajo"""
    
    try:
        fecha_inicio = datetime.strptime(request.form.get('fecha_inicio'), '%Y-%m-%d').date()
        fecha_fin = datetime.strptime(request.form.get('fecha_fin'), '%Y-%m-%d').date()
        porcentaje_ganancia_id = int(request.form.get('porcentaje_ganancia_id'))
        notas = request.form.get('notas')
        
        # Validate dates
        if fecha_fin < fecha_inicio:
            flash('La fecha de fin debe ser posterior a la fecha de inicio', 'error')
            return redirect(url_for('alquiler.index'))
        
        # Get numero de semana
        numero_semana = fecha_inicio.isocalendar()[1]
        anio = fecha_inicio.year
        
        # Check if semana already exists
        existing = SemanaAlquiler.query.filter(
            and_(
                SemanaAlquiler.fecha_inicio == fecha_inicio,
                SemanaAlquiler.fecha_fin == fecha_fin
            )
        ).first()
        
        if existing:
            flash('Ya existe una semana con este rango de fechas', 'error')
            return redirect(url_for('alquiler.index'))
        
        # Create semana
        semana = SemanaAlquiler(
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            numero_semana=numero_semana,
            anio=anio,
            porcentaje_ganancia_id=porcentaje_ganancia_id,
            estado='abierta',
            notas=notas,
            usuario_registro_id=current_user.id
        )
        
        db.session.add(semana)
        db.session.flush()
        
        # Get alquileres activos en este rango
        alquileres_activos = Alquiler.query.filter(
            and_(
                Alquiler.fecha_alquiler_inicio <= fecha_fin,
                Alquiler.fecha_alquiler_fin >= fecha_inicio
            )
        ).all()
        
        # Get porcentaje
        porcentaje = PorcentajeGanancia.query.get(porcentaje_ganancia_id)
        
        # Calculate dias de trabajo
        dias_trabajo = (fecha_fin - fecha_inicio).days + 1
        
        # Get fecha limite (jueves de la semana)
        fecha_limite = fecha_inicio + timedelta(days=(3 - fecha_inicio.weekday()) % 7)
        
        # Create detalles
        total_vehiculos = 0
        socios = set()
        inquilinos = set()
        ingreso_total = 0
        
        for alquiler in alquileres_activos:
            vehiculo = Vehiculo.query.get(alquiler.vehiculo_id)
            inquilino = Inquilino.query.get(alquiler.inquilino_id)
            propietario = Propietario.query.get(vehiculo.propietario_id)
            
            precio_semanal = float(vehiculo.precio_semanal)
            ingreso_calculado = precio_semanal * dias_trabajo
            nomina_empresa = ingreso_calculado * (float(porcentaje.porcentaje) / 100)
            
            # Check if tiene deuda (si hoy es después del jueves y no hay confirmación)
            tiene_deuda = date.today() > fecha_limite
            
            detalle = DetalleAlquilerSemanal(
                semana_alquiler_id=semana.id,
                alquiler_id=alquiler.id,
                vehiculo_id=alquiler.vehiculo_id,
                inquilino_id=alquiler.inquilino_id,
                propietario_id=vehiculo.propietario_id,
                precio_semanal=precio_semanal,
                dias_trabajo=dias_trabajo,
                ingreso_calculado=ingreso_calculado,
                porcentaje_empresa=porcentaje.porcentaje,
                nomina_empresa=nomina_empresa,
                tiene_deuda=tiene_deuda,
                fecha_limite_pago=fecha_limite,
                nomina_final=ingreso_calculado,
                usuario_registro_id=current_user.id
            )
            
            db.session.add(detalle)
            
            total_vehiculos += 1
            socios.add(propietario.id)
            inquilinos.add(inquilino.id)
            ingreso_total += ingreso_calculado
        
        # Update semana totals
        semana.total_vehiculos = total_vehiculos
        semana.total_socios = len(socios)
        semana.total_inquilinos = len(inquilinos)
        semana.ingreso_total = ingreso_total
        
        db.session.commit()
        
        flash(f'Semana creada exitosamente con {total_vehiculos} vehículos', 'success')
        return redirect(url_for('alquiler.index'))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error al crear semana: {str(e)}', 'error')
        return redirect(url_for('alquiler.index'))


# ==========================================
# VER DETALLES DE SEMANA (JSON)
# ==========================================
@alquileres_bp.route('/alquiler/semanas/<int:id>/detalles')
@login_required
def ver_detalles_semana(id):
    """Retorna los detalles de una semana en formato JSON"""
    
    try:
        semana = SemanaAlquiler.query.get_or_404(id)
        detalles = DetalleAlquilerSemanal.query.filter_by(
            semana_alquiler_id=id
        ).all()
        
        detalles_data = []
        for detalle in detalles:
            try:
                # ✅ Cargar relaciones con manejo de errores
                vehiculo = Vehiculo.query.get(detalle.vehiculo_id)
                inquilino = Inquilino.query.get(detalle.inquilino_id)
                propietario = Propietario.query.get(detalle.propietario_id)
                
                # Get marca y modelo
                marca_modelo = None
                if vehiculo:
                    try:
                        marca_modelo = vehiculo.marca_modelo
                    except:
                        print(f"⚠️ Warning: No se pudo cargar marca_modelo para vehículo {vehiculo.id}")
                
                # Get iniciales propietario
                iniciales = '??'
                propietario_nombre = ''
                if propietario:
                    try:
                        propietario_nombre = propietario.nombre_apellido or ''
                        nombre_parts = propietario_nombre.split() if propietario_nombre else ['?']
                        iniciales = ''.join([p[0].upper() for p in nombre_parts[:2]])
                    except Exception as e:
                        print(f"⚠️ Warning: Error al procesar propietario {propietario.id}: {str(e)}")
                        propietario_nombre = 'Error al cargar'
                
                # Get datos del vehículo
                vehiculo_marca = ''
                vehiculo_modelo_str = ''
                vehiculo_placa = ''
                if vehiculo:
                    try:
                        vehiculo_placa = vehiculo.placa or ''
                        if marca_modelo:
                            vehiculo_marca = marca_modelo.marca or ''
                            vehiculo_modelo_str = marca_modelo.modelo or ''
                    except Exception as e:
                        print(f"⚠️ Warning: Error al procesar vehículo {vehiculo.id}: {str(e)}")
                
                # Get datos del inquilino
                inquilino_nombre = ''
                inquilino_telefono = ''
                if inquilino:
                    try:
                        inquilino_nombre = inquilino.nombre_apellido or ''
                        inquilino_telefono = inquilino.telefono or ''
                    except Exception as e:
                        print(f"⚠️ Warning: Error al procesar inquilino {inquilino.id}: {str(e)}")
                
                detalles_data.append({
                    'id': detalle.id,
                    'vehiculo_id': detalle.vehiculo_id,  # ✅ Agregado para edición
                    'inquilino_id': detalle.inquilino_id,  # ✅ Agregado para edición
                    'propietario_id': detalle.propietario_id,  # ✅ Agregado
                    'propietario_nombre': propietario_nombre,
                    'propietario_iniciales': iniciales,
                    'vehiculo_marca': vehiculo_marca,
                    'vehiculo_modelo': vehiculo_modelo_str,
                    'vehiculo_placa': vehiculo_placa,
                    'inquilino_nombre': inquilino_nombre,
                    'inquilino_telefono': inquilino_telefono,
                    'precio_semanal': float(detalle.precio_semanal),
                    'dias_trabajo': detalle.dias_trabajo,
                    'ingreso_calculado': float(detalle.ingreso_calculado),
                    'inversion_mecanica': float(detalle.inversion_mecanica or 0),
                    'concepto_inversion': detalle.concepto_inversion or '',
                    'monto_descuento': float(detalle.monto_descuento or 0),
                    'concepto_descuento': detalle.concepto_descuento or '',
                    'nomina_empresa': float(detalle.nomina_empresa),
                    'porcentaje_empresa': float(detalle.porcentaje_empresa),
                    'tiene_deuda': detalle.tiene_deuda,
                    'monto_deuda': float(detalle.monto_deuda or 0),
                    'nomina_final': float(detalle.nomina_final),
                    'banco_id': detalle.banco_id,
                    'fecha_confirmacion_pago': detalle.fecha_confirmacion_pago.isoformat() if detalle.fecha_confirmacion_pago else '',
                    'pago_confirmado': detalle.pago_confirmado,
                    'notas': detalle.notas or ''
                })
            except Exception as e:
                print(f"❌ Error procesando detalle {detalle.id}: {str(e)}")
                import traceback
                traceback.print_exc()
                # Continuar con el siguiente detalle
                continue
        
        return jsonify({
            'success': True,
            'semana': {
                'id': semana.id,
                'fecha_inicio': semana.fecha_inicio.strftime('%d/%m/%Y'),
                'fecha_fin': semana.fecha_fin.strftime('%d/%m/%Y'),
                'total_vehiculos': semana.total_vehiculos,
                'total_socios': semana.total_socios,
                'total_inquilinos': semana.total_inquilinos,
                'ingreso_total': float(semana.ingreso_total)
            },
            'detalles': detalles_data
        })
        
    except Exception as e:
        print(f"❌ Error en ver_detalles_semana: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500
    
# ==========================================
# GUARDAR CAMBIOS EN DETALLES
# ==========================================
@alquileres_bp.route('/alquiler/semanas/<int:id>/guardar-cambios', methods=['POST'])
@login_required
def guardar_cambios_semana(id):
    """Guarda los cambios realizados en los detalles de la semana"""
    
    try:
        data = request.get_json()
        cambios = data.get('cambios', [])
        
        updated_count = 0
        
        for cambio in cambios:
            detalle = DetalleAlquilerSemanal.query.get(cambio['id'])
            if detalle and detalle.semana_alquiler_id == id:
                # Update fields
                detalle.precio_semanal = cambio.get('precio_semanal')
                detalle.dias_trabajo = cambio.get('dias_trabajo')
                detalle.inversion_mecanica = cambio.get('inversion_mecanica', 0)
                detalle.concepto_inversion = cambio.get('concepto_inversion')
                detalle.monto_descuento = cambio.get('monto_descuento', 0)
                detalle.concepto_descuento = cambio.get('concepto_descuento')
                detalle.monto_deuda = cambio.get('monto_deuda', 0)
                detalle.banco_id = cambio.get('banco_id') if cambio.get('banco_id') else None
                
                if cambio.get('fecha_confirmacion_pago'):
                    detalle.fecha_confirmacion_pago = datetime.strptime(
                        cambio.get('fecha_confirmacion_pago'), '%Y-%m-%d'
                    ).date()
                
                detalle.pago_confirmado = cambio.get('pago_confirmado', False)
                detalle.notas = cambio.get('notas')
                
                # Recalculate
                #detalle.ingreso_calculado = float(detalle.precio_semanal) * int(detalle.dias_trabajo)
                #detalle.nomina_empresa = detalle.ingreso_calculado * (float(detalle.porcentaje_empresa) / 100)
                #detalle.nomina_final = detalle.ingreso_calculado + float(detalle.monto_deuda or 0)
                #  Recalculate con fórmula correcta
                precio_diario = float(detalle.precio_semanal) / 7
                detalle.ingreso_calculado = precio_diario * int(detalle.dias_trabajo)
                detalle.nomina_empresa =  precio_diario * int(detalle.dias_trabajo) #detalle.ingreso_calculado * (float(detalle.porcentaje_empresa) / 100)
                detalle.nomina_final =  precio_diario * int(detalle.dias_trabajo) #detalle.ingreso_calculado + float(detalle.monto_deuda or 0)
                
                detalle.usuario_actualizo_id = current_user.id
                detalle.fecha_hora_actualizo = datetime.utcnow()
                
                updated_count += 1
        
        # Recalculate semana totals
        semana = SemanaAlquiler.query.get(id)
        if semana:
            detalles = DetalleAlquilerSemanal.query.filter_by(semana_alquiler_id=id).all()
            semana.ingreso_total = sum(float(d.ingreso_calculado) for d in detalles)
            semana.usuario_actualizo_id = current_user.id
            semana.fecha_hora_actualizo = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'{updated_count} detalles actualizados',
            'updated': updated_count
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

# ==========================================
# ALQUILERES DISPONIBLES PARA AGREGAR
# ==========================================

@alquileres_bp.route('/alquiler/semanas/<int:id>/alquileres_disponibles')
@login_required
def alquileres_disponibles(id):
    """Retorna alquileres activos que no están en esta semana (VERSIÓN MEJORADA)"""
    
    try:
        semana = SemanaAlquiler.query.get_or_404(id)
        
        # Get alquileres ya en esta semana
        alquileres_en_semana = db.session.query(
            DetalleAlquilerSemanal.alquiler_id
        ).filter_by(semana_alquiler_id=id).all()
        
        alquileres_ids_en_semana = [a[0] for a in alquileres_en_semana]
        
        # Get alquileres activos en el rango de la semana
        alquileres_disponibles = Alquiler.query.filter(
            and_(
                Alquiler.fecha_alquiler_inicio <= semana.fecha_fin,
                Alquiler.fecha_alquiler_fin >= semana.fecha_inicio,
                ~Alquiler.id.in_(alquileres_ids_en_semana)
            )
        ).all()
        
        alquileres_data = []
        for alquiler in alquileres_disponibles:
            vehiculo = Vehiculo.query.get(alquiler.vehiculo_id)
            inquilino = Inquilino.query.get(alquiler.inquilino_id)
            
            if not vehiculo or not inquilino:
                continue
            
            # Get propietario
            propietario = Propietario.query.get(vehiculo.propietario_id) if vehiculo else None
            
            # Get marca y modelo
            marca_modelo = vehiculo.marca_modelo_vehiculo if vehiculo else None
            
            alquileres_data.append({
                'id': alquiler.id,
                'vehiculo_placa': vehiculo.placa,
                'vehiculo_marca': marca_modelo.marca if marca_modelo else 'N/A',
                'vehiculo_modelo': marca_modelo.modelo if marca_modelo else 'N/A',
                'inquilino_nombre': inquilino.nombre_apellido,
                'inquilino_telefono': inquilino.telefono if inquilino.telefono else '',
                'propietario_nombre': propietario.nombre_apellido if propietario else '',
                'precio_semanal': float(vehiculo.precio_semanal) if vehiculo else 0,
                'fecha_inicio': alquiler.fecha_alquiler_inicio.isoformat() if alquiler.fecha_alquiler_inicio else '',
                'fecha_fin': alquiler.fecha_alquiler_fin.isoformat() if alquiler.fecha_alquiler_fin else ''
            })
        
        # Sort by placa
        alquileres_data.sort(key=lambda x: x['vehiculo_placa'])
        
        return jsonify({
            'success': True,
            'alquileres': alquileres_data,
            'total': len(alquileres_data)
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    
# ==========================================
# AGREGAR ALQUILER A SEMANA (VERSIÓN CORREGIDA)
# ==========================================

@alquileres_bp.route('/alquiler/semanas/agregar_alquiler', methods=['POST'])
@login_required
def agregar_alquiler_a_semana():
    """Crea un nuevo detalle de alquiler para la semana (CON REGISTRO EN ALQUILERES)"""
    
    try:
        data = request.get_json()
        semana_id = int(data.get('semana_id'))
        vehiculo_id = int(data.get('vehiculo_id'))
        inquilino_id = int(data.get('inquilino_id'))
        dias_trabajo = int(data.get('dias_trabajo', 7))
        
        # Validar que no exista ya este vehículo en la semana
        existing = DetalleAlquilerSemanal.query.filter_by(
            semana_alquiler_id=semana_id,
            vehiculo_id=vehiculo_id
        ).first()
        
        if existing:
            return jsonify({
                'success': False,
                'message': 'Este vehículo ya está en esta semana'
            }), 400
        
        # Validar que no exista ya este inquilino en la semana
        existing_inquilino = DetalleAlquilerSemanal.query.filter_by(
            semana_alquiler_id=semana_id,
            inquilino_id=inquilino_id
        ).first()
        
        if existing_inquilino:
            return jsonify({
                'success': False,
                'message': 'Este inquilino ya tiene un vehículo asignado en esta semana'
            }), 400
        
        # Get semana
        semana = SemanaAlquiler.query.get_or_404(semana_id)
        
        # Get vehículo
        vehiculo = Vehiculo.query.get_or_404(vehiculo_id)
        propietario = Propietario.query.get(vehiculo.propietario_id)
        
        if not propietario:
            return jsonify({
                'success': False,
                'message': 'El vehículo no tiene propietario asignado'
            }), 400
        
        # Get inquilino
        inquilino = Inquilino.query.get_or_404(inquilino_id)
        
        # Get estado "activo" o el primero disponible
        estado = EstadoAlquiler.query.filter_by(nombre='activo').first()
        if not estado:
            estado = EstadoAlquiler.query.first()
        
        if not estado:
            return jsonify({
                'success': False,
                'message': 'No hay estados de alquiler configurados'
            }), 400
        
        # ✅ PASO 1: Crear registro en tabla ALQUILERES
        precio_semanal = float(vehiculo.precio_semanal)
        ingreso = precio_semanal * dias_trabajo
        
        nuevo_alquiler = Alquiler(
            vehiculo_id=vehiculo_id,
            inquilino_id=inquilino_id,
            estado_id=estado.id,
            fecha_alquiler_inicio=semana.fecha_inicio,
            fecha_alquiler_fin=semana.fecha_fin,
            semana=semana.numero_semana,
            dia_trabajo=dias_trabajo,
            ingreso=ingreso,
            monto_descuento=0.00,
            usuario_registro_id=current_user.id,
            usuario_actualizo_id=current_user.id  # ✅ Agregado
        )
        
        db.session.add(nuevo_alquiler)
        db.session.flush()  # Para obtener el ID
        
        # ✅ PASO 2: Ahora crear el detalle con alquiler_id
        porcentaje = PorcentajeGanancia.query.get(semana.porcentaje_ganancia_id)
        
        ingreso_calculado = precio_semanal * dias_trabajo
        nomina_empresa = ingreso_calculado * (float(porcentaje.porcentaje) / 100)
        
        # Calculate fecha limite (jueves)
        fecha_limite = semana.fecha_inicio + timedelta(
            days=(3 - semana.fecha_inicio.weekday()) % 7
        )
        tiene_deuda = date.today() > fecha_limite
        
        detalle = DetalleAlquilerSemanal(
            semana_alquiler_id=semana_id,
            alquiler_id=nuevo_alquiler.id,  # ✅ Ahora sí tiene valor
            vehiculo_id=vehiculo_id,
            inquilino_id=inquilino_id,
            propietario_id=vehiculo.propietario_id,
            precio_semanal=precio_semanal,
            dias_trabajo=dias_trabajo,
            ingreso_calculado=ingreso_calculado,
            porcentaje_empresa=porcentaje.porcentaje,
            nomina_empresa=nomina_empresa,
            tiene_deuda=tiene_deuda,
            fecha_limite_pago=fecha_limite,
            nomina_final=ingreso_calculado,
            usuario_registro_id=current_user.id
        )
        
        db.session.add(detalle)
        
        # Update semana totals
        semana.total_vehiculos = (semana.total_vehiculos or 0) + 1
        semana.ingreso_total = float(semana.ingreso_total or 0) + ingreso_calculado
        
        # Recalculate unique propietarios and inquilinos
        semana.total_socios = db.session.query(
            func.count(func.distinct(DetalleAlquilerSemanal.propietario_id))
        ).filter_by(semana_alquiler_id=semana_id).scalar() + 1
        
        semana.total_inquilinos = db.session.query(
            func.count(func.distinct(DetalleAlquilerSemanal.inquilino_id))
        ).filter_by(semana_alquiler_id=semana_id).scalar() + 1
        
        semana.usuario_actualizo_id = current_user.id
        semana.fecha_hora_actualizo = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Alquiler agregado exitosamente',
            'detalle_id': detalle.id,
            'alquiler_id': nuevo_alquiler.id
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500

@alquileres_bp.route('/alquiler/semanas/agregar_alquiler_', methods=['POST'])
@login_required
def agregar_alquiler_a_semana_():
    """Crea un nuevo detalle de alquiler para la semana"""
    
    #try:
    data = request.get_json()
    semana_id = int(data.get('semana_id'))
    vehiculo_id = int(data.get('vehiculo_id'))
    inquilino_id = int(data.get('inquilino_id'))
    dias_trabajo = int(data.get('dias_trabajo', 7))
    
    # Validar que no exista ya este vehículo en la semana
    existing = DetalleAlquilerSemanal.query.filter_by(
        semana_alquiler_id=semana_id,
        vehiculo_id=vehiculo_id
    ).first()
    
    if existing:
        return jsonify({
            'success': False,
            'message': 'Este vehículo ya está en esta semana'
        }), 400
    
    # Validar que no exista ya este inquilino en la semana
    existing_inquilino = DetalleAlquilerSemanal.query.filter_by(
        semana_alquiler_id=semana_id,
        inquilino_id=inquilino_id
    ).first()
    
    if existing_inquilino:
        return jsonify({
            'success': False,
            'message': 'Este inquilino ya tiene un vehículo asignado en esta semana'
        }), 400
    
    # Get semana
    semana = SemanaAlquiler.query.get_or_404(semana_id)
    
    # Get vehículo
    vehiculo = Vehiculo.query.get_or_404(vehiculo_id)
    propietario = Propietario.query.get(vehiculo.propietario_id)
    
    if not propietario:
        return jsonify({
            'success': False,
            'message': 'El vehículo no tiene propietario asignado'
        }), 400
    
    # Get inquilino
    inquilino = Inquilino.query.get_or_404(inquilino_id)
    
    # Get porcentaje
    porcentaje = PorcentajeGanancia.query.get(semana.porcentaje_ganancia_id)
    
    # Calculate
    precio_semanal = float(vehiculo.precio_semanal)
    ingreso_calculado = precio_semanal * dias_trabajo
    nomina_empresa = ingreso_calculado * (float(porcentaje.porcentaje) / 100)
    
    # Calculate fecha limite (jueves)
    fecha_limite = semana.fecha_inicio + timedelta(
        days=(3 - semana.fecha_inicio.weekday()) % 7
    )
    tiene_deuda = date.today() > fecha_limite
    
    # Create detalle
    detalle = DetalleAlquilerSemanal(
        semana_alquiler_id=semana_id,
        alquiler_id=None,  # No hay alquiler previo
        vehiculo_id=vehiculo_id,
        inquilino_id=inquilino_id,
        propietario_id=vehiculo.propietario_id,
        precio_semanal=precio_semanal,
        dias_trabajo=dias_trabajo,
        ingreso_calculado=ingreso_calculado,
        porcentaje_empresa=porcentaje.porcentaje,
        nomina_empresa=nomina_empresa,
        tiene_deuda=tiene_deuda,
        fecha_limite_pago=fecha_limite,
        nomina_final=ingreso_calculado,
        usuario_registro_id=current_user.id
    )
    
    db.session.add(detalle)
    
    # Update semana totals
    semana.total_vehiculos = (semana.total_vehiculos or 0) + 1
    semana.ingreso_total = float(semana.ingreso_total or 0) + ingreso_calculado
    
    # Recalculate unique propietarios and inquilinos
    semana.total_socios = db.session.query(
        func.count(func.distinct(DetalleAlquilerSemanal.propietario_id))
    ).filter_by(semana_alquiler_id=semana_id).scalar() + 1
    
    semana.total_inquilinos = db.session.query(
        func.count(func.distinct(DetalleAlquilerSemanal.inquilino_id))
    ).filter_by(semana_alquiler_id=semana_id).scalar() + 1
    
    semana.usuario_actualizo_id = current_user.id
    semana.fecha_hora_actualizo = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Alquiler agregado exitosamente',
        'detalle_id': detalle.id
    })
        
    #except Exception as e:
    #    db.session.rollback()
    #    return jsonify({'success': False, 'message': str(e)}), 500


# ==========================================
# ELIMINAR DETALLE DE SEMANA
# ==========================================
@alquileres_bp.route('/alquiler/detalles/<int:id>/eliminar', methods=['POST'])
@login_required
def eliminar_detalle(id):
    """Elimina un detalle de alquiler de una semana"""
    
    try:
        detalle = DetalleAlquilerSemanal.query.get_or_404(id)
        semana_id = detalle.semana_alquiler_id
        
        # Get semana
        semana = SemanaAlquiler.query.get(semana_id)
        
        if semana.estado != 'abierta':
            return jsonify({
                'success': False,
                'message': 'No se puede eliminar detalles de una semana cerrada'
            }), 400
        
        # Update semana totals
        semana.total_vehiculos = max(0, semana.total_vehiculos - 1)
        semana.ingreso_total = float(semana.ingreso_total or 0) - float(detalle.ingreso_calculado or 0)
        
        # Recalculate propietarios and inquilinos
        db.session.delete(detalle)
        db.session.flush()
        
        semana.total_socios = db.session.query(
            func.count(func.distinct(DetalleAlquilerSemanal.propietario_id))
        ).filter_by(semana_alquiler_id=semana_id).scalar() or 0
        
        semana.total_inquilinos = db.session.query(
            func.count(func.distinct(DetalleAlquilerSemanal.inquilino_id))
        ).filter_by(semana_alquiler_id=semana_id).scalar() or 0
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Detalle eliminado exitosamente'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500
 
# ==========================================
# CERRAR SEMANA
# ==========================================
@alquileres_bp.route('/alquiler/semanas/<int:id>/cerrar', methods=['POST'])
@login_required
def cerrar_semana(id):
    """Cierra una semana de trabajo"""
    
    try:
        semana = SemanaAlquiler.query.get_or_404(id)
        
        if semana.estado != 'abierta':
            return jsonify({'success': False, 'message': 'La semana ya está cerrada'}), 400
        
        semana.estado = 'cerrada'
        semana.usuario_actualizo_id = current_user.id
        semana.fecha_hora_actualizo = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Semana cerrada exitosamente'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

# ==========================================
# EXPORTAR A EXCEL
# ==========================================
@alquileres_bp.route('/alquiler/semanas/<int:id>/exportar-excel')
@login_required
def exportar_excel_semana(id):
    """Exporta los detalles de una semana a Excel"""
    
    try:
        import openpyxl
        from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
        from io import BytesIO
        from flask import send_file
        
        semana = SemanaAlquiler.query.get_or_404(id)
        detalles = DetalleAlquilerSemanal.query.filter_by(semana_alquiler_id=id).all()
        
        # Create workbook
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = f"Semana {semana.numero_semana}"
        
        # Header
        headers = [
            'Propietario', 'Vehículo', 'Placa', 'Inquilino', 'Tel. Inquilino',
            'Semanal', 'DT', 'Ingreso', 'Inversión', 'Concepto Desc.',
            'Nómina', '% Empresa', 'Deuda', 'Nómina 2', 'Banco',
            'Conf. Pago', 'DT2'
        ]
        
        ws.append(headers)
        
        # Style header
        for cell in ws[1]:
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
            cell.alignment = Alignment(horizontal='center', vertical='center')
        
        # Add data
        for detalle in detalles:
            vehiculo = Vehiculo.query.get(detalle.vehiculo_id)
            inquilino = Inquilino.query.get(detalle.inquilino_id)
            propietario = Propietario.query.get(detalle.propietario_id)
            banco = Banco.query.get(detalle.banco_id) if detalle.banco_id else None
            marca_modelo = vehiculo.marca_modelo_vehiculo if vehiculo else None
            
            ws.append([
                propietario.nombre_apellido if propietario else '',
                f"{marca_modelo.marca} {marca_modelo.modelo}" if marca_modelo else '',
                vehiculo.placa if vehiculo else '',
                inquilino.nombre_apellido if inquilino else '',
                inquilino.telefono if inquilino else '',
                float(detalle.precio_semanal),
                detalle.dias_trabajo,
                float(detalle.ingreso_calculado),
                float(detalle.inversion_mecanica or 0),
                detalle.concepto_descuento or '',
                float(detalle.nomina_empresa),
                float(detalle.porcentaje_empresa),
                float(detalle.monto_deuda or 0),
                float(detalle.nomina_final),
                banco.banco if banco else '',
                detalle.fecha_confirmacion_pago.strftime('%d/%m/%Y') if detalle.fecha_confirmacion_pago else '',
                detalle.dias_trabajo
            ])
        
        # Auto-adjust columns
        for column in ws.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(cell.value)
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            ws.column_dimensions[column_letter].width = adjusted_width
        
        # Save to BytesIO
        output = BytesIO()
        wb.save(output)
        output.seek(0)
        
        filename = f"semana_{semana.fecha_inicio.strftime('%Y%m%d')}_{semana.fecha_fin.strftime('%Y%m%d')}.xlsx"
        
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        flash(f'Error al exportar: {str(e)}', 'error')
        return redirect(url_for('alquiler.index'))


# ==========================================
# BANCOS JSON (HELPER)
# ==========================================
@alquileres_bp.route('/alquiler/bancos/json')
@login_required
def bancos_json():
    """Retorna lista de bancos en JSON para los selects"""
    
    try:
        bancos = Banco.query.all()
        bancos_data = [
            {
                'id': banco.id,
                'banco': banco.banco,
                'cuenta': banco.cuenta
            }
            for banco in bancos
        ]
        
        return jsonify({'success': True, 'bancos': bancos_data})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


# ==========================================
# PORCENTAJES DE GANANCIA - CRUD
# ==========================================
@alquileres_bp.route('/porcentajes_ganancia')
@login_required
def porcentajes_ganancia():
    """Pantalla de gestión de porcentajes de ganancia"""
    
    porcentajes = PorcentajeGanancia.query.order_by(
        PorcentajeGanancia.por_defecto.desc(),
        PorcentajeGanancia.activo.desc(),
        PorcentajeGanancia.porcentaje.asc()
    ).all()
    
    porcentajes_activos = sum(1 for p in porcentajes if p.activo)
    porcentaje_defecto = next((p for p in porcentajes if p.por_defecto), None)
    
    # Count semanas usando cada porcentaje
    semanas_con_porcentaje = SemanaAlquiler.query.count()
    
    return render_template(
        'modulos/porcentajes_ganancia.html',
        porcentajes=porcentajes,
        porcentajes_activos=porcentajes_activos,
        porcentaje_defecto=porcentaje_defecto,
        semanas_con_porcentaje=semanas_con_porcentaje
    )


@alquileres_bp.route('/alquiler/porcentajes_ganancia/crear', methods=['POST'])
@login_required
def crear_porcentaje_ganancia():
    """Crea un nuevo porcentaje de ganancia"""
    
    try:
        descripcion = request.form.get('descripcion')
        porcentaje = float(request.form.get('porcentaje'))
        activo = request.form.get('activo') == 'on'
        por_defecto = request.form.get('por_defecto') == 'on'
        
        # Si es por defecto, desmarcar otros
        if por_defecto:
            PorcentajeGanancia.query.update({'por_defecto': False})
        
        nuevo_porcentaje = PorcentajeGanancia(
            descripcion=descripcion,
            porcentaje=porcentaje,
            activo=activo,
            por_defecto=por_defecto,
            usuario_registro_id=current_user.id
        )
        
        db.session.add(nuevo_porcentaje)
        db.session.commit()
        
        flash('Porcentaje de ganancia creado exitosamente', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error al crear porcentaje: {str(e)}', 'error')
    
    return redirect(url_for('alquiler.porcentajes_ganancia'))


@alquileres_bp.route('/alquiler/porcentajes_ganancia/<int:id>/json')
@login_required
def ver_porcentaje_json(id):
    """Retorna un porcentaje en JSON"""
    
    try:
        porcentaje = PorcentajeGanancia.query.get_or_404(id)
        
        return jsonify({
            'success': True,
            'data': {
                'id': porcentaje.id,
                'descripcion': porcentaje.descripcion,
                'porcentaje': float(porcentaje.porcentaje),
                'activo': porcentaje.activo,
                'por_defecto': porcentaje.por_defecto
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 404


@alquileres_bp.route('/alquiler/porcentajes_ganancia/<int:id>/editar', methods=['POST'])
@login_required
def editar_porcentaje_ganancia(id):
    """Edita un porcentaje de ganancia"""
    
    try:
        porcentaje = PorcentajeGanancia.query.get_or_404(id)
        
        porcentaje.descripcion = request.form.get('descripcion')
        porcentaje.porcentaje = float(request.form.get('porcentaje'))
        porcentaje.activo = request.form.get('activo') == 'on'
        por_defecto = request.form.get('por_defecto') == 'on'
        
        if por_defecto and not porcentaje.por_defecto:
            PorcentajeGanancia.query.update({'por_defecto': False})
            porcentaje.por_defecto = True
        elif not por_defecto:
            porcentaje.por_defecto = False
        
        porcentaje.usuario_actualizo_id = current_user.id
        
        db.session.commit()
        
        flash('Porcentaje actualizado exitosamente', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error al actualizar porcentaje: {str(e)}', 'error')
    
    return redirect(url_for('alquiler.porcentajes_ganancia'))


@alquileres_bp.route('/alquiler/porcentajes_ganancia/<int:id>/eliminar', methods=['POST'])
@login_required
def eliminar_porcentaje_ganancia(id):
    """Elimina un porcentaje de ganancia"""
    
    try:
        porcentaje = PorcentajeGanancia.query.get_or_404(id)
        
        # Check if in use
        if porcentaje.semanas_alquiler.count() > 0:
            flash('No se puede eliminar: el porcentaje está en uso', 'error')
            return redirect(url_for('alquiler.porcentajes_ganancia'))
        
        db.session.delete(porcentaje)
        db.session.commit()
        
        flash('Porcentaje eliminado exitosamente', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar porcentaje: {str(e)}', 'error')
    
    return redirect(url_for('alquiler.porcentajes_ganancia'))

# ==========================================
# VEHÍCULOS E INQUILINOS DISPONIBLES
# ==========================================
@alquileres_bp.route('/alquiler/semanas/<int:id>/disponibles')
@login_required
def disponibles_para_alquiler(id):
    """Retorna vehículos e inquilinos disponibles para agregar a la semana"""
    
    try:
        semana = SemanaAlquiler.query.get_or_404(id)
        
        # Get vehículos ya en esta semana
        vehiculos_en_semana = db.session.query(
            DetalleAlquilerSemanal.vehiculo_id
        ).filter_by(semana_alquiler_id=id).all()
        
        vehiculos_ids_en_semana = [v[0] for v in vehiculos_en_semana]
        
        # Get inquilinos ya en esta semana
        inquilinos_en_semana = db.session.query(
            DetalleAlquilerSemanal.inquilino_id
        ).filter_by(semana_alquiler_id=id).all()
        
        inquilinos_ids_en_semana = [i[0] for i in inquilinos_en_semana]
        
        # Get vehículos disponibles
        from sqlalchemy import and_, or_
        
        vehiculos_query = Vehiculo.query.filter(
            Vehiculo.propietario_id.isnot(None)
        )
        
        # Exclude vehicles already in this week
        if vehiculos_ids_en_semana:
            vehiculos_query = vehiculos_query.filter(
                ~Vehiculo.id.in_(vehiculos_ids_en_semana)
            )
        
        vehiculos_disponibles = vehiculos_query.all()
        
        # Get inquilinos disponibles
        inquilinos_query = Inquilino.query
        
        # Exclude inquilinos already in this week
        if inquilinos_ids_en_semana:
            inquilinos_query = inquilinos_query.filter(
                ~Inquilino.id.in_(inquilinos_ids_en_semana)
            )
        
        inquilinos_disponibles = inquilinos_query.all()
        
        # Prepare vehiculos data
        vehiculos_data = []
        for vehiculo in vehiculos_disponibles:
            try:
                marca_modelo = vehiculo.marca_modelo if hasattr(vehiculo, 'marca_modelo') else None
                propietario = Propietario.query.get(vehiculo.propietario_id) if vehiculo.propietario_id else None
                
                vehiculos_data.append({
                    'id': vehiculo.id,
                    'placa': vehiculo.placa if vehiculo.placa else 'N/A',
                    'marca': marca_modelo.marca if marca_modelo else 'N/A',
                    'modelo': marca_modelo.modelo if marca_modelo else 'N/A',
                    'ano': vehiculo.ano if vehiculo.ano else '',
                    'color': vehiculo.color if vehiculo.color else '',
                    'precio_semanal': float(vehiculo.precio_semanal) if vehiculo.precio_semanal else 0,
                    'propietario_id': vehiculo.propietario_id,
                    'propietario_nombre': propietario.nombre_apellido if propietario else ''
                })
            except Exception as e:
                print(f"Error procesando vehículo {vehiculo.id}: {str(e)}")
                continue
        
        # Prepare inquilinos data
        inquilinos_data = []
        for inquilino in inquilinos_disponibles:
            try:
                inquilinos_data.append({
                    'id': inquilino.id,
                    'nombre_apellido': inquilino.nombre_apellido if inquilino.nombre_apellido else 'Sin nombre',
                    'telefono': inquilino.telefono if inquilino.telefono else '',
                    'cedula': inquilino.cedula if inquilino.cedula else ''
                })
            except Exception as e:
                print(f"Error procesando inquilino {inquilino.id}: {str(e)}")
                continue
        
        print(f"✅ Returning {len(vehiculos_data)} vehículos y {len(inquilinos_data)} inquilinos")
        
        return jsonify({
            'success': True,
            'vehiculos': vehiculos_data,
            'inquilinos': inquilinos_data
        })
        
    except Exception as e:
        print(f"❌ Error en disponibles_para_alquiler: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500
    
# ==========================================
# ELIMINAR SEMANA
# ==========================================
@alquileres_bp.route('/alquiler/semanas/<int:id>/eliminar', methods=['POST'])
@login_required
def eliminar_semana(id):
    """Elimina una semana vacía o si el usuario es admin"""
    
    try:
        semana = SemanaAlquiler.query.get_or_404(id)
        
        # Count detalles
        detalles_count = DetalleAlquilerSemanal.query.filter_by(
            semana_alquiler_id=id
        ).count()
        
        # Validar permisos
        if detalles_count > 0 and current_user.rol != 'admin':
            return jsonify({
                'success': False,
                'message': 'Solo los administradores pueden eliminar semanas con alquileres'
            }), 403
        
        # Delete detalles first (si hay)
        if detalles_count > 0:
            DetalleAlquilerSemanal.query.filter_by(
                semana_alquiler_id=id
            ).delete()
        
        # Delete semana
        db.session.delete(semana)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Semana eliminada exitosamente'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


# ==========================================
# EDITAR DETALLE COMPLETO (CON VEHÍCULO E INQUILINO)
# ==========================================
@alquileres_bp.route('/alquiler/detalles/<int:id>/editar_completo', methods=['POST'])
@login_required
def editar_detalle_completo(id):
    """Edita un detalle completo incluyendo vehículo e inquilino"""
    
    try:
        detalle = DetalleAlquilerSemanal.query.get_or_404(id)
        semana = SemanaAlquiler.query.get(detalle.semana_alquiler_id)
        
        if semana.estado != 'abierta':
            return jsonify({
                'success': False,
                'message': 'No se puede editar una semana cerrada'
            }), 400
        
        data = request.get_json()
        
        # Get new values
        nuevo_vehiculo_id = int(data.get('vehiculo_id'))
        nuevo_inquilino_id = int(data.get('inquilino_id'))
        
        # Validate vehículo change
        if nuevo_vehiculo_id != detalle.vehiculo_id:
            # Check if new vehiculo is already in this semana
            existing = DetalleAlquilerSemanal.query.filter(
                and_(
                    DetalleAlquilerSemanal.semana_alquiler_id == detalle.semana_alquiler_id,
                    DetalleAlquilerSemanal.vehiculo_id == nuevo_vehiculo_id,
                    DetalleAlquilerSemanal.id != id
                )
            ).first()
            
            if existing:
                return jsonify({
                    'success': False,
                    'message': 'Este vehículo ya está asignado en esta semana'
                }), 400
        
        # Validate inquilino change
        if nuevo_inquilino_id != detalle.inquilino_id:
            # Check if new inquilino is already in this semana
            existing_inq = DetalleAlquilerSemanal.query.filter(
                and_(
                    DetalleAlquilerSemanal.semana_alquiler_id == detalle.semana_alquiler_id,
                    DetalleAlquilerSemanal.inquilino_id == nuevo_inquilino_id,
                    DetalleAlquilerSemanal.id != id
                )
            ).first()
            
            if existing_inq:
                return jsonify({
                    'success': False,
                    'message': 'Este inquilino ya tiene un vehículo asignado en esta semana'
                }), 400
        
        # Get vehículo data
        vehiculo = Vehiculo.query.get_or_404(nuevo_vehiculo_id)
        
        # Update detalle
        detalle.vehiculo_id = nuevo_vehiculo_id
        detalle.inquilino_id = nuevo_inquilino_id
        detalle.propietario_id = vehiculo.propietario_id
        detalle.precio_semanal = data.get('precio_semanal', vehiculo.precio_semanal)
        detalle.dias_trabajo = int(data.get('dias_trabajo', 7))
        detalle.inversion_mecanica = float(data.get('inversion_mecanica', 0))
        detalle.concepto_inversion = data.get('concepto_inversion', '')
        detalle.monto_descuento = float(data.get('monto_descuento', 0))
        detalle.concepto_descuento = data.get('concepto_descuento', '')
        detalle.monto_deuda = float(data.get('monto_deuda', 0))
        detalle.banco_id = data.get('banco_id') if data.get('banco_id') else None
        
        if data.get('fecha_confirmacion_pago'):
            detalle.fecha_confirmacion_pago = datetime.strptime(
                data.get('fecha_confirmacion_pago'), '%Y-%m-%d'
            ).date()
        
        detalle.pago_confirmado = data.get('pago_confirmado', False)
        detalle.notas = data.get('notas', '')
        
        # Recalculate
        detalle.ingreso_calculado = float(detalle.precio_semanal) * int(detalle.dias_trabajo)
        detalle.nomina_empresa = detalle.ingreso_calculado * (float(detalle.porcentaje_empresa) / 100)
        detalle.nomina_final = detalle.ingreso_calculado + float(detalle.monto_deuda or 0)
        
        detalle.usuario_actualizo_id = current_user.id
        detalle.fecha_hora_actualizo = datetime.utcnow()
        
        # Update semana totals
        semana.usuario_actualizo_id = current_user.id
        semana.fecha_hora_actualizo = datetime.utcnow()
        
        # Recalculate totals
        detalles = DetalleAlquilerSemanal.query.filter_by(
            semana_alquiler_id=detalle.semana_alquiler_id
        ).all()
        
        semana.ingreso_total = sum(float(d.ingreso_calculado) for d in detalles)
        semana.total_vehiculos = len(detalles)
        
        # Recalculate unique counts
        semana.total_socios = db.session.query(
            func.count(func.distinct(DetalleAlquilerSemanal.propietario_id))
        ).filter_by(semana_alquiler_id=detalle.semana_alquiler_id).scalar()
        
        semana.total_inquilinos = db.session.query(
            func.count(func.distinct(DetalleAlquilerSemanal.inquilino_id))
        ).filter_by(semana_alquiler_id=detalle.semana_alquiler_id).scalar()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Detalle actualizado correctamente'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500
"""
En tu app/__init__.py, agregar:

from app.routes.alquileres_routes import alquileres_bp
app.register_blueprint(alquileres_bp)
"""
