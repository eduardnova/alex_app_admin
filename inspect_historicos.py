from app import create_app, db
from sqlalchemy import text

app = create_app()

with app.app_context():
    historico_tables = [
        'historico_contratos',
        'historico_depositos',
        'historico_porcentajes_ganancia',
        'historico_semanas_alquiler'
    ]
    for ht in historico_tables:
        try:
            res = db.session.execute(text(f"SHOW CREATE TABLE {ht};")).fetchone()
            print(f"\n--- SHOW CREATE TABLE {ht} ---")
            print(res[1])
        except Exception as e:
            print(f"Error checking {ht}: {e}")
