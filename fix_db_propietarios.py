from app import create_app, db
from sqlalchemy import text

app = create_app()

with app.app_context():
    queries = [
        "ALTER TABLE propietarios ADD COLUMN metodo_pago_id INT DEFAULT NULL;",
        "ALTER TABLE propietarios ADD COLUMN banco_nombre TEXT DEFAULT NULL;",
        "ALTER TABLE propietarios ADD COLUMN numero_cuenta TEXT DEFAULT NULL;",
        "ALTER TABLE propietarios ADD COLUMN tipo_cuenta_id INT DEFAULT NULL;",
        "ALTER TABLE propietarios ADD CONSTRAINT fk_prop_metodo_pago FOREIGN KEY (metodo_pago_id) REFERENCES metodos_pago(id) ON DELETE SET NULL;",
        "ALTER TABLE propietarios ADD CONSTRAINT fk_prop_tipo_cuenta FOREIGN KEY (tipo_cuenta_id) REFERENCES tipo_cuentas(id) ON DELETE SET NULL;"
    ]

    for q in queries:
        try:
            print(f"Ejecutando: {q}")
            db.session.execute(text(q))
            db.session.commit()
            print("  -> Exito")
        except Exception as e:
            db.session.rollback()
            print(f"  -> Omitido o Fallo: {e}")

    print("Migracion de propietarios completada.")
