// Ruta: frontend/src/services/sesionesCronometro.ts
import { apiFetch } from "./api";

export interface SesionCronometroBackend {
  id_sesion: number;
  fecha_inicio: string;
  fecha_fin: string | null;
  duracion: number | null;
  id_usuario: number;
  id_tarea: number;
}

// Solo el usuario actual puede consultar sus propias sesiones.
export function listarSesionesUsuario(
  idUsuario: number,
): Promise<SesionCronometroBackend[]> {
  return apiFetch<SesionCronometroBackend[]>(
    `/sesiones-cronometro/usuario/${idUsuario}`,
  );
}

// Inicia una sesión abierta. El backend exige que el usuario del JWT sea el mismo.
export function iniciarSesionCronometro(
  idUsuario: number,
  idTarea: number,
): Promise<SesionCronometroBackend> {
  const parametros = new URLSearchParams({
    id_usuario: String(idUsuario),
    id_tarea: String(idTarea),
  });
  return apiFetch<SesionCronometroBackend>(
    `/sesiones-cronometro/iniciar?${parametros.toString()}`,
    { method: "POST" },
  );
}

// Cierra la sesión y guarda su duración.
export function finalizarSesionCronometro(
  idSesion: number,
): Promise<SesionCronometroBackend> {
  return apiFetch<SesionCronometroBackend>(
    `/sesiones-cronometro/${idSesion}/finalizar`,
    { method: "PATCH" },
  );
}

// Borra una sesión abierta sin guardar su duración.
export function descartarSesionCronometro(idSesion: number): Promise<void> {
  return apiFetch<void>(`/sesiones-cronometro/${idSesion}/descartar`, {
    method: "DELETE",
  });
}

// Reiniciar real: borra todas las sesiones (abiertas y cerradas) del usuario
// en la tarea. El backend toma el usuario del JWT.
export function reiniciarSesionesCronometro(idTarea: number): Promise<void> {
  return apiFetch<void>(`/sesiones-cronometro/tarea/${idTarea}/reiniciar`, {
    method: "DELETE",
  });
}

export interface SesionCronometro{
    id_sesion:number;
    fecha_inicio:string;
    fecha_fin:string | null;
    duracion:number | null;
    id_usuario:number;
    id_tarea:number;
}

export interface EstadoCronometroTarea{
    segundos_acumulados:number;
    segundos_sesion_actual:number;
    segundos_ventana:number;
    limite_segundos:number;
    sesion:SesionCronometro | null;
}

export interface VerificacionLimite{
    estado:"activa"|"aviso"|"pausada_automaticamente"|"cerrada";
    limite_segundos:number;
    segundos_gracia_restantes:number|null;
    sesion:SesionCronometro;
}

const BASE="/sesiones-cronometro";

export const obtenerEstadoCronometro = (idTarea: number) =>
    apiFetch<EstadoCronometroTarea>(`${BASE}/tarea/${idTarea}/estado`);

export const iniciarSesion = (idTarea: number) =>
    apiFetch<SesionCronometro>(`${BASE}/tarea/${idTarea}/iniciar`, { method: "POST" });

export const pausarSesion = (idSesion: number) =>
    apiFetch<SesionCronometro>(`${BASE}/${idSesion}/pausar`, { method: "PATCH" });

export const verificarLimite = (idSesion: number) =>
    apiFetch<VerificacionLimite>(`${BASE}/${idSesion}/verificar`, { method: "POST" });

export const confirmarContinuar = (idSesion: number) =>
    apiFetch<VerificacionLimite>(`${BASE}/${idSesion}/confirmar`, { method: "POST" });

export const reiniciarCronometro = (idTarea: number) =>
    apiFetch<EstadoCronometroTarea>(`${BASE}/tarea/${idTarea}/reiniciar`, { method: "POST" });
