// PanelTareasVencidas
import {Link} from 'react-router-dom';
import type { TareaBackend } from "../../services/tareas";
import { TarjetaTarea } from '../tareas/TarjetaTarea';

interface PanelTareasVencidasProps{
    tareas:TareaBackend[];
    nombreCategoria: (id:number)=>string;
    formatearFecha:(iso:string)=>string;
    onVerDetalles:(id:number)=>void;
    onSeleccionar:(tarea:TareaBackend)=> void;
}

export const PanelTareasVencidas=({tareas, nombreCategoria, formatearFecha, onVerDetalles, onSeleccionar}:
    PanelTareasVencidasProps)=>{
    if (tareas.length===0) return null;

  return (
    <section className="panel-grid-bottom panel-vencidas">
      <div className="bottom-header">
        <h3 className="pixel-subtitle-bold">
          Vencidas <span className="panel-contador">{tareas.length}</span>
        </h3>
        <Link to="/tareas" className="link-ver-todas">Ver todas las tareas</Link>
      </div>

      <div className="panel-lista-tareas">
        {tareas.slice(0, 6).map((tarea) => (
          <TarjetaTarea
            key={tarea.id_tarea}
            tarea={tarea}
            nombreCategoria={nombreCategoria}
            formatearFecha={formatearFecha}
            onVerDetalles={onVerDetalles}
            onCambiarEstado={onSeleccionar}
          />
        ))}
      </div>
    </section>
  );
};