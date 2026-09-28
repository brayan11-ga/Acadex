import { useEffect } from 'react';
import { Navigate, Outlet } from 'react-router-dom';
import { useAppSelector, useAppDispatch } from '../hooks/hooks'; // usa la ruta donde realmente esté tu hooks.ts
import { fetchUsuarioActual } from '../store/authSlice';

export const RutaAdmin = () => {
  const dispatch = useAppDispatch();
  const { usuario, error } = useAppSelector((state) => state.auth);
  const token = localStorage.getItem('access_token');

  useEffect(() => {
    if (token && !usuario) dispatch(fetchUsuarioActual());
  }, [token, usuario, dispatch]);

  if (!token) return <Navigate to="/iniciarSesion" replace />;
  if (!usuario && !error) return <p>Verificando acceso...</p>;
  if (!usuario?.es_admin) return <Navigate to="/iniciarSesion" replace />;
  return <Outlet />;
};

export default RutaAdmin;