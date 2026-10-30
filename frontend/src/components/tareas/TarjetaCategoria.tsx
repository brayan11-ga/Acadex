import { Folder, ChevronRight } from "lucide-react";
import type { RendimientoCategoria } from "../../types/estadisticas";

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

  return (
    <article className="pixel-tarea-card pixel-categoria-card" onClick={onAbrir}>
      <div className="pixel-tarea-info">
        <div className="pixel-tarea-header-card">
          <h3 className="pixel-tarea-titulo">{nombre}</h3>
          {nivel !== null ? (
            <span className={`pixel-badge-dificultad nivel-${nivel}`}>
              Nivel {rendimiento!.dificultad_estimada_prom.toFixed(1)}
            </span>
          ) : (
            <span className="pixel-badge-dificultad">Sin clasificar</span>
          )}
        </div>
        <div className="pixel-tarea-detalles">
          <span style={{ display: "flex", alignItems: "center", gap: "6px" }}>
            <Folder size={14} /> {totalTareas} {totalTareas === 1 ? "tarea" : "tareas"}
          </span>
        </div>
      </div>

      <div className="pixel-tarea-acciones">
        <button
          type="button"
          className="pixel-btn-icono"
          style={{ display: "flex", alignItems: "center", gap: "6px" }}
        >
          Ver tareas <ChevronRight size={14} />
        </button>
      </div>
    </article>
  );
};