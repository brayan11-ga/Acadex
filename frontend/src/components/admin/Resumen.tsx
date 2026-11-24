import { useCallback ,useEffect, useMemo, useState } from 'react';
import type { LucideIcon } from 'lucide-react';
import { ListChecks, Tag, UserCog, Users, UsersRound } from 'lucide-react';
import { adminApi } from '../../services/adminapi';
import { usePerfilActual } from '../../hooks/usePerfilActual';
import type { Grupo, Integrante, Usuarios } from '../../services/entidadesConfig';

interface ResumenAdminData{
  usuarios:number;
  categorias:number;
  grupos:number;
  tareas:number;
  integrantes:number;
}

interface Listas{
  usuarios: Usuarios[];
  grupos:Grupo[];
  integrantes:Integrante[];
}

interface Segmentos{
  etiqueta:string;
  valor:number;
  clase:'principal'|'neutro'|'alerta'
}

interface Props{
  onIrA:(clave:string)=>void;
}

interface Tarjeta{
  campo: keyof ResumenAdminData;
  titulo: string;
  icono:LucideIcon;
  destino?:string;
}

const TARJETAS: Tarjeta [] = [
  {campo: 'grupos', titulo:'Grupos', icono:UsersRound , destino:'grupos'},
  {campo: 'usuarios', titulo:'Usuarios', icono:Users , destino:'usuarios'},
  {campo: 'integrantes', titulo:'Integrantes', icono:UserCog , destino:'grupos'},
  {campo: 'tareas', titulo:'Tareas', icono:ListChecks},
  {campo: 'categorias', titulo:'Categorias', icono:Tag , destino:'categorias'},
];

const detalleDe =(campo:keyof ResumenAdminData, d: ResumenAdminData): string=>{
  switch (campo){
    case 'grupos':
      return d.grupos===0 ? 'Aun no hay grupos creados' : `${(d.integrantes/ d.grupos).toFixed(1)} integrantes por grupo`;
      case 'usuarios':
        return 'Cuentas registradas';
      case 'integrantes':
        return 'Membresias en grupos';
      case 'tareas':
        return 'Individuales y grupales';
      case 'categorias':
        return 'Para clasificar tareas'
  }
};

const BarraSegmentada=({titulo,segmentos}:{titulo:string, segmentos:Segmentos[]})=>{
  const total =segmentos.reduce((suma,s)=>suma + s.valor,0);
  return(
    <section className="resumen-panel">
      <h2>{titulo}</h2>
      {total===0?(
        <p className='resumen-aviso'>Sin datos todavia</p>
      ):(
        <>
        <div className="barra-seg" role='img' aria-label={segmentos.map((s)=>`${s.etiqueta}:${s.valor}`).join(',')}>
          {segmentos.filter((s)=>s.valor>0).map((s)=>(
            <span key={s.etiqueta} className={`barra-seg-tramo seg-${s.clase}`} style={{flexGrow:s.valor}}/>
          ))}
        </div>
        <ul className="barra-seg-leyenda">
          {segmentos.map((s)=>(
            <li key={s.etiqueta}>
              <span className={`barra-seg-punto seg-${s.clase}`} aria-hidden="true"/>
              <span>{s.etiqueta}</span>
              <strong>{s.valor}</strong>
            </li>
          ))}
        </ul>
        </>
      )}
    </section>
  );
};

export const Resumen=({onIrA}:Props)=>{
  const [datos, setDatos]=useState<ResumenAdminData | null>(null);
  const [listas, setListas]=useState<Listas|null>(null);
  const [cargando, setCargando]=useState(true);
  const [error, setError]=useState(false);
  const {perfil}=usePerfilActual();

  const cargar=useCallback(async()=>{
    setCargando(true);
    setError(false);
    const [r,u,g,i]=await Promise.all([
      adminApi.resumen<ResumenAdminData>(),
      adminApi.listar<Usuarios>('usuarios'),
      adminApi.listar<Grupo>('grupos'),
      adminApi.listar<Integrante>('integrantes'),
    ]);
    if (r) setDatos(r);
    else setError(true);
    setListas(u && g && i ? {usuarios:u, grupos:g, integrantes:i}:null);
    setCargando(false);
  },[]);

  useEffect(()=>{
    void cargar();
  },[cargar]);

  const estadisticas=useMemo(()=>{
    if (!listas) return null;
    const {usuarios, grupos, integrantes}=listas;

    const porGrupo=new Map<number, Integrante[]>();
    integrantes.forEach((m)=>porGrupo.set(m.id_grupo,[...(porGrupo.get(m.id_grupo)??[]),m]));

    const lideres= integrantes.filter((m)=>m.rol==='lider').length;
    const idsEnGrupo =new Set(integrantes.map((m)=>m.id_usuario));
    const enGrupo=usuarios.filter((u)=>idsEnGrupo.has(u.id_usuario)).length;
    
    const ranking=grupos
    .map((g)=>({
      id:g.id_grupo,
      nombre:g.nombre_grupo,
      total:porGrupo.get(g.id_grupo)?.length??0,
    }))
    .sort((a, b)=>b.total-a.total)
    .slice(0,5);

    const vacios=grupos.filter((g)=>!porGrupo.has(g.id_grupo)).length;
    const sinLider=grupos.filter((g)=>{
      const lista =porGrupo.get(g.id_grupo);
      return lista !==undefined && !lista.some((m)=>m.rol==='lider');
    }).length;

    return{lideres, miembros:integrantes.length-lideres, enGrupo, sinGrupo: usuarios.length-enGrupo, ranking, maximo: Math.max(1, ...ranking.map((r)=>r.total)), vacios, sinLider,};
  },[listas])

  const nombre =perfil?.nombre_usuario?.trim();

  return(
    <section className="resumen">
      <header className="resumen-banner">
        <h1>{nombre?`Hola, ${nombre}`:'Te damos la bienvenida'}</h1>
        <p>Estos son los datos actuales de Acadex. Toca una tarjeta para ver su informacion</p>
      </header>

      {error ?(
        <div className="error-msg" role='alert'>
          <p>No se pudo cargar el resumen</p>
          <button type='button' className='btn btn-secundario' onClick={()=>void cargar()}>
            Reintentar
          </button>
        </div>
      ):(
        <ul className="resumen-grid">
          {TARJETAS.map(({campo, titulo, icono:Icono, destino})=>(
            <li key={campo}>
              <div className={'resumen-card' + (destino ? ' resumen-card--clicable':'') + (cargando ? ' resumen-card--cargando':'')
              }>
                <div className="resumen-card-cabecera">
                  <span className="resumen-icono" aria-hidden="true">
                    <Icono size={20}/>
                  </span>
                  {destino?(
                    <button type="button" className="resumen-link" onClick={()=>onIrA(destino)}>
                      {titulo}
                    </button>
                  ):(
                    <span className="resumen-titulo">{titulo}</span>
                  )}
                </div>
                <span className="resumen-valor">{cargando||!datos ? '-':datos[campo]}</span>
                <span className="resumen-detalle">{cargando|| !datos? 'Cargando...':detalleDe(campo,datos)}</span>
              </div>
            </li>
          ))}
        </ul>
      )}

      <section className='resumen-estadisticas' aria-labelledby='resumen-est-titulo'>
        <h2 id="resumen-est-titulo">Estadisticas</h2>

        {cargando && !estadisticas && <p className='resumen-aviso'>Cargando estadisticas...</p>}
        {!cargando &&!estadisticas&&(<p className='resumen-aviso'>No se logro cargar las estadisticas</p>
        )}

        {estadisticas &&(
          <div className="resumen-paneles">
            <BarraSegmentada
            titulo='Usuarios y grupos'
            segmentos={[
              {etiqueta:'En algun grupo', valor:estadisticas.enGrupo, clase:'principal'},
              {etiqueta:'Sin grupo', valor:estadisticas.sinGrupo,clase:'neutro'},
            ]}
            />

            <BarraSegmentada
            titulo='Roles dentro de los grupos'
            segmentos={[
              {etiqueta:'Lideres', valor:estadisticas.lideres, clase:'principal'},
              {etiqueta:'Miembros', valor:estadisticas.miembros, clase:'neutro'},
            ]}
            />

            <section className='resumen-panel'>
              <h2>Grupos con mas integrantes</h2>
              {estadisticas.ranking.length===0?(
                <p className="resumen-aviso">Aun no hay grupos</p>
              ):(
                <ul className="ranking-lista">
                  {estadisticas.ranking.map((r)=>(
                    <li key={r.id}>
                      <span className="ranking-nombre">{r.nombre}</span>
                      <span className="ranking-barra" aria-hidden="true">
                        <span style={{width:`${(r.total/estadisticas.maximo)*100}%`}}/>
                      </span>
                      <strong>{r.total}</strong>
                    </li>
                  ))}
                </ul>
              )}
            </section>

            <section className='resumen-panel'>
              <h2>Grupo que requiere atencion</h2>
              {estadisticas.sinLider+estadisticas.vacios===0?(
                <p className="resumen-aviso">Todos los grupos tienen lider e integrantes</p>
              ):(
                <ul className="barra-seg-leyenda">
                <li>
                  <span className="barra-seg-punto seg-alerta" aria-hidden="true"/>
                  <span>Sin lider</span>
                  <strong>{estadisticas?.sinLider}</strong>
                </li>
                <li>
                  <span className="barra-seg-punto seg-alerta" aria-hidden="true"/>
                  <span>Sin integrantes</span>
                  <strong>{estadisticas.vacios}</strong>
                </li>
                </ul>
          )}
        </section>
        </div>
      )}
      </section>
    </section>
  );
};

export default Resumen;