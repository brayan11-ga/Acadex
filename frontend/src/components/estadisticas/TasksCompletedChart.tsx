// src/components/estadisticas/TasksCompletedChart.tsx
import React from 'react';
import { BarChart3 } from 'lucide-react';
import type { DiaEstadistica } from '../../types/estadisticas';

interface Props {
  dias: DiaEstadistica[];
}

export const TasksCompletedChart: React.FC<Props> = ({ dias }) => {
  const maxCantidad = Math.max(...dias.map(d => d.cantidad), 5);

  return (
    <div className="stat-card chart-container">
      <div className="stat-card-header">
        <div className="chart-header-info">
          <h3 className="stat-card-title">Tareas Completadas</h3>
          <p className="chart-subtitle">Frecuencia de salida diaria</p>
        </div>
        <div className="stat-card-icon">
          <BarChart3 size={18} />
        </div>
      </div>

      <div className="bars-wrapper">
        {dias.map((item, index) => {
          const alturaPorcentaje = (item.cantidad / maxCantidad) * 100;
          return (
            <div key={index} className="bar-col">
              <div className="bar-track">
                <div 
                  style={{ height: `${Math.max(alturaPorcentaje, 10)}%` }}
                  className={`bar-fill ${item.actual ? 'active' : 'inactive'}`}
                  title={`${item.cantidad} tareas`}
                ></div>
              </div>
              <span className={`bar-label ${item.actual ? 'is-actual' : ''}`}>
                {item.dia}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
};