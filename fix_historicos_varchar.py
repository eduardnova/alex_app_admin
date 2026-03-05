from app import create_app, db
from sqlalchemy import text

app = create_app()

with app.app_context():
    # Encontrar todas las columnas `varchar` en tablas `historico_%` y cambiarlas a `TEXT`
    query = text('''
        SELECT TABLE_NAME, COLUMN_NAME, CHARACTER_MAXIMUM_LENGTH
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = 'alquiler_vehiculos'
          AND TABLE_NAME LIKE 'historico_%'
          AND DATA_TYPE = 'varchar';
    ''')
    
    columnas_a_modificar = db.session.execute(query).fetchall()
    
    print(f"Encontradas {len(columnas_a_modificar)} columnas varchar en tablas historicas para migrar a TEXT.")
    
    for table_name, column_name, max_len in columnas_a_modificar:
        alter_query = text(f"ALTER TABLE {table_name} MODIFY COLUMN {column_name} TEXT;")
        try:
            db.session.execute(alter_query)
            print(f"✅ {table_name}.{column_name} cambiado a TEXT.")
        except Exception as e:
            print(f"❌ Error modificando {table_name}.{column_name}: {e}")
            
    db.session.commit()
    print("Proceso de base de datos completado.")
