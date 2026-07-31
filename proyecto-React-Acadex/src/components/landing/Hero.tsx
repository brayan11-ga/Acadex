// src/components/landing/Hero.tsx
export const Hero = () => {
  return (
    <section id="inicio" className="hero">
      <canvas id="heroParticles" className="hero-particles" aria-hidden="true"></canvas>

      <div className="container hero-grid">
        <div className="hero-content" data-aos="fade-up" data-aos-duration="900">
          <span className="badge">Gestión inteligente de tareas académicas</span>

          <h1>Organiza tus tareas, coordina tu equipo y avanza con más control.</h1>

          <p>
            Acadex ayuda a estudiantes y equipos de trabajo a gestionar actividades,
            asignar responsabilidades, hacer seguimiento del progreso y mantener todo centralizado en un solo lugar.
          </p>

          <div className="hero-buttons">
            <a href="/register.html" className="btn btn-primary">Empezar ahora</a>
            <a href="#funcionalidades" className="btn btn-secondary">Ver funcionalidades</a>
          </div>

          <div className="hero-metrics">
            <div className="metric-card">
              <strong>+120</strong>
              <span>Tareas organizadas</span>
            </div>
            <div className="metric-card">
              <strong>35</strong>
              <span>Equipos activos</span>
            </div>
            <div className="metric-card">
              <strong>80%</strong>
              <span>Seguimiento completo</span>
            </div>
          </div>
        </div>

        <div className="hero-visual" data-aos="fade-left" data-aos-duration="1000">
          <div className="hero-panel">
            <div className="panel-top">
              <div className="panel-dots">
                <span></span>
                <span></span>
                <span></span>
              </div>
              <span className="panel-title">Panel de tareas</span>
            </div>

            <div className="panel-grid">
              <article className="task-card task-card-main">
                <span className="task-label task-label-progress">En progreso</span>
                <h3>Proyecto final de matemáticas</h3>
                <p>Equipo 4 · Entrega en 2 días</p>

                <div className="progress-bar">
                  <div className="progress-fill" style={{ width: '72%' }}></div>
                </div>

                <div className="task-footer">
                  <span><i className="bi bi-clock"></i> 4h 30m</span>
                  <span><i className="bi bi-people"></i> 4 miembros</span>
                </div>
              </article>

              <article className="task-card task-card-side">
                <span className="task-label task-label-done">Completada</span>
                <h4>Resumen de lectura</h4>
                <p>Asignada a 2 integrantes</p>
              </article>

              <article className="task-card task-card-side">
                <span className="task-label task-label-pending">Pendiente</span>
                <h4>Presentación de clase</h4>
                <p>Falta revisar contenido</p>
              </article>

              <article className="task-card task-card-side">
                <span className="task-label task-label-time">Tiempo</span>
                <h4>Tiempo de hoy</h4>
                <p>3h 20m registrados</p>
              </article>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default Hero;