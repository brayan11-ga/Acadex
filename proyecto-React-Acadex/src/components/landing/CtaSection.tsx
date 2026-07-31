// src/components/landing/CtaSection.tsx
export const CtaSection = () => {
  return (
    <section className="section cta-section">
      <div className="container">
        <div className="cta-card" data-aos="zoom-in">
          <div>
            <span className="section-kicker">Empieza hoy</span>
            <h2>Convierte tus tareas en un sistema claro y productivo</h2>
            <p>Ten una plataforma pensada para organizar mejor tu estudio, tus proyectos y tu equipo.</p>
          </div>

          <a href="/register.html" className="btn btn-primary">Crear cuenta</a>
        </div>
      </div>
    </section>
  );
};

export default CtaSection;