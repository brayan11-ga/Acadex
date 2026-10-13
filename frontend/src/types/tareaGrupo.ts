// Ruta: frontend/src/types/tareaGrupo.ts
import type { RolGrupo } from "./grupo";

export type RolIntegrante = RolGrupo;

export interface IntegranteAsignable {
  id_usuario: number;
  correo_electronico: string;
  nombre?: string;
  rol: RolIntegrante;
}
