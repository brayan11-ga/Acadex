// src/components/tareas/ContenidoTareas.tsx
import "../../styles/contenido-tareas.css";
import type { TareaBackend } from "../../services/tareas";
import { FiltrosTareas } from "./FiltrosTareas";
import { TarjetaTarea } from "./TarjetaTarea";
import { ModalDetalleTarea } from "./ModalDetalleTarea";
import { Paginacion } from "./Paginacion";
import { ModalConfirmacion } from "../layout/ModalConfirmacion";
import { useTareas } from "../../hooks/useTareas"; // Importamos nuestro nuevo cerebro

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
    paginaActual, setPaginaActual, totalPaginas, tareasPaginadas, tareasPendientes,
    nombreCategoria, formatearFecha, manejarCambiarEstado, manejarVerDetalles, tareaAEliminar, solicitarEliminar, confirmarEliminar,cancelarEliminar
  } = useTareas(refreshKey);

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

      {cargando && <p className="pixel-tareas-subtitle">Cargando tareas...</p>}
      {error && <p className="pixel-error">{error}</p>}

      {!cargando && !error && (
        <>
          <section className={`pixel-tareas-lista ${modoVista === "cuadricula" ? "vista-cuadricula" : ""}`}>
            {tareasPaginadas.length === 0 ? (
              <p className="pixel-tareas-subtitle" style={{ textAlign: "center", padding: "20px" }}>
                No hay tareas para mostrar.
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
                  onEliminar={solicitarEliminar}
                  onCambiarEstado={manejarCambiarEstado}
                />
              ))
            )}
          </section>

          <Paginacion 
            paginaActual={paginaActual} 
            totalPaginas={totalPaginas} 
            onCambiarPagina={setPaginaActual} 
          />
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

      <ModalConfirmacion
        isOpen={tareaAEliminar !== null}
        title="¿Eliminar Tarea?"
        message="Esta acción no se puede deshacer. La tarea será eliminada permanentemente de tu panel."
        onConfirm={confirmarEliminar}
        onCancel={cancelarEliminar}
      />
    </main>
  );
}

export default ContenidoTareas;