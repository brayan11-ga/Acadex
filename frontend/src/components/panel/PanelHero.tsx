// PanelHero
import type { TareaPanel } from '../../types/panel';
import { Cronometro } from '../../components/cronometro/Cronometro';
import { PanelResumen, type ResumenTareas } from './PanelResumen';

interface PanelHeroProps {
  tareaPrioritaria?: TareaPanel | null;
  resumen:ResumenTareas;
  onCompletarTarea?: (idTarea: number) => void;
}

export const PanelHero = ({ tareaPrioritaria, resumen, onCompletarTarea }: PanelHeroProps) => {
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

      <PanelResumen{...resumen}/>
    </section>
  );
};