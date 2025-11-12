#CRUD PARA VERSION EN AWS (version en bd)

from flask import Blueprint, jsonify, request
from functools import wraps
import json

# Importamos las funciones CRUD del nuevo módulo de base de datos 'database.py'
from db.database import get_all_users, get_user_by_id, create_new_user, update_existing_user, delete_user_by_id, search_users

users_bp = Blueprint('users', __name__)

def validate_user_data(f):
    """
    Decorador para validar que los datos del usuario (nombre, correo, edad)
    sean correctos y estén presentes en la petición JSON.
    """
    @wraps(f)
    def wrapper(*args, **kwargs):
        data = request.get_json(silent=True)
        if not data:
            return jsonify({"error": "No se recibieron datos o formato JSON incorrecto"}), 400
        required_fields = ['nombre', 'correo', 'edad']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"El campo '{field}' es requerido."}), 400
        if not isinstance(data['edad'], int) or data['edad'] <= 0:
            return jsonify({"error": "La edad debe ser un número entero positivo."}), 400
        return f(*args, **kwargs)
    return wrapper

# Obtener todos los usuarios / Crear nuevo usuario
@users_bp.route('/', methods=['GET', 'POST'])
def users():
    """Maneja GET (obtener todos) y POST (crear nuevo)."""
    if request.method == 'GET':
        # Llama a la función que consulta la DB
        return jsonify(get_all_users())
    
    # POST
    @validate_user_data
    def create():
        data = request.get_json()
        # Llama a la función que inserta en la DB
        new_user = create_new_user(data['nombre'], data['correo'], data['edad'])
        
        if new_user is None:
             # Retorna un error 409 si falla la restricción UNIQUE (correo)
             return jsonify({"error": "Error de integridad: el correo ya existe o faltan datos."}), 409
            
        return jsonify(new_user), 201

    return create()

# Buscar usuarios por nombre o correo
@users_bp.route('/search', methods=['GET'])
def search():
    """Busca usuarios usando el parámetro 'q' de la URL."""
    query = request.args.get('q', '')
    if not query:
        return jsonify({"error": "Parámetro 'q' de búsqueda es requerido."}), 400
    # Llama a la función que busca en la DB
    results = search_users(query)
    return jsonify(results)

# Obtener, Actualizar o Eliminar usuario por ID
@users_bp.route('/<int:user_id>', methods=['GET', 'PUT', 'DELETE'])
def user_detail(user_id):
    """Maneja GET, PUT y DELETE para un usuario específico por ID."""
    # Primero verifica si el usuario existe en la DB
    user = get_user_by_id(user_id)
    if not user:
        return jsonify({"error": f"Usuario con ID {user_id} no encontrado"}), 404

    if request.method == 'GET':
        return jsonify(user)

    if request.method == 'DELETE':
        # Llama a la función que elimina de la DB
        success = delete_user_by_id(user_id)
        if success:
            return '', 204 # Retorna 204 No Content si fue exitoso
        else:
            return jsonify({"error": f"Error al eliminar usuario con ID {user_id}."}), 500

    # PUT
    @validate_user_data
    def update():
        data = request.get_json()
        # Llama a la función que actualiza en la DB
        updated_user = update_existing_user(user_id, data['nombre'], data['correo'], data['edad'])
        
        if updated_user is None:
            # Esto puede ocurrir si hubo un fallo interno
            return jsonify({"error": f"Error al actualizar usuario con ID {user_id}."}), 500 
            
        return jsonify(updated_user)
    
    return update()