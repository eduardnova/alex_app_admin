from app import create_app, db
from sqlalchemy import text

app = create_app()

with app.app_context():
    try:
        print("Añadiendo AUTO_INCREMENT a la tabla inquilinos...")
        db.session.execute(text("ALTER TABLE inquilinos MODIFY COLUMN id INT AUTO_INCREMENT;"))
        db.session.commit()
        print("  -> Exito")
    except Exception as e:
        db.session.rollback()
        print(f"  -> Error: {e}")
