from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from datetime import datetime
from sqlalchemy import func, and_, or_
from app import db
from app.models import (
    Deduccion, Vehiculo, Propietario, SemanaAlquiler, 
    DetalleAlquilerSemanal, Usuario
)
import os
from werkzeug.utils import secure_filename

deducciones_bp = Blueprint('deducciones', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'pdf'}
UPLOAD_FOLDER = 'app/static/uploads/deducciones'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_evidence(file, prefix):
    if file and file.filename and allowed_file(file.filename):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = secure_filename(file.filename)
        name, ext = os.path.splitext(filename)
        unique_filename = f"{prefix}_{name}_{timestamp}{ext}"
        filepath = os.path.join(UPLOAD_FOLDER, unique_filename)
        try:
            file.save(filepath)
            return f'uploads/deducciones/{unique_filename}'
        except IOError as e:
            print(f"Error al guardar archivo: {str(e)}")
            return None
    return None

def delete_evidence(path):
    if path:
        full_path = os.path.join('app/static', path)
        if os.path.exists(full_path):
            try:
                os.remove(full_path)
            except IOError:
                pass

@deducciones_bp.route('/deducciones')
@login_required
def index():
    propietarios_list = Propietario.query.all()
    propietarios = sorted(propietarios_list, key=lambda x: x.nombre_apellido if x.nombre_apellido else "")
    vehiculos = Vehiculo.query.all()
    # Sort simple list of vehicles
    vehiculos_sorted = sorted(vehiculos, key=lambda x: x.placa)
    semanas = SemanaAlquiler.query.order_by(SemanaAlquiler.fecha_inicio.desc()).all()
    
    return render_template('modulos/deducciones.html',
                         propietarios=propietarios,
                         vehiculos=vehiculos_sorted,
                         semanas=semanas)

@deducciones_bp.route('/deducciones/api/list')
@login_required
def api_list():
    try:
        # Filters
        propietario_id = request.args.get('propietario_id')
        vehiculo_id = request.args.get('vehiculo_id')
        semana_id = request.args.get('semana_id')
        fecha_inicio_str = request.args.get('fecha_inicio')
        fecha_fin_str = request.args.get('fecha_fin')
        estado = request.args.get('estado')
        
        # Parse Dates
        fecha_inicio = datetime.strptime(fecha_inicio_str, '%Y-%m-%d').date() if fecha_inicio_str else None
        fecha_fin = datetime.strptime(fecha_fin_str, '%Y-%m-%d').date() if fecha_fin_str else None
        
        # --- 1. Fetch Deducciones (the new table) ---
        query_d = Deduccion.query
        
        if propietario_id:
            query_d = query_d.filter_by(propietario_id=propietario_id)
        if vehiculo_id:
            query_d = query_d.filter_by(vehiculo_id=vehiculo_id)
        if semana_id:
            query_d = query_d.filter_by(semana_alquiler_id=semana_id)
        if estado:
            query_d = query_d.filter_by(estado=estado)
        if fecha_inicio:
            query_d = query_d.filter(Deduccion.fecha >= fecha_inicio)
        if fecha_fin:
            query_d = query_d.filter(Deduccion.fecha <= fecha_fin)
            
        deducciones_db = query_d.all()
        
        # --- 2. Fetch TrabajoVehiculo (existing mechanical works) ---
        # Note: We need to import TrabajoVehiculo
        from app.models import TrabajoVehiculo
        
        query_t = TrabajoVehiculo.query
        
        if semana_id:
            semana = SemanaAlquiler.query.get(semana_id)
            if semana:
                query_t = query_t.filter(
                    TrabajoVehiculo.fecha_inicio >= semana.fecha_inicio,
                    TrabajoVehiculo.fecha_inicio <= semana.fecha_fin
                )
        
        if fecha_inicio:
            query_t = query_t.filter(TrabajoVehiculo.fecha_inicio >= fecha_inicio)
        if fecha_fin:
            query_t = query_t.filter(TrabajoVehiculo.fecha_inicio <= fecha_fin)
            
        trabajos_db = query_t.all()

        # --- 3. Fetch DetalleAlquilerSemanal (Ingresos) ---
        query_i = DetalleAlquilerSemanal.query.join(SemanaAlquiler)
        
        if propietario_id:
            query_i = query_i.filter(DetalleAlquilerSemanal.propietario_id == propietario_id)
        if vehiculo_id:
            query_i = query_i.filter(DetalleAlquilerSemanal.vehiculo_id == vehiculo_id)
        if semana_id:
            query_i = query_i.filter(DetalleAlquilerSemanal.semana_alquiler_id == semana_id)
        if fecha_inicio:
            query_i = query_i.filter(SemanaAlquiler.fecha_fin >= fecha_inicio)
        if fecha_fin:
            query_i = query_i.filter(SemanaAlquiler.fecha_fin <= fecha_fin)
            
        ingresos_db = query_i.all()
        
        # --- 4. Merge and Group ---
        grouped_data = {}
        
        # Helper to get/init vehicle group
        def get_group(vid, vehiculo_obj, propietario_obj):
            if vid not in grouped_data:
                marca = vehiculo_obj.marca_modelo.marca if vehiculo_obj.marca_modelo else ""
                modelo = vehiculo_obj.marca_modelo.modelo if vehiculo_obj.marca_modelo else ""
                # Handle encrypted owner name safe access
                prop_name = 'N/A'
                if propietario_obj:
                    prop_name = propietario_obj.nombre_apellido or 'N/A' # Decrypts automatically
                    
                grouped_data[vid] = {
                    'vehiculo_info': {
                        'id': vehiculo_obj.id,
                        'placa': vehiculo_obj.placa,
                        'marca': marca,
                        'modelo': modelo,
                        'propietario_nombre': prop_name
                    },
                    'deducciones': [],
                    'total_deducciones': 0.0
                }
            return grouped_data[vid]

        # Process Deducciones (NEGATIVAS)
        for d in deducciones_db:
            group = get_group(d.vehiculo_id, d.vehiculo, d.propietario)
            
            # NEGATIVE VALUE
            monto_negativo = float(d.monto) * -1
            
            deduction_dict = {
                'id': d.id,
                'source': 'deduccion', # Flag source
                'fecha': d.fecha.strftime('%d/%m/%Y'),
                'semana': f"Semana {d.fecha.isocalendar()[1]} ({d.fecha.year})",
                'concepto': d.concepto,
                'tipo': d.tipo_deduccion,
                'monto': monto_negativo,
                'estado': d.estado,
                'evidencia_path': d.evidencia_path
            }
            group['deducciones'].append(deduction_dict)
            group['total_deducciones'] += monto_negativo
            
        # Process Trabajos (NEGATIVAS)
        for t in trabajos_db:
            # Check owner filter
            if propietario_id and str(t.vehiculo.propietario_id) != str(propietario_id):
                continue
                
            group = get_group(t.vehiculo_id, t.vehiculo, t.vehiculo.propietario)
            
            # Map status
            estado_mapped = 'aplicada' if t.estado == 'completado' else 'pendiente'
            if estado and estado != estado_mapped:
                continue
                
            # NEGATIVE VALUE
            monto_negativo = float(t.costo or 0) * -1

            deduction_dict = {
                'id': t.id,
                'source': 'trabajo', # Flag source
                'fecha': t.fecha_inicio.strftime('%d/%m/%Y'),
                'semana': f"Semana {t.fecha_inicio.isocalendar()[1]} ({t.fecha_inicio.year})",
                'concepto': t.descripcion if t.descripcion == 'Lavado Automático al Ingreso' else f"Trabajo Mecánico: {t.descripcion or ''}",
                'tipo': t.tipo_trabajo.nombre if t.tipo_trabajo else 'Mantenimiento',
                'monto': monto_negativo,
                'estado': estado_mapped,
                'evidencia_path': None # Or t.evidencia if exists
            }
            group['deducciones'].append(deduction_dict)
            group['total_deducciones'] += monto_negativo

        # Process Ingresos (POSITIVOS)
        for i in ingresos_db:
            # Check owner filter just in case, though query handles it
            
            # Need to get owner obj from relation if lazily loaded or direct
            vehiculo_obj = Vehiculo.query.get(i.vehiculo_id) # Ensure we have it
            propietario_obj = Propietario.query.get(i.propietario_id)
            semana_obj = SemanaAlquiler.query.get(i.semana_alquiler_id)
            
            group = get_group(i.vehiculo_id, vehiculo_obj, propietario_obj)
            
            monto_positivo = float(i.ingreso_calculado or 0)
            
            deduction_dict = {
                'id': i.id,
                'source': 'nomina', # Flag source
                'fecha': semana_obj.fecha_fin.strftime('%d/%m/%Y'),
                'semana': f"Semana {semana_obj.numero_semana} ({semana_obj.anio})",
                'concepto': 'INGRESOS GENERADO EN DIAS DE TABAJO SEMANA',
                'tipo': 'Ingreso Alquiler',
                'monto': monto_positivo,
                'estado': 'generado',
                'evidencia_path': None
            }
            group['deducciones'].append(deduction_dict)
            group['total_deducciones'] += monto_positivo
            
        # Convert to list and sort groups? or sort inner lists?
        # Let's sort inner lists by date
        for vid, group in grouped_data.items():
            group['deducciones'].sort(key=lambda x: datetime.strptime(x['fecha'], '%d/%m/%Y'), reverse=True)
            
        result_list = list(grouped_data.values())
        # Sort by Owner Name then Vehicle Placa
        result_list.sort(key=lambda x: (x['vehiculo_info']['propietario_nombre'] or '', x['vehiculo_info']['placa']))
        
        # Calculate totals
        global_total = sum(item['total_deducciones'] for item in result_list)
        
        return jsonify({
            'success': True,
            'data': result_list,
            'global_total': global_total
        })
        
    except Exception as e:
        print(f"Error in deducciones list: {str(e)}")
        # Print traceback for debugging
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500

@deducciones_bp.route('/deducciones/crear', methods=['POST'])
@login_required
def crear_deduccion():
    try:
        vehiculo_id = request.form.get('vehiculo_id')
        vehiculo = Vehiculo.query.get(vehiculo_id)
        if not vehiculo:
            flash('Vehículo no válido', 'error')
            return redirect(url_for('deducciones.index'))
            
        semana_id = request.form.get('semana_id') # Optional
        concepto = request.form.get('concepto')
        monto = request.form.get('monto')
        fecha = request.form.get('fecha')
        tipo = request.form.get('tipo_deduccion')
        estado = request.form.get('estado')
        
        evidencia = request.files.get('evidencia')
        evidencia_path = None
        if evidencia:
            evidencia_path = save_evidence(evidencia, 'deduccion')
            
        nueva_deduccion = Deduccion(
            vehiculo_id=vehiculo_id,
            propietario_id=vehiculo.propietario_id,
            semana_alquiler_id=semana_id if semana_id else None,
            concepto=concepto,
            monto=monto,
            fecha=datetime.strptime(fecha, '%Y-%m-%d').date(),
            tipo_deduccion=tipo,
            estado=estado,
            evidencia_path=evidencia_path,
            usuario_registro_id=current_user.id
        )
        
        db.session.add(nueva_deduccion)
        db.session.commit()
        
        flash('Deducción registrada exitosamente', 'success')
        return redirect(url_for('deducciones.index'))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error al crear deducción: {str(e)}', 'error')
        return redirect(url_for('deducciones.index'))

@deducciones_bp.route('/deducciones/<int:id>/editar', methods=['POST'])
@login_required
def editar_deduccion(id):
    try:
        deduccion = Deduccion.query.get_or_404(id)
        
        deduccion.concepto = request.form.get('concepto')
        deduccion.monto = request.form.get('monto')
        deduccion.fecha = datetime.strptime(request.form.get('fecha'), '%Y-%m-%d').date()
        deduccion.tipo_deduccion = request.form.get('tipo_deduccion')
        deduccion.estado = request.form.get('estado')
        
        # Semana update
        semana_id = request.form.get('semana_id')
        deduccion.semana_alquiler_id = semana_id if semana_id else None
        
        # Vehicle update (if allowed to change vehicle, also update owner)
        new_vehiculo_id = request.form.get('vehiculo_id')
        if new_vehiculo_id and int(new_vehiculo_id) != deduccion.vehiculo_id:
            new_vehiculo = Vehiculo.query.get(new_vehiculo_id)
            if new_vehiculo:
                deduccion.vehiculo_id = new_vehiculo.id
                deduccion.propietario_id = new_vehiculo.propietario_id
        
        # Evidence handling
        evidencia = request.files.get('evidencia')
        if evidencia and evidencia.filename:
            if deduccion.evidencia_path:
                delete_evidence(deduccion.evidencia_path)
            deduccion.evidencia_path = save_evidence(evidencia, 'deduccion')
        elif request.form.get('borrar_evidencia') == 'true':
             if deduccion.evidencia_path:
                delete_evidence(deduccion.evidencia_path)
             deduccion.evidencia_path = None
             
        deduccion.usuario_actualizo_id = current_user.id
        deduccion.fecha_hora_actualizo = datetime.utcnow()
        
        db.session.commit()
        flash('Deducción actualizada', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error al actualizar: {str(e)}', 'error')
        
    return redirect(url_for('deducciones.index'))

@deducciones_bp.route('/deducciones/<int:id>/eliminar', methods=['POST'])
@login_required
def eliminar_deduccion(id):
    try:
        deduccion = Deduccion.query.get_or_404(id)
        
        if deduccion.evidencia_path:
            delete_evidence(deduccion.evidencia_path)
            
        db.session.delete(deduccion)
        db.session.commit()
        flash('Deducción eliminada', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar: {str(e)}', 'error')
        
    return redirect(url_for('deducciones.index'))

@deducciones_bp.route('/deducciones/<int:id>')
@login_required
def get_deduccion(id):
    deduccion = Deduccion.query.get_or_404(id)
    return jsonify({
        'success': True,
        'data': {
            'id': deduccion.id,
            'vehiculo_id': deduccion.vehiculo_id,
            'semana_id': deduccion.semana_alquiler_id,
            'concepto': deduccion.concepto,
            'monto': float(deduccion.monto),
            'fecha': deduccion.fecha.strftime('%Y-%m-%d'),
            'tipo': deduccion.tipo_deduccion,
            'estado': deduccion.estado,
            'evidencia_path': deduccion.evidencia_path
        }
    })
