import type { TareaBackend } from "../../services/tareas";

interface ModalDetalleTareaProps {
  tarea: TareaBackend;
  nombreCategoria: (id: number) => string;
  formatearFecha: (iso: string) => string;
  onCerrar: () => void;
}

export const ModalDetalleTarea = ({
  tarea,
  nombreCategoria,
  formatearFecha,
  onCerrar,
}: ModalDetalleTareaProps) => {
  return (
    <div className="pixel-modal-overlay" onClick={onCerrar}>
      <div className="pixel-modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="pixel-panel">
          <div className="pixel-panel-header">
            <h2 className="pixel-panel-title">{tarea.nombre}</h2>
            <button type="button" className="pixel-link-descartar" onClick={onCerrar}>
              × Cerrar
            </button>
          </div>
          <p><strong>Categoría:</strong> {nombreCategoria(tarea.id_categoria)}</p>
          <p><strong>Estado:</strong> {tarea.estado}</p>
          <p><strong>Fecha de entrega:</strong> {formatearFecha(tarea.fecha_entrega)}</p>
          <p><strong>Dificultad:</strong> Nivel {tarea.dificultad_estimada}</p>
          <p><strong>Tiempo estimado:</strong> {tarea.tiempo_estimado} min</p>
          <p><strong>Descripción:</strong> {tarea.descripcion || "Sin descripción"}</p>
        </div>
      </div>
    </div>
  );
};