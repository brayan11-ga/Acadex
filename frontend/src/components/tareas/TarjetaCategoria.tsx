import { Folder, ChevronRight } from "lucide-react";
import type { RendimientoCategoria } from "../../types/estadisticas";
import "../../styles/tarjetas.css";
import "../../styles/tareas-grupo.css";

const MIN_TAREAS_CATEGORIA = 3;

interface TarjetaCategoriaProps {
  nombre: string;
  totalTareas: number;
  rendimiento: RendimientoCategoria | null;
  onAbrir: () => void;
}

export const TarjetaCategoria = ({
  nombre,
  totalTareas,
  rendimiento,
  onAbrir,
}: TarjetaCategoriaProps) => {
  const clasificada = rendimiento !== null && rendimiento.estado !== "insuficiente";
  const nivel = clasificada
    ? Math.min(5, Math.max(1, Math.round(rendimiento.dificultad_estimada_prom)))
    : null;
    const faltan= clasificada
    ? 0 : Math.max(0, MIN_TAREAS_CATEGORIA - (rendimiento?.total_tareas ?? 0));

    return (
    <article
      className={`tareas-grupo-tarjeta pixel-categoria-card${nivel !== null ? ` pixel-categoria-card--nivel-${nivel}` : ""}`}
      onClick={onAbrir}
    >
      <div className="tareas-grupo-tarjeta-principal">
        <div className="tareas-grupo-tarjeta-titulo-fila">
          <h3 className="tareas-grupo-tarjeta-titulo">{nombre}</h3>
          {nivel !== null ? (
            <span className={`tareas-grupo-nivel tareas-grupo-nivel--${nivel}`}>
              Nivel {rendimiento!.dificultad_estimada_prom.toFixed(1)}
            </span>
          ) : (
            <span className="tareas-grupo-chip">Sin clasificar</span>
          )}
        </div>
        <div className="tareas-grupo-meta">
          <span className="tareas-grupo-meta-item" style={{ alignItems: "center" }}>
            <Folder size={14} /> {totalTareas} {totalTareas === 1 ? "tarea" : "tareas"}
          </span>
          {!clasificada && faltan > 0 && (
            <span className="tareas-grupo-meta-item">
              Completa {faltan} {faltan === 1 ? "tarea más" : "tareas más"} para clasificarla
            </span>
          )}
        </div>
      </div>

      <div className="tareas-grupo-tarjeta-lado">
        <button
          type="button"
          className="tareas-grupo-boton tareas-grupo-boton--secundario tareas-grupo-boton--pequeno"
        >
          Ver tareas <ChevronRight size={14} />
        </button>
      </div>
    </article>
  );
};