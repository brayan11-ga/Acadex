import { useOutletContext } from 'react-router-dom';
import ContenidoTareas from '../components/tareas/ContenidoTareas';
import '../styles/tareas.css';

interface AppContext {
  abrirModalGlobal: () => void;
  refreshKey: number;
}

function Tareas() {
  const { abrirModalGlobal, refreshKey } = useOutletContext<AppContext>();

  return (
    <div className="pixel-tareas-page">
      <ContenidoTareas onNuevaTarea={abrirModalGlobal} refreshKey={refreshKey} />
    </div>
  );
}

export default Tareas;