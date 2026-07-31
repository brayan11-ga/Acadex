// src/components/landing/Features.tsx
export const Features = () => {
  return (
    <section id="funcionalidades" className="section features">
      <div className="container">
        <div className="section-header" data-aos="fade-up">
          <span className="section-kicker">Funcionalidades</span>
          <h2>Todo lo que necesitas para mantener el control</h2>
          <p>Herramientas pensadas para organizar, colaborar y avanzar sin perder el foco.</p>
        </div>

        <div className="feature-grid">
          <article className="card" data-aos="zoom-in" data-aos-delay="100">
            <div className="card-icon"><i className="bi bi-list-task"></i></div>
            <h3>Gestión de tareas</h3>
            <p>Crea, organiza y controla tareas desde una sola interfaz clara y ordenada.</p>
          </article>

          <article className="card" data-aos="zoom-in" data-aos-delay="200">
            <div className="card-icon"><i className="bi bi-people-fill"></i></div>
            <h3>Grupos de trabajo</h3>
            <p>Coordina proyectos con compañeros y asigna responsabilidades de forma eficiente.</p>
          </article>

          <article className="card" data-aos="zoom-in" data-aos-delay="300">
            <div className="card-icon"><i className="bi bi-alarm-fill"></i></div>
            <h3>Seguimiento de tiempo</h3>
            <p>Registra el tiempo real que dedicas a cada actividad y mejora tu productividad.</p>
          </article>

          <article className="card" data-aos="zoom-in" data-aos-delay="400">
            <div className="card-icon"><i className="bi bi-clipboard-data-fill"></i></div>
            <h3>Progreso inteligente</h3>
            <p>Visualiza avances, detecta pendientes y prioriza lo importante con más claridad.</p>
          </article>
        </div>
      </div>
    </section>
  );
};

export default Features;