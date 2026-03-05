from app import create_app, db
from sqlalchemy import text

app = create_app()

with app.app_context():
    print("Forzando la verificacion y creacion exhaustiva de todas las tablas (incluyendo historico_inquilinos)...")
    
    # Asegurarnos de que SQLAlchemy refleje todos los modelos y cree los que falten.
    db.create_all()
    
    # Verificar especificamente si historico_inquilinos se creo
    try:
        res = db.session.execute(text("SHOW CREATE TABLE historico_inquilinos;")).fetchone()
        print("✅ La tabla historico_inquilinos existe y esta lista.")
    except Exception as e:
        print("❌ Error: Todavia falta historico_inquilinos. Intentando creacion manual si es necesario...", e)
        
    print("Proceso completado.")
