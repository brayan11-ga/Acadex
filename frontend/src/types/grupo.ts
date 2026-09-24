//src/types/grupo.ts
export type RolGrupo = "lider" | "miembro";

export interface Grupo {
  id_grupo: number;
  nombre_grupo: string;
  descripcion: string | null;
  codigo_acceso: string;
  fecha_creacion: string;
}

export interface GrupoConRol extends Grupo {
  rol: RolGrupo;
}

export interface Integrante {
  id_integrante: number;
  id_usuario: number;
  correo_electronico: string;
  rol: RolGrupo;
  fecha_ingreso: string;
}