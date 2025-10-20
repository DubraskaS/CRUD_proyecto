#CRUD PARA VERSION EN VERCEL (version en memoria)

from flask import Blueprint, jsonify, request
from .mock import USERS_MOCK, next_id


users_bp = Blueprint('users', __name__)

# 1. Mostrar usuarios (READ) y 6. Mostrar el total
@users_bp.route('/', methods=['GET'])
def get_users():
    # El frontend leerá este array para mostrar la lista
    return jsonify(USERS_MOCK)

# Crear usuario (CREATE)
@users_bp.route('/', methods=['POST'])
def create_user():
    global next_id
    data = request.get_json()
    #VERIFICACIÓN CRUCIAL: Si data es None, devolver error JSON inmediatamente.
    if data is None:
        return jsonify({'error': 'Missing request body or incorrect Content-Type (must be application/json)'}), 400
        
    #Validación de campos obligatorios
    if not all(k in data and data.get(k) is not None for k in ('name', 'email', 'age')):
        return jsonify({'error': 'Missing or empty data (name, email, age)'}), 400
    
    #Validacion de duplicados
    new_email = data.get('email')
    if new_email and any(user['email'] == new_email for user in USERS_MOCK):
        return jsonify({'error': f'Email {new_email} already exists.'}), 409
        
    new_user = {
        'id': next_id,
        'name': data.get('name'),
        'email': data.get('email'),
        'age': data.get('age')
    }
    USERS_MOCK.append(new_user)
    next_id += 1

    print(f"DEBUG: New ID: {next_id}, User: {new_user}")
    return jsonify(new_user), 201

# Eliminar usuario (DELETE) - Instrucción 3
@users_bp.route('/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    global USERS_MOCK
    initial_length = len(USERS_MOCK) 
    # Filtra el array, eliminando al usuario
    USERS_MOCK = [user for user in USERS_MOCK if user['id'] != user_id]
    if len(USERS_MOCK) < initial_length:
        return jsonify({'message': f'User {user_id} deleted (in memory)'})
    else:
        return jsonify({'error': 'User not found'}), 404

# 2. Buscar un usuario en específico (READ con filtro)
@users_bp.route('/search', methods=['GET'])
def search_user():
    # Obtiene el valor del parámetro ?q=nombre
    search_term = request.args.get('q', '').lower() 
    
    if not search_term:
        # Si no hay término de búsqueda, devuelve todos los usuarios
        return jsonify(USERS_MOCK) 

    # Filtra el array por nombre o email
    results = [user for user in USERS_MOCK 
               if search_term in user['name'].lower() or 
                  search_term in user['email'].lower()]
                  
    return jsonify(results)

# 4. Actualizar datos del usuario (UPDATE)
@users_bp.route('/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    data = request.json
    
    # 1. VERIFICACIÓN CRUCIAL: Si data es None, devolver error JSON inmediatamente.
    if data is None:
        return jsonify({'error': 'Missing request body or incorrect Content-Type (must be application/json)'}), 400
        
    for i, user in enumerate(USERS_MOCK):
        if user['id'] == user_id:
            # Encuentra el usuario y aplica los cambios (usando data.get(k, default))
            USERS_MOCK[i]['name'] = data.get('name', user['name'])
            USERS_MOCK[i]['email'] = data.get('email', user['email'])
            
            # Si 'age' existe y no es None, actualízalo
            if 'age' in data and data['age'] is not None:
                 USERS_MOCK[i]['age'] = data['age']
                 
            return jsonify(USERS_MOCK[i]), 200
            
    # Si el usuario no se encuentra
    return jsonify({'error': 'User not found'}), 404