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



# BASE DE DATOS Y SERVIDOR LOCAL

# Aplicar migraciones pendientes
python manage.py migrate

# Crear usuario administrador
python manage.py createsuperuser

# Levantar el servidor de desarrollo
python manage.py runserver


# COMANDO RÁPIDO PARA SESIONES POSTERIORES

# Set-ExecutionPolicy -Scope Process RemoteSigned; .\.venv\Scripts\Activate.ps1; python manage.py runserver