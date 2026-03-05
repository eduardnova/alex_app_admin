from app import create_app, db
from sqlalchemy import text

app = create_app()

with app.app_context():
    queries = [
        "ALTER TABLE inquilinos ADD COLUMN cedula TEXT UNIQUE;",
        "ALTER TABLE inquilinos ADD COLUMN cedula_path TEXT DEFAULT NULL;",
        "ALTER TABLE inquilinos ADD COLUMN licencia TEXT UNIQUE;",
        "ALTER TABLE inquilinos ADD COLUMN licencia_path TEXT DEFAULT NULL;",
        "ALTER TABLE garantes_inquilinos ADD COLUMN cedula TEXT;",
        "ALTER TABLE garantes_inquilinos ADD COLUMN cedula_path TEXT;",
        "ALTER TABLE referencias_inquilinos ADD COLUMN cedula TEXT;",
        "ALTER TABLE referencias_inquilinos ADD COLUMN cedula_path TEXT;"
    ]

    for q in queries:
        try:
            print(f"Ejecutando: {q}")
            db.session.execute(text(q))
            db.session.commit()
            print("  -> Exito")
        except Exception as e:
            db.session.rollback()
            print(f"  -> Omitido (posiblemente la columna ya existe)")

    print("Migracion manual columna por columna completada.")
