// src/components/tareas/ContenidoTareas.tsx
import { useState, useEffect } from "react";
import "../../styles/contenido-tareas.css";
import {
  listarTareas,
  obtenerTarea,
  eliminarTarea,
  actualizarTarea,
  type TareaBackend,
} from "../../services/tareas";
import { listarCategorias, type Categoria } from "../../services/categorias";
import { FiltrosTareas } from "./FiltrosTareas";
import { TarjetaTarea } from "./TarjetaTarea";
import { ModalDetalleTarea } from "./ModalDetalleTarea";

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
  const [filtroActivo, setFiltroActivo] = useState<string>("todas");

  // NUEVO: Estados para la paginación
  const [paginaActual, setPaginaActual] = useState<number>(1);
  const tareasPorPagina = 6;

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

  // NUEVO: Volver a la primera página si cambia el filtro o la cantidad de tareas
  useEffect(() => {
    setPaginaActual(1);
  }, [filtroActivo, tareas.length]);

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

  const tareasFiltradas = tareas.filter((tarea) => {
    if (filtroActivo === "alta") return tarea.dificultad_estimada >= 4;
    if (filtroActivo === "activas") return tarea.estado !== "Completada";
    if (filtroActivo === "completadas") return tarea.estado === "Completada";
    return true;
  });

  // NUEVO: Cálculos de Paginación
  const indiceUltimaTarea = paginaActual * tareasPorPagina;
  const indicePrimeraTarea = indiceUltimaTarea - tareasPorPagina;
  const tareasPaginadas = tareasFiltradas.slice(indicePrimeraTarea, indiceUltimaTarea);
  const totalPaginas = Math.ceil(tareasFiltradas.length / tareasPorPagina);

  const irAPagina = (numeroPagina: number) => {
    setPaginaActual(numeroPagina);
  };

  const manejarEliminar = async (id: number) => {
    if (!window.confirm("¿Seguro que quieres eliminar esta tarea? Esta acción no se puede deshacer.")) return;

    try {
      await eliminarTarea(id);
      setTareas((actuales) => actuales.filter((t) => t.id_tarea !== id));
    } catch {
      setError("No se pudo eliminar la tarea");
    }
  };

  const manejarCambiarEstado = async (tarea: TareaBackend) => {
    const nuevoEstado = tarea.estado === "Completada" ? "Pendiente" : "Completada";

    try {
      const tareaActualizada = await actualizarTarea(tarea.id_tarea, {
        estado: nuevoEstado,
      });

      setTareas((actuales) =>
        actuales.map((t) => (t.id_tarea === tarea.id_tarea ? tareaActualizada : t))
      );
    } catch {
      setError("No se pudo actualizar el estado de la tarea");
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

      <FiltrosTareas filtroActivo={filtroActivo} onCambiarFiltro={setFiltroActivo} />

      {cargando && <p className="pixel-tareas-subtitle">Cargando tareas...</p>}
      {error && <p className="pixel-error">{error}</p>}

      {!cargando && !error && (
        <>
          <section className="pixel-tareas-lista">
            {tareasFiltradas.length === 0 ? (
              <p className="pixel-tareas-subtitle" style={{ textAlign: "center", padding: "20px" }}>
                No hay tareas para mostrar en este filtro.
              </p>
            ) : (
              tareasPaginadas.map((tarea) => (
                <TarjetaTarea
                  key={tarea.id_tarea}
                  tarea={tarea}
                  nombreCategoria={nombreCategoria}
                  formatearFecha={formatearFecha}
                  onVerDetalles={manejarVerDetalles}
                  onEditar={onEditarTarea}
                  onEliminar={manejarEliminar}
                  onCambiarEstado={manejarCambiarEstado}
                />
              ))
            )}
          </section>

          {totalPaginas > 1 && (
            <div className="pixel-paginacion-container">
              <button 
                className="pixel-btn-primario" 
                style={{ padding: '8px 16px', background: paginaActual === 1 ? '#ccc' : undefined }}
                disabled={paginaActual === 1}
                onClick={() => irAPagina(paginaActual - 1)}
              >
                Anterior
              </button>
              <span className="pixel-paginacion-texto">
                Página {paginaActual} de {totalPaginas}
              </span>
              <button 
                className="pixel-btn-primario"
                style={{ padding: '8px 16px', background: paginaActual === totalPaginas ? '#ccc' : undefined }}
                disabled={paginaActual === totalPaginas}
                onClick={() => irAPagina(paginaActual + 1)}
              >
                Siguiente
              </button>
            </div>
          )}
        </>
      )}

      {tareaDetalle && (
        <ModalDetalleTarea
          tarea={tareaDetalle}
          nombreCategoria={nombreCategoria}
          formatearFecha={formatearFecha}
          onCerrar={() => setTareaDetalle(null)}
        />
      )}
    </main>
  );
}

export default ContenidoTareas;