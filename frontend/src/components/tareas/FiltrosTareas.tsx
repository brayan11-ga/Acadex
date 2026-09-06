interface FiltrosTareasProps {
  filtroActivo: string;
  onCambiarFiltro: (filtro: string) => void;
}

export const FiltrosTareas = ({ filtroActivo, onCambiarFiltro }: FiltrosTareasProps) => {
  return (
    <div className="pixel-tareas-filtros">
      <span className="pixel-filtro-label">Filtrar por:</span>
      <button 
        className={`pixel-filtro-btn ${filtroActivo === "todas" ? "activo" : ""}`}
        onClick={() => onCambiarFiltro("todas")}
      >
        Todas
      </button>
      <button 
        className={`pixel-filtro-btn ${filtroActivo === "alta" ? "activo" : ""}`}
        onClick={() => onCambiarFiltro("alta")}
      >
        Alta Prioridad
      </button>
      <button 
        className={`pixel-filtro-btn ${filtroActivo === "activas" ? "activo" : ""}`}
        onClick={() => onCambiarFiltro("activas")}
      >
        Activas
      </button>
      <button 
        className={`pixel-filtro-btn ${filtroActivo === "completadas" ? "activo" : ""}`}
        onClick={() => onCambiarFiltro("completadas")}
      >
        Completadas
      </button>
    </div>
  );
};