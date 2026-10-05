// src/hooks/useTareas.ts
import { useState, useEffect } from "react";
import {
  listarTareas,
  obtenerTarea,
  eliminarTarea,
  actualizarTarea,
  type TareaBackend,
} from "../services/tareas";
import { listarCategorias, type Categoria } from "../services/categorias";

export const useTareas = (refreshKey: number) => {
  const [tareas, setTareas] = useState<TareaBackend[]>([]);
  const [categorias, setCategorias] = useState<Categoria[]>([]);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [tareaDetalle, setTareaDetalle] = useState<TareaBackend | null>(null);
  const [tareaAEliminar, setTareaAEliminar] = useState<number | null>(null);

  // Estados de vista y filtros
  const [filtroActivo, setFiltroActivo] = useState<string>("todas");
  const [modoVista, setModoVista] = useState<"lista" | "cuadricula">("lista");
  const [paginaActual, setPaginaActual] = useState<number>(1);
  const tareasPorPagina = 6;

  // Carga inicial de datos
  useEffect(() => {
    setCargando(true);
    Promise.all([listarTareas(), listarCategorias()])
      .then(([datosTareas, datosCategorias]) => {
        setTareas(datosTareas);
        setCategorias(datosCategorias);
        setError(null);
      })
      .catch(() => setError("No se pudieron cargar las tareas"))
      .finally(() => setCargando(false));
  }, [refreshKey]);

  // Reiniciar paginación al cambiar filtros
  useEffect(() => {
    setPaginaActual(1);
  }, [filtroActivo, tareas.length]);

  // Utilidades y cálculos
  const nombreCategoria = (id: number) =>
    categorias.find((c) => c.id_categoria === id)?.nombre_categoria ?? "Sin categoría";

  const formatearFecha = (iso: string) =>
    new Date(iso).toLocaleString("es-CO", { day: "numeric", month: "short", hour: "2-digit", minute: "2-digit" });

  const tareasPendientes = tareas.filter((t) => t.estado !== "Completada").length;

  const tareasFiltradas = tareas.filter((tarea) => {
    if (filtroActivo === "alta") return tarea.dificultad_estimada >= 4;
    if (filtroActivo === "activas") return tarea.estado !== "Completada";
    if (filtroActivo === "completadas") return tarea.estado === "Completada";
    return true;
  });

  const indiceUltimaTarea = paginaActual * tareasPorPagina;
  const indicePrimeraTarea = indiceUltimaTarea - tareasPorPagina;
  const tareasPaginadas = tareasFiltradas.slice(indicePrimeraTarea, indiceUltimaTarea);
  const totalPaginas = Math.ceil(tareasFiltradas.length / tareasPorPagina);

  // Acciones (Handlers)
  const solicitarEliminar = (id: number) => {
  setTareaAEliminar(id); // Esto abrirá el modal
};

const confirmarEliminar = async () => {
  if (tareaAEliminar === null) return;
  try {
    await eliminarTarea(tareaAEliminar);
    setTareas((actuales) => actuales.filter((t) => t.id_tarea !== tareaAEliminar));
    setTareaAEliminar(null); // Cierra el modal tras el éxito
  } catch {
    setError("No se pudo eliminar la tarea");
    setTareaAEliminar(null); // Cierra el modal aunque falle
  }
};

const cancelarEliminar = () => {
  setTareaAEliminar(null); // Solo cierra el modal
};

  const manejarCambiarEstado = async (tarea: TareaBackend) => {
    const nuevoEstado = tarea.estado === "Completada" ? "Pendiente" : "Completada";
    try {
      const tareaActualizada = await actualizarTarea(tarea.id_tarea, { estado: nuevoEstado });
      setTareas((actuales) => actuales.map((t) => (t.id_tarea === tarea.id_tarea ? tareaActualizada : t)));
    } catch {
      setError("No se pudo actualizar el estado de la tarea");
    }
  };

  const manejarVerDetalles = async (id: number) => {
    try {
      const tarea = await obtenerTarea(id);
      setTareaDetalle(tarea);
    } catch {
      setError("No se pudieron cargar los detalles");
    }
  };

  return {
    cargando, error, tareaDetalle, setTareaDetalle,
    filtroActivo, setFiltroActivo, modoVista, setModoVista,
    paginaActual, setPaginaActual, totalPaginas, tareasPaginadas, tareasPendientes,
    nombreCategoria, formatearFecha, manejarCambiarEstado, manejarVerDetalles,
    tareaAEliminar, solicitarEliminar, confirmarEliminar, cancelarEliminar
  };
};