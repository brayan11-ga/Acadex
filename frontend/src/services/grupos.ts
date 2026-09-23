// frontend/src/services/grupos.ts
import { apiFetch } from "./api";
import type { Grupo, GrupoConRol, Integrante } from "../types/grupo";

export interface NuevoGrupoPayload {
  nombre_grupo: string;
  descripcion: string;
}

export function listarMisGrupos(): Promise<GrupoConRol[]> {
  return apiFetch<GrupoConRol[]>("/grupos/mis-grupos");
}

export function crearGrupo(datos: NuevoGrupoPayload): Promise<Grupo> {
  return apiFetch<Grupo>("/grupos/", {
    method: "POST",
    body: JSON.stringify(datos),
  });
}

export function unirseAGrupo(codigoAcceso: string): Promise<Integrante> {
  return apiFetch<Integrante>("/grupos/unirse", {
    method: "POST",
    body: JSON.stringify({ codigo_acceso: codigoAcceso }),
  });
}

export function obtenerIntegrantes(idGrupo: number): Promise<Integrante[]> {
  return apiFetch<Integrante[]>(`/grupos/${idGrupo}/integrantes`);
}

export function salirDeGrupo(idGrupo: number): Promise<void> {
  return apiFetch<void>(`/grupos/${idGrupo}/salir`, { method: "DELETE" });
}

export function expulsarIntegrante(idGrupo: number, idUsuario: number): Promise<void> {
  return apiFetch<void>(`/grupos/${idGrupo}/integrantes/${idUsuario}`, { method: "DELETE" });
}

export function eliminarGrupo(idGrupo: number): Promise<void> {
  return apiFetch<void>(`/grupos/${idGrupo}`, { method: "DELETE" });
}