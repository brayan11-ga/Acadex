// src/components/panel/PanelHero.tsx
import type { TareaPanel, ProgresoDiario } from '../../types/panel'; 

interface PanelHeroProps {
  tareaPrioritaria?: TareaPanel | null;
  progreso?: ProgresoDiario | null;
  onCompletarTarea?: (idTarea: number) => void;
}

export const PanelHero = ({ tareaPrioritaria, progreso, onCompletarTarea }: PanelHeroProps) => {
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
            <button type="button" className="pixel-btn-play">
              <span className="icon">▶</span> Iniciar Tarea
            </button>
            <button 
              type="button" 
              className="pixel-btn-outline-success"
              onClick={() => onCompletarTarea && onCompletarTarea(tareaPrioritaria.id)}
            >
              <span className="icon">✔</span> Completar
            </button>
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
            {progreso.dias.map((dia, idx) => {
              const tieneTareas = dia.cantidad > 0;
              const alturaBarra = tieneTareas ? Math.max(dia.cantidad * 40, 35) : 8;

              return (
                <div key={idx} className="grafico-columna">
                  <div 
                    className={`grafico-barra ${dia.actual || tieneTareas ? 'barra-activa' : ''}`}
                    style={{ height: `${alturaBarra}%` }}
                  ></div>
                  <span className={`grafico-dia ${dia.actual ? 'dia-activo' : ''}`}>{dia.dia}</span>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </section>
  );
};