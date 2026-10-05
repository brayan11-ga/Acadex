// src/components/tareas/Paginacion.tsx

interface PaginacionProps {
  paginaActual: number;
  totalPaginas: number;
  onCambiarPagina: (numeroPagina: number) => void;
}

export const Paginacion = ({ paginaActual, totalPaginas, onCambiarPagina }: PaginacionProps) => {
  if (totalPaginas <= 1) return null;

  return (
    <div className="pixel-paginacion-container">
      <button
        className="pixel-btn-primario"
        style={{ padding: "8px 16px", background: paginaActual === 1 ? "#ccc" : undefined }}
        disabled={paginaActual === 1}
        onClick={() => onCambiarPagina(paginaActual - 1)}
      >
        Anterior
      </button>
      <span className="pixel-paginacion-texto">
        Página {paginaActual} de {totalPaginas}
      </span>
      <button
        className="pixel-btn-primario"
        style={{ padding: "8px 16px", background: paginaActual === totalPaginas ? "#ccc" : undefined }}
        disabled={paginaActual === totalPaginas}
        onClick={() => onCambiarPagina(paginaActual + 1)}
      >
        Siguiente
      </button>
    </div>
  );
};