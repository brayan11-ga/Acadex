// Ruta: frontend/src/types/tareaGrupo.ts
import type { RolGrupo } from "./grupo";

export type RolIntegrante = RolGrupo;

export interface IntegranteAsignable {
  id_usuario: number;
  correo_electronico: string;
  nombre?: string;
  rol: RolIntegrante;
  // Solo lo envía el detalle de tarea grupal al reasignar; crear tarea no lo usa.
  completado?: boolean;
}
