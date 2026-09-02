// src/types/panel.ts

export interface TareaPanel {
  id: number;
  titulo: string;
  descripcion: string;
  estado: 'pendiente' | 'en_progreso' | 'completada';
  fechaVencimiento: string;
  etiqueta?: string;
}

export interface DiaProgreso {
  dia: string;
  cantidad: number;
  actual?: boolean;
}

export interface ProgresoDiario {
  completadas: number;
  total: number;
  dias: DiaProgreso[];
}