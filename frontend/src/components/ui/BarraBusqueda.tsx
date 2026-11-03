import { Search } from "lucide-react";
import '../../styles/BarraBusqueda.css'

interface Props{
    valor:string;
    onCambiar:(valor:string)=> void;
    placeholder?:string;
    className?:string;
    visibles?:number;
    total?:number;
    unidad?:string;
}

export const BarraBusqueda=({
    valor,
    onCambiar,
    placeholder='Buscar',
    className='',
    visibles,
    total,
    unidad,
}:Props)=>(
    <div className={`busqueda ${className}`.trim()}>
        <label className="busqueda-campo">
            <Search size={16} aria-hidden="true"/>
            <input type="search" value={valor} onChange={(e)=> onCambiar(e.target.value)} placeholder={placeholder} aria-label={placeholder} />
        </label>
        {visibles !== undefined && total !== undefined &&(
            <span className="busqueda-total" aria-live="polite">
                {visibles} de {total} {unidad}
            </span>
        )}
    </div>
);

export default BarraBusqueda;