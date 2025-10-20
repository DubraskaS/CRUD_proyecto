# backend/wsgi.py

import sys
import os

# Agrega la ruta de la carpeta 'backend' al path de Python.
# Esto permite que 'from app import app' funcione correctamente.
sys.path.insert(0, os.path.dirname(__file__))

from app import app

# El nombre de la aplicación debe ser 'application' para el estándar WSGI
# y la configuración de Vercel.
if __name__ == '__main__':
    app.run()
