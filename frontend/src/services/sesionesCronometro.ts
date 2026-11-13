// services/sesionesCronometro.ts
import { apiFetch } from "./api";

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