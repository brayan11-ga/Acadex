// PanelResumen
export interface ResumenTareas{
    vencidas:number;
    hoy:number;
    semana: number;
    pendientes:number;
}

export const PanelResumen=({vencidas, hoy, semana, pendientes}: ResumenTareas)=>{
    const items=[
        {clave:'vencidas', etiqueta:'Vencidas', valor:vencidas},
        {clave:'hoy', etiqueta: 'Para hoy', valor:hoy},
        {clave:'semana', etiqueta:'proximos 7 dias', valor:semana},
        {clave:'pendientes', etiqueta:'Pendientes', valor:pendientes},
    ];

    return (
        <section className="panel-resumen pixel-panel" aria-labelledby="panel-resumen-titulo">
        <header>
        <h2 id="panel-resumen-titulo" className="panel-resumen-titulo">Tu carga de trabajo</h2>
        <p className="panel-resumen-sub">Tareas pendientes según su fecha de entrega</p>
        </header>

        <dl className="panel-resumen-grid">
        {items.map(({ clave, etiqueta, valor }) => (
            <div
            key={clave}
            className={`panel-resumen-item panel-resumen-item--${clave} ${valor === 0 ? 'vacio' : ''}`}
            >
            <dt>{etiqueta}</dt>
            <dd>{valor}</dd>
            </div>
        ))}
        </dl>
    </section>
    );
};
