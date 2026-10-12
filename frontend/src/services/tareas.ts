// src/services/tareas.ts
import { apiFetch, apiFetchBlob } from "./api";

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
  id_usuario?: number;
}

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

// Mapeo corregido a 'desde' y 'hasta' para cumplir con los requerimientos de FastAPI
export function obtenerTareasCalendario(
  fechaInicio: string,
  fechaFin: string
): Promise<TareaBackend[]> {
  return apiFetch<TareaBackend[]>(
    `/tareas/calendario?desde=${fechaInicio}&hasta=${fechaFin}`
  );
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

// frontend/src/services/tareas.ts

// Esta interfaz coincide con lo que Pydantic nos devuelve
export interface TareaPropuestaIA {
  titulo: string;
  descripcion: string;
  dificultad_estimada: number;
  tiempo_estimado: number;
  id_categoria: number | null;
}

export async function analizarDocumentoIA(archivo: File): Promise<TareaPropuestaIA> {
  const formData = new FormData();
  formData.append("archivo", archivo);

  // Usamos apiFetch. Como pasamos formData, se manejarán los headers correctamente
  return apiFetch<TareaPropuestaIA>("/tareas/analizar-documento", {
    method: "POST",
    body: formData,
  });
}

export interface ArchivoTarea {
  id_archivo: number;
  nombre: string;
  tamano: number | null;
  tipo: "PDF" | "DOCX" | "JPG" | "PNG";
  fecha_adjuncion: string;
  id_tarea: number;
  puede_eliminar: boolean;
}

export function listarArchivosTarea(idTarea: number): Promise<ArchivoTarea[]> {
  return apiFetch<ArchivoTarea[]>(`/tareas/${idTarea}/archivos`);
}

export function subirArchivoTarea(idTarea: number, archivo: File): Promise<ArchivoTarea> {
  const formData = new FormData();
  formData.append("archivo", archivo);
  return apiFetch<ArchivoTarea>(`/tareas/${idTarea}/archivos`, {
    method: "POST",
    body: formData,
  });
}

export function descargarArchivoTarea(idTarea: number, idArchivo: number): Promise<Blob> {
  return apiFetchBlob(`/tareas/${idTarea}/archivos/${idArchivo}`);
}

export function eliminarArchivoTarea(idTarea: number, idArchivo: number): Promise<void> {
  return apiFetch<void>(`/tareas/${idTarea}/archivos/${idArchivo}`, {
    method: "DELETE",
  });
}
