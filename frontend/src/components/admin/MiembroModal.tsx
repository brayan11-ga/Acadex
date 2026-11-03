import { useEffect } from "react";
import {X} from 'lucide-react'
import type { Grupo, Integrante, Usuarios } from "../../services/entidadesConfig";
import { formatearFecha } from "../../utils/formatoFecha";

interface Props{
    miembro:Integrante;
    grupo:Grupo;
    usuario?:Usuarios;
    otrosGrupos:string[];
    onCerrar:()=>void;
}

export const MiembroModal=({miembro, grupo, usuario, otrosGrupos, onCerrar}: Props)=>{
    useEffect(()=>{
        const alTeclear = ( e:KeyboardEvent) =>{
            if (e.key=== 'Escape') onCerrar();
        };
        document.addEventListener('keydown',alTeclear);
        return()=>document.removeEventListener('keydown',alTeclear);
    },[onCerrar]);

    const nombre= miembro.correo_electronico?? usuario?.correo_electronico??`Usuario ${miembro.id_usuario}`;

    return(
        <div className="modal" style={{display:'flex'}} onClick={(e)=>{
            if (e.target===e.currentTarget) onCerrar();
        }}
        >
            <div className="modal-content miembro-modal" role="dialog" aria-modal="true" aria-labelledby="miembro-modal-titulo">
                <button type="button" className="miembro-modal-cerrar" onClick={onCerrar} aria-label="Cerrar" autoFocus>
                    <X size={18}/>
                </button>

                <h2 id="miembro-modal-titulo">{nombre}</h2>

                <div className="miembro-modal-badges">
                    <span className={`rol-badge rol-${miembro.rol}`}>
                        {miembro.rol==='lider'?'Lider':'Miembro'}
                    </span>
                    {usuario?.es_admin &&<span className="rol-badge">administrador</span>}
                </div>

                <dl className="miembro-modal-datos">
                    <dt>Grupo</dt>
                    <dd>{grupo.nombre_grupo}</dd>
                    <dt>Miembro desde</dt>
                    <dd>{formatearFecha(miembro.fecha_ingreso)}</dd>
                    {usuario &&(
                        <>
                        <dt>Cuenta Creada</dt>
                        <dd>{formatearFecha(usuario.fecha_registro)}</dd>
                        </>
                    )}
                    <dt>Otro grupos</dt>
                    <dd>{otrosGrupos.length>0 ? otrosGrupos.join(', '):'Solo esta en el grupo'}</dd>
                </dl>
            </div>
        </div>
    );
};

export default MiembroModal;