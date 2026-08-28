import '../../styles/contenidoTarea.css'

function ContenidoTarea() {
  const tareas = [
    {
      id: 1,
      nombre: "Preparar presentación de Acadex",
      categoria: "Proyecto",
      fecha: "7 de septiembre",
      estado: "Pendiente",
    },
    {
      id: 2,
      nombre: "Terminar documentación",
      categoria: "Académica",
      fecha: "5 de septiembre",
      estado: "En progreso",
    },
    {
      id: 3,
      nombre: "Revisar pruebas del proyecto",
      categoria: "Desarrollo",
      fecha: "6 de septiembre",
      estado: "Completada",
    },
  ];

  return (
    <main className="tareas-content">
      <div className="tareas-header">
        <div>
          <h1>Mis tareas</h1>
          <p>Organiza y consulta tus tareas académicas.</p>
        </div>

        <button className="btn-nueva-tarea">
          + Nueva tarea
        </button>
      </div>

      <div className="tareas-filtros">
        <button className="filtro activo">Todas</button>
        <button className="filtro">Pendientes</button>
        <button className="filtro">En progreso</button>
        <button className="filtro">Completadas</button>
      </div>

      <section className="lista-tareas">
        {tareas.map((tarea) => (
          <article className="tarea-card" key={tarea.id}>
            <div className="tarea-info">
              <h3>{tarea.nombre}</h3>

              <div className="tarea-detalles">
                <span>{tarea.categoria}</span>
                <span>📅 {tarea.fecha}</span>
              </div>
            </div>

            <span
              className={`estado ${tarea.estado
                .toLowerCase()
                .replace(" ", "-")}`}
            >
              {tarea.estado}
            </span>
          </article>
        ))}
      </section>
    </main>
  );
}

export default ContenidoTarea;