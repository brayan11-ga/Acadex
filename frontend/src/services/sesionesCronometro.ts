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
