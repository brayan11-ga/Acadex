import { useState } from 'react';
import type { ChangeEvent, FormEvent } from 'react';
import { Link } from 'react-router-dom';
import '../../styles/register.css'; // <-- Importamos su propia hoja de estilos

interface RegisterFormData {
    email: string;
    username: string;
    password: string;
}

interface FormularioRegistroProps {
    onSubmit?: (data: RegisterFormData) => void;
}

export const FormularioRegistro = ({ onSubmit }: FormularioRegistroProps) => {
    const [email, setEmail] = useState<string>('');
    const [username, setUsername] = useState<string>('');
    const [password, setPassword] = useState<string>('');

    const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
        event.preventDefault();
        onSubmit?.({ email, username, password });
    };

    return (
        <section className="register-main">
            <div className="register-box">
                <div className="register-header">
                    <i className="bi bi-mortarboard" style={{ fontSize: '3rem', color: 'var(--azure)' }}></i>
                    <h1>Crear cuenta</h1>
                </div>
                
                <div className="register-container">
                    <form onSubmit={handleSubmit}>
                        <div className="register-inputs">
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
                            />
                        </div>

                        {/* ¡Adiós al style={{marginTop: '8px'}}! Ahora el CSS lo controla */}
                        <button className="button-register" type="submit">
                            Registrarse
                        </button>
                    </form>

                    <div className="divider">
                        <span>O</span>
                    </div>

                    <div className="social-login">
                        <button type="button" className="google-btn">
                            <img src="https://www.google.com/favicon.ico" alt="Google" />
                            Continuar con Google
                        </button>
                    </div>

                    <div className="login-option">
                        <p>
                            ¿Ya tienes una cuenta? <Link to="/iniciarSesion">Inicia sesión</Link>
                        </p>
                    </div>
                </div>
            </div>
        </section>
    );
};

export default FormularioRegistro;