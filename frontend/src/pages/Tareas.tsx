import { useOutletContext } from 'react-router-dom';
import ContenidoTareas from '../components/tareas/ContenidoTareas';
import '../styles/tareas.css';

// Le decimos a TypeScript qué tipo de dato viene en el contexto
interface AppContext {
  abrirModalGlobal: () => void;
}

function Tareas() {
  // Extraemos la función global
  const { abrirModalGlobal } = useOutletContext<AppContext>();

  return (
    <div className="pixel-tareas-page">
      {/* Conectamos tu botón al modal global */}
      <ContenidoTareas onNuevaTarea={abrirModalGlobal} />
    </div>
  );
}

export default Tareas;