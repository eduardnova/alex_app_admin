from app import create_app, db

app = create_app()

with app.app_context():
    print("Verificando y creando tablas faltantes en la base de datos (por ejemplo, historico_propietarios)...")
    db.create_all()
    print("✅ Tablas faltantes creadas con exito.")
