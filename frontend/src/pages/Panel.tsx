// src/pages/Panel.tsx
import { useEffect } from 'react';
import { useAppDispatch, useAppSelector } from '../hooks/hooks';
import { fetchPanelData } from '../store/panelSlice';

import { PanelHero } from '../components/panel/PanelHero';
import { PanelTareasRecientes } from '../components/panel/PanelTareasRecientes';

import '../styles/Panel.css';

export const Panel = () => {
  const dispatch = useAppDispatch();

  const { data: datos, loading: cargando, error } = useAppSelector((state) => state.panel);

  useEffect(() => {
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
      <section className="panel-header-titulos">
        <h1 className="pixel-title-main">Panel</h1>
        <p className="pixel-subtitle">Concéntrate en lo que importa hoy.</p>
      </section>

      <PanelHero tareaPrioritaria={tareaPrioritaria} progreso={progreso} />

      <PanelTareasRecientes proximasTareas={proximasTareas} />
    </div>
  );
};

export default Panel;