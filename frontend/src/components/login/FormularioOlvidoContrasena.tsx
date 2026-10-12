import { useState } from 'react';
import type { ChangeEvent, FormEvent } from 'react';
import { Link } from 'react-router-dom';
import { solicitarRestablecimiento } from '../../services/authService';

export const FormularioOlvidoContrasena = () => {
  const [email, setEmail] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [enviado, setEnviado] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError(null);
    setLoading(true);

    try {
      await solicitarRestablecimiento(email);
      setEnviado(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error inesperado');
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="login">
      <div className="login-header">
        <i className="bi bi-envelope-at" style={{ fontSize: '3rem', color: 'var(--azure)' }}></i>
        <h1>Recuperar contraseña</h1>
      </div>
      <div className="container-login">
        {enviado ? (
          <p role="status">
            Si el correo está registrado, te enviamos un enlace para restablecer tu contraseña.
            El enlace vence en 15 minutos y solo se puede usar una vez.
          </p>
        ) : (
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
            </div>

            {error && <p className="form-error" role="alert">{error}</p>}

            <button className="button-iniciar" type="submit" disabled={loading}>
              {loading ? 'Enviando...' : 'Enviar enlace'}
            </button>
          </form>
        )}

        <div className="register-option">
          <p><Link to="/iniciarSesion">Volver a iniciar sesión</Link></p>
        </div>
      </div>
    </section>
  );
};

export default FormularioOlvidoContrasena;
