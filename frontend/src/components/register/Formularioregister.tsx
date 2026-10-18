import { useState } from 'react';
import type { FormEvent } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { registrarUsuario } from '../../services/authService';
import { obtenerMensajeErrorRegistro } from '../../utils/mensajesAuth';
import { LONGITUD_MINIMA_CONTRASENA } from '../../utils/contrasena';
import '../../styles/register.css';
import '../../styles/register-form.css';
import ConsentimientoRegistro from './ConsentimientoRegistro';
import PasswordField from './PasswordField';

export const FormularioRegistro = () => {
  const [email, setEmail] = useState('');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [aceptaTratamiento, setAceptaTratamiento] = useState(false);
  const [confirmaAviso, setConfirmaAviso] = useState(false);
  const [website, setWebsite] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError(null);
    if (password !== confirmPassword) {
      setError('Las contraseñas no coinciden');
      return;
    }
    if (password.length < LONGITUD_MINIMA_CONTRASENA) {
      setError('La contraseña debe tener al menos 8 caracteres');
      return;
    }

    setLoading(true);
    try {
      await registrarUsuario(email, username, password, aceptaTratamiento, confirmaAviso, website);
      navigate('/iniciarSesion', {
        state: { mensajeExito: '¡Tu cuenta se creó correctamente! Ya puedes iniciar sesión.' },
      });
    } catch (err) {
      setError(obtenerMensajeErrorRegistro(err));
    } finally {
      setLoading(false);
    }
  };

  const consentimientosCompletos = aceptaTratamiento && confirmaAviso;

  return (
    <section className="login">
      <div className="login-header">
        <i className="bi bi-mortarboard" style={{ fontSize: '3rem', color: 'var(--azure)' }} aria-hidden="true" />
        <h1>Crear cuenta</h1>
      </div>
      <div className="container-login">
        <form onSubmit={handleSubmit}>
          <div className="input-container">
            <label htmlFor="email">Correo electrónico</label>
            <input id="email" type="email" value={email} onChange={(event) => setEmail(event.target.value)} placeholder="tu@correo.com" autoComplete="email" required />
            <label htmlFor="username">Nombre de usuario</label>
            <input id="username" type="text" value={username} onChange={(event) => setUsername(event.target.value)} placeholder="Tu nombre de usuario" autoComplete="username" required />
            <PasswordField id="password" label="Contraseña" value={password} onChange={setPassword} placeholder="Crea una contraseña" autoComplete="new-password" minLength={LONGITUD_MINIMA_CONTRASENA} />
            <PasswordField id="confirmPassword" label="Confirmar contraseña" value={confirmPassword} onChange={setConfirmPassword} placeholder="Repite tu contraseña" autoComplete="new-password" />
          </div>

          <ConsentimientoRegistro
            aceptaTratamiento={aceptaTratamiento}
            confirmaAviso={confirmaAviso}
            onTratamientoChange={setAceptaTratamiento}
            onAvisoChange={setConfirmaAviso}
          />
          <div className="register-honeypot" aria-hidden="true">
            <label htmlFor="website">Deja este campo vacío</label>
            <input id="website" name="website" value={website} onChange={(event) => setWebsite(event.target.value)} tabIndex={-1} autoComplete="off" />
          </div>

          {error && <p className="form-error" role="alert">{error}</p>}
          {!consentimientosCompletos && <p className="register-consent-hint">Acepta los avisos para habilitar el registro.</p>}
          <button className="button-iniciar" type="submit" style={{ marginTop: '8px' }} disabled={loading || !consentimientosCompletos}>
            {loading ? 'Registrando...' : 'Registrarse'}
          </button>
        </form>

        <div className="register-option">
          <p>¿Ya tienes una cuenta? <Link to="/iniciarSesion">Inicia sesión</Link></p>
        </div>
      </div>
    </section>
  );
};

export default FormularioRegistro;
