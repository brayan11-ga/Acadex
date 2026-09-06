// src/router/RutaLider.tsx
import { useEffect, useState } from 'react';
import { Navigate, Outlet } from 'react-router-dom';
import { adminApi } from '../services/adminapi';

interface IntegranteConRol {
  id_grupo: number;
  rol: string;
}

export const RutaLider = () => {
  const [estado, setEstado] = useState<'cargando' | 'permitido' | 'denegado'>('cargando');

  useEffect(() => {
    const verificar = async () => {
      const token = localStorage.getItem('access_token');
      if (!token) {
        setEstado('denegado');
        return;
      }

      // Trae los grupos donde el usuario es integrante, y revisa si en alguno es 'lider'
      const integraciones = await adminApi.listar<IntegranteConRol>('integrantes/mis-grupos');

      const esLiderDeAlgunGrupo = integraciones?.some((i) => i.rol === 'lider');

      if (esLiderDeAlgunGrupo) {
        setEstado('permitido');
      } else {
        setEstado('denegado');
      }
    };
    verificar();
  }, []);

  if (estado === 'cargando') return <p>Verificando acceso...</p>;
  if (estado === 'denegado') return <Navigate to="/panel" replace />;

  return <Outlet />;
};

export default RutaLider;