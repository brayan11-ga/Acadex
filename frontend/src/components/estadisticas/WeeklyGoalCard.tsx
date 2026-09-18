// src/components/estadisticas/WeeklyGoalCard.tsx
import React from 'react';
import { Target } from 'lucide-react';
import type { MetaSemanal } from '../../types/estadisticas';

interface Props {
  data: MetaSemanal;
}

export const WeeklyGoalCard: React.FC<Props> = ({ data }) => {
  // Calculamos los grados del gradiente según el porcentaje (0% = 0deg, 100% = 360deg)
  const grados = (data.porcentaje / 100) * 360;
  
  const estiloCirculo = {
    background: `conic-gradient(var(--mint) ${grados}deg, var(--paper-deep) ${grados}deg 360deg)`
  };

  return (
    <div className="stat-card">
      <div className="stat-card-header">
        <h3 className="stat-card-title">Meta Semanal</h3>
        <span className="stat-card-icon">
          <Target size={18} />
        </span>
      </div>

      <div className="stat-card-body">
        <div className="goal-circle" style={estiloCirculo}>
          <div className="goal-circle-inner">
            <div className="goal-circle-content">
              <span className="goal-percentage">{data.porcentaje}%</span>
              <p className="goal-status">EN CURSO</p>
            </div>
          </div>
        </div>
      </div>

      <div className="stat-card-footer">
        <p className="stat-text-main">{data.completadas} de {data.total} tareas completadas</p>
        <p className="stat-text-trend">Tendencia: {data.tendencia}</p>
      </div>
    </div>
  );
};