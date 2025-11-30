# alex_app_admin
alex_app_admin


# AlexRentaCar Admin App

Sistema completo de gestión de alquiler de vehículos construido con Flask, SQLAlchemy, Flask-Login y características avanzadas de seguridad incluyendo encriptación de base de datos y Redis cache opcional.

## 🚗 Características Principales

- **Gestión de Usuarios**: Sistema completo con roles (admin, user, mechanic)
- **Módulos de Negocio**: Propietarios, Inquilinos, Vehículos, Alquileres, Pagos y Deudas
- **Módulo de Mecánicos**: Gestión de trabajos, piezas y mantenimientos
- **Reportes y Dashboard**: Estadísticas en tiempo real y reportes de ganancias
- **Seguridad Avanzada**:
  - Encriptación de datos sensibles (cédulas, licencias, cuentas bancarias)
  - Flask-Talisman para headers de seguridad
  - Flask-Limiter para rate limiting
  - Protección CSRF
  - Bcrypt para passwords
- **Cache Opcional**: Redis cache que puede habilitarse/deshabilitarse
- **Registro de Auditoría**: Tracking completo de accesos y cambios
- **Responsive Design**: Bootstrap 5 con diseño moderno

## 📋 Requisitos

- Python 3.8+
- MySQL 8.0+ (o MariaDB 10.3+)
- Redis 6.0+ (opcional, para cache)
- Sistema operativo: Linux, macOS o Windows

## 🚀 Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/tu-usuario/alexrentacar_adminapp.git
cd alexrentacar_adminapp
```

### 2. Crear entorno virtual

```bash
# Linux/macOS
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar base de datos MySQL

```bash
# Conectar a MySQL
mysql -u root -p

# Ejecutar el script SQL incluido
mysql -u root -p < alquiler_vehiculos_completo.sql

# O desde MySQL shell:
source alquiler_vehiculos_completo.sql
```

### 5. Generar clave de encriptación

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

**¡IMPORTANTE!** Guarda esta clave de forma segura. Perderla significa perder acceso a todos los datos encriptados.

### 6. Configurar variables de entorno

Copia el archivo `.env.example` a `.env`:

```bash
cp .env.example .env
```

Edita `.env` con tus configuraciones:

```bash
# Environment
FLASK_ENV=development
FLASK_DEBUG=True

# Database
SQLALCHEMY_DATABASE_URI=mysql+pymysql://root:tu_password@localhost:3306/alquiler_vehiculos

# Encryption (usa la clave generada en el paso 5)
DATABASE_ENCRYPTION_KEY=tu-clave-generada-aqui

# Secret Keys (genera claves únicas para producción)
SECRET_KEY=tu-secret-key-super-segura
JWT_SECRET_KEY=tu-jwt-secret-key

# Redis Cache (opcional)
ENABLE_CACHE=True
REDIS_URL=redis://localhost:6379/0

# Rate Limiting
RATELIMIT_ENABLED=True
RATELIMIT_STORAGE_URL=redis://localhost:6379/1
```

### 7. Inicializar migraciones y crear datos iniciales

```bash
# Crear las migraciones
flask db init
flask db migrate -m "Initial migration"
flask db upgrade

# Crear datos iniciales (usuarios admin, catálogos, etc.)
flask init-db
```

### 8. Ejecutar la aplicación

```bash
# Modo desarrollo
python run.py

# O usando Flask CLI
flask run

# Con Gunicorn (producción)
gunicorn -w 4 -b 0.0.0.0:5000 run:app
```

La aplicación estará disponible en: `http://localhost:5000`

## 🔐 Credenciales por Defecto

**Usuario Administrador:**
- Usuario: `admin`
- Contraseña: `admin123`

**Usuario Regular:**
- Usuario: `user1`
- Contraseña: `user123`

**⚠️ IMPORTANTE:** Cambia estas contraseñas inmediatamente en producción.

## 📁 Estructura del Proyecto

```
alexrentacar_adminapp/
│
├── app/
│   ├── __init__.py              # Factory de aplicación
│   ├── config.py                # Configuración por entornos
│   ├── models.py                # Modelos SQLAlchemy
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth_routes.py       # Autenticación
│   │   ├── admin_routes.py      # Administración
│   │   ├── settings_routes.py   # Configuración usuario
│   │   ├── modulos_routes.py    # Módulos de negocio
│   │   ├── reportes_routes.py   # Reportes y dashboard
│   │   └── mecanicos_routes.py  # Gestión mecánicos
│   ├── services/
│   │   ├── __init__.py
│   │   └── user_service.py      # Lógica de negocio usuarios
│   ├── templates/               # Plantillas Jinja2
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── auth/
│   │   ├── admin/
│   │   ├── catalogos/
│   │   ├── modulos/
│   │   ├── reportes/
│   │   ├── mecanicos/
│   │   ├── settings/
│   │   └── errors/
│   └── static/
│       ├── css/
│       ├── js/
│       └── uploads/
│
├── migrations/                   # Migraciones Flask-Migrate
├── .env.example                  # Template de variables de entorno
├── .env                          # Variables de entorno (no versionado)
├── .gitignore
├── requirements.txt
├── run.py                        # Punto de entrada
├── alquiler_vehiculos_completo.sql  # Script SQL inicial
└── README.md
```

## 🔧 Comandos Flask CLI Personalizados

```bash
# Inicializar base de datos con datos iniciales
flask init-db

# Crear usuario administrador manualmente
flask create-admin

# Acceder a shell interactivo con contexto de la app
flask shell
```

## 🛡️ Características de Seguridad

### Encriptación de Datos

Los siguientes campos están encriptados en la base de datos usando Fernet:
- Cédulas (propietarios e inquilinos)
- Licencias de conducir
- Números de cuentas bancarias

```python
# Ejemplo de uso en modelos
propietario = Propietario.query.get(1)
cedula = propietario.cedula  # Automáticamente desencriptado
propietario.cedula = "001-1234567-8"  # Automáticamente encriptado
db.session.commit()
```

### Protección CSRF

Todas las formas HTML están protegidas con tokens CSRF mediante Flask-WTF.

### Rate Limiting

- Login: 5 intentos por minuto
- Password reset: 3 intentos por hora
- API endpoints: 200 por día, 50 por hora

### Headers de Seguridad

Flask-Talisman configura automáticamente:
- Content Security Policy
- Strict-Transport-Security
- X-Content-Type-Options
- X-Frame-Options
- X-XSS-Protection

## 💾 Redis Cache (Opcional)

El sistema puede funcionar con o sin Redis:

**Con Redis** (mejor rendimiento):
```bash
# Instalar Redis
sudo apt-get install redis-server

# Iniciar Redis
redis-server

# Habilitar en .env
ENABLE_CACHE=True
REDIS_URL=redis://localhost:6379/0
```

**Sin Redis** (modo SimpleCache):
```bash
# Deshabilitar en .env
ENABLE_CACHE=False
```

El sistema usa automáticamente SimpleCache como fallback si Redis no está disponible.

## 📊 Gestión de Base de Datos

### Migraciones

```bash
# Crear nueva migración después de cambios en models.py
flask db migrate -m "Descripción del cambio"

# Aplicar migraciones
flask db upgrade

# Revertir última migración
flask db downgrade

# Ver historial
flask db history
```

### Backup de Base de Datos

```bash
# Backup completo
mysqldump -u root -p alquiler_vehiculos > backup_$(date +%Y%m%d).sql

# Restaurar desde backup
mysql -u root -p alquiler_vehiculos < backup_20240101.sql
```

## 🔄 Despliegue en Producción

### Configuración para Producción

1. **Cambiar a modo producción** en `.env`:
```bash
FLASK_ENV=production
FLASK_DEBUG=False
SESSION_COOKIE_SECURE=True
```

2. **Generar claves secretas únicas**:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

3. **Configurar HTTPS**:
```bash
TALISMAN_FORCE_HTTPS=True
```

4. **Usar servidor WSGI**:
```bash
# Con Gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 --timeout 120 run:app

# Con systemd (crear servicio)
sudo nano /etc/systemd/system/alexrentacar.service
```

Ejemplo de servicio systemd:
```ini
[Unit]
Description=AlexRentaCar Admin App
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/alexrentacar
Environment="PATH=/var/www/alexrentacar/venv/bin"
ExecStart=/var/www/alexrentacar/venv/bin/gunicorn -w 4 -b 0.0.0.0:8000 run:app

[Install]
WantedBy=multi-user.target
```

### Nginx como Proxy Reverso

```nginx
server {
    listen 80;
    server_name tudominio.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /var/www/alexrentacar/app/static;
        expires 30d;
    }
}
```

## 🐛 Solución de Problemas

### Error: "No module named 'MySQLdb'"
```bash
pip install PyMySQL
# Añadir al inicio de run.py:
import pymysql
pymysql.install_as_MySQLdb()
```

### Error: "Can't connect to MySQL server"
```bash
# Verificar que MySQL está corriendo
sudo systemctl status mysql

# Verificar credenciales en .env
# Verificar que la base de datos existe
mysql -u root -p -e "SHOW DATABASES;"
```

### Error: "Redis connection failed"
```bash
# Si no quieres usar Redis, desactívalo:
ENABLE_CACHE=False

# O instala y inicia Redis:
sudo apt-get install redis-server
sudo systemctl start redis
```

### Error: "Encryption/Decryption error"
```bash
# Verifica que DATABASE_ENCRYPTION_KEY esté configurado
# Si cambiaste la clave, los datos antiguos NO podrán desencriptarse
# Deberás migrar los datos con la clave anterior
```

## 📝 Licencia

Este proyecto es privado y propiedad de AlexRentaCar. Todos los derechos reservados.

## 👥 Soporte

Para soporte técnico o consultas:
- Email: soporte@alexrentacar.com
- Teléfono: +1 (809) 000-0000

## 📚 Recursos Adicionales

- [Documentación Flask](https://flask.palletsprojects.com/)
- [SQLAlchemy ORM](https://docs.sqlalchemy.org/)
- [Flask-Login](https://flask-login.readthedocs.io/)
- [Bootstrap 5](https://getbootstrap.com/docs/5.3/)