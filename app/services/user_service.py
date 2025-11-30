"""
User Service - Business logic for user management
"""
from app import db
from app.models import (
    Usuario, VehiculoMarcaModelo, EstadoAlquiler, MetodoPago, 
    TipoCuenta, Banco, Parentesco, TipoTrabajo, Mecanico, Pieza
)
from flask import current_app


def create_user(username, password, email, nombre, apellido, rol='user', telefono=None):
    """Create a new user"""
    try:
        # Check if user exists
        if Usuario.query.filter_by(username=username).first():
            current_app.logger.error(f"Username {username} already exists")
            return None
        
        if Usuario.query.filter_by(email=email).first():
            current_app.logger.error(f"Email {email} already exists")
            return None
        
        # Create user
        user = Usuario(
            username=username,
            nombre=nombre,
            apellido=apellido,
            email=email,
            telefono=telefono,
            rol=rol,
            activo=True
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        current_app.logger.info(f"User {username} created successfully")
        return user
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error creating user: {str(e)}")
        return None


def get_user_by_email(email):
    """Get user by email"""
    return Usuario.query.filter_by(email=email).first()


def get_user_by_username(username):
    """Get user by username"""
    return Usuario.query.filter_by(username=username).first()


def verify_password(user, password):
    """Verify user password"""
    if user:
        return user.check_password(password)
    return False


def assign_role(user, role):
    """Assign role to user"""
    try:
        if role not in ['admin', 'user', 'mechanic']:
            return False
        
        user.rol = role
        db.session.commit()
        return True
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error assigning role: {str(e)}")
        return False


def create_initial_data():
    """Create initial data for the database"""
    try:
        # Create admin user
        admin = Usuario.query.filter_by(username='admin').first()
        if not admin:
            admin = create_user(
                username='admin',
                password='admin123',
                email='admin@alexrentacar.com',
                nombre='Administrador',
                apellido='Sistema',
                rol='admin',
                telefono='809-000-0000'
            )
            current_app.logger.info("Admin user created")
        
        # Create regular user
        user = Usuario.query.filter_by(username='user1').first()
        if not user:
            user = create_user(
                username='user1',
                password='user123',
                email='user@alexrentacar.com',
                nombre='Usuario',
                apellido='Prueba',
                rol='user',
                telefono='809-111-1111'
            )
            current_app.logger.info("Regular user created")
        
        user_id = admin.id if admin else 1
        
        # Create Estados de Alquiler
        estados = [
            ('Pendiente', 'Alquiler pendiente de confirmación'),
            ('En curso', 'Alquiler activo en progreso'),
            ('Validado', 'Alquiler validado y confirmado'),
            ('Pausado', 'Alquiler temporalmente pausado'),
            ('Finalizado', 'Alquiler completado exitosamente'),
            ('Cancelado', 'Alquiler cancelado antes de iniciar'),
            ('Vencido', 'Alquiler vencido con deuda pendiente')
        ]
        
        for nombre, desc in estados:
            if not EstadoAlquiler.query.filter_by(nombre=nombre).first():
                estado = EstadoAlquiler(
                    nombre=nombre,
                    descripcion=desc,
                    usuario_registro_id=user_id,
                    usuario_actualizo_id=user_id
                )
                db.session.add(estado)
        
        # Create Métodos de Pago
        metodos = [
            ('Efectivo', 'Pago en efectivo'),
            ('Transferencia', 'Transferencia bancaria'),
            ('Tarjeta débito', 'Pago con tarjeta de débito'),
            ('Tarjeta crédito', 'Pago con tarjeta de crédito'),
            ('Depósito', 'Depósito bancario'),
            ('Cheque', 'Pago con cheque')
        ]
        
        for nombre, desc in metodos:
            if not MetodoPago.query.filter_by(nombre=nombre).first():
                metodo = MetodoPago(
                    nombre=nombre,
                    descripcion=desc,
                    usuario_registro_id=user_id,
                    usuario_actualizo_id=user_id
                )
                db.session.add(metodo)
        
        # Create Tipos de Cuentas
        tipos_cuenta = [
            ('Ahorros', 'Cuenta de ahorros'),
            ('Corriente', 'Cuenta corriente'),
            ('Nómina', 'Cuenta de nómina')
        ]
        
        for tipo, desc in tipos_cuenta:
            if not TipoCuenta.query.filter_by(tipo_cuenta=tipo).first():
                tipo_cuenta = TipoCuenta(
                    tipo_cuenta=tipo,
                    descripcion=desc,
                    usuario_registro_id=user_id,
                    usuario_actualizo_id=user_id
                )
                db.session.add(tipo_cuenta)
        
        db.session.commit()
        
        # Create Parentescos
        parentescos = [
            'Padre', 'Madre', 'Hermano', 'Hermana', 'Hijo', 'Hija',
            'Esposo', 'Esposa', 'Primo', 'Prima', 'Tío', 'Tía',
            'Sobrino', 'Sobrina', 'Abuelo', 'Abuela', 'Nieto', 'Nieta',
            'Cuñado', 'Cuñada', 'Suegro', 'Suegra', 'Yerno', 'Nuera',
            'Amigo', 'Conocido', 'Compañero de trabajo', 'Jefe', 'Otro'
        ]
        
        for p in parentescos:
            if not Parentesco.query.filter_by(parentesco=p).first():
                parentesco = Parentesco(
                    parentesco=p,
                    usuario_registro_id=user_id,
                    usuario_actualizo_id=user_id
                )
                db.session.add(parentesco)
        
        # Create Marcas y Modelos
        marcas_modelos = [
            ('Toyota', 'Corolla', 'Sedán', 'Sedán compacto'),
            ('Toyota', 'Yaris', 'Sedán', 'Sedán subcompacto'),
            ('Toyota', 'RAV4', 'SUV', 'SUV compacta'),
            ('Honda', 'Civic', 'Sedán', 'Sedán compacto'),
            ('Honda', 'CR-V', 'SUV', 'SUV compacta'),
            ('Hyundai', 'Elantra', 'Sedán', 'Sedán compacto'),
            ('Nissan', 'Sentra', 'Sedán', 'Sedán compacto'),
            ('Kia', 'Rio', 'Sedán', 'Sedán subcompacto'),
            ('Mitsubishi', 'Lancer', 'Sedán', 'Sedán compacto'),
            ('Suzuki', 'Swift', 'Hatchback', 'Compacto hatchback')
        ]
        
        for marca, modelo, tipo, desc in marcas_modelos:
            if not VehiculoMarcaModelo.query.filter_by(
                marca=marca, modelo=modelo
            ).first():
                mm = VehiculoMarcaModelo(
                    marca=marca,
                    modelo=modelo,
                    tipo=tipo,
                    descripcion=desc,
                    usuario_registro_id=user_id,
                    usuario_actualizo_id=user_id
                )
                db.session.add(mm)
        
        # Create Tipos de Trabajos
        tipos_trabajos = [
            ('Mantenimiento preventivo', 'Revisión general programada'),
            ('Cambio de aceite', 'Cambio de aceite y filtro'),
            ('Reparación de motor', 'Reparación o ajuste de motor'),
            ('Reparación de frenos', 'Cambio o ajuste de sistema de frenos'),
            ('Cambio de neumáticos', 'Reemplazo de neumáticos'),
            ('Reparación eléctrica', 'Reparación de sistema eléctrico'),
            ('Alineación y balanceo', 'Alineación de ruedas y balanceo')
        ]
        
        for nombre, desc in tipos_trabajos:
            if not TipoTrabajo.query.filter_by(nombre=nombre).first():
                tipo = TipoTrabajo(
                    nombre=nombre,
                    descripcion=desc,
                    usuario_registro_id=user_id,
                    usuario_actualizo_id=user_id
                )
                db.session.add(tipo)
        
        db.session.commit()
        current_app.logger.info("Initial data created successfully")
        return True
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error creating initial data: {str(e)}")
        return False