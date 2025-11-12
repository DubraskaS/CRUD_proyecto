from flask import Flask, jsonify
from flask_cors import CORS #type:ignore
from db.database import init_db
# Importa la lógica de las rutas (endpoints)
from backend.routes.users import users_bp

# ----------------------------------------------------------------------
# INICIALIZACIÓN DE LA APLICACIÓN
# ----------------------------------------------------------------------
app = Flask(__name__)

# Habilita CORS para permitir que tu frontend de React acceda a la API
CORS(app)

# Configuración crítica para el manejo de JSON y CORS
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
app.config['JSON_AS_ASCII'] = False
app.url_map.strict_slashes = False
app.json.compact = True

# Registra el Blueprint de usuarios
# Las rutas de users.py se acceden a través de /users/
app.register_blueprint(users_bp, url_prefix='/api/users')

# Ruta de inicio para confirmar que la API funciona
@app.route('/', methods=['GET'])
def home():
    return jsonify({"message": "API de Gestión de Usuarios operativa. Usa /users para acceder a los datos."}), 200

# ----------------------------------------------------------------------
# INICIALIZACIÓN DE LA BASE DE DATOS
# ----------------------------------------------------------------------
# Inicializa la base de datos (crea la tabla si no existe)
try:
    init_db()
    print("Inicialización de la DB (init_db) completada.")
except Exception as e:
    print(f"Fallo crítico en init_db durante el arranque: {e}")

# Esto es para pruebas locales, Vercel no lo ejecuta directamente
if __name__ == '__main__':
    app.run(debug=True, port=5000)