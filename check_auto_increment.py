from app import create_app, db
from sqlalchemy import text

app = create_app()

with app.app_context():
    query = """
    SELECT TABLE_NAME, COLUMN_NAME
    FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_SCHEMA = 'alquiler_vehiculos'
      AND COLUMN_NAME = 'id'
      AND EXTRA NOT LIKE '%auto_increment%';
    """
    
    result = db.session.execute(text(query)).fetchall()
    
    print("Tablas sin AUTO_INCREMENT en su ID:")
    if not result:
        print("¡Todas las tablas tienen AUTO_INCREMENT!")
    else:
        for row in result:
            print(f"- {row[0]}")
