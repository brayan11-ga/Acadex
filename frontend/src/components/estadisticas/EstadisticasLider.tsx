// src/components/estadisticas/EstadisticasAdmin.tsx
import React from 'react';
import { LayoutDashboard } from 'lucide-react';

export interface ItemResumen {
  label: string;
  valor: number;
}

interface Props {
  titulo: string;
  items: ItemResumen[];
  cargando: boolean;
}

export const EstadisticasAdmin: React.FC<Props> = ({ titulo, items, cargando }) => {
  if (cargando) {
    return (
      <div className="stat-card">
        <p className="chart-subtitle">Cargando resumen de administración...</p>
      </div>
    );
  }

  return (
    <div className="stat-card chart-container">
      <div className="stat-card-header">
        <div className="chart-header-info">
          <h3 className="stat-card-title">{titulo}</h3>
          <p className="chart-subtitle">Resumen general</p>
        </div>
        <div className="stat-card-icon">
          <LayoutDashboard size={18} />
        </div>
      </div>

      <div className="resumen-grid">
        {items.map((item, index) => (
          <div key={index} className="resumen-item">
            <span className="resumen-label">{item.label}</span>
            <p className="resumen-valor">{item.valor}</p>
          </div>
        ))}
      </div>
    </div>
  );
};