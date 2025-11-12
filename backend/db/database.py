import psycopg2
import os
from typing import List, Dict, Any

# --- Variables de control para inicialización ---
DB_INITIALIZED = False

# --- Configuración de Conexión (Lee Variables de Entorno de Vercel) ---
DB_HOST = os.environ.get('RDS_HOSTNAME')
DB_NAME = os.environ.get('RDS_DB_NAME')
DB_USER = os.environ.get('RDS_USERNAME')
DB_PASSWORD = os.environ.get('RDS_PASSWORD')
DB_PORT = os.environ.get('RDS_PORT', 5432) 

def init_db():
    """
    Inicializa el esquema de la base de datos (crea la tabla 'users').
    Esta función NO debe llamarse si no hay conexión exitosa.
    """
    global DB_INITIALIZED
    if DB_INITIALIZED:
        return

    conn = get_db_connection()
    if conn is None: 
        print("ADVERTENCIA: No se pudo inicializar la DB porque la conexión falló.")
        return

    try:
        conn.autocommit = True
        with conn.cursor() as cur:
            # Creamos la tabla 'users' si no existe
            cur.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    nombre VARCHAR(100) NOT NULL,
                    correo VARCHAR(100) NOT NULL UNIQUE,
                    edad INTEGER NOT NULL
                );
            ''')
        print("ÉXITO: La tabla 'users' ha sido inicializada/verificada correctamente.")
        DB_INITIALIZED = True # Marca como inicializada solo si tiene éxito
    except Exception as e:
        print(f"ERROR CRÍTICO durante init_db (creación de tabla): {e}")
    finally:
        if conn and conn.closed == 0:
            conn.close()

def get_db_connection():
    """Obtiene y retorna una conexión a la base de datos de AWS RDS."""
    
    # 1. Verificación de credenciales
    if not all([DB_HOST, DB_NAME, DB_USER, DB_PASSWORD]):
        print("ERROR CRÍTICO: FALTAN VARIABLES DE ENTORNO RDS. Revisar Vercel.")
        return None
        
    try:
        # 2. Conexión con todos los parámetros requeridos
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            port=DB_PORT
            # CRÍTICO: Añadir un timeout bajo para evitar que Vercel espere 
            # eternamente si falla la red, aunque ya sabemos que funciona localmente.
            # connect_timeout=5 
        )
        return conn
    except Exception as e:
        # Imprime el error si falla la conexión (red, credenciales, etc.)
        print(f"ERROR: Fallo al conectar a la DB.")
        print(f"Detalle del error: {e}")
        return None 

# CRÍTICO: Eliminamos la llamada init_db() de aquí. Ahora se llamará condicionalmente.
# init_db()

# --- Funciones de Ayuda para Mapeo de Datos ---
def map_row_to_dict(row, cursor) -> Dict[str, Any]:
    """Mapea una fila de datos a un diccionario usando los nombres de las columnas."""
    columns = [desc[0] for desc in cursor.description]
    return dict(zip(columns, row))

# --- Operaciones CRUD Adaptadas a PostgreSQL ---
# CRÍTICO: Todas las funciones CRUD ahora llaman a init_db() al inicio.

def get_all_users() -> List[Dict[str, Any]]:
    init_db() # Intenta inicializar antes de la operación
    conn = get_db_connection()
    if conn is None: return []

    try:
        with conn.cursor() as cur:
            cur.execute('SELECT id, nombre, correo, edad FROM users;')
            rows = cur.fetchall()
            users = [map_row_to_dict(row, cur) for row in rows]
        return users
    except Exception as e:
        print(f"Error en get_all_users: {e}")
        return []
    finally:
        if conn and conn.closed == 0:
            conn.close()

def get_user_by_id(user_id: int) -> Dict[str, Any] | None:
    init_db() # Intenta inicializar antes de la operación
    conn = get_db_connection()
    if conn is None: return None

    try:
        with conn.cursor() as cur:
            cur.execute('SELECT id, nombre, correo, edad FROM users WHERE id = %s;', (user_id,))
            row = cur.fetchone()
            user = map_row_to_dict(row, cur) if row else None
        return user
    except Exception as e:
        print(f"Error en get_user_by_id: {e}")
        return None
    finally:
        if conn and conn.closed == 0:
            conn.close()


def create_new_user(nombre: str, correo: str, edad: int) -> Dict[str, Any] | None:
    init_db() # Intenta inicializar antes de la operación
    conn = get_db_connection()
    if conn is None: return None
    
    try:
        with conn.cursor() as cur:
            cur.execute(
                'INSERT INTO users (nombre, correo, edad) VALUES (%s, %s, %s) RETURNING id;',
                (nombre, correo, edad)
            )
            new_id = cur.fetchone()[0]
        conn.commit()
        
        return {'id': new_id, 'nombre': nombre, 'correo': correo, 'edad': edad}

    except psycopg2.IntegrityError:
        conn.rollback() 
        return None 
    except Exception as e:
        print(f"Error inesperado al crear usuario: {e}")
        conn.rollback()
        return None
    finally:
        if conn and conn.closed == 0:
            conn.close()

def update_existing_user(user_id: int, nombre: str, correo: str, edad: int) -> Dict[str, Any] | None:
    init_db() # Intenta inicializar antes de la operación
    conn = get_db_connection()
    if conn is None: return None

    try:
        with conn.cursor() as cur:
            cur.execute(
                'UPDATE users SET nombre = %s, correo = %s, edad = %s WHERE id = %s;',
                (nombre, correo, edad, user_id)
            )
        conn.commit()
        return get_user_by_id(user_id) 
    except Exception as e:
        conn.rollback()
        print(f"Error al actualizar usuario: {e}")
        return None
    finally:
        if conn and conn.closed == 0:
            conn.close()

def delete_user_by_id(user_id: int) -> bool:
    init_db() # Intenta inicializar antes de la operación
    conn = get_db_connection()
    if conn is None: return False

    try:
        with conn.cursor() as cur:
            cur.execute('DELETE FROM users WHERE id = %s;', (user_id,))
            rows_deleted = cur.rowcount 
        conn.commit()
        return rows_deleted > 0
    except Exception as e:
        print(f"Error al eliminar usuario: {e}")
        conn.rollback()
        return False
    finally:
        if conn and conn.closed == 0:
            conn.close()

def search_users(query: str) -> List[Dict[str, Any]]:
    init_db() # Intenta inicializar antes de la operación
    conn = get_db_connection()
    if conn is None: return []

    try:
        with conn.cursor() as cur:
            search_term = f"%{query}%"
            cur.execute(
                'SELECT id, nombre, correo, edad FROM users WHERE nombre ILIKE %s OR correo ILIKE %s;',
                (search_term, search_term)
            )
            rows = cur.fetchall()
            users = [map_row_to_dict(row, cur) for row in rows]
        return users
    except Exception as e:
        print(f"Error en search_users: {e}")
        return []
    finally:
        if conn and conn.closed == 0:
            conn.close()