// src/pages/Panel.tsx
import { useEffect, useState } from 'react';
import { useAppDispatch, useAppSelector } from '../hooks/hooks';
import { fetchPanelData } from '../store/panelSlice';
import { actualizarTarea } from '../services/tareas';

import { PanelHero } from '../components/panel/PanelHero';
import { PanelTareasRecientes } from '../components/panel/PanelTareasRecientes';

import '../styles/Panel.css';

export const Panel = () => {
  const dispatch = useAppDispatch();
  const { data: datos, loading: cargando } = useAppSelector((state) => state.panel);
  const [errorAccion, setErrorAccion] = useState<string | null>(null);

  useEffect(() => {
    dispatch(fetchPanelData());
  }, [dispatch]);

  const manejarCompletarTarea = async (idTarea: number) => {
    try {
      setErrorAccion(null);
      // Actualizamos el estado en el backend a "Completada"
      await actualizarTarea(idTarea, { estado: "Completada" });
      dispatch(fetchPanelData());
    } catch {
      setErrorAccion("No se pudo completar la tarea desde el panel.");
    }
  };

  if (cargando && !datos) {
    return (
      <div className="panel-contenedor panel-estado-container">
        <div className="pixel-panel panel-mensaje-cargando">
          <p className="pixel-text">Cargando tu panel...</p>
        </div>
      </div>
    );
  }

  const tareaPrioritaria = datos?.tareaPrioritaria;
  const progreso = datos?.progreso;
  const proximasTareas = datos?.proximasTareas;

  return (
    <div className="panel-contenedor">
      <section className="panel-header-titulos">
        <h1 className="pixel-title-main">Panel</h1>
        <p className="pixel-subtitle">Concéntrate en lo que importa hoy.</p>
      </section>

      {errorAccion && <p className="pixel-error">{errorAccion}</p>}

      <PanelHero 
        tareaPrioritaria={tareaPrioritaria} 
        progreso={progreso} 
        onCompletarTarea={manejarCompletarTarea} 
      />

      <PanelTareasRecientes proximasTareas={proximasTareas} />
    </div>
  );
};

export default Panel;