# Usar imagen oficial de Python con Debian
FROM python:3.11-slim-bookworm

# Establecer variables de entorno
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Crear directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema necesarias para PyMySQL y cryptography
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements.txt
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copiar el código de la aplicación
COPY . .

# Crear usuario no-root para ejecutar la aplicación
RUN useradd -m -u 1000 flaskuser && \
    chown -R flaskuser:flaskuser /app

# Cambiar al usuario no-root
USER flaskuser

# Exponer el puerto
EXPOSE 5000

# Comando para ejecutar la aplicación con Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120", "app:app"]
```

## 2. .dockerignore
```
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
.venv
.env
*.sqlite
*.db
.git
.gitignore
.vscode
.idea
*.log
instance/
.pytest_cache/
.coverage
htmlcov/
dist/
build/
*.egg-info/
.DS_Store