"""
Database Models for AlexRentaCar Admin App
Maps SQL schema to SQLAlchemy ORM with encryption support
"""
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from cryptography.fernet import Fernet ,InvalidToken# <-- Importar InvalidToken de cryptography.fernet
from app import db
from flask import current_app


# ==================== Funciones Helper de Cifrado ====================
def get_cipher():
    """Obtiene la instancia de Fernet cipher"""
    key = current_app.config.get('FERNET_KEY')
    
    # Validar que la clave existe
    if not key:
        # Este error detendrá la aplicación al iniciar si falta la clave.
        raise ValueError("FERNET_KEY no está configurada en la aplicación")
    
    # Si la clave es string, convertir a bytes (Fernet requiere bytes)
    if isinstance(key, str):
        key = key.encode()
    
    # Validar formato de la clave
    try:
        return Fernet(key)
    except Exception as e:
        # Clave mal formateada (no base64 URL-safe)
        raise ValueError(f"FERNET_KEY inválida: {str(e)}")


def encrypt_data(data):
    """Cifra datos sensibles (como Cédula, Licencia, Teléfono)"""
    if data is None or data == '':
        return None
    
    try:
        cipher = get_cipher()
        # Asegurar que data es string antes de codificar a bytes
        if not isinstance(data, str):
            data = str(data)
        # Cifra la cadena y la decodifica de bytes a string para la BD
        return cipher.encrypt(data.encode()).decode()
    except Exception as e:
        print(f"Error al encriptar: {str(e)}")
        # Propaga el error para detener la operación si falla la encriptación
        raise


def decrypt_data(encrypted_data):
    """Descifra datos sensibles. Maneja el error de clave incorrecta."""
    if encrypted_data is None or encrypted_data == '':
        return None
    
    try:
        cipher = get_cipher()
        # El descifrado puede fallar si la clave es incorrecta o el token está corrupto
        return cipher.decrypt(encrypted_data.encode()).decode()
    except InvalidToken: 
        # Error específico: La clave FERNET_KEY es incorrecta o el dato cifrado está corrupto
        print("Error al desencriptar: Clave incorrecta (FERNET_KEY) o dato cifrado inválido.")
        # Es crucial forzar la reversión (ROLLBACK) si no se puede leer un dato crítico.
        raise
    except Exception as e:
        # Para cualquier otro error (ej. problema con la codificación)
        print(f"Error inesperado al desencriptar: {str(e)}")
        raise


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
    propietarios = db.relationship('Propietario', foreign_keys='Propietario.usuario_id',  backref='usuario_cuenta', lazy='dynamic')
    
    def set_password(self, password):
        self.password = generate_password_hash(password, method='pbkdf2:sha256')
    
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
    usuario_registro_id = db.Column(db.Integer,  db.ForeignKey('usuarios.id', ondelete='CASCADE'),  nullable=False)
    fecha_hora_registro = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_actualizo_id = db.Column(db.Integer,  db.ForeignKey('usuarios.id', ondelete='CASCADE'),   nullable=False)
    fecha_hora_actualizo = db.Column(db.DateTime, default=datetime.utcnow,  onupdate=datetime.utcnow)
    
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
    cuenta = db.Column('cuenta', db.String(255), unique=True, nullable=False)  # Encrypted
    tipo_cuenta_id = db.Column(db.Integer,   db.ForeignKey('tipo_cuentas.id', ondelete='CASCADE'),   nullable=False)
    cedula = db.Column('cedula', db.String(255), nullable=False)  # Encrypted
    administrador = db.Column(db.String(100), nullable=False)
    logo_path = db.Column(db.String(255))
    descripcion = db.Column(db.Text)
    usuario_registro_id = db.Column(db.Integer, db.ForeignKey('usuarios.id', ondelete='CASCADE'))
    fecha_hora_registro = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_actualizo_id = db.Column(db.Integer,  db.ForeignKey('usuarios.id', ondelete='CASCADE'))
    fecha_hora_actualizo = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Banco {self.banco}>'


# ==================== TABLA: parentescos ====================
class Parentesco(db.Model):
    __tablename__ = 'parentescos'
    
    id = db.Column(db.Integer, primary_key=True)
    # CORRECCIÓN
    parentesco = db.Column(db.String(100), nullable=False)
    
    usuario_registro_id = db.Column(db.Integer, db.ForeignKey('usuarios.id', ondelete='CASCADE'))
    fecha_hora_registro = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_actualizo_id = db.Column(db.Integer,  db.ForeignKey('usuarios.id', ondelete='CASCADE'))
    fecha_hora_actualizo = db.Column(db.DateTime, default=datetime.utcnow,  onupdate=datetime.utcnow)
    
    
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

    # Campos encriptados (YA ESTABAN CORRECTOS con mapeo explícito)
    _nombre_apellido = db.Column("nombre_apellido", db.Text, nullable=False)
    _documento_buena_conducta_path = db.Column("documento_buena_conducta_path", db.Text)
    _cedula = db.Column("cedula", db.Text)
    _cedula_path = db.Column("cedula_path", db.Text)
    _licencia = db.Column("licencia", db.Text)
    _licencia_path = db.Column("licencia_path", db.Text)
    _direccion = db.Column("direccion", db.Text)
    _telefono = db.Column("telefono", db.Text)
    _email = db.Column("email", db.Text)

    usuario_registro_id = db.Column(db.Integer, db.ForeignKey('usuarios.id', ondelete='CASCADE'))
    fecha_hora_registro = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_actualizo_id = db.Column(db.Integer, db.ForeignKey('usuarios.id', ondelete='CASCADE'))
    fecha_hora_actualizo = db.Column(db.DateTime, default=datetime.utcnow,
                                     onupdate=datetime.utcnow)
    
    vehiculos = db.relationship('Vehiculo', backref='propietario', lazy='dynamic')
    referencias = db.relationship('ReferenciaPropietario', backref='propietario',
                                  cascade='all, delete-orphan', lazy='dynamic')

    # ------------------------
    # PROPIEDADES ENCRIPTADAS
    # ------------------------

    # nombre_apellido
    @property
    def nombre_apellido(self):
        return decrypt_data(self._nombre_apellido)

    @nombre_apellido.setter
    def nombre_apellido(self, value):
        self._nombre_apellido = encrypt_data(value)

    # documento_buena_conducta_path
    @property
    def documento_buena_conducta_path(self):
        return decrypt_data(self._documento_buena_conducta_path)

    @documento_buena_conducta_path.setter
    def documento_buena_conducta_path(self, value):
        self._documento_buena_conducta_path = encrypt_data(value)

    # cedula
    @property
    def cedula(self):
        return decrypt_data(self._cedula)
    
    @cedula.setter
    def cedula(self, value):
        self._cedula = encrypt_data(value)

    # cedula_path
    @property
    def cedula_path(self):
        return decrypt_data(self._cedula_path)

    @cedula_path.setter
    def cedula_path(self, value):
        self._cedula_path = encrypt_data(value)

    # licencia
    @property
    def licencia(self):
        return decrypt_data(self._licencia)

    @licencia.setter
    def licencia(self, value):
        self._licencia = encrypt_data(value)

    # licencia_path
    @property
    def licencia_path(self):
        return decrypt_data(self._licencia_path)

    @licencia_path.setter
    def licencia_path(self, value):
        self._licencia_path = encrypt_data(value)

    # direccion
    @property
    def direccion(self):
        return decrypt_data(self._direccion)

    @direccion.setter
    def direccion(self, value):
        self._direccion = encrypt_data(value)

    # telefono
    @property
    def telefono(self):
        return decrypt_data(self._telefono)

    @telefono.setter
    def telefono(self, value):
        self._telefono = encrypt_data(value)

    # email
    @property
    def email(self):
        return decrypt_data(self._email)

    @email.setter
    def email(self, value):
        self._email = encrypt_data(value)
        
    @property
    def tipo_socio(self):
        """Calcula el tipo de socio según cantidad de vehículos"""
        cantidad_vehiculos = self.vehiculos.count()
        if cantidad_vehiculos >= 3:
            return 'SOCIO_POTENCIAL'
        elif cantidad_vehiculos >= 1:
            return 'SOCIO_MINORISTA'
        else:
            return 'SIN_VEHICULOS'
    
    @property
    def badge_socio(self):
        """Retorna el badge CSS según el tipo de socio"""
        tipo = self.tipo_socio
        if tipo == 'SOCIO_POTENCIAL':
            return 'badge-success'
        elif tipo == 'SOCIO_MINORISTA':
            return 'badge-info'
        else:
            return 'badge-secondary'

    def __repr__(self):
        return f'<Propietario {self.nombre_apellido}>'

# ==================== TABLA: referencias_propietarios ====================
class ReferenciaPropietario(db.Model):
    __tablename__ = 'referencias_propietarios'
    
    id = db.Column(db.Integer, primary_key=True)
    propietario_id = db.Column(db.Integer,  db.ForeignKey('propietarios.id', ondelete='CASCADE'),   nullable=False, index=True)
    
    # CORRECCIÓN
    _nombre_apellido = db.Column('nombre_apellido', db.Text, nullable=False)
    
    parentesco_id = db.Column(db.Integer,  db.ForeignKey('parentescos.id', ondelete='CASCADE'),  nullable=False)
    
    # CORRECCIÓN
    _telefono = db.Column('telefono', db.Text, nullable=False)
    
    usuario_registro_id = db.Column(db.Integer,   db.ForeignKey('usuarios.id', ondelete='CASCADE'))
    fecha_hora_registro = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_actualizo_id = db.Column(db.Integer,  db.ForeignKey('usuarios.id', ondelete='CASCADE'))
    fecha_hora_actualizo = db.Column(db.DateTime, default=datetime.utcnow,  onupdate=datetime.utcnow)
    
    parentesco = db.relationship('Parentesco', backref='referencias_propietarios') 
    
    # nombre_apellido
    @property
    def nombre_apellido(self):
        return decrypt_data(self._nombre_apellido)

    @nombre_apellido.setter
    def nombre_apellido(self, value):
        self._nombre_apellido = encrypt_data(value)
        
    # telefono
    @property
    def telefono(self):
        return decrypt_data(self._telefono)

    @telefono.setter
    def telefono(self, value):
        self._telefono = encrypt_data(value)
    
    def __repr__(self):
        return f'<ReferenciaPropietario {self.nombre_apellido}>'


# ==================== TABLA: inquilinos ====================
class Inquilino(db.Model):
    __tablename__ = 'inquilinos'
    
    id = db.Column(db.Integer, primary_key=True)
    # CORRECCIÓN
    _nombre_apellido = db.Column('nombre_apellido', db.Text, nullable=False, index=True)
    _direccion = db.Column('direccion', db.Text)  
    _telefono = db.Column('telefono', db.Text)
    _email = db.Column('email', db.Text)
    _documento_buena_conducta_path = db.Column('documento_buena_conducta_path', db.Text)
    
    # Estos ya estaban bien mapeados:
    _cedula = db.Column('cedula', db.Text)  
    _cedula_path = db.Column('cedula_path', db.Text)
    _licencia = db.Column('licencia', db.Text)  
    _licencia_path = db.Column('licencia_path', db.Text)
    
    usuario_registro_id = db.Column(db.Integer,  db.ForeignKey('usuarios.id', ondelete='CASCADE'))
    fecha_hora_registro = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_actualizo_id = db.Column(db.Integer, db.ForeignKey('usuarios.id', ondelete='CASCADE'))
    fecha_hora_actualizo = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    alquileres = db.relationship('Alquiler', backref='inquilino', lazy='dynamic')
    garantes = db.relationship('GaranteInquilino', backref='inquilino', cascade='all, delete-orphan', lazy='dynamic')
    referencias = db.relationship('ReferenciaInquilino', backref='inquilino',  cascade='all, delete-orphan', lazy='dynamic')
    deudas = db.relationship('Deuda', backref='inquilino', lazy='dynamic')
    
    @property
    def nombre_apellido(self):
        return decrypt_data(self._nombre_apellido)
    
    @nombre_apellido.setter
    def nombre_apellido(self, value):
        self._nombre_apellido = encrypt_data(value) if value else None
        
    @property
    def direccion(self):
        return decrypt_data(self._direccion)
    
    @direccion.setter
    def direccion(self, value):
        self._direccion = encrypt_data(value) if value else None
        
    @property
    def telefono(self):
        return decrypt_data(self._telefono)
    
    @telefono.setter
    def telefono(self, value):
        self._telefono = encrypt_data(value) if value else None
        
    @property
    def email(self):
        return decrypt_data(self._email)
    
    @email.setter
    def email(self, value):
        self._email = encrypt_data(value) if value else None
        
    @property
    def documento_buena_conducta_path(self):
        return decrypt_data(self._documento_buena_conducta_path)
    
    @documento_buena_conducta_path.setter
    def documento_buena_conducta_path(self, value):
        self._documento_buena_conducta_path = encrypt_data(value) if value else None       
    
    @property
    def cedula(self):
        return decrypt_data(self._cedula)
    
    @cedula.setter
    def cedula(self, value):
        self._cedula = encrypt_data(value) if value else None
         
    @property
    def cedula_path(self):
        return decrypt_data(self._cedula_path)
    
    @cedula_path.setter
    def cedula_path(self, value):
        self._cedula_path = encrypt_data(value) if value else None
    
    @property
    def licencia(self):
        return decrypt_data(self._licencia)
    
    @licencia.setter
    def licencia(self, value):
        self._licencia = encrypt_data(value) if value else None
        
    @property
    def licencia_path(self):
        return decrypt_data(self._licencia_path)
    
    @licencia_path.setter
    def licencia_path(self, value):
        self._licencia_path = encrypt_data(value) if value else None
         
    def __repr__(self):
        return f'<Inquilino {self.nombre_apellido}>'

# ==================== TABLA: garantes_inquilinos ====================
class GaranteInquilino(db.Model):
    __tablename__ = 'garantes_inquilinos'
    
    id = db.Column(db.Integer, primary_key=True)
    inquilino_id = db.Column(db.Integer,  db.ForeignKey('inquilinos.id', ondelete='CASCADE'),  nullable=False, index=True)
    
    # CORRECCIÓN
    _nombre_apellido = db.Column('nombre_apellido', db.Text, nullable=False)
    _direccion = db.Column('direccion', db.Text)
    _telefono = db.Column('telefono', db.Text)
    _email = db.Column('email', db.Text)
    
    #  AGREGAR ESTOS DOS CAMPOS
    _cedula = db.Column('cedula', db.Text)
    _cedula_path = db.Column('cedula_path', db.Text)
    
    parentesco_id = db.Column(db.Integer,  db.ForeignKey('parentescos.id', ondelete='CASCADE'),  nullable=False)
    
    # CORRECCIÓN
    _documento_referencia_laboral_path = db.Column('documento_referencia_laboral_path', db.Text)
    
    usuario_registro_id = db.Column(db.Integer,  db.ForeignKey('usuarios.id', ondelete='CASCADE'))
    fecha_hora_registro = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_actualizo_id = db.Column(db.Integer,  db.ForeignKey('usuarios.id', ondelete='CASCADE'))
    fecha_hora_actualizo = db.Column(db.DateTime, default=datetime.utcnow,  onupdate=datetime.utcnow)
    
    parentesco = db.relationship('Parentesco', backref='garantes')
    
    # nombre_apellido
    @property
    def nombre_apellido(self):
        return decrypt_data(self._nombre_apellido)

    @nombre_apellido.setter
    def nombre_apellido(self, value):
        self._nombre_apellido = encrypt_data(value)

    # direccion
    @property
    def direccion(self):
        return decrypt_data(self._direccion)

    @direccion.setter
    def direccion(self, value):
        self._direccion = encrypt_data(value)

    # telefono
    @property
    def telefono(self):
        return decrypt_data(self._telefono)

    @telefono.setter
    def telefono(self, value):
        self._telefono = encrypt_data(value)

    # email
    @property
    def email(self):
        return decrypt_data(self._email)

    @email.setter
    def email(self, value):
        self._email = encrypt_data(value)
        
    # AGREGAR ESTAS PROPERTIES
    @property
    def cedula(self):
        return decrypt_data(self._cedula)

    @cedula.setter
    def cedula(self, value):
        self._cedula = encrypt_data(value) if value else None
    
    @property
    def cedula_path(self):
        return decrypt_data(self._cedula_path)

    @cedula_path.setter
    def cedula_path(self, value):
        self._cedula_path = encrypt_data(value) if value else None


    # documento_referencia_laboral_path
    @property
    def documento_referencia_laboral_path(self):
        return decrypt_data(self._documento_referencia_laboral_path)

    @documento_referencia_laboral_path.setter
    def documento_referencia_laboral_path(self, value):
        self._documento_referencia_laboral_path = encrypt_data(value)

    def __repr__(self):
        return f'<GaranteInquilino {self.nombre_apellido}>'


# ==================== TABLA: referencias_inquilinos ====================
class ReferenciaInquilino(db.Model):
    __tablename__ = 'referencias_inquilinos'
    
    id = db.Column(db.Integer, primary_key=True)
    inquilino_id = db.Column(db.Integer, db.ForeignKey('inquilinos.id', ondelete='CASCADE'), nullable=False, index=True)
    _nombre_apellido = db.Column('nombre_apellido', db.Text, nullable=False)
    _telefono = db.Column('telefono', db.Text, nullable=False)
    
    # ✅ AGREGAR ESTOS DOS CAMPOS
    _cedula = db.Column('cedula', db.Text)
    _cedula_path = db.Column('cedula_path', db.Text)
    
    parentesco_id = db.Column(db.Integer, db.ForeignKey('parentescos.id', ondelete='CASCADE'), nullable=False)
    usuario_registro_id = db.Column(db.Integer, db.ForeignKey('usuarios.id', ondelete='CASCADE'))
    fecha_hora_registro = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_actualizo_id = db.Column(db.Integer, db.ForeignKey('usuarios.id', ondelete='CASCADE'))
    fecha_hora_actualizo = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    parentesco = db.relationship('Parentesco', backref='referencias_inquilinos')
    
    # Properties existentes...
    @property
    def nombre_apellido(self):
        return decrypt_data(self._nombre_apellido)

    @nombre_apellido.setter
    def nombre_apellido(self, value):
        self._nombre_apellido = encrypt_data(value)

    @property
    def telefono(self):
        return decrypt_data(self._telefono)

    @telefono.setter
    def telefono(self, value):
        self._telefono = encrypt_data(value)

    #  AGREGAR ESTAS PROPERTIES
    @property
    def cedula(self):
        return decrypt_data(self._cedula)

    @cedula.setter
    def cedula(self, value):
        self._cedula = encrypt_data(value) if value else None
    
    @property
    def cedula_path(self):
        return decrypt_data(self._cedula_path)

    @cedula_path.setter
    def cedula_path(self, value):
        self._cedula_path = encrypt_data(value) if value else None

    def __repr__(self):
        return f'<ReferenciaInquilino {self.nombre_apellido}>'


# ==================== TABLA: vehiculos ====================

# Nota: Se asume que encrypt_data y decrypt_data están definidos
# en el mismo archivo (models.py) o importados.

class Vehiculo(db.Model):
    __tablename__ = 'vehiculos'
    
    id = db.Column(db.Integer, primary_key=True)
    propietario_id = db.Column(db.Integer,  db.ForeignKey('propietarios.id', ondelete='CASCADE'),  nullable=False, index=True)
    
    # CORRECCIÓN: Mapeo explícito a la columna 'placa' de la base de datos
    _placa = db.Column('placa', db.Text, unique=True, nullable=False, index=True)
    
    marca_modelo_vehiculo_id = db.Column(db.Integer,   db.ForeignKey('vehiculo_marca_modelo.id',  ondelete='RESTRICT'),   nullable=False)
    
    # CORRECCIÓN: Mapeo explícito para el resto de columnas encriptadas
    _ano = db.Column('ano', db.Text)
    _color = db.Column('color', db.Text)
    _descripcion = db.Column('descripcion', db.Text)
    _precio_semanal = db.Column('precio_semanal', db.Text, nullable=False)
    _condiciones = db.Column('condiciones', db.Text)
    _disponible = db.Column('disponible', db.Text)
    
    usuario_registro_id = db.Column(db.Integer,   db.ForeignKey('usuarios.id', ondelete='CASCADE'))
    fecha_hora_registro = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_actualizo_id = db.Column(db.Integer,   db.ForeignKey('usuarios.id', ondelete='CASCADE'))
    fecha_hora_actualizo = db.Column(db.DateTime, default=datetime.utcnow,   onupdate=datetime.utcnow)
    
    # Relationships
    alquileres = db.relationship('Alquiler', backref='vehiculo', lazy='dynamic')
    trabajos = db.relationship('TrabajoVehiculo', backref='vehiculo', 
                               cascade='all, delete-orphan', lazy='dynamic')
    deudas = db.relationship('Deuda', backref='vehiculo', lazy='dynamic')
    
    # placa
    @property
    def placa(self):
        return decrypt_data(self._placa)

    @placa.setter
    def placa(self, value):
        self._placa = encrypt_data(value)

    # ano
    @property
    def ano(self):
        if self._ano is None:
            return None
        return int(decrypt_data(self._ano))

    @ano.setter
    def ano(self, value):
        if value is None:
            self._ano = None
        else:
            self._ano = encrypt_data(str(value))

    # color
    @property
    def color(self):
        return decrypt_data(self._color)

    @color.setter
    def color(self, value):
        self._color = encrypt_data(value)

    # descripcion
    @property
    def descripcion(self):
        return decrypt_data(self._descripcion)

    @descripcion.setter
    def descripcion(self, value):
        self._descripcion = encrypt_data(value)

    # precio_semanal
    @property
    def precio_semanal(self):
        from decimal import Decimal
        if self._precio_semanal is None:
            return None
        return Decimal(decrypt_data(self._precio_semanal))

    @precio_semanal.setter
    def precio_semanal(self, value):
        if value is None:
            self._precio_semanal = None
        else:
            self._precio_semanal = encrypt_data(str(value))

    # condiciones
    @property
    def condiciones(self):
        return decrypt_data(self._condiciones)

    @condiciones.setter
    def condiciones(self, value):
        self._condiciones = encrypt_data(value)

    # disponible
    @property
    def disponible(self):
        if self._disponible is None:
            return True  # assuming default True
        return bool(int(decrypt_data(self._disponible)))

    @disponible.setter
    def disponible(self, value):
        self._disponible = encrypt_data('1' if value else '0')

    def __repr__(self):
        return f'<Vehiculo {self.placa}>'

class VehiculoImagen(db.Model):
    __tablename__ = 'vehiculos_imagenes'
    
    id = db.Column(db.Integer, primary_key=True)
    vehiculo_id = db.Column(db.Integer, db.ForeignKey('vehiculos.id', ondelete='CASCADE'), nullable=False, index=True)
    tipo = db.Column(db.Enum('imagen', 'video'), default='imagen', nullable=False)
    ruta = db.Column(db.String(500), nullable=False)
    nombre_archivo = db.Column(db.String(255))
    orden = db.Column(db.Integer, default=0)
    es_principal = db.Column(db.Boolean, default=False)
    usuario_registro_id = db.Column(db.Integer, db.ForeignKey('usuarios.id', ondelete='CASCADE'))
    fecha_hora_registro = db.Column(db.DateTime, default=datetime.utcnow)
    
    vehiculo = db.relationship('Vehiculo', backref=db.backref('imagenes', lazy='dynamic', cascade='all, delete-orphan'))
    
    def __repr__(self):
        return f'<VehiculoImagen {self.id} - Vehiculo {self.vehiculo_id}>'
    
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

# ==================== TABLA: porcentajes_ganancia ====================
class PorcentajeGanancia(db.Model):
    """
    Tabla para gestionar los porcentajes de ganancia de la empresa
    que se aplican al calcular la nómina en los alquileres
    """
    __tablename__ = 'porcentajes_ganancia'
    
    id = db.Column(db.Integer, primary_key=True)
    descripcion = db.Column(db.String(100), nullable=False)
    porcentaje = db.Column(db.Numeric(5, 2), nullable=False)  # Ej: 15.50 = 15.5%
    activo = db.Column(db.Boolean, default=True)
    por_defecto = db.Column(db.Boolean, default=False)  # Solo uno puede ser por defecto
    
    usuario_registro_id = db.Column(db.Integer, 
                                    db.ForeignKey('usuarios.id', ondelete='CASCADE'))
    fecha_hora_registro = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_actualizo_id = db.Column(db.Integer, 
                                     db.ForeignKey('usuarios.id', ondelete='CASCADE'))
    fecha_hora_actualizo = db.Column(db.DateTime, default=datetime.utcnow, 
                                     onupdate=datetime.utcnow)
    
    # Relationship
    semanas_alquiler = db.relationship('SemanaAlquiler', backref='porcentaje_ganancia', 
                                       lazy='dynamic')
    
    def __repr__(self):
        return f'<PorcentajeGanancia {self.descripcion} - {self.porcentaje}%>'


# ==================== TABLA: semanas_alquiler ====================
class SemanaAlquiler(db.Model):
    """
    Tabla para gestionar semanas de trabajo de alquileres
    Cada registro representa una semana completa con su configuración
    """
    __tablename__ = 'semanas_alquiler'
    
    id = db.Column(db.Integer, primary_key=True)
    fecha_inicio = db.Column(db.Date, nullable=False, index=True)
    fecha_fin = db.Column(db.Date, nullable=False, index=True)
    numero_semana = db.Column(db.Integer)  # Número de semana del año
    anio = db.Column(db.Integer, nullable=False, index=True)
    
    # Porcentaje de ganancia aplicado a esta semana
    porcentaje_ganancia_id = db.Column(db.Integer, 
                                       db.ForeignKey('porcentajes_ganancia.id', 
                                                     ondelete='RESTRICT'),
                                       nullable=False)
    
    # Estado de la semana
    estado = db.Column(db.Enum('abierta', 'cerrada', 'cancelada'), 
                      default='abierta', nullable=False)
    
    # Totales calculados
    total_vehiculos = db.Column(db.Integer, default=0)
    total_socios = db.Column(db.Integer, default=0)
    total_inquilinos = db.Column(db.Integer, default=0)
    ingreso_total = db.Column(db.Numeric(12, 2), default=0.00)
    
    # Notas
    notas = db.Column(db.Text)
    
    usuario_registro_id = db.Column(db.Integer, 
                                    db.ForeignKey('usuarios.id', ondelete='CASCADE'))
    fecha_hora_registro = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_actualizo_id = db.Column(db.Integer, 
                                     db.ForeignKey('usuarios.id', ondelete='CASCADE'))
    fecha_hora_actualizo = db.Column(db.DateTime, default=datetime.utcnow, 
                                     onupdate=datetime.utcnow)
    
    # Relationships
    detalles_alquiler = db.relationship('DetalleAlquilerSemanal', 
                                        backref='semana', 
                                        cascade='all, delete-orphan',
                                        lazy='dynamic')
    
    def __repr__(self):
        return f'<SemanaAlquiler {self.fecha_inicio} - {self.fecha_fin}>'
    
    @property
    def dias_semana(self):
        """Calcula los días de la semana"""
        if self.fecha_inicio and self.fecha_fin:
            return (self.fecha_fin - self.fecha_inicio).days + 1
        return 0


# ==================== TABLA: detalles_alquiler_semanal ====================
class DetalleAlquilerSemanal(db.Model):
    """
    Tabla detallada de cada alquiler en una semana específica
    Contiene toda la información por vehículo/inquilino en esa semana
    """
    __tablename__ = 'detalles_alquiler_semanal'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Relaciones principales
    semana_alquiler_id = db.Column(db.Integer, 
                                   db.ForeignKey('semanas_alquiler.id', 
                                                 ondelete='CASCADE'),
                                   nullable=False, index=True)
    alquiler_id = db.Column(db.Integer, 
                           db.ForeignKey('alquileres.id', ondelete='CASCADE'),
                           nullable=False, index=True)
    vehiculo_id = db.Column(db.Integer, 
                           db.ForeignKey('vehiculos.id', ondelete='CASCADE'),
                           nullable=False, index=True)
    inquilino_id = db.Column(db.Integer, 
                            db.ForeignKey('inquilinos.id', ondelete='CASCADE'),
                            nullable=False, index=True)
    propietario_id = db.Column(db.Integer, 
                              db.ForeignKey('propietarios.id', ondelete='CASCADE'),
                              nullable=False, index=True)
    
    # Campos de pago
    precio_semanal = db.Column(db.Numeric(10, 2), nullable=False)  # Valor semanal
    dias_trabajo = db.Column(db.Integer, nullable=False)  # DT
    ingreso_calculado = db.Column(db.Numeric(10, 2), nullable=False)  # precio_semanal * dias_trabajo
    
    # Inversión mecánica
    inversion_mecanica = db.Column(db.Numeric(10, 2), default=0.00)
    concepto_inversion = db.Column(db.Text)
    trabajo_vehiculo_id = db.Column(db.Integer, 
                                    db.ForeignKey('trabajos_vehiculos.id', 
                                                  ondelete='SET NULL'))  # Referencia opcional
    
    # Descuentos
    monto_descuento = db.Column(db.Numeric(10, 2), default=0.00)
    concepto_descuento = db.Column(db.Text)
    
    # Nómina y ganancia empresa
    porcentaje_empresa = db.Column(db.Numeric(5, 2), nullable=False)  # % aplicado
    nomina_empresa = db.Column(db.Numeric(10, 2), nullable=False)  # ingreso * % empresa
    
    # Deuda
    tiene_deuda = db.Column(db.Boolean, default=False)
    monto_deuda = db.Column(db.Numeric(10, 2), default=0.00)
    fecha_limite_pago = db.Column(db.Date)  # Jueves de la semana
    
    # Nómina final
    nomina_final = db.Column(db.Numeric(10, 2), nullable=False)  # ingreso + deuda
    
    # Pago
    banco_id = db.Column(db.Integer, 
                        db.ForeignKey('bancos.id', ondelete='SET NULL'))
    fecha_confirmacion_pago = db.Column(db.Date)
    pago_confirmado = db.Column(db.Boolean, default=False)
    
    # Notas adicionales
    notas = db.Column(db.Text)
    
    usuario_registro_id = db.Column(db.Integer, 
                                    db.ForeignKey('usuarios.id', ondelete='CASCADE'))
    fecha_hora_registro = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_actualizo_id = db.Column(db.Integer, 
                                     db.ForeignKey('usuarios.id', ondelete='CASCADE'))
    fecha_hora_actualizo = db.Column(db.DateTime, default=datetime.utcnow, 
                                     onupdate=datetime.utcnow)
    
    # Relationships
    alquiler = db.relationship('Alquiler', backref='detalles_semanales')
    vehiculo = db.relationship('Vehiculo', backref='detalles_alquiler_semanal')
    inquilino = db.relationship('Inquilino', backref='detalles_alquiler_semanal')
    propietario = db.relationship('Propietario', backref='detalles_alquiler_semanal')
    banco = db.relationship('Banco', backref='detalles_alquiler_semanal')
    trabajo_vehiculo = db.relationship('TrabajoVehiculo', backref='detalles_alquiler_semanal')
    
    def __repr__(self):
        return f'<DetalleAlquilerSemanal {self.id} - Semana {self.semana_alquiler_id}>'
    
    @property
    def esta_en_mora(self):
        """Verifica si el pago está en mora"""
        if not self.pago_confirmado and self.fecha_limite_pago:
            from datetime import date
            return date.today() > self.fecha_limite_pago
        return False
    
    @property
    def dias_mora(self):
        """Calcula días de mora"""
        if self.esta_en_mora:
            from datetime import date
            return (date.today() - self.fecha_limite_pago).days
        return 0


# ==================== TABLA: historico_porcentajes_ganancia ====================
class HistoricoPorcentajeGanancia(db.Model):
    """Tabla histórica para porcentajes de ganancia"""
    __tablename__ = 'historico_porcentajes_ganancia'
    
    id_historico = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tipo_operacion = db.Column(db.Enum('INSERT', 'UPDATE', 'DELETE'), nullable=False)
    fecha_hora_operacion = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_operacion_id = db.Column(db.Integer)
    
    # Campos históricos
    id = db.Column(db.Integer)
    descripcion = db.Column(db.String(100))
    porcentaje = db.Column(db.Numeric(5, 2))
    activo = db.Column(db.Boolean)
    por_defecto = db.Column(db.Boolean)
    usuario_registro_id = db.Column(db.Integer)
    fecha_hora_registro = db.Column(db.DateTime)
    usuario_actualizo_id = db.Column(db.Integer)
    fecha_hora_actualizo = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<HistoricoPorcentajeGanancia {self.id} - {self.tipo_operacion}>'


# ==================== TABLA: historico_semanas_alquiler ====================
class HistoricoSemanaAlquiler(db.Model):
    """Tabla histórica para semanas de alquiler"""
    __tablename__ = 'historico_semanas_alquiler'
    
    id_historico = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tipo_operacion = db.Column(db.Enum('INSERT', 'UPDATE', 'DELETE'), nullable=False)
    fecha_hora_operacion = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_operacion_id = db.Column(db.Integer)
    
    # Campos históricos
    id = db.Column(db.Integer)
    fecha_inicio = db.Column(db.Date)
    fecha_fin = db.Column(db.Date)
    numero_semana = db.Column(db.Integer)
    anio = db.Column(db.Integer)
    porcentaje_ganancia_id = db.Column(db.Integer)
    estado = db.Column(db.String(20))
    total_vehiculos = db.Column(db.Integer)
    total_socios = db.Column(db.Integer)
    total_inquilinos = db.Column(db.Integer)
    ingreso_total = db.Column(db.Numeric(12, 2))
    notas = db.Column(db.Text)
    usuario_registro_id = db.Column(db.Integer)
    fecha_hora_registro = db.Column(db.DateTime)
    usuario_actualizo_id = db.Column(db.Integer)
    fecha_hora_actualizo = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<HistoricoSemanaAlquiler {self.id} - {self.tipo_operacion}>'

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
    

# ==================== TABLA: historico_usuarios ====================
class HistoricoUsuario(db.Model):
    __tablename__ = 'historico_usuarios'
    
    id_historico = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tipo_operacion = db.Column(db.Enum('INSERT', 'UPDATE', 'DELETE'), nullable=False)
    fecha_hora_operacion = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_operacion_id = db.Column(db.Integer)
    
    # Campos históricos del usuario
    id = db.Column(db.Integer)
    username = db.Column(db.String(50))
    password = db.Column(db.String(255))
    rol = db.Column(db.Enum('admin', 'user', 'mechanic'))
    nombre = db.Column(db.String(100))
    apellido = db.Column(db.String(100))
    email = db.Column(db.String(100))
    telefono = db.Column(db.String(20))
    fecha_creacion = db.Column(db.DateTime)
    activo = db.Column(db.Boolean)
    
    def __repr__(self):
        return f'<HistoricoUsuario {self.id} - {self.tipo_operacion}>'


# ==================== TABLA: historico_vehiculo_marca_modelo ====================
class HistoricoVehiculoMarcaModelo(db.Model):
    __tablename__ = 'historico_vehiculo_marca_modelo'
    
    id_historico = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tipo_operacion = db.Column(db.Enum('INSERT', 'UPDATE', 'DELETE'), nullable=False)
    fecha_hora_operacion = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_operacion_id = db.Column(db.Integer)
    
    id = db.Column(db.Integer)
    marca = db.Column(db.String(50))
    modelo = db.Column(db.String(50))
    tipo = db.Column(db.String(20))
    logo_path = db.Column(db.String(255))
    descripcion = db.Column(db.Text)
    usuario_registro_id = db.Column(db.Integer)
    fecha_hora_registro = db.Column(db.DateTime)
    usuario_actualizo_id = db.Column(db.Integer)
    fecha_hora_actualizo = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<HistoricoVehiculoMarcaModelo {self.id} - {self.tipo_operacion}>'


# ==================== TABLA: historico_estados_alquiler ====================
class HistoricoEstadoAlquiler(db.Model):
    __tablename__ = 'historico_estados_alquiler'
    
    id_historico = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tipo_operacion = db.Column(db.Enum('INSERT', 'UPDATE', 'DELETE'), nullable=False)
    fecha_hora_operacion = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_operacion_id = db.Column(db.Integer)
    
    id = db.Column(db.Integer)
    nombre = db.Column(db.String(50))
    descripcion = db.Column(db.Text)
    usuario_registro_id = db.Column(db.Integer)
    fecha_hora_registro = db.Column(db.DateTime)
    usuario_actualizo_id = db.Column(db.Integer)
    fecha_hora_actualizo = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<HistoricoEstadoAlquiler {self.id} - {self.tipo_operacion}>'


# ==================== TABLA: historico_metodos_pago ====================
class HistoricoMetodoPago(db.Model):
    __tablename__ = 'historico_metodos_pago'
    
    id_historico = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tipo_operacion = db.Column(db.Enum('INSERT', 'UPDATE', 'DELETE'), nullable=False)
    fecha_hora_operacion = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_operacion_id = db.Column(db.Integer)
    
    id = db.Column(db.Integer)
    nombre = db.Column(db.String(50))
    descripcion = db.Column(db.Text)
    usuario_registro_id = db.Column(db.Integer)
    fecha_hora_registro = db.Column(db.DateTime)
    usuario_actualizo_id = db.Column(db.Integer)
    fecha_hora_actualizo = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<HistoricoMetodoPago {self.id} - {self.tipo_operacion}>'


# ==================== TABLA: historico_tipo_cuentas ====================
class HistoricoTipoCuenta(db.Model):
    __tablename__ = 'historico_tipo_cuentas'
    
    id_historico = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tipo_operacion = db.Column(db.Enum('INSERT', 'UPDATE', 'DELETE'), nullable=False)
    fecha_hora_operacion = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_operacion_id = db.Column(db.Integer)
    
    id = db.Column(db.Integer)
    tipo_cuenta = db.Column(db.String(20))
    descripcion = db.Column(db.Text)
    usuario_registro_id = db.Column(db.Integer)
    fecha_hora_registro = db.Column(db.DateTime)
    usuario_actualizo_id = db.Column(db.Integer)
    fecha_hora_actualizo = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<HistoricoTipoCuenta {self.id} - {self.tipo_operacion}>'


# ==================== TABLA: historico_bancos ====================
class HistoricoBanco(db.Model):
    __tablename__ = 'historico_bancos'
    
    id_historico = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tipo_operacion = db.Column(db.Enum('INSERT', 'UPDATE', 'DELETE'), nullable=False)
    fecha_hora_operacion = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_operacion_id = db.Column(db.Integer)
    
    id = db.Column(db.Integer)
    banco = db.Column(db.String(50))
    cuenta = db.Column(db.String(30))
    tipo_cuenta_id = db.Column(db.Integer)
    cedula = db.Column(db.String(20))
    administrador = db.Column(db.String(100))
    logo_path = db.Column(db.String(255))
    descripcion = db.Column(db.Text)
    usuario_registro_id = db.Column(db.Integer)
    fecha_hora_registro = db.Column(db.DateTime)
    usuario_actualizo_id = db.Column(db.Integer)
    fecha_hora_actualizo = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<HistoricoBanco {self.id} - {self.tipo_operacion}>'


# ==================== TABLA: historico_parentescos ====================
class HistoricoParentesco(db.Model):
    __tablename__ = 'historico_parentescos'
    
    id_historico = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tipo_operacion = db.Column(db.Enum('INSERT', 'UPDATE', 'DELETE'), nullable=False)
    fecha_hora_operacion = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_operacion_id = db.Column(db.Integer)
    
    id = db.Column(db.Integer)
    parentesco = db.Column(db.String(50))
    usuario_registro_id = db.Column(db.Integer)
    fecha_hora_registro = db.Column(db.DateTime)
    usuario_actualizo_id = db.Column(db.Integer)
    fecha_hora_actualizo = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<HistoricoParentesco {self.id} - {self.tipo_operacion}>'


# ==================== TABLA: historico_propietarios ====================
class HistoricoPropietario(db.Model):
    __tablename__ = 'historico_propietarios'
    
    id_historico = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tipo_operacion = db.Column(db.Enum('INSERT', 'UPDATE', 'DELETE'), nullable=False)
    fecha_hora_operacion = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_operacion_id = db.Column(db.Integer)
    
    id = db.Column(db.Integer)
    usuario_id = db.Column(db.Integer)
    nombre_apellido = db.Column(db.String(100))
    documento_buena_conducta_path = db.Column(db.String(255))
    cedula = db.Column(db.String(20))
    cedula_path = db.Column(db.String(255))
    licencia = db.Column(db.String(50))
    licencia_path = db.Column(db.String(255))
    direccion = db.Column(db.String(255))
    telefono = db.Column(db.String(20))
    email = db.Column(db.String(100))
    usuario_registro_id = db.Column(db.Integer)
    fecha_hora_registro = db.Column(db.DateTime)
    usuario_actualizo_id = db.Column(db.Integer)
    fecha_hora_actualizo = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<HistoricoPropietario {self.id} - {self.tipo_operacion}>'


# ==================== TABLA: historico_referencias_propietarios ====================
class HistoricoReferenciaPropietario(db.Model):
    __tablename__ = 'historico_referencias_propietarios'
    
    id_historico = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tipo_operacion = db.Column(db.Enum('INSERT', 'UPDATE', 'DELETE'), nullable=False)
    fecha_hora_operacion = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_operacion_id = db.Column(db.Integer)
    
    id = db.Column(db.Integer)
    propietario_id = db.Column(db.Integer)
    nombre_apellido = db.Column(db.String(100))
    parentesco_id = db.Column(db.Integer)
    telefono = db.Column(db.String(20))
    usuario_registro_id = db.Column(db.Integer)
    fecha_hora_registro = db.Column(db.DateTime)
    usuario_actualizo_id = db.Column(db.Integer)
    fecha_hora_actualizo = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<HistoricoReferenciaPropietario {self.id} - {self.tipo_operacion}>'


# ==================== TABLA: historico_inquilinos ====================
class HistoricoInquilino(db.Model):
    __tablename__ = 'historico_inquilinos'
    
    id_historico = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tipo_operacion = db.Column(db.Enum('INSERT', 'UPDATE', 'DELETE'), nullable=False)
    fecha_hora_operacion = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_operacion_id = db.Column(db.Integer)
    
    id = db.Column(db.Integer)
    nombre_apellido = db.Column(db.String(100))
    direccion = db.Column(db.String(255))
    telefono = db.Column(db.String(20))
    email = db.Column(db.String(100))
    documento_buena_conducta_path = db.Column(db.String(255))
    cedula = db.Column(db.String(20))
    cedula_path = db.Column(db.String(255))
    licencia = db.Column(db.String(50))
    licencia_path = db.Column(db.String(255))
    usuario_registro_id = db.Column(db.Integer)
    fecha_hora_registro = db.Column(db.DateTime)
    usuario_actualizo_id = db.Column(db.Integer)
    fecha_hora_actualizo = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<HistoricoInquilino {self.id} - {self.tipo_operacion}>'


# ==================== TABLA: historico_garantes_inquilinos ====================
class HistoricoGaranteInquilino(db.Model):
    __tablename__ = 'historico_garantes_inquilinos'
    
    id_historico = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tipo_operacion = db.Column(db.Enum('INSERT', 'UPDATE', 'DELETE'), nullable=False)
    fecha_hora_operacion = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_operacion_id = db.Column(db.Integer)
    
    id = db.Column(db.Integer)
    inquilino_id = db.Column(db.Integer)
    nombre_apellido = db.Column(db.String(100))
    direccion = db.Column(db.String(255))
    telefono = db.Column(db.String(20))
    email = db.Column(db.String(100))
    parentesco_id = db.Column(db.Integer)
    documento_referencia_laboral_path = db.Column(db.String(255))
    usuario_registro_id = db.Column(db.Integer)
    fecha_hora_registro = db.Column(db.DateTime)
    usuario_actualizo_id = db.Column(db.Integer)
    fecha_hora_actualizo = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<HistoricoGaranteInquilino {self.id} - {self.tipo_operacion}>'


# ==================== TABLA: historico_referencias_inquilinos ====================
class HistoricoReferenciaInquilino(db.Model):
    __tablename__ = 'historico_referencias_inquilinos'
    
    id_historico = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tipo_operacion = db.Column(db.Enum('INSERT', 'UPDATE', 'DELETE'), nullable=False)
    fecha_hora_operacion = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_operacion_id = db.Column(db.Integer)
    
    id = db.Column(db.Integer)
    inquilino_id = db.Column(db.Integer)
    nombre_apellido = db.Column(db.String(100))
    telefono = db.Column(db.String(20))
    parentesco_id = db.Column(db.Integer)
    usuario_registro_id = db.Column(db.Integer)
    fecha_hora_registro = db.Column(db.DateTime)
    usuario_actualizo_id = db.Column(db.Integer)
    fecha_hora_actualizo = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<HistoricoReferenciaInquilino {self.id} - {self.tipo_operacion}>'


# ==================== TABLA: historico_vehiculos ====================
class HistoricoVehiculo(db.Model):
    __tablename__ = 'historico_vehiculos'
    
    id_historico = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tipo_operacion = db.Column(db.Enum('INSERT', 'UPDATE', 'DELETE'), nullable=False)
    fecha_hora_operacion = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_operacion_id = db.Column(db.Integer)
    
    id = db.Column(db.Integer)
    propietario_id = db.Column(db.Integer)
    placa = db.Column(db.String(20))
    marca_modelo_vehiculo_id = db.Column(db.Integer)
    ano = db.Column(db.Integer)
    color = db.Column(db.String(30))
    descripcion = db.Column(db.Text)
    precio_semanal = db.Column(db.Numeric(10, 2))
    condiciones = db.Column(db.Text)
    disponible = db.Column(db.Boolean)
    usuario_registro_id = db.Column(db.Integer)
    fecha_hora_registro = db.Column(db.DateTime)
    usuario_actualizo_id = db.Column(db.Integer)
    fecha_hora_actualizo = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<HistoricoVehiculo {self.id} - {self.tipo_operacion}>'


# ==================== TABLA: historico_mecanicos ====================
class HistoricoMecanico(db.Model):
    __tablename__ = 'historico_mecanicos'
    
    id_historico = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tipo_operacion = db.Column(db.Enum('INSERT', 'UPDATE', 'DELETE'), nullable=False)
    fecha_hora_operacion = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_operacion_id = db.Column(db.Integer)
    
    id = db.Column(db.Integer)
    nombre = db.Column(db.String(100))
    direccion = db.Column(db.String(255))
    telefono = db.Column(db.String(20))
    email = db.Column(db.String(100))
    especialidad = db.Column(db.String(100))
    usuario_registro_id = db.Column(db.Integer)
    fecha_hora_registro = db.Column(db.DateTime)
    usuario_actualizo_id = db.Column(db.Integer)
    fecha_hora_actualizo = db.Column(db.DateTime)
    activo = db.Column(db.Boolean)
    
    def __repr__(self):
        return f'<HistoricoMecanico {self.id} - {self.tipo_operacion}>'


# ==================== TABLA: historico_tipos_trabajos ====================
class HistoricoTipoTrabajo(db.Model):
    __tablename__ = 'historico_tipos_trabajos'
    
    id_historico = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tipo_operacion = db.Column(db.Enum('INSERT', 'UPDATE', 'DELETE'), nullable=False)
    fecha_hora_operacion = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_operacion_id = db.Column(db.Integer)
    
    id = db.Column(db.Integer)
    nombre = db.Column(db.String(100))
    descripcion = db.Column(db.Text)
    usuario_registro_id = db.Column(db.Integer)
    fecha_hora_registro = db.Column(db.DateTime)
    usuario_actualizo_id = db.Column(db.Integer)
    fecha_hora_actualizo = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<HistoricoTipoTrabajo {self.id} - {self.tipo_operacion}>'


# ==================== TABLA: historico_trabajos_vehiculos ====================
class HistoricoTrabajoVehiculo(db.Model):
    __tablename__ = 'historico_trabajos_vehiculos'
    
    id_historico = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tipo_operacion = db.Column(db.Enum('INSERT', 'UPDATE', 'DELETE'), nullable=False)
    fecha_hora_operacion = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_operacion_id = db.Column(db.Integer)
    
    id = db.Column(db.Integer)
    vehiculo_id = db.Column(db.Integer)
    mecanico_id = db.Column(db.Integer)
    tipo_trabajo_id = db.Column(db.Integer)
    fecha_inicio = db.Column(db.Date)
    fecha_fin = db.Column(db.Date)
    descripcion = db.Column(db.Text)
    costo = db.Column(db.Numeric(10, 2))
    estado = db.Column(db.Enum('pendiente', 'en_progreso', 'completado', 'cancelado'))
    notas = db.Column(db.Text)
    usuario_registro_id = db.Column(db.Integer)
    fecha_hora_registro = db.Column(db.DateTime)
    usuario_actualizo_id = db.Column(db.Integer)
    fecha_hora_actualizo = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<HistoricoTrabajoVehiculo {self.id} - {self.tipo_operacion}>'


# ==================== TABLA: historico_piezas ====================
class HistoricoPieza(db.Model):
    __tablename__ = 'historico_piezas'
    
    id_historico = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tipo_operacion = db.Column(db.Enum('INSERT', 'UPDATE', 'DELETE'), nullable=False)
    fecha_hora_operacion = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_operacion_id = db.Column(db.Integer)
    
    id = db.Column(db.Integer)
    nombre = db.Column(db.String(100))
    marca = db.Column(db.String(50))
    modelo = db.Column(db.String(50))
    estado = db.Column(db.Enum('nueva', 'usada'))
    costo = db.Column(db.Numeric(10, 2))
    descripcion = db.Column(db.Text)
    usuario_registro_id = db.Column(db.Integer)
    fecha_hora_registro = db.Column(db.DateTime)
    usuario_actualizo_id = db.Column(db.Integer)
    fecha_hora_actualizo = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<HistoricoPieza {self.id} - {self.tipo_operacion}>'


# ==================== TABLA: historico_piezas_usadas ====================
class HistoricoPiezaUsada(db.Model):
    __tablename__ = 'historico_piezas_usadas'
    
    id_historico = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tipo_operacion = db.Column(db.Enum('INSERT', 'UPDATE', 'DELETE'), nullable=False)
    fecha_hora_operacion = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_operacion_id = db.Column(db.Integer)
    
    id = db.Column(db.Integer)
    trabajo_id = db.Column(db.Integer)
    pieza_id = db.Column(db.Integer)
    cantidad = db.Column(db.Integer)
    costo_unitario = db.Column(db.Numeric(10, 2))
    notas = db.Column(db.Text)
    usuario_registro_id = db.Column(db.Integer)
    fecha_hora_registro = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<HistoricoPiezaUsada {self.id} - {self.tipo_operacion}>'


# ==================== TABLA: historico_alquileres ====================
class HistoricoAlquiler(db.Model):
    __tablename__ = 'historico_alquileres'
    
    id_historico = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tipo_operacion = db.Column(db.Enum('INSERT', 'UPDATE', 'DELETE'), nullable=False)
    fecha_hora_operacion = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_operacion_id = db.Column(db.Integer)
    
    id = db.Column(db.Integer)
    vehiculo_id = db.Column(db.Integer)
    inquilino_id = db.Column(db.Integer)
    estado_id = db.Column(db.Integer)
    fecha_alquiler_inicio = db.Column(db.Date)
    fecha_alquiler_fin = db.Column(db.Date)
    semana = db.Column(db.Integer)
    dia_trabajo = db.Column(db.Integer)
    ingreso = db.Column(db.Numeric(10, 2))
    monto_descuento = db.Column(db.Numeric(10, 2))
    concepto_descuento = db.Column(db.Text)
    notas = db.Column(db.Text)
    usuario_registro_id = db.Column(db.Integer)
    fecha_hora_registro = db.Column(db.DateTime)
    usuario_actualizo_id = db.Column(db.Integer)
    fecha_hora_actualizo = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<HistoricoAlquiler {self.id} - {self.tipo_operacion}>'


# ==================== TABLA: historico_deudas ====================
class HistoricoDeuda(db.Model):
    __tablename__ = 'historico_deudas'
    
    id_historico = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tipo_operacion = db.Column(db.Enum('INSERT', 'UPDATE', 'DELETE'), nullable=False)
    fecha_hora_operacion = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_operacion_id = db.Column(db.Integer)
    
    id = db.Column(db.Integer)
    vehiculo_id = db.Column(db.Integer)
    inquilino_id = db.Column(db.Integer)
    alquiler_id = db.Column(db.Integer)
    monto_deuda = db.Column(db.Numeric(10, 2))
    dias_retraso = db.Column(db.Integer)
    penalizacion_diaria = db.Column(db.Numeric(10, 2))
    estado = db.Column(db.Enum('pendiente', 'pagado', 'condonado'))
    fecha_vencimiento = db.Column(db.Date)
    notas = db.Column(db.Text)
    usuario_registro_id = db.Column(db.Integer)
    fecha_hora_registro = db.Column(db.DateTime)
    usuario_actualizo_id = db.Column(db.Integer)
    fecha_hora_actualizo = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<HistoricoDeuda {self.id} - {self.tipo_operacion}>'


# ==================== TABLA: historico_pagos ====================
class HistoricoPago(db.Model):
    __tablename__ = 'historico_pagos'
    
    id_historico = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tipo_operacion = db.Column(db.Enum('INSERT', 'UPDATE', 'DELETE'), nullable=False)
    fecha_hora_operacion = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_operacion_id = db.Column(db.Integer)
    
    id = db.Column(db.Integer)
    alquiler_id = db.Column(db.Integer)
    metodo_pago_id = db.Column(db.Integer)
    monto = db.Column(db.Numeric(10, 2))
    fecha_pago = db.Column(db.Date)
    deducciones = db.Column(db.Numeric(10, 2))
    neto = db.Column(db.Numeric(10, 2))
    comprobante = db.Column(db.String(100))
    notas = db.Column(db.Text)
    usuario_registro_id = db.Column(db.Integer)
    fecha_hora_registro = db.Column(db.DateTime)
    usuario_actualizo_id = db.Column(db.Integer)
    fecha_hora_actualizo = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<HistoricoPago {self.id} - {self.tipo_operacion}>'