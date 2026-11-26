// src/components/tareas/TarjetaTarea.tsx
import { useState, useRef, useEffect } from "react";
import type { TareaBackend } from "../../services/tareas";
import { Check, Undo2, MoreVertical, Pencil, Trash2 } from "lucide-react";
import { ETIQUETAS_PRIORIDAD, mapearPrioridad } from "../../utils/prioridad";
import "../../styles/tareas-grupo.css";

interface TarjetaTareaProps {
  tarea: TareaBackend;
  nombreCategoria: (id: number) => string;
  formatearFecha: (iso: string) => string;
  onVerDetalles: (id: number) => void;
  onEditar?: (tarea: TareaBackend) => void;
  onEliminar?: (id: number) => void;
  onCambiarEstado?: (tarea: TareaBackend) => void;
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
  const esVencida = !esCompletada && tarea.vencida === true;
  const prioridad = mapearPrioridad(tarea.prioridad);

  const [menuAbierto, setMenuAbierto] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const manejarClicFuera = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setMenuAbierto(false);
      }
    };
    document.addEventListener("mousedown", manejarClicFuera);
    return () => document.removeEventListener("mousedown", manejarClicFuera);
  }, []);

  const ejecutarAccion = (accion: () => void) => {
    setMenuAbierto(false);
    accion();
  };

  return (
    <article className={`pixel-tarea-card ${esCompletada ? "completada" : ""} ${esVencida ? "vencida" : ""}`}>
      <div className="pixel-tarea-info">
        <div className="pixel-tarea-header-card">
          <h3 className={`pixel-tarea-titulo ${esCompletada ? "tachado" : ""}`}>{tarea.nombre}</h3>
          <span className={`pixel-badge-dificultad nivel-${tarea.dificultad_estimada}`}>
            Nivel {tarea.dificultad_estimada}
          </span>
          {esVencida && <span className="pixel-etiqueta-vencida">Vencida</span>}
        </div>
        <dl className="pixel-tarea-detalles">
          <div className={`pixel-tarea-meta ${esVencida ? "pixel-tarea-meta--vencida" : ""}`}>
            <dt>Entrega</dt>
            <dd>{formatearFecha(tarea.fecha_entrega)}</dd>
          </div>
          <div className="pixel-tarea-meta">
            <dt>Categoría</dt>
            <dd>{nombreCategoria(tarea.id_categoria)}</dd>
          </div>
        </dl>
      </div>

      <div className="pixel-tarea-acciones">
        <span className={`pixel-estado-badge ${tarea.estado.replace(" ", "-").toLowerCase()}`}>
          {tarea.estado.toLowerCase()}
        </span>
        {prioridad && (
          <span className={`pixel-estado-badge pixel-prioridad pixel-prioridad--${prioridad}`}>
            {ETIQUETAS_PRIORIDAD[prioridad]}
          </span>
        )}
      </div>

            <div className="pixel-tarea-botones" ref={menuRef}>
        <button
          type="button"
          className="tareas-grupo-boton tareas-grupo-boton--primario tareas-grupo-boton--pequeno"
          onClick={() => onVerDetalles(tarea.id_tarea)}
        >
          Ver
        </button>
        {onCambiarEstado && (
          <button
            type="button"
            className="tareas-grupo-boton tareas-grupo-boton--secundario tareas-grupo-boton--pequeno"
            onClick={() => onCambiarEstado(tarea)}
            title={esCompletada ? "Marcar como pendiente" : "Marcar como completada"}
          >
            {esCompletada ? (
              <><Undo2 size={14} /> Reabrir</>
            ) : (
              <><Check size={14} /> Completar</>
            )}
          </button>
        )}

        {onEditar && onEliminar && (
          <div className="pixel-menu-kebab-container">
            <button
              type="button"
              className="pixel-btn-kebab"
              onClick={() => setMenuAbierto(!menuAbierto)}
              title="Más opciones"
            >
              <MoreVertical size={18} />
            </button>

            {menuAbierto && (
              <div className="pixel-dropdown-menu">
                <button type="button" onClick={() => ejecutarAccion(() => onEditar?.(tarea))}>
                  <Pencil size={16} /> Editar Tarea
                </button>
                <div className="pixel-dropdown-divisor"></div>
                <button
                  type="button"
                  className="pixel-btn-peligro-texto"
                  onClick={() => ejecutarAccion(() => onEliminar?.(tarea.id_tarea))}
                >
                  <Trash2 size={16} /> Eliminar
                </button>
              </div>
            )}
          </div>
        )}
      </div>
    </article>
  );
};