import { useState } from 'react';
import type { ChangeEvent, FormEvent } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { restablecerContrasena } from '../../services/authService';

export const FormularioRestablecerContrasena = () => {
  const [searchParams] = useSearchParams();
  const token = searchParams.get('token');

  const [password, setPassword] = useState('');
  const [confirmacion, setConfirmacion] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [exito, setExito] = useState(false);
  const [loading, setLoading] = useState(false);

  const navigate = useNavigate();

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError(null);

    if (password !== confirmacion) {
      setError('Las contraseñas no coinciden');
      return;
    }

    setLoading(true);
    try {
      await restablecerContrasena(token as string, password);
      setExito(true);
      setTimeout(() => navigate('/iniciarSesion'), 2500);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error inesperado');
    } finally {
      setLoading(false);
    }
  };

  if (!token) {
    return (
      <section className="login">
        <div className="container-login">
          <p className="form-error" role="alert">El enlace no es válido.</p>
          <Link to="/olvide-contrasena">Solicitar un enlace nuevo</Link>
        </div>
      </section>
    );
  }

  return (
    <section className="login">
      <div className="login-header">
        <i className="bi bi-shield-lock" style={{ fontSize: '3rem', color: 'var(--azure)' }}></i>
        <h1>Nueva contraseña</h1>
      </div>
      <div className="container-login">
        {exito ? (
          <p role="status">Contraseña actualizada. Te llevamos a iniciar sesión...</p>
        ) : (
          <form onSubmit={handleSubmit}>
            <div className="input-container">
              <label htmlFor="password">Nueva contraseña</label>
              <input
                type="password"
                id="password"
                value={password}
                onChange={(e: ChangeEvent<HTMLInputElement>) => setPassword(e.target.value)}
                placeholder="Mínimo 8 caracteres"
                minLength={8}
                required
              />

              <label htmlFor="confirmacion">Confirmar contraseña</label>
              <input
                type="password"
                id="confirmacion"
                value={confirmacion}
                onChange={(e: ChangeEvent<HTMLInputElement>) => setConfirmacion(e.target.value)}
                placeholder="Repite la contraseña"
                minLength={8}
                required
              />
            </div>

            {error && <p className="form-error" role="alert">{error}</p>}

            <button className="button-iniciar" type="submit" disabled={loading}>
              {loading ? 'Guardando...' : 'Cambiar contraseña'}
            </button>
          </form>
        )}
      </div>
    </section>
  );
};

export default FormularioRestablecerContrasena;