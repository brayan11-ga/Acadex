import React from 'react';
import { Users, TrendingUp, ListChecks, type LucideIcon } from 'lucide-react';

export interface ItemResumen {
  label: string;
  valor: number;
  icon?: LucideIcon;
}

interface Props {
  titulo: string;
  items: ItemResumen[];
  cargando: boolean;
}

const iconosPorDefecto: LucideIcon[] = [Users, ListChecks, TrendingUp];

export const EstadisticasAdmin: React.FC<Props> = ({ titulo, items, cargando }) => {
  if (cargando) {
    return (
      <div className="stat-card admin-loading">
        <p>Cargando resumen de administración...</p>
      </div>
    );
  }

  return (
    <div className="admin-resumen">
      <h2 className="admin-resumen-titulo">{titulo}</h2>
      <div className="admin-resumen-grid">
        {items.map((item, index) => {
          const Icon = item.icon ?? iconosPorDefecto[index % iconosPorDefecto.length];
          return (
            <div key={index} className="stat-card admin-resumen-card">
              <div className="stat-card-header">
                <span className="chart-subtitle admin-resumen-label">{item.label}</span>
                <div className="stat-card-icon">
                  <Icon size={18} />
                </div>
              </div>
              <p className="stat-main-value">{item.valor}</p>
            </div>
          );
        })}
      </div>
    </div>
  );
};