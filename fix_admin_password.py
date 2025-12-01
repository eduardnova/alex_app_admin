"""Script para reparar la contraseña del usuario admin"""
from app import create_app, db
from app.models import Usuario

def fix_admin_password():
    app = create_app()
    
    with app.app_context():
        # Buscar el usuario admin
        admin = Usuario.query.filter_by(username='admin').first()
        
        if not admin:
            print("❌ Usuario 'admin' no encontrado")
            return
        
        print(f"✓ Usuario encontrado: {admin.username}")
        print(f"  - Nombre: {admin.nombre}")
        print(f"  - Email: {admin.email}")
        print(f"  - Hash actual: {admin.password[:50]}...")
        
        # Establecer nueva contraseña
        nueva_password = input("\n🔑 Ingresa la nueva contraseña para admin: ")
        
        if len(nueva_password) < 6:
            print("❌ La contraseña debe tener al menos 6 caracteres")
            return
        
        # Actualizar contraseña
        admin.set_password(nueva_password)
        db.session.commit()
        
        print(f"\n✅ Contraseña actualizada exitosamente!")
        print(f"   Nuevo hash: {admin.password[:50]}...")

if __name__ == '__main__':
    fix_admin_password()