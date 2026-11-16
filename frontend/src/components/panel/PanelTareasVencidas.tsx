import type { TareaBackend } from "../../services/tareas";

interface PanelTareasVencidasProps{
    tareas:TareaBackend[];
    nombreCategoria: (id:number)=>string;
    onSeleccionar:(tarea:TareaBackend)=> void;
}

const textoRetraso =(iso:string)=>{
    const dias =Math.floor((Date.now()-new Date(iso).getTime())/86400000);
    return dias <1 ?"Vencio hoy": `Hace ${dias === 1 ? "dias":"dias"}`;
};

export const PanelTareasVencidas=({tareas, nombreCategoria, onSeleccionar}:PanelTareasVencidasProps)=>{
    if (tareas.length===0) return null;

    return(
        <section className="panel_grid-bottom panel-vencidas">
            <div className="button-header">
                <h3 className="pixel-subtitle-bold">Vencidas ({tareas.length})</h3>
                <a href="/tareas" className="link-ver-todas">Ver todas las tareas</a>
            </div>

            <div className="proximas-tareas-grid">
                {tareas.slice(0,6).map((tarea)=>(
                    <div 
                    key={tarea.id_tarea} 
                    className="tarjeta-mini pixel-panel tarjeta-vencida" 
                    role="button" 
                    tabIndex={0} 
                    aria-label={`${tarea.nombre}, vencida. Abrir aviso`} 
                    onClick={()=>onSeleccionar(tarea)} 
                    onKeyDown={(e)=>{if (e.key==="Enter"|| e.key===" "){e.preventDefault(); onSeleccionar(tarea);
                    }
                }}>
                    <div className="tarjeta-mini-top">
                        <span className="tarjeta-icono">📄</span>
                        <span className="tarjeta-hora">{textoRetraso(tarea.fecha_entrega)}</span>
                    </div>
                    <h4 className="tarjeta-mini-titulo">{tarea.nombre}</h4>
                    <p className="tarjeta-mini-desc">{tarea.descripcion}</p>
                    <div className="tarjeta-mini-footer">
                        <span className="pixel-chip-tach">{nombreCategoria(tarea.id_categoria).toUpperCase()}</span>
                    </div>
                </div>
                ))}
            </div>
        </section>
    );
};