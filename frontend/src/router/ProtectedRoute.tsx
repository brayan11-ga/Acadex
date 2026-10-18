import { useEffect } from 'react';
import { Navigate, Outlet } from 'react-router-dom';
import { useAppDispatch, useAppSelector } from '../hooks/hooks';
import { fetchUsuarioActual } from '../store/authSlice';

export const ProtectedRoute = () => {
  const dispatch = useAppDispatch();
  const { usuario, error } = useAppSelector((state) => state.auth);
  const token = localStorage.getItem('access_token');

  useEffect(() => {
    if (token && !usuario) dispatch(fetchUsuarioActual());
  }, [token, usuario, dispatch]);

  if (!token) return <Navigate to="/iniciarSesion" replace />;
  if (!usuario && !error) return <p>Verificando sesión...</p>;
  if (!usuario) return <Navigate to="/iniciarSesion" replace />;
  return <Outlet />;
};
