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
