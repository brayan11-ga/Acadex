// src/components/Login/FormularioLogin.tsx (o tu ruta actual)
import { useState } from 'react';
import type { ChangeEvent, FormEvent } from 'react';
import { Link, useNavigate } from "react-router-dom"; // Importamos useNavigate

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
  const [errorLogin, setErrorLogin] = useState<string | null>(null);
  const navigate = useNavigate(); // Hook para redirigir entre páginas

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setErrorLogin(null);

    // 1. Validamos contra nuestro usuario de prueba en memoria
    const USUARIO_PRUEBA = {
      email: "admin@acadex.com",
      password: "123456",
      nombre: "Juan ",
      rol: "ESTUDIANTE ADSO"
    };

    if (email === USUARIO_PRUEBA.email && password === USUARIO_PRUEBA.password) {
      // 2. Guardamos la sesión simulada en localStorage para que otras vistas la lean
      localStorage.setItem("usuario_acadex", JSON.stringify({
        nombre: USUARIO_PRUEBA.nombre,
        rol: USUARIO_PRUEBA.rol,
        email: USUARIO_PRUEBA.email
      }));

      // Si el componente padre pasó un onSubmit, lo ejecutamos
      onSubmit?.({ email, password });

      // 3. Redirigimos automáticamente al panel
      navigate("/panel");
    } else {
      // Si falla, mostramos un error amigable
      setErrorLogin("Correo o contraseña incorrectos. Pruebe con: admin@acadex.com / 123456");
    }
  };

  return (
      <section className="login">
        <div className="login-header">
          <i className="bi bi-person-circle" style={{ fontSize: '3rem', color: 'var(--azure)' }}></i>
          <h1>Iniciar Sesión</h1>
        </div>
        <div className="container-login">
          {/* Mensaje de error visual si fallan las credenciales */}
          {errorLogin && (
            <div style={{ backgroundColor: 'rgba(239, 68, 68, 0.1)', border: '1px solid #ef4444', color: '#ef4444', padding: '10px', borderRadius: '6px', marginBottom: '16px', fontSize: '0.85rem' }}>
              {errorLogin}
            </div>
          )}

          <form onSubmit={handleSubmit}>
            <div className="input-container">
              <label htmlFor="email">Correo electrónico</label>
              <input
                type="email"
                id="email"
                value={email}
                onChange={(e: ChangeEvent<HTMLInputElement>) => setEmail(e.target.value)}
                placeholder="admin@acadex.com"
                required
              />

              <label htmlFor="password">Contraseña</label>
              <input
                type="password"
                id="password"
                value={password}
                onChange={(e: ChangeEvent<HTMLInputElement>) => setPassword(e.target.value)}
                placeholder="123456"
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

export default FormularioLogin;