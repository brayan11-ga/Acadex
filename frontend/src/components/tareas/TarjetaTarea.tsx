// src/components/tareas/TarjetaTarea.tsx
import { useState, useRef, useEffect } from "react";
import type { TareaBackend } from "../../services/tareas";
import { 
  CalendarDays, 
  Folder, 
  Check, 
  Undo2, 
  MoreVertical, 
  Eye, 
  Pencil, 
  Trash2 
} from "lucide-react";

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
          <span style={{ display: "flex", alignItems: "center", gap: "6px" }}>
            <CalendarDays size={14} /> {formatearFecha(tarea.fecha_entrega)}
          </span>
          <span style={{ display: "flex", alignItems: "center", gap: "6px" }}>
            <Folder size={14} /> {nombreCategoria(tarea.id_categoria)}
          </span>
        </div>
      </div>

      <div className="pixel-tarea-acciones">
        <span className={`pixel-estado-badge ${tarea.estado.replace(" ", "-").toLowerCase()}`}>
          {tarea.estado}
        </span>
        
        <div className="pixel-tarea-botones" ref={menuRef}>
          <button
            type="button"
            className={`pixel-btn-icono ${esCompletada ? "" : "pixel-btn-success"}`}
            style={{ display: "flex", alignItems: "center", gap: "6px" }}
            onClick={() => onCambiarEstado(tarea)}
            title={esCompletada ? "Marcar como pendiente" : "Marcar como completada"}
          >
            {esCompletada ? (
              <><Undo2 size={14} /> Reabrir</>
            ) : (
              <><Check size={14} /> Completar</>
            )}
          </button>

          <div className="pixel-menu-kebab-container">
            <button 
              className="pixel-btn-kebab" 
              onClick={() => setMenuAbierto(!menuAbierto)}
              title="Más opciones"
            >
              <MoreVertical size={18} />
            </button>

            {menuAbierto && (
              <div className="pixel-dropdown-menu">
                <button type="button" onClick={() => ejecutarAccion(() => onVerDetalles(tarea.id_tarea))}>
                  <Eye size={16} /> Ver Detalles
                </button>
                <button type="button" onClick={() => ejecutarAccion(() => onEditar(tarea))}>
                  <Pencil size={16} /> Editar Tarea
                </button>
                <div className="pixel-dropdown-divisor"></div>
                <button 
                  type="button" 
                  className="pixel-btn-peligro-texto" 
                  onClick={() => ejecutarAccion(() => onEliminar(tarea.id_tarea))}
                >
                  <Trash2 size={16} /> Eliminar
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </article>
  );
};