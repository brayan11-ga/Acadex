import { useState, useEffect } from "react";
import "../../styles/contenido-tareas.css";
import { listarTareas, type TareaBackend } from "../../services/tareas";
import { listarCategorias, type Categoria } from "../../services/categorias";

interface ContenidoTareaProps {
  onNuevaTarea: () => void;
  refreshKey: number;
}

function ContenidoTareas({ onNuevaTarea, refreshKey }: ContenidoTareaProps) {
  const [tareas, setTareas] = useState<TareaBackend[]>([]);
  const [categorias, setCategorias] = useState<Categoria[]>([]);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Se ejecuta al montar Y cada vez que refreshKey cambia (cuando se crea una tarea)
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

  // Mapa id_categoria -> nombre, para mostrar el nombre en la tarjeta
  const nombreCategoria = (id: number) =>
    categorias.find((c) => c.id_categoria === id)?.nombre ?? "Sin categoría";

  const formatearFecha = (iso: string) =>
    new Date(iso).toLocaleString("es-CO", {
      day: "numeric",
      month: "short",
      hour: "2-digit",
      minute: "2-digit",
    });

  const tareasPendientes = tareas.filter((t) => t.estado !== "Completada").length;

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
              </div>
            </article>
          ))}
        </section>
      )}
    </main>
  );
}

export default ContenidoTareas;