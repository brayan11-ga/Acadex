// src/components/Login/FormularioLogin.tsx (o tu ruta actual)
import { useState } from 'react';
import type { ChangeEvent, FormEvent } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { iniciarSesion } from '../../services/authService';

export const FormularioLogin = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const navigate = useNavigate();

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const data = await iniciarSesion(email, password);
      localStorage.setItem('access_token', data.access_token);
      navigate('/dashboard'); // ajusta a tu ruta post-login
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error inesperado');
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="login">
      <div className="login-header">
        <i className="bi bi-person-circle" style={{ fontSize: '3rem', color: 'var(--azure)' }}></i>
        <h1>Iniciar Sesión</h1>
      </div>
      <div className="container-login">
        <form onSubmit={handleSubmit}>
          <div className="input-container">
            <label htmlFor="email">Correo electrónico</label>
            <input
              type="email"
              id="email"
              value={email}
              onChange={(e: ChangeEvent<HTMLInputElement>) => setEmail(e.target.value)}
              placeholder="Ingresa tu correo"
              required
            />

            <label htmlFor="password">Contraseña</label>
            <input
              type="password"
              id="password"
              value={password}
              onChange={(e: ChangeEvent<HTMLInputElement>) => setPassword(e.target.value)}
              placeholder="Ingresa tu contraseña"
              required
            />
          </div>

          <div className="password-option">
            <a href="#">¿Olvidaste tu contraseña?</a>
          </div>

          {error && <p className="form-error" role="alert">{error}</p>}

          <button className="button-iniciar" type="submit" disabled={loading}>
            {loading ? 'Iniciando sesión...' : 'Iniciar sesión'}
          </button>
        </form>

        <div className="divider">
          <span>o</span>
        </div>

        <div className="social-login">
          <button type="button" className="google-btn">
            <img src="https://www.google.com/favicon.ico" alt="Google" />
            Continuar con Google
          </button>
        </div>

        <div className="register-option">
          <p>
            ¿No tienes una cuenta? <Link to="/registrarse">Regístrate aquí</Link>
          </p>
        </div>
      </div>
    </section>
  );
};

export default FormularioLogin;