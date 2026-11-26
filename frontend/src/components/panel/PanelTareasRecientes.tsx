import {Link} from 'react-router-dom';
import type { TareaBackend } from '../../services/tareas';
import { TarjetaTarea } from '../tareas/TarjetaTarea';
import { EmptyState } from "../ui/EmptyState";

interface PanelTareasRecientesProps{
  tareas: TareaBackend[];
  nombreCategoria: (id:number)=>string;
  formatearFecha: (iso:string)=>string;
  onVerDetalles: (id:number)=>void;
  onCompletar: (tarea:TareaBackend)=>void;
  onCrearTarea?: ()=>void;
}

export const PanelTareasRecientes = ({ tareas, nombreCategoria, formatearFecha, onVerDetalles, onCompletar, onCrearTarea }:
  PanelTareasRecientesProps) => {
  return (
  <section className="panel-grid-bottom">
    <div className="bottom-header">
      <h3 className="pixel-subtitle-bold">
        Próximas tareas
        {tareas.length > 0 && <span className="panel-contador">{tareas.length}</span>}
      </h3>
      <Link to="/tareas" className="link-ver-todas">Ver todas las tareas</Link>
    </div>

    <div className="panel-lista-tareas">
      {tareas.length > 0 ? (
        tareas.map((tarea) => (
          <TarjetaTarea
            key={tarea.id_tarea}
            tarea={tarea}
            nombreCategoria={nombreCategoria}
            formatearFecha={formatearFecha}
            onVerDetalles={onVerDetalles}
            onCambiarEstado={onCompletar}
          />
        ))
      ) : (
        <EmptyState
          className="empty-state--panel"
          headingLevel={4}
          title="No tienes tareas próximas"
          description="Crea una tarea para empezar a organizar tus actividades."
          action={onCrearTarea ? { label: 'Crear tarea', onClick: onCrearTarea } : undefined}
        />
      )}
    </div>
  </section>
);
}