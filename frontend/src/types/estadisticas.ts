// src/types/estadisticas.ts

export interface MetaSemanal {
  porcentaje: number;
  completadas: number;
  total: number;
  tendencia: string;
}

export type EstadoCategoria='eficiente'|'deficiente'|'insuficiente';
export type MejoraTiempo='mejora'|'estable'|'empeora';
export type RecomendacionDificultad='subir'|'mantener'|'bajar'|'sin_datos';

export interface RendimientoCategoria{
  categoria:string;
  total_tareas:number;
  tiempo_estimado_prom:number;
  tiempo_real_prom:number;
  dificultad_estimada_prom:number;
  dificultad_real_prom:number|null;
  estado:EstadoCategoria;
  mejora_tiempo:MejoraTiempo|null;
  variacion_tiempo_pct:number|null;
  recomendacion:RecomendacionDificultad;
}

export interface ResumenEstadisticas {
  meta_semanal: MetaSemanal;
  categorias:RendimientoCategoria[];
}