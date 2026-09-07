import { useEffect, useState } from 'react';
import { Navigate, Outlet } from 'react-router-dom';
import { adminApi } from '../services/adminapi';

interface UsuarioMe {
    id_usuario: number;
    correo_electronico: string;
    es_admin: boolean;
}

export const RutaAdmin = () => {
    const [estado, setEstado] = useState<'cargando' | 'permitido' | 'denegado'>('cargando');

    useEffect(() => {
    const verificar = async () => {
        const token = localStorage.getItem('access_token');
        if (!token) {
        setEstado('denegado');
        return;
        }
        const usuario = await adminApi.obtenerMe<UsuarioMe>();
        if (usuario?.es_admin) {
        setEstado('permitido');
        } else {
        setEstado('denegado');
        }
    };
    verificar();
    }, []);

    if (estado === 'cargando') return <p>Verificando acceso...</p>;
    if (estado === 'denegado') return <Navigate to="/iniciarSesion" replace />;
    return <Outlet />;
};

export default RutaAdmin;