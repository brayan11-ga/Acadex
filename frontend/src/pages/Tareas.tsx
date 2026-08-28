import Sidebar from '../components/dashboard/Sidebar';
import ContenidoTarea from '../components/dashboard/ContenidoTareas';

import '../styles/tareas.css';

function Tareas() {
  return (
    <div className="tareas-page">
      <Sidebar />

      <div className="tareas-main">
        <ContenidoTarea />
      </div>
    </div>
  );
}

export default Tareas;