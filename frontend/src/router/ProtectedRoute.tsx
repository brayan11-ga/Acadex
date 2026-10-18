import { useEffect } from 'react';
import { Navigate, Outlet } from 'react-router-dom';
import { useAppDispatch, useAppSelector } from '../hooks/hooks';
import { cerrarSesion, fetchUsuarioActual } from '../store/authSlice';

export const ProtectedRoute = () => {
  const dispatch = useAppDispatch();
  const { usuario, loading, error, errorStatus } = useAppSelector((state) => state.auth);
  const token = localStorage.getItem('access_token');

  useEffect(() => {
    if (token && !usuario && !loading && !error) dispatch(fetchUsuarioActual());
    if (token && errorStatus === 401) dispatch(cerrarSesion());
  }, [token, usuario, loading, error, errorStatus, dispatch]);

  if (!token) return <Navigate to="/iniciarSesion" replace />;
  if (errorStatus === 401) return <Navigate to="/iniciarSesion" replace />;
  if (error) {
    return (
      <div role="alert">
        <p>{error}</p>
        <button type="button" onClick={() => dispatch(fetchUsuarioActual())} disabled={loading}>
          Reintentar
        </button>
      </div>
    );
  }
  if (loading || !usuario) return <p>Verificando sesión...</p>;
  return <Outlet />;
};
