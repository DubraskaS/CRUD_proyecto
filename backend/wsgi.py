# backend/wsgi.py

import sys
import os

# Agrega la ruta de la carpeta 'backend' al path de Python.
# Esto permite que 'from app import app' funcione correctamente.
sys.path.insert(0, os.path.dirname(__file__))

from app import app 