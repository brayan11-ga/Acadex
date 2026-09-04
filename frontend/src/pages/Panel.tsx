// src/pages/Panel.tsx
import { useEffect } from 'react';
import { useAppDispatch, useAppSelector } from '../hooks/hooks';
import { fetchPanelData } from '../store/panelSlice';
import '../styles/Panel.css'; 

export const Panel = () => {
  const dispatch = useAppDispatch();
  
  // Consumimos el estado global de Redux
  const { data: datos, loading: cargando, error } = useAppSelector((state) => state.panel);

  const nombreUsuario = "Cargando...";
  const rolUsuario = "Perfil";

  useEffect(() => {
    // Disparamos la acción para traer los datos reales de la BD al montar el componente
    dispatch(fetchPanelData());
  }, [dispatch]);

  if (cargando) {
    return <div className="panel-estado pixel-text">Cargando tu panel desde la base de datos...</div>;
  }

  if (error || !datos) {
    return <div className="panel-estado pixel-error">{error || "No se encontraron datos."}</div>;
  }

  const { tareaPrioritaria, progreso, proximasTareas } = datos;

  return (
    <div className="panel-contenedor">
      {/* --- TopBar: Buscador y Perfil --- */}
      <header className="panel-topbar">
        <div className="search-container pixel-panel-flat">
          <span className="search-icon">🔍</span>
          <input 
            type="text" 
            placeholder="Buscar tareas o comandos..." 
            className="pixel-input-search"
          />
        </div>
        
        <div className="user-profile">
          <button className="btn-notificacion" aria-label="Notificaciones">🔔</button>
          <div className="user-info">
            <span className="user-name">{nombreUsuario}</span>
            <span className="user-role">{rolUsuario}</span>
          </div>
          <div className="user-avatar pixel-avatar"></div>
        </div>
      </header>

      {/* --- Encabezado --- */}
      <section className="panel-header-titulos">
        <h1 className="pixel-title-main">Panel</h1>
        <p className="pixel-subtitle">Concéntrate en lo que importa hoy.</p>
      </section>

      {/* --- Grid Superior (Hero) --- */}
      <section className="panel-grid-top">
        {tareaPrioritaria && (
          <div className="tarjeta-prioridad pixel-panel">
            <div className="prioridad-top">
              <span className="pixel-chip-priority">{tareaPrioritaria.etiqueta}</span>
              <span className="prioridad-tiempo">▾ {tareaPrioritaria.fechaVencimiento}</span>
            </div>
            
            <h2 className="prioridad-titulo">{tareaPrioritaria.titulo}</h2>
            <p className="prioridad-desc">{tareaPrioritaria.descripcion}</p>
            
            <div className="prioridad-acciones">
              <button className="pixel-btn-play">
                <span className="icon">▶</span> Iniciar Tarea
              </button>
              <button className="pixel-btn-outline-success">
                <span className="icon">✔</span> Completar
              </button>
            </div>
          </div>
        )}

        {progreso && (
          <div className="tarjeta-progreso pixel-panel">
            <h3 className="progreso-titulo">PROGRESO DIARIO</h3>
            <div className="progreso-stats">
              <span className="progreso-completadas">{progreso.completadas}</span>
              <span className="progreso-total">/{progreso.total}</span>
            </div>
            <p className="progreso-desc">
              {progreso.completadas} tareas completadas, faltan {progreso.total - progreso.completadas}
            </p>
            
            <div className="progreso-grafico">
              {progreso.dias.map((dia, idx) => (
                <div key={idx} className="grafico-columna">
                  <div 
                    className={`grafico-barra ${dia.actual ? 'barra-activa' : ''}`}
                    style={{ height: `${dia.cantidad > 0 ? dia.cantidad * 25 : 10}%` }}
                  ></div>
                  <span className={`grafico-dia ${dia.actual ? 'dia-activo' : ''}`}>
                    {dia.dia}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}
      </section>

      {/* --- Grid Inferior: Próximas Tareas --- */}
      <section className="panel-grid-bottom">
        <div className="bottom-header">
          <h3 className="pixel-subtitle-bold">Próximas Tareas</h3>
          <a href="/tareas" className="link-ver-todas">Ver todas las tareas</a>
        </div>
        
        <div className="proximas-tareas-grid">
          {proximasTareas.map((tarea) => (
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
                {tarea.id === 4 && (
                  <div className="mini-barra-progreso">
                    <div className="mini-barra-relleno" style={{ width: '80%' }}></div>
                    <span className="mini-barra-porcentaje">80%</span>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
};

export default Panel;