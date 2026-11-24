// src/pages/Panel.tsx
import { useEffect, useState } from 'react';
import { useOutletContext } from 'react-router-dom';
import { useAppDispatch, useAppSelector } from '../hooks/hooks';
import { fetchPanelData } from '../store/panelSlice';
import type { AppLayoutContext } from '../types/AppLayoutContext';
import { listarTareas, actualizarTarea, type TareaBackend } from '../services/tareas';
import { listarCategorias, type Categoria } from '../services/categorias';
import { ModalConfirmacion } from '../components/layout/ModalConfirmacion';
import { PanelTareasVencidas } from '../components/panel/PanelTareasVencidas';
import { PanelHero } from '../components/panel/PanelHero';
import { PanelTareasRecientes } from '../components/panel/PanelTareasRecientes';
import { PanelLoadingSkeleton } from '../components/skeletons/LoadingSkeletons';

import '../styles/Panel.css';

export const Panel = () => {
  const dispatch = useAppDispatch();
  const { data: datos, error } = useAppSelector((state) => state.panel);
  const { nombreUsuario, abrirModalGlobal } = useOutletContext<AppLayoutContext>();
  const [errorAccion, setErrorAccion] = useState<string | null>(null);
  const [vencidas, setVencidas] = useState<TareaBackend[]>([]);
  const [categoria, setCategorias]= useState<Categoria[]>([]);
  const [tareaVencida, setTareaVencida]= useState<TareaBackend | null>(null);

  const cargarVencidas =()=>
    Promise.all([listarTareas(), listarCategorias()])
      .then(([tareas, cats])=>{
        setCategorias(cats);
        setVencidas(
          tareas.filter((t)=>t.id_usuario !== null && t.estado !== 'Completada' && t.vencida)
        );
      })
      .catch(()=> setVencidas([]));

  useEffect(() => {
    dispatch(fetchPanelData());
    void cargarVencidas();
  }, [dispatch]);

  const manejarCompletarTarea = async (idTarea: number) => {
    try {
      setErrorAccion(null);
      // Actualizamos el estado en el backend a "Completada"
      await actualizarTarea(idTarea, { estado: "Completada" });
      dispatch(fetchPanelData());
      void cargarVencidas();
    } catch {
      setErrorAccion("No se pudo completar la tarea desde el panel.");
    }
  };

  const confirmarCompletarVencida=async()=>{
    if (!tareaVencida) return;
    const id = tareaVencida.id_tarea;
    setTareaVencida(null);
    await manejarCompletarTarea(id);
  };

  const nombreCategoria =(id:number)=>
    categoria.find((e)=> e.id_categoria === id)?.nombre_categoria ?? 'Sin categoria';

  if (!datos && !error) {
    return <PanelLoadingSkeleton />;
  }

  if (error && !datos) {
    return (
      <div className="panel-contenedor">
        <section className="empty-state" role="alert">
          <h1 className="empty-state__title">No pudimos cargar tu panel</h1>
          <p className="empty-state__description">Revisa tu conexión e inténtalo de nuevo.</p>
          <button
            type="button"
            className="empty-state__action"
            onClick={() => void dispatch(fetchPanelData())}
          >
            Reintentar
          </button>
        </section>
      </div>
    );
  }

  const tareaPrioritaria = datos?.tareaPrioritaria;
  const progreso = datos?.progreso;
  const proximasTareas = datos?.proximasTareas;

  const saludo = nombreUsuario
    ? '¡Te damos la bienvenida a Acadex, ' + nombreUsuario + '!'
    : '¡Te damos la bienvenida a Acadex!';

  return (
    <div className="panel-contenedor">
      <section className="panel-header-titulos">
        <h1 className="pixel-title-main">{saludo}</h1>
        <p className="pixel-subtitle">Aquí tienes un resumen para organizar tu estudio.</p>
      </section>

      {errorAccion && <p className="pixel-error">{errorAccion}</p>}

      <PanelHero 
        tareaPrioritaria={tareaPrioritaria} 
        progreso={progreso} 
        onCompletarTarea={manejarCompletarTarea} 
      />

      <PanelTareasRecientes
      proximasTareas={proximasTareas} 
      onCrearTarea={abrirModalGlobal} 
      />
      <PanelTareasVencidas
      tareas={vencidas}
      nombreCategoria={nombreCategoria}
      onSeleccionar={setTareaVencida}
      />
      <ModalConfirmacion
      isOpen={tareaVencida !==null}
      title="Esta tarea vencio"
      message="La fecha de entrega ya paso. ¿Quieres marcarla como completada de todas formas? Se registrara como entregada con retraso."
      onConfirm={confirmarCompletarVencida}
      onCancel={()=> setTareaVencida(null)}
      />
    </div>
  );
};

export default Panel;
