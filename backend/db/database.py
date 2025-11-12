import psycopg2
import os
from typing import List, Dict, Any

# --- Configuración de Conexión (Lee Variables de Entorno) ---
DB_HOST = os.environ.get('database-crud.chum8swwq3kx.us-east-2.rds.amazonaws.com')
DB_NAME = os.environ.get('-')
DB_USER = os.environ.get('postgres')
DB_PASSWORD = os.environ.get('crudclave')

def get_db_connection():
    """Obtiene y retorna una conexión a la base de datos de AWS RDS."""
    # Verificación de credenciales
    if not all([DB_HOST, DB_NAME, DB_USER, DB_PASSWORD]):
        print("ERROR: FALTAN VARIABLES DE ENTORNO RDS (HOST, NAME, USER, PASSWORD).")
        return None
        
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        return conn
    except Exception as e:
        # En un entorno de producción, es clave registrar este error
        print(f"Error al conectar con la base de datos de RDS: {e}")
        return None 

def init_db():
    """
    Inicializa el esquema de la base de datos (crea la tabla 'users')
    siempre y cuando la conexión sea exitosa.
    """
    conn = get_db_connection()
    if conn is None:
        return

    # Usamos un bloque with para asegurar que el cursor se cierre automáticamente
    with conn.cursor() as cur:
        # Creamos la tabla 'users'
        cur.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                nombre VARCHAR(100) NOT NULL,
                correo VARCHAR(100) NOT NULL UNIQUE,
                edad INTEGER NOT NULL
            );
        ''')
        conn.commit()
    print("ÉXITO: La tabla 'users' ha sido inicializada/verificada.")
    conn.close()

# CRÍTICO: Inicializa la base de datos al inicio.
init_db()

# --- Funciones de Ayuda para Mapeo de Datos ---
def map_row_to_dict(row, cursor) -> Dict[str, Any]:
    """Mapea una fila de datos a un diccionario usando los nombres de las columnas."""
    columns = [desc[0] for desc in cursor.description]
    return dict(zip(columns, row))

# --- Operaciones CRUD Adaptadas a PostgreSQL ---

def get_all_users() -> List[Dict[str, Any]]:
    conn = get_db_connection()
    if conn is None: return []

    with conn.cursor() as cur:
        cur.execute('SELECT id, nombre, correo, edad FROM users;')
        rows = cur.fetchall()
        users = [map_row_to_dict(row, cur) for row in rows]
    conn.close()
    return users

def get_user_by_id(user_id: int) -> Dict[str, Any] | None:
    conn = get_db_connection()
    if conn is None: return None

    with conn.cursor() as cur:
        cur.execute('SELECT id, nombre, correo, edad FROM users WHERE id = %s;', (user_id,))
        row = cur.fetchone()
        if row:
            user = map_row_to_dict(row, cur)
        else:
            user = None
    conn.close()
    return user

def create_new_user(nombre: str, correo: str, edad: int) -> Dict[str, Any] | None:
    conn = get_db_connection()
    if conn is None: return None
    
    try:
        with conn.cursor() as cur:
            # RETURNING id devuelve el ID que PostgreSQL acaba de generar
            cur.execute(
                'INSERT INTO users (nombre, correo, edad) VALUES (%s, %s, %s) RETURNING id;',
                (nombre, correo, edad)
            )
            new_id = cur.fetchone()[0]
        conn.commit()
        conn.close()
        return get_user_by_id(new_id)
    except psycopg2.IntegrityError:
        # Maneja el caso de correo duplicado
        conn.rollback() 
        conn.close()
        return None 

def update_existing_user(user_id: int, nombre: str, correo: str, edad: int) -> Dict[str, Any] | None:
    conn = get_db_connection()
    if conn is None: return None

    try:
        with conn.cursor() as cur:
            cur.execute(
                'UPDATE users SET nombre = %s, correo = %s, edad = %s WHERE id = %s;',
                (nombre, correo, edad, user_id)
            )
        conn.commit()
        conn.close()
        return get_user_by_id(user_id) 
    except Exception as e:
        conn.rollback()
        conn.close()
        print(f"Error al actualizar usuario: {e}")
        return None

def delete_user_by_id(user_id: int) -> bool:
    conn = get_db_connection()
    if conn is None: return False

    with conn.cursor() as cur:
        cur.execute('DELETE FROM users WHERE id = %s;', (user_id,))
        rows_deleted = cur.rowcount 
    conn.commit()
    conn.close()
    return rows_deleted > 0

def search_users(query: str) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    if conn is None: return []

    with conn.cursor() as cur:
        search_term = f"%{query}%"
        # Búsqueda ILIKE (insensible a mayúsculas/minúsculas)
        cur.execute(
            'SELECT id, nombre, correo, edad FROM users WHERE nombre ILIKE %s OR correo ILIKE %s;',
            (search_term, search_term)
        )
        rows = cur.fetchall()
        users = [map_row_to_dict(row, cur) for row in rows]
    conn.close()
    return users