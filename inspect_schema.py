from app import create_app, db
from sqlalchemy import text

app = create_app()

with app.app_context():
    try:
        res1 = db.session.execute(text("SHOW CREATE TABLE inquilinos;")).fetchone()
        print("--- SHOW CREATE TABLE inquilinos ---")
        print(res1[1])
        
        res2 = db.session.execute(text("SHOW CREATE TABLE propietarios;")).fetchone()
        print("\n--- SHOW CREATE TABLE propietarios ---")
        print(res2[1])
    except Exception as e:
        print(e)
