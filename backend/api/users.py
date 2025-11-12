from flask import Blueprint, jsonify, request

from db.database import get_all_users, create_new_user, get_user_by_id, update_existing_user, delete_user_by_id, search_users

# Crea el Blueprint, que es el módulo de rutas para usuarios
users_bp = Blueprint('users', __name__)

# ----------------------------------------------------------------------
# RUTA: /api/users/ (GET: Obtener todos, POST: Crear nuevo)
# ----------------------------------------------------------------------
@users_bp.route('/', methods=['GET', 'POST'])
def handle_users():
    """Maneja las solicitudes GET (obtener todos) y POST (crear nuevo)."""
    
    # --- GET: Obtener todos los usuarios ---
    if request.method == 'GET':
        # La función get_all_users en db/database.py ya se encarga 
        # de mapear las tuplas de PostgreSQL a diccionarios (JSON)
        users = get_all_users()
        
        # Devuelve directamente la lista de diccionarios/usuarios
        return jsonify(users), 200

    # --- POST: Crear un nuevo usuario ---
    elif request.method == 'POST':
        try:
            data = request.get_json()
            nombre = data.get('nombre')
            correo = data.get('correo')
            edad = data.get('edad')

            # Validar datos
            if not nombre or not correo or not edad:
                return jsonify({"error": "Faltan campos obligatorios (nombre, correo, edad)."}), 400

            try:
                edad = int(edad)
            except ValueError:
                return jsonify({"error": "La edad debe ser un número entero."}), 400

            # Crear usuario en la DB
            new_user = create_new_user(nombre, correo, edad)

            if new_user:
                # Si se creó exitosamente, retorna el objeto del nuevo usuario y 201 Created
                return jsonify(new_user), 201
            else:
                # Esto cubre el caso de violación de unicidad (correo ya existe)
                return jsonify({"error": "Error de integridad: el correo ya existe o fallan datos."}), 409
        
        except Exception as e:
            # Error genérico en la solicitud
            print(f"ERROR en POST /: {e}")
            return jsonify({"error": "Error interno del servidor al crear usuario."}), 500

# ----------------------------------------------------------------------
# RUTA: /api/users/<user_id> (GET, PUT, DELETE)
# ----------------------------------------------------------------------
@users_bp.route('/<int:user_id>', methods=['GET', 'PUT', 'DELETE'])
def handle_user_by_id(user_id):
    """Maneja las solicitudes GET, PUT y DELETE para un usuario específico."""

    # --- GET: Obtener usuario por ID ---
    if request.method == 'GET':
        user = get_user_by_id(user_id)
        if user:
            return jsonify(user), 200
        else:
            return jsonify({"error": "Usuario no encontrado."}), 404

    # --- PUT: Actualizar usuario ---
    elif request.method == 'PUT':
        data = request.get_json()
        nombre = data.get('nombre')
        correo = data.get('correo')
        edad = data.get('edad')

        if not nombre or not correo or not edad:
            return jsonify({"error": "Faltan campos obligatorios para actualizar."}), 400

        try:
            edad = int(edad)
        except ValueError:
            return jsonify({"error": "La edad debe ser un número entero."}), 400

        updated_user = update_existing_user(user_id, nombre, correo, edad)

        if updated_user:
            return jsonify(updated_user), 200
        else:
            return jsonify({"error": "Usuario no encontrado o conflicto de datos (ej. correo ya existe)."}), 409

    # --- DELETE: Eliminar usuario ---
    elif request.method == 'DELETE':
        if delete_user_by_id(user_id):
            return jsonify({"message": f"Usuario con ID {user_id} eliminado."}), 200
        else:
            return jsonify({"error": "Usuario no encontrado o fallo al eliminar."}), 404

# ----------------------------------------------------------------------
# RUTA: /api/users/search (GET)
# ----------------------------------------------------------------------
@users_bp.route('/search', methods=['GET'])
def handle_search():
    """Busca usuarios por nombre o correo."""
    query = request.args.get('q')
    if not query:
        return jsonify({"error": "Falta el parámetro de búsqueda 'q'."}), 400

    results = search_users(query)
    # Devuelve la lista de resultados de búsqueda
    return jsonify(results), 200