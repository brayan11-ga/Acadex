// GruposAdmin
import { useCallback, useEffect, useMemo, useState } from "react";
import type{ MouseEvent } from "react";
import { ArrowLeft, Check, Copy, Search } from "lucide-react";
import { adminApi } from "../../services/adminapi";
import type { Grupo, Integrante } from "../../services/entidadesConfig";
import { AdminTableLoadingSkeleton } from "../skeletons/LoadingSkeletons";
import {EmptyState} from "../ui/EmptyState";

const formatearFecha=(f:string)=>
    new Date(f.length===10? `${f}T00:00:00`:f).toLocaleDateString('es-CO',{
        day:'numeric',
        month:'short',
        year:'numeric',
    });

    const BotonCopiar=({texto}:{texto:string})=>{
        const [copiado,setCopiado]=useState(false);

        const copiar=async(e:MouseEvent)=>{
            e.stopPropagation();
            try{
                await navigator.clipboard.writeText(texto);
                setCopiado(true);
                setTimeout(()=> setCopiado(false),1500);
            } catch{
                // sin permiso del porta papeles no hace nada
            }
        };
        return(
            <button type="button" className="codigo-grupo" onClick={copiar} aria-label={copiado ? 'Codigo copiado':`Copiar codigo ${texto}`}>
                <span>{texto}</span>
                {copiado ? <Check size={14}/>:<Copy size={14}/>}
            </button>
        );
    };

export const GruposAdmin=()=>{
    const [grupos, setGrupos]=useState<Grupo[]>([]);
    const [integrantes, setIntegrantes]= useState<Integrante[]>([]);
    const [cargando, setCargando]=useState(true);
    const [error, setError]=useState<string | null>(null);
    const [busqueda, setBusqueda]=useState('');
    const [seleccionandoId, setSeleccionandoId]=useState<number | null>(null);

    const cargar= useCallback(async()=>{
        setCargando(true);
        setError(null);
        const [g,i]=await Promise.all([
            adminApi.listar<Grupo>('grupos'),
            adminApi.listar<Integrante>('integrantes'),
        ]);
        if (g === null || i === null){
            setError('No se pudo cargar la informacion');
        }else{
            setGrupos(g);
            setIntegrantes(i);
        }
        setCargando(false);
    },[]);
    useEffect(()=>{
        void cargar();
    },[cargar]);

    const miembrosPorGrupo=useMemo(()=>{
        const mapa=new Map<number, Integrante[]>();
        integrantes.forEach((m)=>{
            const lista=mapa.get(m.id_grupo)??[];
            lista.push(m);
            mapa.set(m.id_grupo, lista);
        });
        mapa.forEach((lista)=>lista.sort((a, b)=>Number(b.rol==='lider')-Number(a.rol==='lider')));
        return mapa;
    },[integrantes]);

    const filtrados=useMemo(()=>{
        const q=busqueda.trim().toLowerCase();
        if(!q)return grupos;
        return grupos.filter(
            (g)=>g.nombre_grupo.toLowerCase().includes(q)|| g.codigo_acceso.toLowerCase().includes(q),
        );
    },[grupos,busqueda]);

    if (cargando){
        return<AdminTableLoadingSkeleton columns={['Grupo','Codigo','Integrantes']} hasActions={false} />;
    }

    if (error){
        return(
            <div className="error-msg" role="alert">
                <p>{error}</p>
                <button type="button" className="btn btn-secundario" onClick={()=>void cargar()}>
                    Reintentar
                </button>
            </div>
        );
    }

    const grupo=grupos.find((g)=>g.id_grupo===seleccionandoId);

    if (grupo){
        const miembros=miembrosPorGrupo.get(grupo.id_grupo)??[];
        const lider =miembros.find((m)=>m.rol==='lider');

        return(
            <section className="grupo-detalle">
                <button type="button" className="btn btn-secundario" onClick={()=> setSeleccionandoId(null)}>
                    <ArrowLeft size={14}/>Volver a grupos
                </button>

                <header className="grupo-detalle-cabecera">
                    <h2>{grupo.nombre_grupo}</h2>
                    {grupo.descripcion && <p>{grupo.descripcion}</p>}
                </header>

                <div className="grupo-detalle-cuerpo">
                    <div>
                        <h3>Integrantes({miembros.length})</h3>
                        {miembros.length===0?(
                            <EmptyState className="empty-state--compact" title="Este grupo no tiene integrantes" description="Cuando alguien se una con el codigo, aparecera aqui"/>
                        ):(
                            <ul className="miembros-lista">
                                {miembros.map((m)=>(
                                    <li key={m.id_integrante} className="miembro-fila">
                                        <span className="miembro-correo">
                                            {m.correo_electronico??`Usuario ${m.id_usuario}`}
                                        </span>
                                        <span className={`rol-badge rol-${m.rol}`}>
                                            {m.rol === 'lider'?'Lider':'Miembro'}
                                        </span>
                                        <span className="miembro-fecha">Desde{formatearFecha(m.fecha_ingreso)}</span>
                                    </li>
                                ))}
                            </ul>
                        )}
                    </div>

                    <aside className="grupo-resumen" aria-label="Datos del grupo">
                        <dl>
                            <dt>Codigo de acceso</dt>
                            <dd><BotonCopiar texto={grupo.codigo_acceso}/></dd>
                            <dt>Lider</dt>
                            <dd>{lider?.correo_electronico??'Sin lider asignado'}</dd>
                            <dt>Integrantes</dt>
                            <dd>{miembros.length}</dd>
                            <dt>Creado</dt>
                            <dd>{formatearFecha(grupo.fecha_creacion)}</dd>
                        </dl>
                    </aside>
                </div>
            </section>
        );
    }

    return(
        <div className="grupos-admin">
            <div className="grupos-barra">
                <label className="grupos-buscador">
                    <Search size={16} aria-hidden="true"/>
                    <input type="search" value={busqueda} onChange={(e) => setBusqueda(e.target.value)} placeholder="Buscar por nombre o codigo"/>
                </label>
                <span className="grupos-total">
                    {filtrados.length} de {grupos.length} grupos
                </span>
            </div>
            {filtrados.length===0?(
                <EmptyState className="empty-state--compact" title={grupos.length===0?'Aun no hay grupos creados':'Ningun grupo coincide'} description={grupos.length===0?'los grupos de estudio apareceran aqui cuando se creen':'prueba con otro nombre o codigo'}
                />
            ):(
                <ul className="grupos-grid">
                    {filtrados.map((g)=>{
                        const total = miembrosPorGrupo.get(g.id_grupo)?.length ?? 0;
                        return(
                            <li key={g.id_grupo} className="grupo-card">
                                <h3>{g.nombre_grupo}</h3>
                                <p className="grupo-card-desc">{g.descripcion|| 'Sin descripcion'}</p>
                                <div className="grupo-card-pie">
                                    <BotonCopiar texto="g.codigo_acceso"/>
                                    <button type="button" className="btn btn-secundario" onClick={()=>setSeleccionandoId(g.id_grupo)}> Ver integrantes({total})</button>
                                </div>
                            </li>
                        );
                    })}
                </ul>
            )}
        </div>
    );
};

export default GruposAdmin;