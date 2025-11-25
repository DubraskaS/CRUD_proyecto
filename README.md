# CRUD de Usuarios: Persistencia Dinámica (React + Flask)

Este proyecto implementa una aplicación completa de Crear, Leer, Actualizar y Eliminar (CRUD) de usuarios. Utiliza **React** para la interfaz de usuario dinámica y **Flask** para el backend, y está diseñado para funcionar en dos modos de persistencia distintos, gestionados a través de ramas del repositorio.

## Enlaces de Despliegue (Vercel)

Accede a las dos versiones funcionales del proyecto a través de los siguientes enlaces de Vercel, basados en la rama desplegada:

| Versión | Rama | Estado de Persistencia | Enlace de Acceso |
| :--- | :--- | :--- | :--- |
| **Mock Data** | `main` | En Memoria (No persistente) | [Abrir Versión Mock Data](https://crud-proyecto-final.vercel.app/) |
| **AWS RDS** | `aws-rds` | PostgreSQL (Persistente) | [Abrir Versión AWS RDS](https://crud-proyecto-final-aws-rds.vercel.app/) |

---

## Tecnologías Clave

| Componente | Tecnología | Descripción |
| :--- | :--- | :--- |
| **Frontend** | React (Vite/CRA) | Interfaz de usuario dinámica y gestión del estado. |
| **Backend** | Flask | Servidor API ligero para manejar las peticiones CRUD. |
| **Despliegue** | Vercel | Plataforma serverless para alojar ambos componentes. |

## Estructura del Proyecto

El proyecto está organizado en dos directorios principales:

```
CRUD_PROYECTO_FINAL/
├── backend/                  # Contiene el código de la API de Flask
│   ├── routes/               # Lógica de las rutas (users.py)
│   ├── db/                   # Lógica de persistencia
│   ├── app.py                # Inicialización de la aplicación Flask y DB
│   └── wsgi.py               # Punto de entrada para Vercel
├── frontend/                 # Contiene el código de la aplicación React
│   └── src/
└── vercel.json               # Configuración crucial para el despliegue Híbrido
```

## VERSIONES DE PERSISTENCIA

El proyecto soporta dos versiones de la base de datos, cada una alojada en una rama distinta de este repositorio:

### A. Versión "main" (Mock Data en Memoria)

Esta versión es ideal para pruebas rápidas y demostraciones de la funcionalidad del CRUD sin requerir bases de datos externas.

| Característica | Detalle |
| :--- | :--- |
| **Rama** | `main` |
| **Persistencia** | **En Memoria** (Python Dictionaries) |
| **Archivo Clave** | `backend/db/mock.py` |
| **Comportamiento** | Los datos **se pierden** con cada reinicio de la función serverless de Vercel. |
| **Dependencias** | Mínimas (`Flask`, `flask-cors`). |

### B. Versión "aws-rds" (PostgreSQL Persistente)

Esta versión utiliza una base de datos PostgreSQL alojada en AWS RDS para la persistencia real de los datos.

| Característica | Detalle |
| :--- | :--- |
| **Rama** | `aws-rds` (o similar) |
| **Persistencia** | **AWS RDS (PostgreSQL)** |
| **Archivo Clave** | `backend/db/database.py` |
| **Comportamiento** | Los datos son **persistentes** a través de los despliegues y reinicios. |
| **Dependencias** | `psycopg2-binary`. |
| **Estado** | La conexión y el mapeo de datos están configurados, pero el despliegue final puede requerir ajustes en los **Grupos de Seguridad (Security Groups)** de AWS. |

## Instalación y Ejecución Local

Para ejecutar cualquiera de las versiones localmente:

### 1. Backend (Flask)

1. Navega a la carpeta del backend: `cd backend`

2. **Asegúrate de estar en la rama correcta** (main para Mock Data, aws-rds para PostgreSQL).

3. Instala las dependencias: `pip install -r requirements.txt`

   * **Nota:** Si usas la rama `aws-rds`, `requirements.txt` incluirá `psycopg2-binary`.

4. Inicia el servidor Flask: `python app.py`

   * El servidor estará disponible en `http://127.0.0.1:5000/`.

### 2. Frontend (React)

1. Abre una nueva terminal y navega a la carpeta del frontend: `cd frontend`

2. Instala las dependencias de Node.js: `npm install`

3. Inicia la aplicación React: `npm start` (o `npm run dev`)

   * La aplicación se comunicará con el backend localmente.

## Configuración de Despliegue en Vercel

### Despliegue Híbrido

El proyecto utiliza un despliegue **híbrido** en Vercel: el frontend de React se sirve como archivos estáticos, mientras que el backend de Flask se ejecuta como una **Serverless Function** en la ruta `/api/`. La configuración en `vercel.json` es crucial para este enrutamiento.

### Requerimientos para la Versión RDS

Si se despliega la rama `aws-rds`, es **OBLIGATORIO** configurar las variables de entorno en Vercel:

| Variable | Descripción |
| :--- | :--- |
| `RDS_HOSTNAME` | Punto de enlace de la instancia RDS. |
| `RDS_DB_NAME` | Nombre de la base de datos. |
| `RDS_USERNAME` | Usuario maestro de la DB. |
| `RDS_PASSWORD` | Contraseña. |
| `RDS_PORT` | Puerto (generalmente `5432`). |

Además, el **Grupo de Seguridad de AWS RDS** debe tener una regla de entrada que permita el tráfico TCP en el puerto `5432` desde el **`0.0.0.0/0`** (acceso público) para que Vercel pueda conectarse.