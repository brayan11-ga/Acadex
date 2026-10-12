// src/services/panelService.ts
import { apiFetch } from './api'; // <-- Ya activo para conectar con tu FastAPI
import type { TareaPanel, ProgresoDiario } from '../types/panel';

export interface DatosPanel {
  tareaPrioritaria: TareaPanel | null;
  progreso: ProgresoDiario | null;
  proximasTareas: TareaPanel[];
}

export const obtenerDatosPanel = async (): Promise<DatosPanel> => {
  return await apiFetch<DatosPanel>('/panel');
};