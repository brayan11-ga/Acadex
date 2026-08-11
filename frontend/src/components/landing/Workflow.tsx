// src/components/landing/Workflow.tsx
export const Workflow = () => {
  return (
    <section id="como-funciona" className="section workflow">
            <div className="container">

                <div className="section-header" data-reveal>
                    <span className="eyebrow">Proceso</span>
                    <h2>¿Cómo funciona Acadex?</h2>
                    <p>
                        Organiza tus actividades académicas en pasos simples y fáciles de seguir.
                    </p>
                </div>

                <div className="workflow-steps">

                    <div className="step" data-reveal>
                        <span className="step-index">01</span>
                        <h3>Crea tus tareas</h3>
                        <p>
                            Registra actividades, entregas y objetivos académicos.
                        </p>
                    </div>

                    <div className="step-line" aria-hidden="true"></div>

                    <div className="step" data-reveal>
                        <span className="step-index">02</span>
                        <h3>Organiza prioridades</h3>
                        <p>
                            Decide qué es urgente, qué está en proceso y qué ya está listo.
                        </p>
                    </div>

                    <div className="step-line" aria-hidden="true"></div>

                    <div className="step" data-reveal>
                        <span className="step-index">03</span>
                        <h3>Colabora en equipo</h3>
                        <p>
                            Asigna tareas, coordina responsabilidades y mantén a todos alineados.
                        </p>
                    </div>

                    <div className="step-line" aria-hidden="true"></div>

                    <div className="step" data-reveal>
                        <span className="step-index">04</span>
                        <h3>Monitorea avances</h3>
                        <p>
                            Revisa progreso, tiempo invertido y resultados en tiempo real.
                        </p>
                    </div>

                </div>

            </div>
        </section>
  );
};

export default Workflow;