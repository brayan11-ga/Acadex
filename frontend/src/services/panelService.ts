// src/services/panelService.ts
// import { apiFetch } from './api'; // Se usará cuando el backend tenga el endpoint /panel
import type { TareaPanel, ProgresoDiario } from '../types/panel';

export interface DatosPanel {
  tareaPrioritaria: TareaPanel | null;
  progreso: ProgresoDiario | null;
  proximasTareas: TareaPanel[];
}

export const obtenerDatosPanel = async (): Promise<DatosPanel> => {
  // Cuando el endpoint del panel esté creado en FastAPI, descomenta esto y borra la promesa simulada:
  // return await apiFetch<DatosPanel>('/panel');

  // Simulación temporal mientras tu backend implementa el endpoint
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({
        tareaPrioritaria: {
          id: 1,
          titulo: "Rediseñar la Arquitectura del Sistema",
          descripcion: "Completar la documentación técnica y los esquemas iniciales para la nueva capa de escalabilidad.",
          estado: 'pendiente',
          fechaVencimiento: "Vence en 4 horas",
          etiqueta: "TAREA PRIORITARIA"
        },
        progreso: {
          completadas: 3,
          total: 5,
          dias: [
            { dia: 'LUN', cantidad: 2 },
            { dia: 'MAR', cantidad: 3 },
            { dia: 'MIE', cantidad: 1 },
            { dia: 'JUE', cantidad: 4, actual: true },
            { dia: 'VIE', cantidad: 1 },
          ]
        },
        proximasTareas: [
          {
            id: 2,
            titulo: "Sincronización de Feedback",
            descripcion: "Discutir la hoja de ruta del Q3 y priorizar características.",
            estado: 'pendiente',
            fechaVencimiento: "14:00",
          },
          {
            id: 3,
            titulo: "Auditoría de Rendimiento",
            descripcion: "Ejecutar pruebas de rendimiento en producción.",
            estado: 'pendiente',
            fechaVencimiento: "16:30",
            etiqueta: "DEUDA TÉCNICA"
          },
          {
            id: 4,
            titulo: "Exportar Assets Móviles",
            descripcion: "Preparar todos los SVGs y PNGs para iOS.",
            estado: 'pendiente',
            fechaVencimiento: "Mañana",
          }
        ]
      });
    }, 600);
  });
};