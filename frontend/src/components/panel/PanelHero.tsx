import type { TareaPanel, ProgresoDiario } from '../../types/panel';
import { Cronometro } from '../Cronometro/Cronometro';
import { TasksCompletedChart } from '../estadisticas/TasksCompletedChart';

import '../../styles/estadisticas.css';

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

          <Cronometro idTarea={tareaPrioritaria.id} />

          <div className="prioridad-acciones">
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
        <TasksCompletedChart
          dias={progreso.dias.map((dia) => ({ ...dia, actual: dia.actual ?? false }))}
        />
      )}
    </section>
  );
};