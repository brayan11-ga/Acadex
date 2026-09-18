// src/services/estadisticasService.ts
import { apiFetch } from './api';
import type { ResumenEstadisticas } from '../types/estadisticas';

export const obtenerEstadisticas = async (): Promise<ResumenEstadisticas> => {
  try {
    // Llamamos a la ruta relativa; apiFetch se encarga de la BASE_URL y del token JWT
    return await apiFetch<ResumenEstadisticas>('/estadisticas/resumen');
  } catch (error) {
    console.error("Error al obtener las estadísticas del dashboard:", error);
    throw error;
  }
};