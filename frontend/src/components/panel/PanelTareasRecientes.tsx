interface TareaMini {
  id: number | string;
  fechaVencimiento: string;
  titulo: string;
  descripcion: string;
  etiqueta?: string;
}

interface PanelTareasRecientesProps {
  proximasTareas?: TareaMini[];
}

export const PanelTareasRecientes = ({ proximasTareas }: PanelTareasRecientesProps) => {
  return (
    <section className="panel-grid-bottom">
      <div className="bottom-header">
        <h3 className="pixel-subtitle-bold">Próximas Tareas</h3>
        <a href="/tareas" className="link-ver-todas">Ver todas las tareas</a>
      </div>
      
      <div className="proximas-tareas-grid">
        {proximasTareas?.map((tarea) => (
          <div key={tarea.id} className="tarjeta-mini pixel-panel">
            <div className="tarjeta-mini-top">
              <span className="tarjeta-icono">📄</span>
              <span className="tarjeta-hora">{tarea.fechaVencimiento}</span>
            </div>
            <h4 className="tarjeta-mini-titulo">{tarea.titulo}</h4>
            <p className="tarjeta-mini-desc">{tarea.descripcion}</p>
            
            <div className="tarjeta-mini-footer">
              {tarea.etiqueta ? (
                <span className="pixel-chip-tech">{tarea.etiqueta}</span>
              ) : (
                <div className="tarjeta-equipo">
                  <div className="avatar-micro avatar-1"></div>
                  <div className="avatar-micro avatar-2"></div>
                  <span className="equipo-texto">+2 otros</span>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </section>
  );
};