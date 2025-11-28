// frontend/src/UserCRUD.js (CÓDIGO MODIFICADO)
import React, { useState, useEffect, useCallback } from 'react';

// 💡 CORRECCIÓN 1: Leer la URL de la API de la variable de entorno de Vercel/Vite
const API_BASE_URL = import.meta.env.VITE_API_URL; 

// Verificación para desarrollo (opcional)
if (!API_BASE_URL) {
    console.error("VITE_API_URL no está definida. Usando fallback de prueba.");
    // Fallback: Si no está definida (solo en entorno local/dev), usar localhost
    // NOTA: En Vercel, esta variable DEBE estar configurada para que funcione.
    // API_BASE_URL = 'http://localhost:5000'; 
}


const UserCRUD = () => {
    const [users, setUsers] = useState([]);
    const [name, setName] = useState('');
    const [email, setEmail] = useState('');
    const [age, setAge] = useState('');
    const [search, setSearch] = useState('');
    const [editingUser, setEditingUser] = useState(null);

    // ------------------------------------
    // LECTURA DE DATOS (READ ALL)
    // ------------------------------------
    const fetchUsers = useCallback(async () => {
        // 💡 CORRECCIÓN 2: Usar API_BASE_URL + /api/usuarios
        // Si API_BASE_URL ya termina en /api, solo hay que agregar /users
        const url = `${API_BASE_URL}/users`; 
        
        try {
            const response = await fetch(url);
            
            if (!response.ok) { 
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            setUsers(data);
        } catch (error) {
            console.error("Error al obtener usuarios:", error);
            // Mensaje de ayuda si falla la conexión
            if (error.message.includes('Failed to fetch')) {
                 alert("Error de Conexión: La API (Vercel Backend) no responde. Revisa VITE_API_URL y CORS.");
            }
        }
    }, []);

    useEffect(() => {
        fetchUsers();
    }, [fetchUsers]); 

    // ------------------------------------
    // 5. TRUNCAR NOMBRE (Lógica Frontend)
    // ------------------------------------
    const truncateName = (name) => {
        if (!name || name.length <= 10) {
            return name;
        }
        return name.substring(0, 7) + '...';
    };

    // ------------------------------------
    // 2. BUSCAR UN USUARIO (READ FILTER)
    // ------------------------------------
    const handleSearch = async () => {
        // 💡 CORRECCIÓN 3: Usar API_BASE_URL como prefijo
        const searchURL = `${API_BASE_URL}/users/search?q=${search}`;
        try {
            const response = await fetch(searchURL);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            setUsers(data);
        } catch (error) {
            console.error("Error en la búsqueda:", error);
            setUsers([]);
        }
    };
    
    useEffect(() => {
        if (!search) {
            fetchUsers();
        }
    }, [search, fetchUsers]);


    // ------------------------------------
    // 3. ELIMINAR USUARIO (DELETE)
    // ------------------------------------
    const handleDelete = async (id) => {
        if (!window.confirm(`¿Seguro que quieres eliminar al usuario con ID ${id}?`)) return;
        
        // 💡 CORRECCIÓN 4: Usar API_BASE_URL como prefijo
        try {
            const response = await fetch(`${API_BASE_URL}/users/${id}`, {
                method: 'DELETE',
            });
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            alert(`Usuario ${id} eliminado correctamente.`);
            fetchUsers();
        } catch (error) {
            console.error("Error al eliminar:", error);
            alert("Error al intentar eliminar el usuario.");
        }
    };


    // ------------------------------------
    // 4. CREAR/ACTUALIZAR (CREATE/UPDATE)
    // ------------------------------------
    const handleSubmit = async (e) => {
        e.preventDefault();
        const userData = { name, email, age: parseInt(age) };

        // Verificaciòn para no enviar strings vacios
        if (!name || !email || !age) {
            alert("Todos los campos son obligatorios.");
            return; 
        }
        
        const method = editingUser ? 'PUT' : 'POST';
        // 💡 CORRECCIÓN 5: Usar API_BASE_URL como prefijo en la URL
        const url = editingUser ? `${API_BASE_URL}/users/${editingUser.id}` : `${API_BASE_URL}/users`;

        try {
            const response = await fetch(url, {
                method: method,
                headers: {
                    // El Content-Type ya estaba CORRECTO, ¡bien!
                    'Content-Type': 'application/json',
                },
                // El JSON.stringify ya estaba CORRECTO, ¡bien!
                body: JSON.stringify(userData), 
            });

            if (response.ok) {
                alert(`Usuario ${editingUser ? 'actualizado' : 'creado'} con éxito!`);
                setEditingUser(null);
                fetchUsers();
            } else {
                let errorMessage = `HTTP error! Status: ${response.status}`;
                
                try {
                    const errorData = await response.json();
                    // Captura el mensaje de error del backend (ej: "Faltan datos requeridos...")
                    errorMessage = errorData.error || errorMessage;
                } catch (jsonError) {
                    console.error("No se pudo leer el JSON de error.");
                }

                throw new Error(errorMessage);
            }

        } catch (error) {
            console.error(`Error al ${editingUser ? 'actualizar' : 'crear'}:`, error);
            alert(`Error: ${error.message}`);
        }
            
        // Limpiar formulario
        setName(''); setEmail(''); setAge('');
    };

    // Función para iniciar el modo de edición
    const startEdit = (user) => {
        setEditingUser(user);
        setName(user.name);
        setEmail(user.email);
        setAge(String(user.age));
    };

    // ------------------------------------
    // RENDERIZADO (El JSX)
    // ------------------------------------
    return (
        <div className="main-container"> 
            
            {/* 💡 2. Contenedor de las dos columnas */}
            <div className="content-columns"> 
                
                {/* Panel Izquierdo: Crear y Buscar */}
                <div className="left-panel">
                    <h1>CRUD de Usuarios Dsolorzano</h1>
                    {/* 6. MOSTRAR EL TOTAL DE USUARIOS */}
                    <h3 className="total-users">Total de Usuarios: {users.length}</h3>

                    {/* FORMULARIO DE CREACIÓN/EDICIÓN */}
                    <h2>{editingUser ? 'Editar Usuario' : 'Crear Nuevo Usuario'}</h2>
                    <form onSubmit={handleSubmit}>
                        <div className="form-group">
                            <input type="text" value={name} onChange={(e) => setName(e.target.value)} placeholder="Nombre" required />
                        </div>
                        <div className="form-group">
                            <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="Correo" required />
                        </div>
                        <div className="form-group">
                            <input type="number" value={age} onChange={(e) => setAge(e.target.value)} placeholder="Edad" required />
                        </div>
                        <div className="button-group">
                            <button type="submit">{editingUser ? 'Guardar Cambios' : 'Crear Usuario'}</button>
                            {editingUser && 
                                <button 
                                    type="button" 
                                    onClick={() => {setEditingUser(null); setName(''); setEmail(''); setAge('');}}
                                >
                                    Cancelar
                                </button>
                            }
                        </div>
                    </form>

                    <hr/>

                    {/* BARRA DE BÚSQUEDA */}
                    <h2>Buscar Usuario</h2>
                    <div className="search-group">
                        <input 
                            type="text" 
                            value={search} 
                            onChange={(e) => setSearch(e.target.value)} 
                            placeholder="Buscar por nombre o correo..."
                            onKeyUp={handleSearch} 
                        />
                    </div>
                </div>

                {/* Panel Derecho: Lista de Usuarios */}
                <div className="right-panel">
                    <h2>Lista de Usuarios</h2>
                    <table>
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Nombre</th>
                                <th>Correo</th>
                                <th>Edad</th>
                                <th>Acciones</th>
                            </tr>
                        </thead>
                        <tbody>
                            {users.map(user => (
                                <tr key={user.id}>
                                    <td>{user.id}</td>
                                    <td>{truncateName(user.name)}</td> 
                                    <td>{user.email}</td>
                                    <td>{user.age}</td>
                                    <td>
                                        <div className="button-group">
                                            <button onClick={() => startEdit(user)}>Editar</button>
                                            <button onClick={() => handleDelete(user.id)}>Eliminar</button>
                                        </div>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
};

export default UserCRUD;