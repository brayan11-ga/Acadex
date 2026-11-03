export const formatearFecha=(fecha:string):string=>
    new Date(fecha.length===10? `${fecha}T00:00:00`:fecha).toLocaleDateString('es-CO',{
        day: 'numeric',
        month:'short',
        year:'numeric'
    });