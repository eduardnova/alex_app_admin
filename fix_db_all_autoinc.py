from app import create_app, db
from sqlalchemy import text

app = create_app()

with app.app_context():
    tables_to_fix = [
        'historico_contratos',
        'historico_depositos',
        'historico_porcentajes_ganancia',
        'historico_semanas_alquiler',
        'inquilinos',
        'parentescos',
        'propietarios'
    ]
    
    for table in tables_to_fix:
        try:
            print(f"Modificando tabla {table} para agregar PRIMARY KEY y AUTO_INCREMENT...")
            
            # 1. Aseguramos de que ID sea Primary Key (si no lo es, esto la añade)
            # Primero intentamos dropear la llave primaria vieja por si acaso
            try:
                db.session.execute(text(f"ALTER TABLE {table} DROP PRIMARY KEY;"))
            except Exception:
                pass # Si no hay primary key vieja, ignoramos
            
            # Ahora le añadimos el PRIMARY KEY
            try:
                db.session.execute(text(f"ALTER TABLE {table} ADD PRIMARY KEY (id);"))
            except Exception as e:
                print(f"  -> Error al agregar PRIMARY KEY (tal vez ya lo era): {e}")

            # 2. Le añadimos el AUTO_INCREMENT
            # Necesitamos saber el tipo. Usualmente es INT
            db.session.execute(text(f"ALTER TABLE {table} MODIFY COLUMN id INT AUTO_INCREMENT;"))
            
            db.session.commit()
            print(f"  -> {table} arreglada con exito.")
        except Exception as e:
            db.session.rollback()
            print(f"  -> Error fatal procesando {table}: {e}")
            
    print("\nProceso global de reparacion completado.")
