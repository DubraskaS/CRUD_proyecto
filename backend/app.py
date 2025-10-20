from flask import Flask
from flask_cors import CORS #type:ignore
# Importa la lógica de las rutas (endpoints)
from routes.users import users_bp

app = Flask(__name__)
# Habilita CORS para permitir que tu frontend de React acceda a esta API
CORS(app) 

# --- NUEVA CONFIGURACIÓN CRÍTICA ---
# Forzar a Flask a usar JSON por defecto para todas las respuestas.
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
app.config['JSON_AS_ASCII'] = False
# Esto asegura que el Content-Type sea siempre application/json
app.url_map.strict_slashes = False 
app.json.compact = True 
# --- FIN DE CONFIGURACIÓN CRÍTICA ---

# Registra el Blueprint de usuarios
app.register_blueprint(users_bp, url_prefix='/api/users')

@app.route('/')
def home():
    # Una ruta simple para verificar que el servidor esté vivo
    return "Flask User API is Running!"

if __name__ == '__main__':
    # Flask se ejecuta por defecto en http://127.0.0.1:5000/
    app.run(debug=True, port=5000)
