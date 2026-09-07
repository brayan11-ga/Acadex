// src/services/perfil.ts
import { apiFetch } from "./api";

export interface PerfilBackend {
  id_perfil: number;
  nombre_usuario: string;
  telefono: string | null;
  foto_perfil: string | null;
  descripcion: string | null;
  notif_activas: boolean;
  limite_cronometro: number | null;
  id_usuario: number;
}

// Todos opcionales porque el PerfilUpdate del backend acepta solo lo que cambió
export interface ActualizarPerfilPayload {
  nombre_usuario?: string;
  telefono?: string;
  foto_perfil?: string;
  descripcion?: string;
  notif_activas?: boolean;
  limite_cronometro?: number;
}

export function obtenerMiPerfil(): Promise<PerfilBackend> {
  return apiFetch<PerfilBackend>("/perfiles/me");
}

export function actualizarMiPerfil(
  datos: ActualizarPerfilPayload
): Promise<PerfilBackend> {
  return apiFetch<PerfilBackend>("/perfiles/me", {
    method: "PATCH",
    body: JSON.stringify(datos),
  });
}