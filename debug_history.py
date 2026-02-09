from app import create_app, db
from app.models import HistoricoVehiculo, Vehiculo

app = create_app()

with app.app_context():
    print("Checking HistoricoVehiculo table...")
    count = HistoricoVehiculo.query.count()
    print(f"Total records in HistoricoVehiculo: {count}")
    
    if count > 0:
        print("\nLast 5 records:")
        records = HistoricoVehiculo.query.order_by(HistoricoVehiculo.fecha_hora_operacion.desc()).limit(5).all()
        for r in records:
            print(f"ID Hist: {r.id_historico} | Vehiculo ID: {r.id} | Op: {r.tipo_operacion} | Fecha: {r.fecha_hora_operacion}")
            
    # Check if there are any vehicles
    v_count = Vehiculo.query.count()
    print(f"\nTotal vehicles: {v_count}")
