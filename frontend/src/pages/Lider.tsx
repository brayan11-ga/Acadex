// Ruta: frontend/src/pages/Lider.tsx
import { useEffect, useState, useCallback } from 'react';
import { Navigate, useNavigate,useParams } from 'react-router-dom';
import { listarMisGrupos, obtenerIntegrantes, expulsarIntegrante, eliminarGrupo, regenerarCodigoAcceso } from '../services/grupos';import type { GrupoConRol, Integrante } from '../types/grupo';
import { obtenerIdUsuarioActual } from '../utils/jwt';
import { GroupMembersLoadingSkeleton } from '../components/skeletons/LoadingSkeletons';
import '../styles/group-detail.css';

function formatearTiempoRestante(segundos: number): string {
    const minutos = Math.floor(segundos / 60);
    const resto = segundos % 60;
    return `${String(minutos).padStart(2, "0")}:${String(resto).padStart(2, "0")}`;
}

function Lider(){
    const {idGrupo}=useParams();
    const id=Number(idGrupo);
    if (Number.isNaN(id)) return <Navigate to="/grupos" replace />;
    return <PanelLider key={id} id={id} />;
}

function PanelLider({ id }: { id: number }) {
    const navigate=useNavigate();
    const idUsuarioActual=obtenerIdUsuarioActual();

    const [grupo, setGrupo]=useState<GrupoConRol | null>(null);
    const [Integrantes, setIntegrantes] =useState<Integrante[]>([]);
    const [cargando, setCargando]= useState(true);
    const [error, setError]= useState<string | null >(null);
    const [copiado, setCopiado]=useState(false);
    const [regenerando, setRegenerando]=useState(false);
    const [errorRegenerar, setErrorRegenerar]=useState<string | null>(null);
    const [contador, setContador] = useState<{ inicial: number; restante: number } | null>(null);
    const segundosRestantes = contador?.restante ?? null;

    const cargar = useCallback(() => Promise.all([listarMisGrupos(), obtenerIntegrantes(id)])
        .then(([grupos, miembros]) => {
            const encontrado = grupos.find((g) => g.id_grupo === id) ?? null;
            const inicial = encontrado?.segundos_restantes_codigo ?? null;
            setGrupo(encontrado);
            setIntegrantes(miembros);
            setError(null);
            setContador((previo) => {
                if (inicial === null) return null;
                return previo?.inicial === inicial ? previo : { inicial, restante: inicial };
            });
        })
        .catch(() => {
            setError("No se encontro el panel");
        })
        .finally(() => {
            setCargando(false);
        }), [id]);
    useEffect(()=>{
        void cargar();
    },[cargar]);

    const contadorActivo = segundosRestantes !== null && segundosRestantes > 0;
    useEffect(()=>{
        if (!contadorActivo) return;
        const intervalo = setInterval(()=>{
            setContador((previo) =>
                previo && { ...previo, restante: Math.max(0, previo.restante - 1) },
            );
        }, 1000);
        return ()=> clearInterval(intervalo);
    }, [contadorActivo]);

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
        if (!grupo || !grupo.codigo_acceso) return;
        await navigator.clipboard.writeText(grupo.codigo_acceso);
        setCopiado(true);
        setTimeout(()=>setCopiado(false),2000);
    };

    const handleRegenerar = async()=>{
        if (!grupo) return;
        const confirmado = window.confirm(
            "¿Regenerar el código de acceso? El código anterior dejará de funcionar de inmediato y no podrás volver a usarlo."
        );
        if (!confirmado) return;

        setRegenerando(true);
        setErrorRegenerar(null);
        try{
            const actualizado = await regenerarCodigoAcceso(id);
            setGrupo((prev)=> prev ? {
                ...prev,
                codigo_acceso: actualizado.codigo_acceso,
                fecha_expiracion_codigo: actualizado.fecha_expiracion_codigo,
                segundos_restantes_codigo: actualizado.segundos_restantes_codigo,
            } : prev);
            const inicial = actualizado.segundos_restantes_codigo ?? null;
            setContador(inicial === null ? null : { inicial, restante: inicial });
            setCopiado(false);
        }catch(error){
            setErrorRegenerar(
                error instanceof Error
                    ? error.message
                    : "No se logró regenerar el código de acceso"
            );
        }finally{
            setRegenerando(false);
        }
    };
    
    if (cargando) return <GroupMembersLoadingSkeleton label="Cargando el panel de líder" />;
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
        Codigo de acceso:<strong>{grupo.codigo_acceso ?? "—"}</strong>
        <span>
        {" · "}
        {segundosRestantes === null || segundosRestantes <= 0
            ? "Vencido"
            : `Vence en ${formatearTiempoRestante(segundosRestantes)}`}
        </span>
        <button className='detail-btn' onClick={copiarCodigo} disabled={regenerando}>
        {copiado ? "¡Copiado": "Copiar"}
        </button>
        <button className='detail-btn' onClick={handleRegenerar} disabled={regenerando}>
        {regenerando ? "Regenerando..." : "Regenerar código"}
        </button>
        </p>
        {errorRegenerar && <p className='detail-error'>{errorRegenerar}</p>}
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
