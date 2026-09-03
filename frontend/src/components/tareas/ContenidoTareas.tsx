// src/components/tareas/ContenidoTareas.tsx
import { useState, useEffect } from "react";
import "../../styles/contenido-tareas.css";
import {
  listarTareas,
  obtenerTarea,
  eliminarTarea,
  type TareaBackend,
} from "../../services/tareas";
import { listarCategorias, type Categoria } from "../../services/categorias";

interface ContenidoTareaProps {
  onNuevaTarea: () => void;
  onEditarTarea: (tarea: TareaBackend) => void;
  refreshKey: number;
}

function ContenidoTareas({ onNuevaTarea, onEditarTarea, refreshKey }: ContenidoTareaProps) {
  const [tareas, setTareas] = useState<TareaBackend[]>([]);
  const [categorias, setCategorias] = useState<Categoria[]>([]);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [tareaDetalle, setTareaDetalle] = useState<TareaBackend | null>(null);

  useEffect(() => {
    setCargando(true);
    Promise.all([listarTareas(), listarCategorias()])
      .then(([datosTareas, datosCategorias]) => {
        setTareas(datosTareas);
        setCategorias(datosCategorias);
        setError(null);
      })
      .catch(() => setError("No se pudieron cargar las tareas"))
      .finally(() => setCargando(false));
  }, [refreshKey]);

  const nombreCategoria = (id: number) =>
    categorias.find((c) => c.id_categoria === id)?.nombre_categoria ?? "Sin categoría";

  const formatearFecha = (iso: string) =>
    new Date(iso).toLocaleString("es-CO", {
      day: "numeric",
      month: "short",
      hour: "2-digit",
      minute: "2-digit",
    });

  const tareasPendientes = tareas.filter((t) => t.estado !== "Completada").length;

  const manejarEliminar = async (id: number) => {
    const confirmar = window.confirm(
      "¿Seguro que quieres eliminar esta tarea? Esta acción no se puede deshacer."
    );
    if (!confirmar) return;

    try {
      await eliminarTarea(id);
      // La quitamos de la lista sin tener que volver a pedir todo al backend
      setTareas((actuales) => actuales.filter((t) => t.id_tarea !== id));
    } catch {
      setError("No se pudo eliminar la tarea");
    }
  };

  const manejarVerDetalles = async (id: number) => {
    try {
      const tarea = await obtenerTarea(id);
      setTareaDetalle(tarea);
    } catch {
      setError("No se pudieron cargar los detalles de la tarea");
    }
  };

  return (
    <main className="pixel-tareas-main">
      <header className="pixel-tareas-header">
        <div>
          <h1 className="pixel-tareas-title">Tus Tareas</h1>
          <p className="pixel-tareas-subtitle">
            Tienes {tareasPendientes} tareas pendientes esta semana. Mantén el enfoque.
          </p>
        </div>
        <button className="pixel-btn-primario" onClick={onNuevaTarea}>
          + Crear Tarea
        </button>
      </header>

      <div className="pixel-tareas-filtros">
        <span className="pixel-filtro-label">Filtrar por:</span>
        <button className="pixel-filtro-btn activo">Todas</button>
        <button className="pixel-filtro-btn">Alta Prioridad</button>
        <button className="pixel-filtro-btn">Activas</button>
        <button className="pixel-filtro-btn">Completadas</button>
      </div>

      {cargando && <p className="pixel-tareas-subtitle">Cargando tareas...</p>}
      {error && <p className="pixel-error">{error}</p>}

      {!cargando && !error && (
        <section className="pixel-tareas-lista">
          {tareas.map((tarea) => (
            <article
              key={tarea.id_tarea}
              className={`pixel-tarea-card ${tarea.estado === "Completada" ? "completada" : ""}`}
            >
              <div className="pixel-tarea-info">
                <div className="pixel-tarea-header-card">
                  <h3 className="pixel-tarea-titulo">{tarea.nombre}</h3>
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
                    className="pixel-btn-icono"
                    onClick={() => manejarVerDetalles(tarea.id_tarea)}
                  >
                    Ver
                  </button>
                  <button
                    type="button"
                    className="pixel-btn-icono"
                    onClick={() => onEditarTarea(tarea)}
                  >
                    Editar
                  </button>
                  <button
                    type="button"
                    className="pixel-btn-icono pixel-btn-peligro"
                    onClick={() => manejarEliminar(tarea.id_tarea)}
                  >
                    Eliminar
                  </button>
                </div>
              </div>
            </article>
          ))}
        </section>
      )}

      {tareaDetalle && (
        <div className="pixel-modal-overlay" onClick={() => setTareaDetalle(null)}>
          <div className="pixel-modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="pixel-panel">
              <div className="pixel-panel-header">
                <h2 className="pixel-panel-title">{tareaDetalle.nombre}</h2>
                <button
                  type="button"
                  className="pixel-link-descartar"
                  onClick={() => setTareaDetalle(null)}
                >
                  × Cerrar
                </button>
              </div>
              <p><strong>Categoría:</strong> {nombreCategoria(tareaDetalle.id_categoria)}</p>
              <p><strong>Estado:</strong> {tareaDetalle.estado}</p>
              <p><strong>Fecha de entrega:</strong> {formatearFecha(tareaDetalle.fecha_entrega)}</p>
              <p><strong>Dificultad:</strong> Nivel {tareaDetalle.dificultad_estimada}</p>
              <p><strong>Tiempo estimado:</strong> {tareaDetalle.tiempo_estimado} min</p>
              <p><strong>Descripción:</strong> {tareaDetalle.descripcion || "Sin descripción"}</p>
            </div>
          </div>
        </div>
      )}
    </main>
  );
}

export default ContenidoTareas;