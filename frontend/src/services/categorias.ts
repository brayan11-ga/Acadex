import { apiFetch } from "./api";

export interface Categoria {
  id_categoria: number;
  nombre_categoria: string;
}

export function listarCategorias(): Promise<Categoria[]> {
  return apiFetch<Categoria[]>("/categorias/");
}