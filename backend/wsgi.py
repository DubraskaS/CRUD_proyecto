# backend/wsgi.py

from app import app as application 
# Vercel necesita que la instancia de Flask se llame 'application'
# Importamos 'app' desde app.py y la renombramos como 'application'