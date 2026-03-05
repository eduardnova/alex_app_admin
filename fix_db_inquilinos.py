from app import create_app, db
from sqlalchemy import text

app = create_app()

with app.app_context():
    try:
        # Inquilinos
        print("Modificando tabla inquilinos...")
        db.session.execute(text("ALTER TABLE inquilinos ADD COLUMN cedula TEXT UNIQUE;"))
        db.session.execute(text("ALTER TABLE inquilinos ADD COLUMN cedula_path TEXT DEFAULT NULL;"))
        db.session.execute(text("ALTER TABLE inquilinos ADD COLUMN licencia TEXT UNIQUE;"))
        db.session.execute(text("ALTER TABLE inquilinos ADD COLUMN licencia_path TEXT DEFAULT NULL;"))
        print("Tabla inquilinos modificada con exito.")
    except Exception as e:
        print(f"Error modificando inquilinos (quizas las columnas ya existan): {e}")

    try:
        # Garantes Inquilinos
        print("Modificando tabla garantes_inquilinos...")
        db.session.execute(text("ALTER TABLE garantes_inquilinos ADD COLUMN cedula TEXT;"))
        db.session.execute(text("ALTER TABLE garantes_inquilinos ADD COLUMN cedula_path TEXT;"))
        print("Tabla garantes_inquilinos modificada con exito.")
    except Exception as e:
        print(f"Error modificando garantes_inquilinos (quizas las columnas ya existan): {e}")

    try:
        # Referencias Inquilinos
        print("Modificando tabla referencias_inquilinos...")
        db.session.execute(text("ALTER TABLE referencias_inquilinos ADD COLUMN cedula TEXT;"))
        db.session.execute(text("ALTER TABLE referencias_inquilinos ADD COLUMN cedula_path TEXT;"))
        print("Tabla referencias_inquilinos modificada con exito.")
    except Exception as e:
        print(f"Error modificando referencias_inquilinos (quizas las columnas ya existan): {e}")

    db.session.commit()
    print("Migracion manual completada y guardada.")
