// src/components/landing/Benefits.tsx
export const Benefits = () => {
  return (
    <section id="beneficios" className="section benefits">
            <div className="container">

                <div className="section-header" data-reveal>
                    <span className="eyebrow">Ventajas</span>
                    <h2>¿Por qué utilizar Acadex?</h2>
                    <p>
                        Más que una lista de tareas, Acadex te ayuda a trabajar con estructura y enfoque.
                    </p>
                </div>

                <div className="plain-grid">

                    <article className="plain-item" data-reveal>
                        <i className="bi bi-diagram-3 plain-icon"></i>
                        <h3>Mayor organización</h3>
                        <p>
                            Mantén todas tus actividades y proyectos centralizados en un solo lugar.
                        </p>
                    </article>

                    <article className="plain-item" data-reveal>
                        <i className="bi bi-people plain-icon"></i>
                        <h3>Trabajo colaborativo</h3>
                        <p>
                            Coordina tareas y responsabilidades con tus compañeros de forma sencilla.
                        </p>
                    </article>

                    <article className="plain-item" data-reveal>
                        <i className="bi bi-graph-up plain-icon"></i>
                        <h3>Control del progreso</h3>
                        <p>
                            Visualiza avances y detecta fácilmente qué tareas necesitan atención.
                        </p>
                    </article>

                    <article className="plain-item" data-reveal>
                        <i className="bi bi-clock-history plain-icon"></i>
                        <h3>Mejor gestión del tiempo</h3>
                        <p>
                            Identifica prioridades y organiza tus actividades con más eficiencia.
                        </p>
                    </article>

                </div>

            </div>
        </section>
    );
};

export default Benefits;