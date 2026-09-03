// src/services/tareas.ts
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

// Payload para editar: todos los campos son opcionales porque tu TareaUpdate
// del backend permite mandar solo lo que cambió
export interface ActualizarTareaPayload {
  nombre?: string;
  descripcion?: string;
  fecha_entrega?: string;
  dificultad_estimada?: number;
  tiempo_estimado?: number;
  id_categoria?: number;
  estado?: string;
}

export function listarTareas(): Promise<TareaBackend[]> {
  return apiFetch<TareaBackend[]>("/tareas/");
}

export function obtenerTarea(idTarea: number): Promise<TareaBackend> {
  return apiFetch<TareaBackend>(`/tareas/${idTarea}`);
}

export function crearTarea(datos: NuevaTareaPayload): Promise<TareaBackend> {
  return apiFetch<TareaBackend>("/tareas/", {
    method: "POST",
    body: JSON.stringify(datos),
  });
}

export function actualizarTarea(
  idTarea: number,
  datos: ActualizarTareaPayload
): Promise<TareaBackend> {
  return apiFetch<TareaBackend>(`/tareas/${idTarea}`, {
    method: "PUT",
    body: JSON.stringify(datos),
  });
}

export function eliminarTarea(idTarea: number): Promise<void> {
  return apiFetch<void>(`/tareas/${idTarea}`, {
    method: "DELETE",
  });
}