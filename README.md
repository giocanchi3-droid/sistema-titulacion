# INICIALIZACIÓN Y CONFIGURACIÓN DEL PROYECTO


# 1. Crear el entorno virtual
python -m venv .venv

# 2. Habilitar ejecución de scripts en la sesión actual y activar el entorno virtual
Set-ExecutionPolicy -Scope Process RemoteSigned; .\.venv\Scripts\Activate.ps1

# 3. Verificar archivos ocultos (opcional)
Get-ChildItem -Hidden

# 4. Actualizar pip
python -m pip install --upgrade pip


# OPCIÓN A: PROYECTO EXISTENTE (CLONADO)

# Instalar dependencias registradas
pip install -r requirements.txt


# OPCIÓN B: PROYECTO DESDE CERO

# Instalar Django e inicializar la estructura
pip install django
django-admin startproject config .


# Crear la base de datos en PostgreSQL usando psycopg
python -c "import psycopg; conn = psycopg.connect('dbname=postgres user=postgres password=(contraseña aqui) host=127.0.0.1 port=5432', autocommit=True); conn.execute('CREATE DATABASE sistema_titulacion'); conn.close(); print('¡Base de datos creada exitosamente!')"

# Generar y aplicar las migraciones
python manage.py makemigrations
python manage.py migrate

# Crear usuario administrador
python manage.py createsuperuser

# Levantar el servidor de desarrollo
python manage.py runserver


# DESPLIEGUE EN RENDER

# Build Command
bash build.sh

# Start Command
gunicorn config.wsgi:application

# Variables obligatorias
# DATABASE_URL: URL interna de PostgreSQL de Render
# SECRET_KEY: clave secreta de producción
# DEBUG=False
# RENDER=True

# Persistent Disk de Render
# Nombre: pucetec-media
# Mount Path: /var/data
# Tamaño: 1 GB mínimo
# MEDIA_ROOT se configura automáticamente como /var/data/media.
# El disco persistente es necesario para conservar Word y PDF entre deploys.


# COMANDO RÁPIDO PARA SESIONES POSTERIORES

# Set-ExecutionPolicy -Scope Process RemoteSigned; .\.venv\Scripts\Activate.ps1; python manage.py runserver