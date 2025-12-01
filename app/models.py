"""
Database Models for AlexRentaCar Admin App
Maps SQL schema to SQLAlchemy ORM with encryption support
"""
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from cryptography.fernet import Fernet
from flask import current_app


# Encryption helper functions
def get_cipher():
    """Get Fernet cipher instance"""
    return Fernet(current_app.config['FERNET_KEY'])


def encrypt_data(data):
    """Encrypt sensitive data"""
    if data is None:
        return None
    cipher = get_cipher()
    return cipher.encrypt(data.encode()).decode()


def decrypt_data(encrypted_data):
    """Decrypt sensitive data"""
    if encrypted_data is None:
        return None
    try:
        cipher = get_cipher()
        return cipher.decrypt(encrypted_data.encode()).decode()
    except Exception:
        return None


# ==================== TABLA: usuarios ====================
class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    password = db.Column(db.String(255), nullable=False)
    rol = db.Column(db.Enum('admin', 'user', 'mechanic'), nullable=False, default='user')
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False, index=True)
    telefono = db.Column(db.String(20))
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    activo = db.Column(db.Boolean, default=True)
    
    # Relationships
    propietarios = db.relationship('Propietario', foreign_keys='Propietario.usuario_id', 
                                   backref='usuario_cuenta', lazy='dynamic')
    
    def set_password(self, password):
        """Hash and set password"""
        self.password = generate_password_hash(password)
    
    def check_password(self, password):
        """Verify password"""
        if not self.password or self.password == '':  # ← DEBE ESTAR AQUÍ
            return False
        return check_password_hash(self.password, password)
    
    def __repr__(self):
        return f'<Usuario {self.username} ({self.rol})>'


# ==================== TABLA: registro_acceso ====================
class RegistroAcceso(db.Model):
    __tablename__ = 'registro_acceso'
    
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id', ondelete='CASCADE'), 
                           nullable=False, index=True)
    fecha_hora = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    accion = db.Column(db.String(255), nullable=False)
    ip_address = db.Column(db.String(45))
    detalles = db.Column(db.Text)
    
    usuario = db.relationship('Usuario', backref='accesos')
    
    def __repr__(self):
        return f'<RegistroAcceso {self.usuario_id} - {self.accion}>'


# ==================== TABLA: vehiculo_marca_modelo ====================
class VehiculoMarcaModelo(db.Model):
    __tablename__ = 'vehiculo_marca_modelo'
    
    id = db.Column(db.Integer, primary_key=True)
    marca = db.Column(db.String(50), nullable=False, index=True)
    modelo = db.Column(db.String(50), nullable=False, index=True)
    tipo = db.Column(db.String(20), nullable=False)
    logo_path = db.Column(db.String(255))
    descripcion = db.Column(db.Text)
    usuario_registro_id = db.Column(db.Integer, 
                                    db.ForeignKey('usuarios.id', ondelete='CASCADE'), 
                                    nullable=False)
    fecha_hora_registro = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_actualizo_id = db.Column(db.Integer, 
                                     db.ForeignKey('usuarios.id', ondelete='CASCADE'), 
                                     nullable=False)
    fecha_hora_actualizo = db.Column(db.DateTime, default=datetime.utcnow, 
                                     onupdate=datetime.utcnow)
    
    usuario_registro = db.relationship('Usuario', foreign_keys=[usuario_registro_id])
    usuario_actualizo = db.relationship('Usuario', foreign_keys=[usuario_actualizo_id])
    vehiculos = db.relationship('Vehiculo', backref='marca_modelo', lazy='dynamic')
    
    def __repr__(self):
        return f'<VehiculoMarcaModelo {self.marca} {self.modelo}>'


# ==================== TABLA: estados_alquiler ====================
class EstadoAlquiler(db.Model):
    __tablename__ = 'estados_alquiler'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), unique=True, nullable=False, index=True)
    descripcion = db.Column(db.Text)
    usuario_registro_id = db.Column(db.Integer, 
                                    db.ForeignKey('usuarios.id', ondelete='CASCADE'))
    fecha_hora_registro = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_actualizo_id = db.Column(db.Integer, 
                                     db.ForeignKey('usuarios.id', ondelete='CASCADE'))
    fecha_hora_actualizo = db.Column(db.DateTime, default=datetime.utcnow, 
                                     onupdate=datetime.utcnow)
    
    alquileres = db.relationship('Alquiler', backref='estado', lazy='dynamic')
    
    def __repr__(self):
        return f'<EstadoAlquiler {self.nombre}>'


# ==================== TABLA: metodos_pago ====================
class MetodoPago(db.Model):
    __tablename__ = 'metodos_pago'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), unique=True, nullable=False, index=True)
    descripcion = db.Column(db.Text)
    usuario_registro_id = db.Column(db.Integer, 
                                    db.ForeignKey('usuarios.id', ondelete='CASCADE'))
    fecha_hora_registro = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_actualizo_id = db.Column(db.Integer, 
                                     db.ForeignKey('usuarios.id', ondelete='CASCADE'))
    fecha_hora_actualizo = db.Column(db.DateTime, default=datetime.utcnow, 
                                     onupdate=datetime.utcnow)
    
    pagos = db.relationship('Pago', backref='metodo_pago', lazy='dynamic')
    
    def __repr__(self):
        return f'<MetodoPago {self.nombre}>'


# ==================== TABLA: tipo_cuentas ====================
class TipoCuenta(db.Model):
    __tablename__ = 'tipo_cuentas'
    
    id = db.Column(db.Integer, primary_key=True)
    tipo_cuenta = db.Column(db.String(20), unique=True, nullable=False, index=True)
    descripcion = db.Column(db.Text)
    usuario_registro_id = db.Column(db.Integer, 
                                    db.ForeignKey('usuarios.id', ondelete='CASCADE'))
    fecha_hora_registro = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_actualizo_id = db.Column(db.Integer, 
                                     db.ForeignKey('usuarios.id', ondelete='CASCADE'))
    fecha_hora_actualizo = db.Column(db.DateTime, default=datetime.utcnow, 
                                     onupdate=datetime.utcnow)
    
    bancos = db.relationship('Banco', backref='tipo_cuenta', lazy='dynamic')
    
    def __repr__(self):
        return f'<TipoCuenta {self.tipo_cuenta}>'


# ==================== TABLA: bancos ====================
class Banco(db.Model):
    __tablename__ = 'bancos'
    
    id = db.Column(db.Integer, primary_key=True)
    banco = db.Column(db.String(50), nullable=False)
    _cuenta = db.Column('cuenta', db.String(255), unique=True, nullable=False)  # Encrypted
    tipo_cuenta_id = db.Column(db.Integer, 
                               db.ForeignKey('tipo_cuentas.id', ondelete='CASCADE'), 
                               nullable=False)
    _cedula = db.Column('cedula', db.String(255), nullable=False)  # Encrypted
    administrador = db.Column(db.String(100), nullable=False)
    logo_path = db.Column(db.String(255))
    descripcion = db.Column(db.Text)
    usuario_registro_id = db.Column(db.Integer, 
                                    db.ForeignKey('usuarios.id', ondelete='CASCADE'))
    fecha_hora_registro = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_actualizo_id = db.Column(db.Integer, 
                                     db.ForeignKey('usuarios.id', ondelete='CASCADE'))
    fecha_hora_actualizo = db.Column(db.DateTime, default=datetime.utcnow, 
                                     onupdate=datetime.utcnow)
    
    @property
    def cuenta(self):
        return decrypt_data(self._cuenta)
    
    @cuenta.setter
    def cuenta(self, value):
        self._cuenta = encrypt_data(value)
    
    @property
    def cedula(self):
        return decrypt_data(self._cedula)
    
    @cedula.setter
    def cedula(self, value):
        self._cedula = encrypt_data(value)
    
    def __repr__(self):
        return f'<Banco {self.banco}>'


# ==================== TABLA: parentescos ====================
class Parentesco(db.Model):
    __tablename__ = 'parentescos'
    
    id = db.Column(db.Integer, primary_key=True)
    parentesco = db.Column(db.String(50), unique=True, nullable=False, index=True)
    usuario_registro_id = db.Column(db.Integer, 
                                    db.ForeignKey('usuarios.id', ondelete='CASCADE'))
    fecha_hora_registro = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_actualizo_id = db.Column(db.Integer, 
                                     db.ForeignKey('usuarios.id', ondelete='CASCADE'))
    fecha_hora_actualizo = db.Column(db.DateTime, default=datetime.utcnow, 
                                     onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Parentesco {self.parentesco}>'
    
"""
Database Models - Part 2: Propietarios, Inquilinos, Vehículos, Mecánicos, Alquileres
"""

# ==================== TABLA: propietarios ====================
class Propietario(db.Model):
    __tablename__ = 'propietarios'
    
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id', ondelete='SET NULL'))
    nombre_apellido = db.Column(db.String(100), nullable=False, index=True)
    documento_buena_conducta_path = db.Column(db.String(255))
    _cedula = db.Column('cedula', db.String(255), unique=True)  # Encrypted
    cedula_path = db.Column(db.String(255))
    _licencia = db.Column('licencia', db.String(255), unique=True)  # Encrypted
    licencia_path = db.Column(db.String(255))
    direccion = db.Column(db.String(255))
    telefono = db.Column(db.String(20))
    email = db.Column(db.String(100))
    usuario_registro_id = db.Column(db.Integer, 
                                    db.ForeignKey('usuarios.id', ondelete='CASCADE'))
    fecha_hora_registro = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_actualizo_id = db.Column(db.Integer, 
                                     db.ForeignKey('usuarios.id', ondelete='CASCADE'))
    fecha_hora_actualizo = db.Column(db.DateTime, default=datetime.utcnow, 
                                     onupdate=datetime.utcnow)
    
    vehiculos = db.relationship('Vehiculo', backref='propietario', lazy='dynamic')
    referencias = db.relationship('ReferenciaPropietario', backref='propietario', 
                                  cascade='all, delete-orphan', lazy='dynamic')
    
    @property
    def cedula(self):
        return decrypt_data(self._cedula)
    
    @cedula.setter
    def cedula(self, value):
        self._cedula = encrypt_data(value) if value else None
    
    @property
    def licencia(self):
        return decrypt_data(self._licencia)
    
    @licencia.setter
    def licencia(self, value):
        self._licencia = encrypt_data(value) if value else None
    
    def __repr__(self):
        return f'<Propietario {self.nombre_apellido}>'


# ==================== TABLA: referencias_propietarios ====================
class ReferenciaPropietario(db.Model):
    __tablename__ = 'referencias_propietarios'
    
    id = db.Column(db.Integer, primary_key=True)
    propietario_id = db.Column(db.Integer, 
                               db.ForeignKey('propietarios.id', ondelete='CASCADE'), 
                               nullable=False, index=True)
    nombre_apellido = db.Column(db.String(100), nullable=False)
    parentesco_id = db.Column(db.Integer, 
                              db.ForeignKey('parentescos.id', ondelete='CASCADE'), 
                              nullable=False)
    telefono = db.Column(db.String(20), nullable=False)
    usuario_registro_id = db.Column(db.Integer, 
                                    db.ForeignKey('usuarios.id', ondelete='CASCADE'))
    fecha_hora_registro = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_actualizo_id = db.Column(db.Integer, 
                                     db.ForeignKey('usuarios.id', ondelete='CASCADE'))
    fecha_hora_actualizo = db.Column(db.DateTime, default=datetime.utcnow, 
                                     onupdate=datetime.utcnow)
    
    parentesco = db.relationship('Parentesco', backref='referencias_propietarios')
    
    def __repr__(self):
        return f'<ReferenciaPropietario {self.nombre_apellido}>'


# ==================== TABLA: inquilinos ====================
class Inquilino(db.Model):
    __tablename__ = 'inquilinos'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre_apellido = db.Column(db.String(100), nullable=False, index=True)
    direccion = db.Column(db.String(255))
    telefono = db.Column(db.String(20))
    email = db.Column(db.String(100))
    documento_buena_conducta_path = db.Column(db.String(255))
    _cedula = db.Column('cedula', db.String(255), unique=True)  # Encrypted
    cedula_path = db.Column(db.String(255))
    _licencia = db.Column('licencia', db.String(255), unique=True)  # Encrypted
    licencia_path = db.Column(db.String(255))
    usuario_registro_id = db.Column(db.Integer, 
                                    db.ForeignKey('usuarios.id', ondelete='CASCADE'))
    fecha_hora_registro = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_actualizo_id = db.Column(db.Integer, 
                                     db.ForeignKey('usuarios.id', ondelete='CASCADE'))
    fecha_hora_actualizo = db.Column(db.DateTime, default=datetime.utcnow, 
                                     onupdate=datetime.utcnow)
    
    alquileres = db.relationship('Alquiler', backref='inquilino', lazy='dynamic')
    garantes = db.relationship('GaranteInquilino', backref='inquilino', 
                               cascade='all, delete-orphan', lazy='dynamic')
    referencias = db.relationship('ReferenciaInquilino', backref='inquilino', 
                                  cascade='all, delete-orphan', lazy='dynamic')
    deudas = db.relationship('Deuda', backref='inquilino', lazy='dynamic')
    
    @property
    def cedula(self):
        return decrypt_data(self._cedula)
    
    @cedula.setter
    def cedula(self, value):
        self._cedula = encrypt_data(value) if value else None
    
    @property
    def licencia(self):
        return decrypt_data(self._licencia)
    
    @licencia.setter
    def licencia(self, value):
        self._licencia = encrypt_data(value) if value else None
    
    def __repr__(self):
        return f'<Inquilino {self.nombre_apellido}>'


# ==================== TABLA: garantes_inquilinos ====================
class GaranteInquilino(db.Model):
    __tablename__ = 'garantes_inquilinos'
    
    id = db.Column(db.Integer, primary_key=True)
    inquilino_id = db.Column(db.Integer, 
                             db.ForeignKey('inquilinos.id', ondelete='CASCADE'), 
                             nullable=False, index=True)
    nombre_apellido = db.Column(db.String(100), nullable=False)
    direccion = db.Column(db.String(255))
    telefono = db.Column(db.String(20))
    email = db.Column(db.String(100))
    parentesco_id = db.Column(db.Integer, 
                              db.ForeignKey('parentescos.id', ondelete='CASCADE'), 
                              nullable=False)
    documento_referencia_laboral_path = db.Column(db.String(255))
    usuario_registro_id = db.Column(db.Integer, 
                                    db.ForeignKey('usuarios.id', ondelete='CASCADE'))
    fecha_hora_registro = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_actualizo_id = db.Column(db.Integer, 
                                     db.ForeignKey('usuarios.id', ondelete='CASCADE'))
    fecha_hora_actualizo = db.Column(db.DateTime, default=datetime.utcnow, 
                                     onupdate=datetime.utcnow)
    
    parentesco = db.relationship('Parentesco', backref='garantes')
    
    def __repr__(self):
        return f'<GaranteInquilino {self.nombre_apellido}>'


# ==================== TABLA: referencias_inquilinos ====================
class ReferenciaInquilino(db.Model):
    __tablename__ = 'referencias_inquilinos'
    
    id = db.Column(db.Integer, primary_key=True)
    inquilino_id = db.Column(db.Integer, 
                             db.ForeignKey('inquilinos.id', ondelete='CASCADE'), 
                             nullable=False, index=True)
    nombre_apellido = db.Column(db.String(100), nullable=False)
    telefono = db.Column(db.String(20), nullable=False)
    parentesco_id = db.Column(db.Integer, 
                              db.ForeignKey('parentescos.id', ondelete='CASCADE'), 
                              nullable=False)
    usuario_registro_id = db.Column(db.Integer, 
                                    db.ForeignKey('usuarios.id', ondelete='CASCADE'))
    fecha_hora_registro = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_actualizo_id = db.Column(db.Integer, 
                                     db.ForeignKey('usuarios.id', ondelete='CASCADE'))
    fecha_hora_actualizo = db.Column(db.DateTime, default=datetime.utcnow, 
                                     onupdate=datetime.utcnow)
    
    parentesco = db.relationship('Parentesco', backref='referencias_inquilinos')
    
    def __repr__(self):
        return f'<ReferenciaInquilino {self.nombre_apellido}>'


# ==================== TABLA: vehiculos ====================
class Vehiculo(db.Model):
    __tablename__ = 'vehiculos'
    
    id = db.Column(db.Integer, primary_key=True)
    propietario_id = db.Column(db.Integer, 
                               db.ForeignKey('propietarios.id', ondelete='CASCADE'), 
                               nullable=False, index=True)
    placa = db.Column(db.String(20), unique=True, nullable=False, index=True)
    marca_modelo_vehiculo_id = db.Column(db.Integer, 
                                         db.ForeignKey('vehiculo_marca_modelo.id', 
                                                      ondelete='RESTRICT'), 
                                         nullable=False)
    ano = db.Column(db.Integer)
    color = db.Column(db.String(30))
    descripcion = db.Column(db.Text)
    precio_semanal = db.Column(db.Numeric(10, 2), nullable=False)
    condiciones = db.Column(db.Text)
    disponible = db.Column(db.Boolean, default=True)
    usuario_registro_id = db.Column(db.Integer, 
                                    db.ForeignKey('usuarios.id', ondelete='CASCADE'))
    fecha_hora_registro = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_actualizo_id = db.Column(db.Integer, 
                                     db.ForeignKey('usuarios.id', ondelete='CASCADE'))
    fecha_hora_actualizo = db.Column(db.DateTime, default=datetime.utcnow, 
                                     onupdate=datetime.utcnow)
    
    alquileres = db.relationship('Alquiler', backref='vehiculo', lazy='dynamic')
    trabajos = db.relationship('TrabajoVehiculo', backref='vehiculo', 
                               cascade='all, delete-orphan', lazy='dynamic')
    deudas = db.relationship('Deuda', backref='vehiculo', lazy='dynamic')
    
    def __repr__(self):
        return f'<Vehiculo {self.placa}>'


# ==================== TABLA: mecanicos ====================
class Mecanico(db.Model):
    __tablename__ = 'mecanicos'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False, index=True)
    direccion = db.Column(db.String(255))
    telefono = db.Column(db.String(20))
    email = db.Column(db.String(100))
    especialidad = db.Column(db.String(100))
    usuario_registro_id = db.Column(db.Integer, 
                                    db.ForeignKey('usuarios.id', ondelete='CASCADE'))
    fecha_hora_registro = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_actualizo_id = db.Column(db.Integer, 
                                     db.ForeignKey('usuarios.id', ondelete='CASCADE'))
    fecha_hora_actualizo = db.Column(db.DateTime, default=datetime.utcnow, 
                                     onupdate=datetime.utcnow)
    activo = db.Column(db.Boolean, default=True)
    
    trabajos = db.relationship('TrabajoVehiculo', backref='mecanico', lazy='dynamic')
    
    def __repr__(self):
        return f'<Mecanico {self.nombre}>'


# ==================== TABLA: tipos_trabajos ====================
class TipoTrabajo(db.Model):
    __tablename__ = 'tipos_trabajos'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), unique=True, nullable=False, index=True)
    descripcion = db.Column(db.Text)
    usuario_registro_id = db.Column(db.Integer, 
                                    db.ForeignKey('usuarios.id', ondelete='CASCADE'))
    fecha_hora_registro = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_actualizo_id = db.Column(db.Integer, 
                                     db.ForeignKey('usuarios.id', ondelete='CASCADE'))
    fecha_hora_actualizo = db.Column(db.DateTime, default=datetime.utcnow, 
                                     onupdate=datetime.utcnow)
    
    trabajos = db.relationship('TrabajoVehiculo', backref='tipo_trabajo', lazy='dynamic')
    
    def __repr__(self):
        return f'<TipoTrabajo {self.nombre}>'


# ==================== TABLA: trabajos_vehiculos ====================
class TrabajoVehiculo(db.Model):
    __tablename__ = 'trabajos_vehiculos'
    
    id = db.Column(db.Integer, primary_key=True)
    vehiculo_id = db.Column(db.Integer, 
                            db.ForeignKey('vehiculos.id', ondelete='CASCADE'), 
                            nullable=False, index=True)
    mecanico_id = db.Column(db.Integer, 
                            db.ForeignKey('mecanicos.id', ondelete='RESTRICT'), 
                            nullable=False)
    tipo_trabajo_id = db.Column(db.Integer, 
                                db.ForeignKey('tipos_trabajos.id', ondelete='SET NULL'))
    fecha_inicio = db.Column(db.Date, nullable=False, index=True)
    fecha_fin = db.Column(db.Date)
    descripcion = db.Column(db.Text, nullable=False)
    costo = db.Column(db.Numeric(10, 2), default=0.00)
    estado = db.Column(db.Enum('pendiente', 'en_progreso', 'completado', 'cancelado'), 
                      default='pendiente')
    notas = db.Column(db.Text)
    usuario_registro_id = db.Column(db.Integer, 
                                    db.ForeignKey('usuarios.id', ondelete='CASCADE'))
    fecha_hora_registro = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_actualizo_id = db.Column(db.Integer, 
                                     db.ForeignKey('usuarios.id', ondelete='CASCADE'))
    fecha_hora_actualizo = db.Column(db.DateTime, default=datetime.utcnow, 
                                     onupdate=datetime.utcnow)
    
    piezas_usadas = db.relationship('PiezaUsada', backref='trabajo', 
                                    cascade='all, delete-orphan', lazy='dynamic')
    
    def __repr__(self):
        return f'<TrabajoVehiculo {self.id} - {self.estado}>'


# ==================== TABLA: piezas ====================
class Pieza(db.Model):
    __tablename__ = 'piezas'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False, index=True)
    marca = db.Column(db.String(50), nullable=False)
    modelo = db.Column(db.String(50))
    estado = db.Column(db.Enum('nueva', 'usada'), nullable=False)
    costo = db.Column(db.Numeric(10, 2), nullable=False)
    descripcion = db.Column(db.Text)
    usuario_registro_id = db.Column(db.Integer, 
                                    db.ForeignKey('usuarios.id', ondelete='CASCADE'))
    fecha_hora_registro = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_actualizo_id = db.Column(db.Integer, 
                                     db.ForeignKey('usuarios.id', ondelete='CASCADE'))
    fecha_hora_actualizo = db.Column(db.DateTime, default=datetime.utcnow, 
                                     onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Pieza {self.nombre} - {self.marca}>'


# ==================== TABLA: piezas_usadas ====================
class PiezaUsada(db.Model):
    __tablename__ = 'piezas_usadas'
    
    id = db.Column(db.Integer, primary_key=True)
    trabajo_id = db.Column(db.Integer, 
                           db.ForeignKey('trabajos_vehiculos.id', ondelete='CASCADE'), 
                           nullable=False, index=True)
    pieza_id = db.Column(db.Integer, 
                         db.ForeignKey('piezas.id', ondelete='RESTRICT'), 
                         nullable=False)
    cantidad = db.Column(db.Integer, default=1)
    costo_unitario = db.Column(db.Numeric(10, 2), nullable=False)
    notas = db.Column(db.Text)
    usuario_registro_id = db.Column(db.Integer, 
                                    db.ForeignKey('usuarios.id', ondelete='CASCADE'))
    fecha_hora_registro = db.Column(db.DateTime, default=datetime.utcnow)
    
    pieza = db.relationship('Pieza', backref='usos')
    
    def __repr__(self):
        return f'<PiezaUsada {self.pieza_id} x{self.cantidad}>'


# ==================== TABLA: alquileres ====================
class Alquiler(db.Model):
    __tablename__ = 'alquileres'
    
    id = db.Column(db.Integer, primary_key=True)
    vehiculo_id = db.Column(db.Integer, 
                            db.ForeignKey('vehiculos.id', ondelete='CASCADE'), 
                            nullable=False, index=True)
    inquilino_id = db.Column(db.Integer, 
                             db.ForeignKey('inquilinos.id', ondelete='CASCADE'), 
                             nullable=False, index=True)
    estado_id = db.Column(db.Integer, 
                          db.ForeignKey('estados_alquiler.id', ondelete='RESTRICT'), 
                          nullable=False)
    fecha_alquiler_inicio = db.Column(db.Date, nullable=False, index=True)
    fecha_alquiler_fin = db.Column(db.Date, nullable=False, index=True)
    semana = db.Column(db.Integer, nullable=False)
    dia_trabajo = db.Column(db.Integer)
    ingreso = db.Column(db.Numeric(10, 2), nullable=False)
    monto_descuento = db.Column(db.Numeric(10, 2), default=0.00)
    concepto_descuento = db.Column(db.Text)
    notas = db.Column(db.Text)
    usuario_registro_id = db.Column(db.Integer, 
                                    db.ForeignKey('usuarios.id', ondelete='CASCADE'))
    fecha_hora_registro = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_actualizo_id = db.Column(db.Integer, 
                                     db.ForeignKey('usuarios.id', ondelete='CASCADE'))
    fecha_hora_actualizo = db.Column(db.DateTime, default=datetime.utcnow, 
                                     onupdate=datetime.utcnow)
    
    pagos = db.relationship('Pago', backref='alquiler', 
                           cascade='all, delete-orphan', lazy='dynamic')
    deudas = db.relationship('Deuda', backref='alquiler', lazy='dynamic')
    
    def __repr__(self):
        return f'<Alquiler {self.id} - Vehículo {self.vehiculo_id}>'


# ==================== TABLA: deudas ====================
class Deuda(db.Model):
    __tablename__ = 'deudas'
    
    id = db.Column(db.Integer, primary_key=True)
    vehiculo_id = db.Column(db.Integer, 
                            db.ForeignKey('vehiculos.id', ondelete='CASCADE'), 
                            nullable=False, index=True)
    inquilino_id = db.Column(db.Integer, 
                             db.ForeignKey('inquilinos.id', ondelete='CASCADE'), 
                             nullable=False, index=True)
    alquiler_id = db.Column(db.Integer, 
                            db.ForeignKey('alquileres.id', ondelete='CASCADE'), 
                            nullable=False)
    monto_deuda = db.Column(db.Numeric(10, 2), nullable=False)
    dias_retraso = db.Column(db.Integer, nullable=False)
    penalizacion_diaria = db.Column(db.Numeric(10, 2), default=0.00)
    estado = db.Column(db.Enum('pendiente', 'pagado', 'condonado'), default='pendiente')
    fecha_vencimiento = db.Column(db.Date, nullable=False, index=True)
    notas = db.Column(db.Text)
    usuario_registro_id = db.Column(db.Integer, 
                                    db.ForeignKey('usuarios.id', ondelete='CASCADE'))
    fecha_hora_registro = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_actualizo_id = db.Column(db.Integer, 
                                     db.ForeignKey('usuarios.id', ondelete='CASCADE'))
    fecha_hora_actualizo = db.Column(db.DateTime, default=datetime.utcnow, 
                                     onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Deuda {self.id} - ${self.monto_deuda} ({self.estado})>'


# ==================== TABLA: pagos ====================
class Pago(db.Model):
    __tablename__ = 'pagos'
    
    id = db.Column(db.Integer, primary_key=True)
    alquiler_id = db.Column(db.Integer, 
                            db.ForeignKey('alquileres.id', ondelete='CASCADE'), 
                            nullable=False, index=True)
    metodo_pago_id = db.Column(db.Integer, 
                               db.ForeignKey('metodos_pago.id', ondelete='RESTRICT'), 
                               nullable=False)
    monto = db.Column(db.Numeric(10, 2), nullable=False)
    fecha_pago = db.Column(db.Date, nullable=False, index=True)
    deducciones = db.Column(db.Numeric(10, 2), default=0.00)
    neto = db.Column(db.Numeric(10, 2), nullable=False)
    comprobante = db.Column(db.String(100))
    notas = db.Column(db.Text)
    usuario_registro_id = db.Column(db.Integer, 
                                    db.ForeignKey('usuarios.id', ondelete='CASCADE'))
    fecha_hora_registro = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_actualizo_id = db.Column(db.Integer, 
                                     db.ForeignKey('usuarios.id', ondelete='CASCADE'))
    fecha_hora_actualizo = db.Column(db.DateTime, default=datetime.utcnow, 
                                     onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Pago {self.id} - ${self.monto}>'