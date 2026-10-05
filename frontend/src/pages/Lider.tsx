import { useEffect, useState, useCallback } from 'react';
import { Navigate, useNavigate,useParams } from 'react-router-dom';
import { listarMisGrupos, obtenerIntegrantes, expulsarIntegrante, eliminarGrupo } from '../services/grupos';import type { GrupoConRol, Integrante } from '../types/grupo';
import { obtenerIdUsuarioActual } from '../utils/jwt';
import '../styles/group-detail.css';

function Lider(){
    const {idGrupo}=useParams();
    const id=Number(idGrupo);
    const navigate=useNavigate();
    const idUsuarioActual=obtenerIdUsuarioActual();

    const [grupo, setGrupo]=useState<GrupoConRol | null>(null);
    const [Integrantes, setIntegrantes] =useState<Integrante[]>([]);
    const [cargando, setCargando]= useState(true);
    const [error, setError]= useState<string | null >(null);
    const [copiado, setCopiado]=useState(false);

    const cargar = useCallback(async()=>{
        try{
            const [grupo, miembros]= await Promise.all([
                listarMisGrupos(),
                obtenerIntegrantes(id),
            ]);
            setGrupo(grupo.find((g)=> g.id_grupo===id)?? null);
            setIntegrantes(miembros);
            setError(null);
        } catch{
            setError("No se encontro el panel");
        } finally{
            setCargando(false);
        }
    },[id]);
    useEffect(()=>{
        cargar();
    },[cargar]);

    const handleKick=async (idUsuario:number)=>{
        if (!window.confirm("¿expulsar a este integrante del grupo?")) return;
        try{
            await expulsarIntegrante(id, idUsuario);
            await cargar();
        }catch{
            setError("No se logro expulsar al integrante");
        }
    };
    const handleDelete = async () => {
    if (!window.confirm("¿Eliminar este grupo? Esta acción no se puede deshacer.")) return;
    try {
        await eliminarGrupo(id);
        navigate("/grupos");
    } catch {
        setError("No se logró eliminar el grupo");
    }
};
    const copiarCodigo = async()=>{
        if (!grupo) return;
        await navigator.clipboard.writeText(grupo.codigo_acceso);
        setCopiado(true);
        setTimeout(()=>setCopiado(false),2000);
    };
    
    console.log({ idGrupo, id, cargando, error, grupo });
    if (Number.isNaN(id)) return<Navigate to="/grupos" replace/>;
    if (cargando) return <p>Cargando panel...</p>;
    if (error) return <p>{error}</p>;
    if (!grupo || grupo.rol !=="lider") return <Navigate to="/grupos" replace/>;


    return (
    <section className="detail-view">
        <button className='detail-back' onClick={()=>navigate("/grupos")}>
        Volver a mis grupos
        </button>
        <header className='detail-header'>
        <div className='detail-header-info'>
        <h1 className='detail-title'>Panel de Líder — {grupo.nombre_grupo}</h1>
        <p className='detail.desc'>
        Codigo de acceso:<strong>{grupo.codigo_acceso}</strong>
        <button className='detail-btn' onClick={copiarCodigo}>
        {copiado ? "¡Copiado": "Copiar"}
        </button>
        </p>
        </div>
        <div className="detail-header-action">
        <button className="detail-btn detail-btn-danger" onClick={handleDelete}>
            Eliminar grupo
        </button>
        </div>
        </header>

        <div className='detail-members-block'>
        <h2 className='detail-section-title'>
            Integrantes<span className='detail-count'>{Integrantes.length}</span>
        </h2>
        <ul className='member-list'>
        {Integrantes.map((m)=>{
            const esYo =m.id_usuario ===idUsuarioActual;
            return(
                <li key={m.id_usuario} className='member-row'>
                    <div className="member-info">
                        <span className="member-avatar" arial-hidden="true">
                        {m.correo_electronico.charAt(0).toUpperCase()}
                        </span>
                        <div className="member-text">
                            <span className="member-email">
                                {m.correo_electronico}
                                {esYo && <span className='member-you'>tu</span>}
                            </span>
                            <span className={`member-role member-role--${m.rol==="lider"?"leader":"member"}`}>
                                {m.rol === "lider"?"Lider":"Miembro"}
                            </span>
                        </div>
                    </div>
                    {!esYo &&(
                        <button className='member-kick' onClick={()=>handleKick(m.id_usuario)}>
                            Expulsar
                        </button>
                    )}
                </li>
            );
        })}
        </ul>
        </div>
    </section>
    );
};

export default Lider;