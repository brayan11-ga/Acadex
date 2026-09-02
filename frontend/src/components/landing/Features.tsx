export const Features = () => {
  return (
    <section id="funcionalidades" className="section features">
            <div className="container">

                <div className="section-header" data-reveal>
                    <span className="eyebrow">Funcionalidades</span>
                    <h2>Todo lo que necesitas para mantener el control</h2>
                    <p>
                        Herramientas pensadas para organizar, colaborar y avanzar sin perder el foco.
                    </p>
                </div>

                <div className="plain-grid">

                    <article className="plain-item" data-reveal>
                        <i className="bi bi-list-task plain-icon"></i>
                        <h3>Gestión de tareas</h3>
                        <p>
                            Crea, organiza y controla tareas desde una sola interfaz clara y ordenada.
                        </p>
                    </article>

                    <article className="plain-item" data-reveal>
                        <i className="bi bi-people plain-icon"></i>
                        <h3>Grupos de trabajo</h3>
                        <p>
                            Coordina proyectos con compañeros y asigna responsabilidades de forma eficiente.
                        </p>
                    </article>

                    <article className="plain-item" data-reveal>
                        <i className="bi bi-alarm plain-icon"></i>
                        <h3>Seguimiento de tiempo</h3>
                        <p>
                            Registra el tiempo real que dedicas a cada actividad y mejora tu productividad.
                        </p>
                    </article>

                    <article className="plain-item" data-reveal>
                        <i className="bi bi-clipboard-data plain-icon"></i>
                        <h3>Progreso inteligente</h3>
                        <p>
                            Visualiza avances, detecta pendientes y prioriza lo importante con más claridad.
                        </p>
                    </article>

                </div>

            </div>
        </section>
  );
};

export default Features;