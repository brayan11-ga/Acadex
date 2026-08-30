import "../../styles/contenido-tareas.css"; // Importamos los estilos limpios

interface ContenidoTareaProps {
  onNuevaTarea: () => void;
}

// Interfaz fuertemente tipada basada en la estructura del formulario de Samuel
interface Tarea {
  id: number;
  titulo: string;
  categoria: string;
  fecha: string;
  dificultad: number; // del 1 al 5
  estado: "Pendiente" | "En progreso" | "Completada";
}

// Datos de prueba temporales
const TAREAS_MOCK: Tarea[] = [
  { id: 1, titulo: "Preparar presentación de Acadex", categoria: "Documentación", fecha: "Hoy, 5:00 PM", dificultad: 5, estado: "Pendiente" },
  { id: 2, titulo: "Terminar API del Backend", categoria: "Backend", fecha: "Mañana, 10:00 AM", dificultad: 3, estado: "En progreso" },
  { id: 3, titulo: "Revisar prototipos en Figma", categoria: "Diseño", fecha: "Completado hace 2h", dificultad: 1, estado: "Completada" },
];

function ContenidoTareas({ onNuevaTarea }: ContenidoTareaProps) {
  // Calculamos tareas pendientes para el subtítulo
  const tareasPendientes = TAREAS_MOCK.filter(t => t.estado !== "Completada").length;

  return (
    <main className="pixel-tareas-main">
      {/* Encabezado */}
      <header className="pixel-tareas-header">
        <div>
          <h1 className="pixel-tareas-title">Tus Tareas</h1>
          <p className="pixel-tareas-subtitle">Tienes {tareasPendientes} tareas pendientes esta semana. Mantén el enfoque.</p>
        </div>
        
        {/* Este botón luego activará el modal del formulario */}
        <button className="pixel-btn-primario" onClick={onNuevaTarea}>
          + Crear Tarea
        </button>
      </header>

      {/* Barra de Filtros tipo "TaskFlow Elite" */}
      <div className="pixel-tareas-filtros">
        <span className="pixel-filtro-label">Filtrar por:</span>
        <button className="pixel-filtro-btn activo">Todas</button>
        <button className="pixel-filtro-btn">Alta Prioridad</button>
        <button className="pixel-filtro-btn">Activas</button>
        <button className="pixel-filtro-btn">Completadas</button>
      </div>

      {/* Lista de Tarjetas */}
      <section className="pixel-tareas-lista">
        {TAREAS_MOCK.map((tarea) => (
          <article 
            key={tarea.id} 
            className={`pixel-tarea-card ${tarea.estado === 'Completada' ? 'completada' : ''}`}
          >
            <div className="pixel-tarea-info">
              <div className="pixel-tarea-header-card">
                <h3 className="pixel-tarea-titulo">{tarea.titulo}</h3>
                {/* Badge de dificultad usando las variables de Samuel */}
                <span className={`pixel-badge-dificultad nivel-${tarea.dificultad}`}>
                  Nivel {tarea.dificultad}
                </span>
              </div>
              <div className="pixel-tarea-detalles">
                <span>📅 {tarea.fecha}</span>
                <span>📂 {tarea.categoria}</span>
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
    </main>
  );
}

export default ContenidoTareas;