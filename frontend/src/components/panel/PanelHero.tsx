// src/components/panel/PanelHero.tsx
import type { TareaPanel, ProgresoDiario } from '../../types/panel'; 

interface PanelHeroProps {
  tareaPrioritaria?: TareaPanel | null;
  progreso?: ProgresoDiario | null;
}

export const PanelHero = ({ tareaPrioritaria, progreso }: PanelHeroProps) => {
  return (
    <section className="panel-grid-top">
      {tareaPrioritaria && (
        <div className="tarjeta-prioridad pixel-panel">
          <div className="prioridad-top">
            {tareaPrioritaria.etiqueta && (
              <span className="pixel-chip-priority">{tareaPrioritaria.etiqueta}</span>
            )}
            <span className="prioridad-tiempo">▾ {tareaPrioritaria.fechaVencimiento}</span>
          </div>
          
          <h2 className="prioridad-titulo">{tareaPrioritaria.titulo}</h2>
          <p className="prioridad-desc">{tareaPrioritaria.descripcion}</p>
          
          <div className="prioridad-acciones">
            <button className="pixel-btn-play"><span className="icon">▶</span> Iniciar Tarea</button>
            <button className="pixel-btn-outline-success"><span className="icon">✔</span> Completar</button>
          </div>
        </div>
      )}

      {progreso && (
        <div className="tarjeta-progreso pixel-panel">
          <h3 className="progreso-titulo">PROGRESO DIARIO</h3>
          <div className="progreso-stats">
            <span className="progreso-completadas">{progreso.completadas}</span>
            <span className="progreso-total">/{progreso.total}</span>
          </div>
          <p className="progreso-desc">
            {progreso.completadas} tareas completadas, faltan {progreso.total - progreso.completadas}
          </p>
          
          <div className="progreso-grafico">
            {progreso.dias.map((dia, idx) => (
              <div key={idx} className="grafico-columna">
                <div 
                  className={`grafico-barra ${dia.actual ? 'barra-activa' : ''}`}
                  style={{ height: `${dia.cantidad > 0 ? dia.cantidad * 25 : 10}%` }}
                ></div>
                <span className={`grafico-dia ${dia.actual ? 'dia-activo' : ''}`}>{dia.dia}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </section>
  );
};