// frontend/src/UserCRUD.js (Usando fetch)
import React, { useState, useEffect, useCallback } from 'react';
import { RefreshCw, Search, Plus, Edit, Trash2, XCircle, CheckCircle, Info, AlertTriangle } from 'lucide-react';

// CRÍTICO: Lee la URL de la API desde las variables de entorno de Vercel/React.
// Si no está definida (ej. en desarrollo), usa una ruta relativa para probar localmente.
const API_BASE_URL = process.env.REACT_APP_API_URL || '/api';

function UserCRUD() {
    const [users, setUsers] = useState([]);
    const [newUser, setNewUser] = useState({ nombre: '', correo: '', edad: '' });
    const [editingUser, setEditingUser] = useState(null);
    const [searchQuery, setSearchQuery] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [message, setMessage] = useState(''); // Para mostrar alertas
    const [showConfirm, setShowConfirm] = useState(null); // Para el diálogo de confirmación

    // Función para mostrar mensajes de alerta
    const showAlert = (msg, type = 'info') => {
        setMessage({ text: msg, type });
        setTimeout(() => setMessage(''), 5000);
    };

    // ------------------------------------
    // 1. OBTENER USUARIOS (READ)
    // ------------------------------------
    const fetchUsers = useCallback(async () => {
        setIsLoading(true);
        try {
            const url = searchQuery
                ? `${API_BASE_URL}/users/search?query=${searchQuery}`
                : `${API_BASE_URL}/users`;

            const response = await fetch(url);

            if (!response.ok) {
                let errorMessage = `Error HTTP! Estado: ${response.status}`;
                try {
                    const errorData = await response.json();
                    errorMessage = errorData.error || errorMessage;
                } catch (jsonError) {
                    console.error("La respuesta de error no fue JSON:", response.statusText);
                }
                throw new Error(errorMessage);
            }

            const data = await response.json();
            setUsers(data);
            setIsLoading(false);
        } catch (error) {
            console.error('Error al obtener usuarios:', error);
            showAlert(`Error al cargar datos: ${error.message}`, 'error');
            setIsLoading(false);
            setUsers([]); // Limpiar lista en caso de error
        }
    }, [searchQuery]);

    useEffect(() => {
        fetchUsers();
    }, [fetchUsers]);

    // ------------------------------------
    // 2. CREAR/ACTUALIZAR (CREATE/UPDATE)
    // ------------------------------------
    const handleSubmit = async (e) => {
        e.preventDefault();

        const userToSave = editingUser || newUser;
        const method = editingUser ? 'PUT' : 'POST';
        const url = editingUser ? `${API_BASE_URL}/users/${editingUser.id}` : `${API_BASE_URL}/users`;

        // Validaciones básicas en el frontend
        if (!userToSave.nombre || !userToSave.correo || !userToSave.edad) {
            showAlert('Todos los campos son obligatorios. Por favor, complete el formulario.', 'warning');
            return;
        }
        if (isNaN(parseInt(userToSave.edad)) || parseInt(userToSave.edad) < 1) {
            showAlert('La edad debe ser un número entero positivo.', 'warning');
            return;
        }

        setIsLoading(true);

        // Datos a enviar
        const dataToSend = {
            nombre: userToSave.nombre,
            correo: userToSave.correo,
            edad: parseInt(userToSave.edad)
        };
        
        console.log("Datos enviados al API:", dataToSend); // Debugging

        try {
            const response = await fetch(url, {
                method: method,
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(dataToSend),
            });

            if (response.ok) {
                showAlert(`Usuario ${editingUser ? 'actualizado' : 'creado'} con éxito!`, 'success');
                setEditingUser(null);
                setNewUser({ nombre: '', correo: '', edad: '' });
                fetchUsers();
            } else {
                let errorMessage = `Error HTTP! Estado: ${response.status}`;
                
                try {
                    const errorData = await response.json();
                    errorMessage = errorData.error || errorMessage;
                } catch (jsonError) {
                    console.error("No se pudo leer el JSON de error.", response.statusText);
                }

                throw new Error(errorMessage);
            }

        } catch (error) {
            console.error(`Error al ${editingUser ? 'actualizar' : 'crear'}:`, error);
            showAlert(`Error: ${error.message}`, 'error');
        } finally {
            setIsLoading(false);
        }
    };

    // ------------------------------------
    // 3. ELIMINAR (DELETE)
    // ------------------------------------
    const handleDeleteConfirmed = async (id) => {
        setShowConfirm(null); // Ocultar el diálogo de confirmación
        setIsLoading(true);
        try {
            const response = await fetch(`${API_BASE_URL}/users/${id}`, {
                method: 'DELETE',
            });

            if (response.ok) {
                showAlert(`Usuario con ID ${id} eliminado con éxito.`, 'success');
                fetchUsers();
            } else {
                let errorMessage = `Error HTTP! Estado: ${response.status}`;
                try {
                    const errorData = await response.json();
                    errorMessage = errorData.error || errorMessage;
                } catch (jsonError) {
                    console.error("No se pudo leer el JSON de error.", response.statusText);
                }
                throw new Error(errorMessage);
            }
        } catch (error) {
            console.error('Error al eliminar:', error);
            showAlert(`Error al eliminar: ${error.message}`, 'error');
        } finally {
            setIsLoading(false);
        }
    };

    // Abre el diálogo de confirmación personalizado de React
    const handleDeleteClick = (user) => {
        setShowConfirm({
            id: user.id,
            nombre: user.nombre,
            message: `¿Estás seguro de que quieres eliminar a ${user.nombre} (ID: ${user.id})? Esta acción es irreversible.`
        });
    };

    // ------------------------------------
    // 4. Manejo de Estado
    // ------------------------------------
    const handleInputChange = (e) => {
        const { name, value } = e.target;
        if (editingUser) {
            setEditingUser({ ...editingUser, [name]: value });
        } else {
            setNewUser({ ...newUser, [name]: value });
        }
    };

    const handleSearchChange = (e) => {
        setSearchQuery(e.target.value);
    };

    const handleSearchSubmit = (e) => {
        e.preventDefault();
        fetchUsers();
    };

    const handleEditClick = (user) => {
        setEditingUser({
            id: user.id,
            nombre: user.nombre,
            correo: user.correo,
            // Convertir a string para el input type="number"
            // Se usa el valor de 'edad' como número en la petición PUT
            edad: String(user.edad) 
        });
        setNewUser({ nombre: '', correo: '', edad: '' }); // Limpiar el formulario de creación
    };

    const handleCancelEdit = () => {
        setEditingUser(null);
        setNewUser({ nombre: '', correo: '', edad: '' });
    };

    // Determinar qué valores mostrar en el formulario
    const formValues = editingUser || newUser;
    
    // Icono para el mensaje de alerta
    const getMessageIcon = (type) => {
        switch (type) {
            case 'success': return <CheckCircle size={20} className="mr-2" />;
            case 'error': return <XCircle size={20} className="mr-2" />;
            case 'warning': return <AlertTriangle size={20} className="mr-2" />;
            default: return <Info size={20} className="mr-2" />;
        }
    };

    // ------------------------------------
    // 5. Renderizado
    // ------------------------------------
    return (
        <div className="min-h-screen bg-gray-50 flex flex-col items-center p-4 sm:p-8 font-inter">
            <style jsx global>{`
                body {
                    font-family: 'Inter', sans-serif;
                }
                .modal-overlay {
                    position: fixed;
                    top: 0;
                    left: 0;
                    right: 0;
                    bottom: 0;
                    background-color: rgba(0, 0, 0, 0.5);
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    z-index: 50;
                }
            `}</style>

            {/* Contenedor Principal */}
            <div className="w-full max-w-4xl bg-white shadow-xl rounded-xl p-6 md:p-10">
                <h1 className="text-3xl font-bold text-gray-800 mb-6 border-b pb-2">
                    CRUD de Usuarios con AWS RDS
                </h1>
                
                {/* Mensaje de Alerta Global */}
                {message && (
                    <div className={`p-3 mb-4 rounded-lg text-sm font-medium flex items-center ${
                        message.type === 'error' ? 'bg-red-100 text-red-700' :
                        message.type === 'success' ? 'bg-green-100 text-green-700' :
                        message.type === 'warning' ? 'bg-yellow-100 text-yellow-700' :
                        'bg-blue-100 text-blue-700'
                    }`}>
                        {getMessageIcon(message.type)}
                        {message.text}
                    </div>
                )}

                {/* Formulario de Creación/Edición */}
                <div className="mb-8 border p-5 rounded-lg bg-indigo-50/50">
                    <h2 className="text-xl font-semibold text-indigo-700 mb-4">
                        {editingUser ? 'Editar Usuario (ID: ' + editingUser.id + ')' : 'Crear Nuevo Usuario'}
                    </h2>
                    <form onSubmit={handleSubmit} className="grid grid-cols-1 sm:grid-cols-4 gap-4 items-end">
                        <input
                            type="text"
                            name="nombre"
                            placeholder="Nombre Completo"
                            value={formValues.nombre}
                            onChange={handleInputChange}
                            required
                            className="p-2 border border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-indigo-500 col-span-1 sm:col-span-1"
                        />
                        <input
                            type="email"
                            name="correo"
                            placeholder="Correo Electrónico"
                            value={formValues.correo}
                            onChange={handleInputChange}
                            required
                            className="p-2 border border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-indigo-500 col-span-1 sm:col-span-1"
                        />
                        <input
                            type="number"
                            name="edad"
                            placeholder="Edad"
                            value={formValues.edad}
                            onChange={handleInputChange}
                            required
                            min="1"
                            className="p-2 border border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-indigo-500 col-span-1 sm:col-span-1"
                        />
                        
                        <div className="flex space-x-2 col-span-1 sm:col-span-1">
                            <button
                                type="submit"
                                disabled={isLoading}
                                className={`flex-1 flex items-center justify-center p-2 rounded-lg text-white font-medium transition duration-150 ${
                                    isLoading ? 'bg-gray-400 cursor-not-allowed' : 'bg-indigo-600 hover:bg-indigo-700'
                                }`}
                            >
                                {editingUser ? <><Edit size={18} className="mr-1" /> Actualizar</> : <><Plus size={18} className="mr-1" /> Crear</>}
                            </button>
                            {editingUser && (
                                <button
                                    type="button"
                                    onClick={handleCancelEdit}
                                    className="p-2 rounded-lg bg-gray-200 text-gray-700 hover:bg-gray-300 transition duration-150"
                                >
                                    Cancelar
                                </button>
                            )}
                        </div>
                    </form>
                </div>

                {/* Sección de Búsqueda y Carga */}
                <div className="flex justify-between items-center mb-6 border-b pb-4">
                    <form onSubmit={handleSearchSubmit} className="flex space-x-2 w-full sm:w-2/3">
                        <input
                            type="text"
                            placeholder="Buscar por nombre o correo..."
                            value={searchQuery}
                            onChange={handleSearchChange}
                            className="flex-1 p-2 border border-gray-300 rounded-lg focus:ring-sky-500 focus:border-sky-500"
                        />
                        <button
                            type="submit"
                            className="p-2 bg-sky-500 text-white rounded-lg hover:bg-sky-600 transition duration-150 flex items-center"
                        >
                            <Search size={18} />
                        </button>
                    </form>
                    <button
                        onClick={fetchUsers}
                        disabled={isLoading}
                        className={`p-2 ml-4 rounded-lg transition duration-150 flex items-center ${
                            isLoading ? 'bg-gray-400 cursor-not-allowed' : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                        }`}
                        title="Recargar usuarios"
                    >
                        <RefreshCw size={18} className={isLoading ? "animate-spin" : ""} />
                    </button>
                </div>

                {/* Tabla de Usuarios */}
                <div className="overflow-x-auto shadow-lg rounded-lg">
                    <table className="min-w-full divide-y divide-gray-200">
                        <thead className="bg-gray-50">
                            <tr>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">ID</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Nombre</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Correo</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Edad</th>
                                <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">Acciones</th>
                            </tr>
                        </thead>
                        <tbody className="bg-white divide-y divide-gray-200">
                            {users.length === 0 && !isLoading ? (
                                <tr>
                                    <td colSpan="5" className="px-6 py-4 text-center text-sm text-gray-500">
                                        No se encontraron usuarios.
                                    </td>
                                </tr>
                            ) : (
                                users.map((user) => (
                                    <tr key={user.id}>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{user.id}</td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">{user.nombre}</td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">{user.correo}</td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">{user.edad}</td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-center">
                                            <div className="flex justify-center space-x-2">
                                                <button
                                                    onClick={() => handleEditClick(user)}
                                                    className="text-indigo-600 hover:text-indigo-900 p-1 rounded-md hover:bg-indigo-50 transition"
                                                    title="Editar"
                                                >
                                                    <Edit size={18} />
                                                </button>
                                                <button
                                                    onClick={() => handleDeleteClick(user)}
                                                    className="text-red-600 hover:text-red-900 p-1 rounded-md hover:bg-red-50 transition"
                                                    title="Eliminar"
                                                >
                                                    <Trash2 size={18} />
                                                </button>
                                            </div>
                                        </td>
                                    </tr>
                                ))
                            )}
                        </tbody>
                    </table>
                </div>

                {/* URL de la API */}
                <div className="mt-6 p-3 text-xs bg-gray-100 rounded-lg text-gray-600">
                    <p className="font-semibold mb-1">URL Base de la API (Punto 8 - AWS):</p>
                    <code className="block break-all">{API_BASE_URL}</code>
                    <p className="mt-1 italic">
                        El frontend se conecta a esta URL, la cual se debe configurar en las variables de entorno de Vercel (REACT_APP_API_URL).
                    </p>
                </div>
            </div>

            {/* Diálogo de Confirmación (Modal) */}
            {showConfirm && (
                <div className="modal-overlay">
                    <div className="bg-white p-6 rounded-xl shadow-2xl max-w-sm w-full">
                        <h3 className="text-lg font-bold text-red-600 flex items-center mb-4">
                            <AlertTriangle size={20} className="mr-2" />
                            Confirmar Eliminación
                        </h3>
                        <p className="text-gray-700 mb-6">{showConfirm.message}</p>
                        <div className="flex justify-end space-x-3">
                            <button
                                onClick={() => setShowConfirm(null)}
                                className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition"
                            >
                                Cancelar
                            </button>
                            <button
                                onClick={() => handleDeleteConfirmed(showConfirm.id)}
                                className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition flex items-center"
                                disabled={isLoading}
                            >
                                <Trash2 size={16} className="mr-1" />
                                Eliminar
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}

export default UserCRUD;