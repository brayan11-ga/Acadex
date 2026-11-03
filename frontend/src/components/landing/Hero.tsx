import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useHeroMotion } from './useHeroMotion';

export const Hero = () => {
  const [isAmbientPaused, setAmbientPaused] = useState(false);
  const heroRef = useHeroMotion(isAmbientPaused);

  return (
    <section id="inicio" className="landing-hero" aria-labelledby="hero-title" ref={heroRef}>
      <div className="landing-hero__grid">
        <div className="landing-hero__content">
          <span className="landing-hero__eyebrow" data-hero-enter>
            <span aria-hidden="true" />
            UN ESPACIO. TODO POR AVANZAR.
          </span>
          <h1 id="hero-title" className="landing-hero__title" data-hero-enter>
            Tu mundo,{' '}<br />
            <span>en orden.</span>
          </h1>
          <p className="landing-hero__description" data-hero-enter>
            De las tareas dispersas a un espacio donde todo avanza.
            Organiza tus entregas, coordina tu equipo y sigue tu progreso con Acadex.
          </p>
          <div className="landing-hero__actions">
            <Link to="/registrarse" className="landing-hero__button landing-hero__button--primary">
              Crear mi espacio
              <svg viewBox="0 0 20 20" width="18" height="18" aria-hidden="true" focusable="false">
                <path d="M3 10h13M10 4h3v3h3v6h-3v3h-3" fill="none" stroke="currentColor" strokeWidth="2" />
              </svg>
            </Link>
            <Link to="/iniciarSesion" className="landing-hero__button landing-hero__button--secondary">
              Iniciar sesión
            </Link>
          </div>
          <a className="landing-hero__explore" href="#funcionalidades">
            Explora Acadex <span aria-hidden="true">↓</span>
          </a>
        </div>

        <figure className="landing-hero__figure">
          <div className="landing-hero__scene" data-hero-scene aria-hidden="true">
            <div className="landing-hero__sky" data-hero-depth="far">
              <div className="landing-hero__stars"><span /><span /></div>
              <div className="landing-hero__moon" />
              <svg className="landing-hero__mountains" viewBox="0 0 800 640" fill="none" shapeRendering="crispEdges" focusable="false">
                <path className="landing-hero__ridge--far" d="M0 400V310H40V286H72V254H104V226H144V250H176V276H216V312H264V280H304V244H336V210H376V176H408V150H448V184H480V220H512V254H552V286H600V258H640V226H680V194H720V224H752V260H800V640H0Z" />
                <path className="landing-hero__ridge--near" data-hero-depth="near" d="M0 640V390H48V366H88V340H136V372H184V404H232V384H280V350H328V322H376V294H416V326H456V358H504V392H552V366H600V338H648V308H696V344H744V380H800V640Z" />
                <path className="landing-hero__horizon" d="M0 440H800M0 472H800M0 520H800M0 584H800M400 400L0 640M400 400L160 640M400 400L320 640M400 400L480 640M400 400L640 640M400 400L800 640" />
              </svg>
            </div>
            <div className="landing-hero__world" data-hero-depth="island">
              <div className="landing-hero__beam" data-hero-beam />
              <svg className="landing-hero__island" viewBox="0 0 800 640" fill="none" shapeRendering="crispEdges" focusable="false">
                <path className="landing-hero__island-base" d="M112 440L400 296L704 448V496L432 632L112 472Z" />
                <path className="landing-hero__island-side" d="M432 600L704 464V496L432 632Z" />
                <path className="landing-hero__island-top" d="M112 440L400 296L704 448L432 584Z" />
                <path className="landing-hero__island-edge" d="M112 440L432 600L704 464V448L432 584L112 424Z" />
                <path className="landing-hero__circuit" d="M180 436L244 404L436 500L564 436L628 468M244 468L308 436M372 532L436 500M500 500L564 532M500 404L564 372" />
                <path className="landing-hero__circuit landing-hero__circuit--bright" d="M180 436L244 404L308 436M436 500L500 468L564 500" />
                <path className="landing-hero__plinth-side" d="M264 412V444L432 528L592 448V416L432 496Z" />
                <path className="landing-hero__plinth-top" d="M264 412L424 332L592 416L432 496Z" />
                <path className="landing-hero__signal" d="M204 364H216V352H228V340H240M608 328H620V316H632V304H644" />
                <rect className="landing-hero__pixel" x="176" y="388" width="12" height="12" />
                <rect className="landing-hero__pixel" x="624" y="400" width="12" height="12" />
                <rect className="landing-hero__pixel landing-hero__pixel--violet" x="300" y="540" width="8" height="8" />
              </svg>
              <div className="landing-hero__station" data-hero-depth="station">
                <span className="landing-hero__station-aura" />
                <div className="landing-hero__station-bar">
                  <span className="landing-hero__station-brand"><span /> ACADEX</span>
                  <span className="landing-hero__window-dots">▪ ▪ ▪</span>
                </div>
                <div className="landing-hero__station-body">
                  <span className="landing-hero__station-label">MI ESPACIO</span>
                  <div className="landing-hero__station-heading">Aquí toma forma<br />lo que sigue.</div>
                  <div className="landing-hero__task">
                    <span className="landing-hero__task-icon">✓</span>
                    <div>
                      <strong>Proyecto de clase</strong>
                      <span>En progreso</span>
                    </div>
                    <span className="landing-hero__task-pixels"><i /><i /><i /></span>
                  </div>
                  <div className="landing-hero__station-footer">
                    <span><i /> Tareas</span>
                    <span><i /> Equipo</span>
                    <span><i /> Progreso</span>
                  </div>
                </div>
              </div>
              <div className="landing-hero__beacon landing-hero__beacon--left"><span /></div>
              <div className="landing-hero__beacon landing-hero__beacon--right"><span /></div>
            </div>
          </div>
          <figcaption className="landing-hero__caption">
            <span aria-hidden="true">✦</span> El universo Acadex · Vista conceptual
            <button
              type="button"
              className="landing-hero__motion-toggle"
              onClick={() => setAmbientPaused((paused) => !paused)}
            >
              <svg viewBox="0 0 12 12" width="12" height="12" fill="currentColor" aria-hidden="true" focusable="false">
                <path d={isAmbientPaused ? 'M3 1v10l8-5Z' : 'M2 1h3v10H2Zm5 0h3v10H7Z'} />
              </svg>
              {isAmbientPaused ? 'Reanudar ambiente' : 'Pausar ambiente'}
            </button>
          </figcaption>
        </figure>
      </div>
    </section>
  );
};

export default Hero;
