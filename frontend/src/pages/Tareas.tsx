// src/pages/Tareas.tsx
import { useOutletContext } from 'react-router-dom';
import ContenidoTareas from '../components/tareas/ContenidoTareas';
import type { AppLayoutContext } from '../types/AppLayoutContext';
import '../styles/tareas.css';

function Tareas() {
  const { abrirModalGlobal, abrirModalEditar, refreshKey } = useOutletContext<AppLayoutContext>();

  return (
    <div className="pixel-tareas-page">
      <ContenidoTareas
        onNuevaTarea={abrirModalGlobal}
        onEditarTarea={abrirModalEditar}
        refreshKey={refreshKey}
      />
    </div>
  );
}

export default Tareas;
