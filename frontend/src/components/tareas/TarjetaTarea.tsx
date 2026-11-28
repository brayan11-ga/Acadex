// src/components/tareas/TarjetaTarea.tsx
import type { ReactNode } from "react";
import { useState, useRef, useEffect } from "react";
import type { TareaBackend } from "../../services/tareas";
import { Check, Undo2, MoreVertical, Pencil, Trash2 } from "lucide-react";
import { ETIQUETAS_PRIORIDAD, mapearPrioridad } from "../../utils/prioridad";
import { useDesbordado } from "../../hooks/useDesbordado";
import "../../styles/tarjetas.css";
import "../../styles/difuminado.css";
import "../../styles/tareas-grupo.css";

interface TarjetaTareaProps {
  esTuya?: boolean;
  vencida?: boolean;
  accionesExtra?: ReactNode;
  children?: ReactNode;
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
  esTuya,
  vencida,
  accionesExtra,
  children,
}: TarjetaTareaProps) => {
  const esCompletada = tarea.estado === "Completada";
  const esVencida = !esCompletada && (vencida ?? tarea.vencida === true);
  const prioridad = mapearPrioridad(tarea.prioridad);

  const [menuAbierto, setMenuAbierto] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);
  const [tituloRef, tituloDesborda] = useDesbordado<HTMLHeadingElement>(
    tarea.nombre,
  );
  const [descRef, descDesborda] = useDesbordado<HTMLParagraphElement>(
    tarea.descripcion,
  );

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

  const clases = [
    "tareas-grupo-tarjeta",
    prioridad && `tareas-grupo-tarjeta--${prioridad}`,
    esVencida && "tareas-grupo-tarjeta--vencida",
    esCompletada && "tareas-grupo-tarjeta--completada",
  ]
    .filter(Boolean)
    .join(" ");

  return (
    <article className={clases}>
      <div className="tareas-grupo-tarjeta-principal">
        <div className="tareas-grupo-tarjeta-titulo-fila">
          <h3
            ref={tituloRef}
            className={`tareas-grupo-tarjeta-titulo texto-difuminado ${tituloDesborda ? "texto-difuminado--desborda" : ""} ${esCompletada ? "tachado" : ""}`}
            title={tarea.nombre}
          >
            {tarea.nombre}
          </h3>
          <span
            className={`tareas-grupo-nivel tareas-grupo-nivel--${tarea.dificultad_estimada}`}
          >
            Nivel {tarea.dificultad_estimada}
          </span>
          {esTuya && <span className="tareas-grupo-etiqueta-tuya">Tuya</span>}
          {esVencida && (
            <span className="tareas-grupo-etiqueta-vencida">Vencida</span>
          )}
        </div>
        {tarea.descripcion?.trim() && (
          <p
            ref={descRef}
            className={`tareas-grupo-desc texto-difuminado ${descDesborda ? "texto-difuminado--desborda" : ""}`}
            title={tarea.descripcion}
          >
            {tarea.descripcion}
          </p>
        )}

        <dl className="tareas-grupo-meta">
          <div
            className={`tareas-grupo-meta-item ${esVencida ? "tareas-grupo-meta-item--vencida" : ""}`}
          >
            <dt>Entrega</dt>
            <dd>{formatearFecha(tarea.fecha_entrega)}</dd>
          </div>
          <div className="tareas-grupo-meta-item">
            <dt>Categoría</dt>
            <dd>{nombreCategoria(tarea.id_categoria)}</dd>
          </div>
        </dl>
      </div>

      <div className="tareas-grupo-tarjeta-lado">
        <span
          className={`tareas-grupo-chip tareas-grupo-estado--${tarea.estado.trim().toLowerCase().replace(/\s+/g, "-")}`}
        >
          <span className="tareas-grupo-sr-only">Estado: </span>
          {tarea.estado.toLowerCase()}
        </span>
        {prioridad && (
          <span
            className={`tareas-grupo-chip tareas-grupo-prioridad tareas-grupo-prioridad--${prioridad}`}
          >
            {ETIQUETAS_PRIORIDAD[prioridad]}
          </span>
        )}
      </div>
      <div className="tareas-grupo-tarjeta-pie" ref={menuRef}>
        <button
          type="button"
          className="tareas-grupo-boton tareas-grupo-boton--primario tareas-grupo-boton--pequeno"
          onClick={() => onVerDetalles(tarea.id_tarea)}
        >
          Ver
        </button>
        {accionesExtra}
        {onCambiarEstado && (
          <button
            type="button"
            className="tareas-grupo-boton tareas-grupo-boton--secundario tareas-grupo-boton--pequeno"
            onClick={() => onCambiarEstado(tarea)}
            title={
              esCompletada ? "Marcar como pendiente" : "Marcar como completada"
            }
          >
            {esCompletada ? (
              <>
                <Undo2 size={14} /> Reabrir
              </>
            ) : (
              <>
                <Check size={14} /> Completar
              </>
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
                <button
                  type="button"
                  onClick={() => ejecutarAccion(() => onEditar?.(tarea))}
                >
                  <Pencil size={16} /> Editar Tarea
                </button>
                <div className="pixel-dropdown-divisor"></div>
                <button
                  type="button"
                  className="pixel-btn-peligro-texto"
                  onClick={() =>
                    ejecutarAccion(() => onEliminar?.(tarea.id_tarea))
                  }
                >
                  <Trash2 size={16} /> Eliminar
                </button>
              </div>
            )}
          </div>
        )}
      </div>
      {children}
    </article>
  );
};
