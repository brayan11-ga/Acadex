import { Link } from "react-router-dom";

// src/components/landing/CtaSection.tsx
export const CtaSection = () => {
  return (
    <section className="section cta-section">
            <div className="container cta-inner" data-reveal>
                <span className="eyebrow">Empieza hoy</span>
                <h2>Convierte tus tareas en un sistema claro y productivo</h2>
                <p>
                    Ten una plataforma pensada para organizar mejor tu estudio, tus proyectos y tu equipo.
                </p>

                <Link to="/registrarse" className="btn btn-primary">Regístrate aquí</Link>
            </div>
        </section>
  );
};

export default CtaSection;