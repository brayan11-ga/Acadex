// src/components/tareas/ContenidoTareas.tsx
import { useEffect, useState } from "react";
import { TarjetaTarea } from "./TarjetaTarea";
import "../../styles/contenido-tareas.css";
import type { TareaBackend } from "../../services/tareas";
import { FiltrosTareas } from "./FiltrosTareas";
import { Paginacion } from "./Paginacion";
import { TarjetaCategoria } from "./TarjetaCategoria";
import { TaskListLoadingSkeleton } from "../skeletons/LoadingSkeletons";
import { EmptyState } from "../ui/EmptyState";
import { ModalConfirmarEliminar } from "./ModalConfirmarEliminar";
import { useTareas } from "../../hooks/useTareas"; // Importamos nuestro nuevo cerebro
import { ModalDetalleTarea } from "./ModalDetalleTarea";

interface ContenidoTareaProps {
  onNuevaTarea: () => void;
  onEditarTarea: (tarea: TareaBackend) => void;
  refreshKey: number;
}

function ContenidoTareas({ onNuevaTarea, onEditarTarea, refreshKey }: ContenidoTareaProps) {
  // Extraemos toda la lógica desde nuestro Custom Hook
    const {
  cargando, error, tareaDetalle, setTareaDetalle,
  filtroActivo, setFiltroActivo, modoVista, setModoVista,
  paginaActual, setPaginaActual, totalPaginas, gruposPaginados, gruposFiltrados, tareasPendientes,
  totalTareas,
  nombreCategoria, formatearFecha, manejarCambiarEstado, manejarVerDetalles,
  tareaAEliminar, solicitarEliminar, confirmarEliminar, cancelarEliminar
} = useTareas(refreshKey);

  const [categoriaAbierta, setCategoriaAbierta] = useState<number | null>(null);
  const grupoAbierto = gruposFiltrados.find((g) => g.idCategoria === categoriaAbierta) ?? null;
  const [paginaTareas, setPaginaTareas]= useState(1)
  const TAREAS_POR_PAGINA=modoVista==="cuadricula"?12:6;

  useEffect(()=>{
    setPaginaTareas(1);
  }, [categoriaAbierta ,filtroActivo, modoVista]);

  const totalPaginasTareas=Math.max(
    1,
    Math.ceil((grupoAbierto?.tareas.length??0)/TAREAS_POR_PAGINA)
  );

  const paginaSegura= Math.min(paginaTareas, totalPaginasTareas);
  const tareasPaginadas =
  grupoAbierto?.tareas.slice(
    (paginaSegura-1)* TAREAS_POR_PAGINA,
    paginaSegura * TAREAS_POR_PAGINA
  )??[];

  return (
    <main className="pixel-tareas-main">
      <header className="pixel-tareas-header">
        <div>
          <h1 className="pixel-tareas-title">Tus Tareas</h1>
          <p className="pixel-tareas-subtitle">
            {totalTareas === 0
              ? "Crea tu primera tarea para empezar a organizar tus actividades."
              : tareasPendientes === 0
                ? "¡Vas al día! No tienes tareas pendientes."
                : `Tienes ${tareasPendientes} tareas pendientes esta semana. Mantén el enfoque.`}
          </p>
        </div>
        <button className="pixel-btn-primario" onClick={onNuevaTarea}>
          + Crear Tarea
        </button>
      </header>

      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", flexWrap: "wrap", gap: "1rem" }}>
        <FiltrosTareas filtroActivo={filtroActivo} onCambiarFiltro={setFiltroActivo} />

        <div className="pixel-tareas-filtros" style={{ marginBottom: "2rem" }}>
          <span className="pixel-filtro-label">Vista:</span>
          <button
            className={`pixel-filtro-btn ${modoVista === "lista" ? "activo" : ""}`}
            onClick={() => setModoVista("lista")}
          >
            ☰ Lista
          </button>
          <button
            className={`pixel-filtro-btn ${modoVista === "cuadricula" ? "activo" : ""}`}
            onClick={() => setModoVista("cuadricula")}
          >
            ⊞ Cuadrícula
          </button>
        </div>
      </div>

      {cargando && <TaskListLoadingSkeleton />}
      {error && <p className="pixel-error">{error}</p>}

      {!cargando && !error && (
  categoriaAbierta !== null ? (
    <>
      <button
        type="button"
        className="pixel-filtro-btn"
        style={{ marginBottom: "1.5rem" }}
        onClick={() => setCategoriaAbierta(null)}
      >
        ← Volver a categorías
      </button>

      {grupoAbierto ? (
        <section className="pixel-categoria-grupo">
          <h2 className="pixel-categoria-titulo">
            {grupoAbierto.nombre}
          </h2>
            <p className="pixel-categoria-subtitulo">
              Total tareas: {grupoAbierto.tareas.length}
            </p>
          <div className={`pixel-tareas-lista ${modoVista === "cuadricula" ? "vista-cuadricula" : ""}`}>
            {tareasPaginadas.map((tarea) => (
              <TarjetaTarea
                key={tarea.id_tarea}
                tarea={tarea}
                nombreCategoria={nombreCategoria}
                formatearFecha={formatearFecha}
                onVerDetalles={manejarVerDetalles}
                onEditar={onEditarTarea}
                onEliminar={solicitarEliminar}
                onCambiarEstado={manejarCambiarEstado}
              />
            ))}
          </div>
          <Paginacion
          paginaActual={paginaSegura}
          totalPaginas={totalPaginasTareas}
          onCambiarPagina={setPaginaTareas}
          />
        </section>
      ) : (
        <EmptyState
          title="No hay tareas de esta categoría con este filtro"
          description="Prueba con otro filtro o vuelve a las categorías."
          action={{ label: "Ver todas las tareas", onClick: () => setFiltroActivo("todas") }}
        />
      )}
    </>
  ) : (
    <>
      <div className={`pixel-tareas-grupos ${modoVista === "cuadricula" ? "vista-cuadricula" : ""}`}>
        {gruposPaginados.length === 0 ? (
          totalTareas === 0 ? (
            <EmptyState
              title="Aún no tienes tareas"
              description="Usa el botón «Crear tarea» para agregar tu primera actividad."
            />
          ) : (
            <EmptyState
              title="No encontramos tareas con este filtro"
              description="Prueba con otro filtro o vuelve a ver todas tus tareas."
              action={{ label: "Ver todas las tareas", onClick: () => setFiltroActivo("todas") }}
            />
          )
        ) : (
          gruposPaginados.map((grupo) => (
            <TarjetaCategoria
              key={grupo.idCategoria}
              nombre={grupo.nombre}
              totalTareas={grupo.tareas.length}
              rendimiento={grupo.rendimiento}
              onAbrir={() => setCategoriaAbierta(grupo.idCategoria)}
            />
          ))
        )}
      </div>

      <Paginacion
        paginaActual={paginaActual}
        totalPaginas={totalPaginas}
        onCambiarPagina={setPaginaActual}
      />
    </>
  )
)}
      {tareaDetalle && (
        <ModalDetalleTarea
          tarea={tareaDetalle}
          nombreCategoria={nombreCategoria}
          formatearFecha={formatearFecha}
          onCerrar={() => setTareaDetalle(null)}
        />
      )}

      {tareaAEliminar !== null &&(
        <ModalConfirmarEliminar
        onConfirmar={confirmarEliminar}
        onCancelar={cancelarEliminar}
        />
      )}


    </main>
  );
}

export default ContenidoTareas;