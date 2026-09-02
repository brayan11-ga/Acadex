import { useState } from 'react';
import type { ChangeEvent, FormEvent } from 'react';
import '../../styles/register.css'; // <-- Importamos su propia hoja de estilos
import { Link, useNavigate } from 'react-router-dom';
import { registrarUsuario } from '../../services/authService';

export const FormularioRegistro = () => {
    const [email, setEmail] = useState('');
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
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
    if (password.length < 8) {
        setError('La contraseña debe tener al menos 8 caracteres');
        return;
    }

    setLoading(true);
    try {
        await registrarUsuario(email, username, password);
        navigate('/iniciarSesion');
    } catch (err) {
        setError(err instanceof Error ? err.message : 'Error inesperado');
    } finally {
        setLoading(false);
    }
};

    return (
    <section className="login">
        <div className="login-header">
        <i className="bi bi-mortarboard" style={{ fontSize: '3rem', color: 'var(--azure)' }}></i>
        <h1>Crear cuenta</h1>
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
            placeholder="tu@correo.com"
            required
            />
            <label htmlFor="username">Nombre de usuario</label>
            <input
            type="text"
            id="username"
            value={username}
            onChange={(e: ChangeEvent<HTMLInputElement>) => setUsername(e.target.value)}
            placeholder="Tu nombre de usuario"
            required
            />

            <label htmlFor="password">Contraseña</label>
            <input
            type="password"
            id="password"
            value={password}
            onChange={(e: ChangeEvent<HTMLInputElement>) => setPassword(e.target.value)}
            placeholder="Crea una contraseña"
            required
            minLength={8}
            />

            <label htmlFor="confirmPassword">Confirmar contraseña</label>
            <input
            type="password"
            id="confirmPassword"
            value={confirmPassword}
            onChange={(e: ChangeEvent<HTMLInputElement>) => setConfirmPassword(e.target.value)}
            placeholder="Repite tu contraseña"
            required
            />
            </div>

            {error && <p className="form-error" role="alert">{error}</p>}

            <button
            className="button-iniciar"
            type="submit"
            style={{ marginTop: '8px' }}
            disabled={loading}
            >
            {loading ? 'Registrando...' : 'Registrarse'}
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
            ¿Ya tienes una cuenta? <Link to="/iniciarSesion">Inicia sesión</Link>
            </p>
        </div>
        </div>
    </section>
    );
};

export default FormularioRegistro;