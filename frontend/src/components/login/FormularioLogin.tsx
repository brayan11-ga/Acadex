import { useState } from 'react';
import type { ChangeEvent, FormEvent } from 'react';
import { Link } from "react-router-dom";

interface LoginFormData {
  email: string;
  password: string;
}

interface FormularioLoginProps {
  onSubmit?: (data: LoginFormData) => void;
}

export const FormularioLogin = ({ onSubmit }: FormularioLoginProps) => {
  const [email, setEmail] = useState<string>('');
  const [password, setPassword] = useState<string>('');

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    onSubmit?.({ email, password });
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

            <button className="button-iniciar" type="submit">
              Iniciar sesión
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

export default FormularioLogin