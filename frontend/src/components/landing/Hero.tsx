import { Link } from "react-router-dom";


// src/components/landing/Hero.tsx
export const Hero = () => {
  return (
    <section id="inicio" className="hero">
            <div className="container hero-grid">

                <div className="hero-content">
                    <span className="eyebrow">Gestión inteligente de tareas académicas</span>

                    <h1>
                        Organiza tus tareas, coordina tu equipo
                        y <span className="text-gradient">avanza con más control</span>
                    </h1>

                    <p>
                        Acadex ayuda a estudiantes y equipos de trabajo a gestionar actividades,
                        asignar responsabilidades, hacer seguimiento del progreso y mantener
                        todo centralizado en un solo lugar.
                    </p>

                    <div className="hero-buttons">
                        <Link to="/registrarse" className="btn btn-primary">Regístrate aquí</Link>
                        <a href="#funcionalidades" className="btn btn-secondary">
                            Ver funcionalidades
                        </a>
                    </div>

                    <div className="hero-stats">
                        <div className="stat">
                            <strong>+120</strong>
                            <span>Tareas organizadas</span>
                        </div>
                        <div className="stat-divider"></div>
                        <div className="stat">
                            <strong>35</strong>
                            <span>Equipos activos</span>
                        </div>
                        <div className="stat-divider"></div>
                        <div className="stat">
                            <strong>80%</strong>
                            <span>Seguimiento completo</span>
                        </div>
                    </div>
                </div>

                <div className="hero-visual" data-reveal>
                    
                    <div className="preview-panel">
                        <span className="preview-tag">Panel de tareas</span>

                        <div className="preview-main">
                            <span className="task-chip chip-progress">En progreso</span>
                            <h3>Proyecto final de matemáticas</h3>
                            <p>Equipo 4 · Entrega en 2 días</p>

                            <div className="progress-bar">
                                <div className="progress-fill" style={{width: '72%'}}></div>
                            </div>

                            <div className="preview-meta">
                                <span><i className="bi bi-clock"></i> 4h 30m</span>
                                <span><i className="bi bi-people"></i> 4 miembros</span>
                            </div>
                        </div>

                        <ul className="preview-list">
                            <li>
                                <span className="task-chip chip-done">Completada</span>
                                <div className="preview-list-text">
                                    <strong>Resumen de lectura</strong>
                                    <span>Asignada a 2 integrantes</span>
                                </div>
                            </li>
                            <li>
                                <span className="task-chip chip-pending">Pendiente</span>
                                <div className="preview-list-text">
                                    <strong>Presentación de clase</strong>
                                    <span>Falta revisar contenido</span>
                                </div>
                            </li>
                            <li>
                                <span className="task-chip chip-time">Tiempo</span>
                                <div className="preview-list-text">
                                    <strong>Tiempo de hoy</strong>
                                    <span>3h 20m registrados</span>
                                </div>
                            </li>
                        </ul>
                    </div>
                </div>

            </div>
        </section>
);
};

export default Hero;