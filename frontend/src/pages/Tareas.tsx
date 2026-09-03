// src/pages/Tareas.tsx
import { useOutletContext } from 'react-router-dom';
import ContenidoTareas from '../components/tareas/ContenidoTareas';
import type { TareaBackend } from '../services/tareas';
import '../styles/tareas.css';

interface AppContext {
  abrirModalGlobal: () => void;
  abrirModalEditar: (tarea: TareaBackend) => void;
  refreshKey: number;
}

function Tareas() {
  const { abrirModalGlobal, abrirModalEditar, refreshKey } = useOutletContext<AppContext>();

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