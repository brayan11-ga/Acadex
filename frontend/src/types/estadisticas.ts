// src/types/estadisticas.ts

export interface MetaSemanal {
  porcentaje: number;
  completadas: number;
  total: number;
  tendencia: string;
}

export interface DiaEstadistica {
  dia: string;
  cantidad: number;
  actual: boolean;
}

export interface FocusScore {
  puntaje: number;
  nivel: string;
}

export interface CategoriaTop {
  nombre: string;
  horas_dedicadas: number;
}

export interface PromedioTiempo {
  minutos: number;
  tendencia: string;
}

export interface Insight {
  titulo: string;
  descripcion: string;
}

export interface ResumenEstadisticas {
  meta_semanal: MetaSemanal;
  grafico_diario: DiaEstadistica[];
  focus_score: FocusScore;
  categoria_top: CategoriaTop;
  promedio_tiempo: PromedioTiempo;
  insights: Insight[];
  sugerencia_ia?: Insight | null;
}