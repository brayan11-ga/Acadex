import type { TareaBackend } from "../../services/tareas";

interface TarjetaTareaProps {
  tarea: TareaBackend;
  nombreCategoria: (id: number) => string;
  formatearFecha: (iso: string) => string;
  onVerDetalles: (id: number) => void;
  onEditar: (tarea: TareaBackend) => void;
  onEliminar: (id: number) => void;
  onCambiarEstado: (tarea: TareaBackend) => void;
}

export const TarjetaTarea = ({
  tarea,
  nombreCategoria,
  formatearFecha,
  onVerDetalles,
  onEditar,
  onEliminar,
  onCambiarEstado,
}: TarjetaTareaProps) => {
  const esCompletada = tarea.estado === "Completada";

  return (
    <article className={`pixel-tarea-card ${esCompletada ? "completada" : ""}`}>
      <div className="pixel-tarea-info">
        <div className="pixel-tarea-header-card">
          <h3 className={`pixel-tarea-titulo ${esCompletada ? "tachado" : ""}`}>
            {tarea.nombre}
          </h3>
          <span className={`pixel-badge-dificultad nivel-${tarea.dificultad_estimada}`}>
            Nivel {tarea.dificultad_estimada}
          </span>
        </div>
        <div className="pixel-tarea-detalles">
          <span>📅 {formatearFecha(tarea.fecha_entrega)}</span>
          <span>📂 {nombreCategoria(tarea.id_categoria)}</span>
        </div>
      </div>

      <div className="pixel-tarea-acciones">
        <span className={`pixel-estado-badge ${tarea.estado.replace(" ", "-").toLowerCase()}`}>
          {tarea.estado}
        </span>
        <div className="pixel-tarea-botones">
          <button
            type="button"
            className={`pixel-btn-icono ${esCompletada ? "" : "pixel-btn-success"}`}
            onClick={() => onCambiarEstado(tarea)}
            title={esCompletada ? "Marcar como pendiente" : "Marcar como completada"}
          >
            {esCompletada ? "↩️ Reabrir" : "✓ Completar"}
          </button>
          <button type="button" className="pixel-btn-icono" onClick={() => onVerDetalles(tarea.id_tarea)}>
            Ver
          </button>
          <button type="button" className="pixel-btn-icono" onClick={() => onEditar(tarea)}>
            Editar
          </button>
          <button type="button" className="pixel-btn-icono pixel-btn-peligro" onClick={() => onEliminar(tarea.id_tarea)}>
            Eliminar
          </button>
        </div>
      </div>
    </article>
  );
};