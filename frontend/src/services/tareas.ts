import { apiFetch } from "./api";

export interface TareaBackend {
  id_tarea: number;
  nombre: string;
  descripcion: string | null;
  fecha_entrega: string;
  estado: string;
  dificultad_estimada: number;
  tiempo_estimado: number;
  prioridad: number | null;
  id_categoria: number;
  id_usuario: number | null;
  id_grupo: number | null;
}

export interface NuevaTareaPayload {
  nombre: string;
  descripcion: string;
  fecha_entrega: string;
  dificultad_estimada: number;
  tiempo_estimado: number;
  id_categoria: number;
  id_usuario: number;
}

export function listarTareas(): Promise<TareaBackend[]> {
  return apiFetch<TareaBackend[]>("/tareas/");
}

export function crearTarea(datos: NuevaTareaPayload): Promise<TareaBackend> {
  return apiFetch<TareaBackend>("/tareas/", {
    method: "POST",
    body: JSON.stringify(datos),
  });
}