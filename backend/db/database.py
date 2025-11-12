import psycopg2
import os
from typing import List, Dict, Any
from contextlib import contextmanager

# --- Configuración de Conexión (Lee Variables de Entorno) ---
DB_HOST = os.environ.get('DB_HOST')
DB_NAME = os.environ.get('DB_NAME')
DB_USER = os.environ.get('DB_USER')
DB_PASSWORD = os.environ.get('DB_PASSWORD')
# El puerto debe ser leído también, usando 5432 como valor por defecto.
DB_PORT = os.environ.get('RDS_PORT', 5432) 

# ----------------------------------------------------------------------
# Conexión y Context Manager
# ----------------------------------------------------------------------

@contextmanager
def get_db_connection():
    """
    Función que devuelve una conexión a la base de datos utilizando un 
    context manager (bloque 'with'). 
    Se encarga de cerrar la conexión automáticamente.
    """
    conn = None
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            port=DB_PORT
        )
        yield conn
    except Exception as e:
        print(f"ERROR DE CONEXIÓN A RDS: {e}")
        # No re-lanzamos la excepción aquí; solo registramos el error de conexión.
        yield None
    finally:
        if conn and not conn.closed:
            conn.close()

def init_db():
    """Inicializa la tabla 'users' si no existe."""
    try:
        with get_db_connection() as conn:
            if conn is None:
                print("INIT_DB FALLIDO: No se pudo establecer la conexión a la base de datos.")
                return
            
            with conn.cursor() as cur:
                cur.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                        id SERIAL PRIMARY KEY,
                        nombre VARCHAR(100) NOT NULL,
                        correo VARCHAR(100) NOT NULL UNIQUE,
                        edad INTEGER NOT NULL
                    );
                ''')
                conn.commit()
                print("Tabla 'users' verificada/creada exitosamente.")
                
    except Exception as e:
        print(f"ERROR al inicializar la DB: {e}")

# ----------------------------------------------------------------------
# Funciones CRUD
# ----------------------------------------------------------------------

def get_all_users():
    """Obtiene todos los usuarios y los retorna como una lista de diccionarios."""
    users = []
    try:
        with get_db_connection() as conn:
            if conn is None:
                return users # Retorna lista vacía si no hay conexión
                
            with conn.cursor() as cur:
                # 1. Ejecutar consulta
                cur.execute("SELECT id, nombre, correo, edad FROM users ORDER BY id DESC")
                users_raw = cur.fetchall()
                
                # 2. Mapear resultados (¡LA CLAVE DE LA CORRECCIÓN!)
                # Esto convierte los resultados de la base de datos (tuplas)
                # a diccionarios que el Frontend de React espera.
                for user in users_raw:
                    users.append({
                        'id': user[0],
                        'nombre': user[1],
                        'correo': user[2],
                        'edad': user[3]
                    })
                
    except Exception as e:
        print(f"ERROR en get_all_users: {e}")
        
    return users # Retorna lista de diccionarios

def get_user_by_id(user_id):
    """Obtiene un usuario por su ID."""
    user = None
    try:
        with get_db_connection() as conn:
            if conn is None:
                return None
                
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT id, nombre, correo, edad FROM users WHERE id = %s;",
                    (user_id,)
                )
                user_raw = cur.fetchone()
                
                if user_raw:
                    # Mapear el resultado único
                    user = {
                        'id': user_raw[0],
                        'nombre': user_raw[1],
                        'correo': user_raw[2],
                        'edad': user_raw[3]
                    }
    except Exception as e:
        print(f"ERROR en get_user_by_id: {e}")
        
    return user


def create_new_user(nombre, correo, edad):
    """Inserta un nuevo usuario y retorna el objeto del nuevo usuario (incluyendo el ID)."""
    new_user = None
    try:
        with get_db_connection() as conn:
            if conn is None:
                return None
                
            with conn.cursor() as cur:
                cur.execute(
                    'INSERT INTO users (nombre, correo, edad) VALUES (%s, %s, %s) RETURNING id, nombre, correo, edad;',
                    (nombre, correo, edad)
                )
                new_user_raw = cur.fetchone()
                conn.commit()
                
                if new_user_raw:
                    new_user = {
                        'id': new_user_raw[0],
                        'nombre': new_user_raw[1],
                        'correo': new_user_raw[2],
                        'edad': new_user_raw[3]
                    }
                    
    except psycopg2.errors.UniqueViolation:
        # Esto captura el error si el correo ya existe
        print(f"ADVERTENCIA: Correo '{correo}' ya existe.")
        return None # Retorna None si hay violación de unicidad
    except Exception as e:
        print(f"ERROR en create_new_user: {e}")
        return None
        
    return new_user


def update_existing_user(user_id, nombre, correo, edad):
    """Actualiza un usuario existente y retorna el objeto actualizado."""
    updated_user = None
    try:
        with get_db_connection() as conn:
            if conn is None:
                return None
                
            with conn.cursor() as cur:
                cur.execute(
                    'UPDATE users SET nombre = %s, correo = %s, edad = %s WHERE id = %s RETURNING id, nombre, correo, edad;',
                    (nombre, correo, edad, user_id)
                )
                updated_user_raw = cur.fetchone()
                conn.commit()
                
                if updated_user_raw:
                    updated_user = {
                        'id': updated_user_raw[0],
                        'nombre': updated_user_raw[1],
                        'correo': updated_user_raw[2],
                        'edad': updated_user_raw[3]
                    }

    except psycopg2.errors.UniqueViolation:
        print(f"ADVERTENCIA: Correo '{correo}' ya existe.")
        return None
    except Exception as e:
        print(f"ERROR en update_existing_user: {e}")
        return None
        
    return updated_user


def delete_user_by_id(user_id):
    """Elimina un usuario por ID."""
    try:
        with get_db_connection() as conn:
            if conn is None:
                return False
                
            with conn.cursor() as cur:
                cur.execute(
                    'DELETE FROM users WHERE id = %s;',
                    (user_id,)
                )
                deleted_rows = cur.rowcount
                conn.commit()
                
                return deleted_rows > 0 # Retorna True si se eliminó al menos una fila
                
    except Exception as e:
        print(f"ERROR en delete_user_by_id: {e}")
        return False


def search_users(query):
    """Busca usuarios por nombre o correo (parcial y sin distinción de mayúsculas/minúsculas)."""
    results = []
    # Crear un patrón de búsqueda que pueda coincidir parcialmente
    search_pattern = f'%{query.lower()}%' 
    
    try:
        with get_db_connection() as conn:
            if conn is None:
                return results
                
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, nombre, correo, edad FROM users 
                    WHERE LOWER(nombre) LIKE %s OR LOWER(correo) LIKE %s
                    ORDER BY id DESC;
                    """,
                    (search_pattern, search_pattern)
                )
                users_raw = cur.fetchall()
                
                for user in users_raw:
                    results.append({
                        'id': user[0],
                        'nombre': user[1],
                        'correo': user[2],
                        'edad': user[3]
                    })
                    
    except Exception as e:
        print(f"ERROR en search_users: {e}")
        
    return results

# Inicializa la DB al cargar el módulo (puede ser necesario para el entorno Vercel)
init_db()