// src/components/estadisticas/StatCard.tsx
import React from 'react';
import { Zap, Rocket, Clock, BarChart2 } from 'lucide-react';

interface Props {
  titulo: string;
  valorPrincipal: string | number;
  subtexto: string;
  icono?: 'zap' | 'rocket' | 'clock' | string;
  colorSubtexto?: string;
}

export const StatCard: React.FC<Props> = ({ 
  titulo, 
  valorPrincipal, 
  subtexto, 
  icono = "barChart", 
  colorSubtexto = "positive" 
}) => {
  const renderIcono = () => {
    switch (icono) {
      case 'zap': return <Zap size={18} />;
      case 'rocket': return <Rocket size={18} />;
      case 'clock': return <Clock size={18} />;
      default: return <BarChart2 size={18} />;
    }
  };

  return (
    <div className="stat-card">
      <div className="stat-card-header">
        <span className="stat-card-title">{titulo}</span>
        <span className="stat-card-icon">
          {renderIcono()}
        </span>
      </div>
      <div className="stat-card-body-main">
        <h4 className="stat-main-value">{valorPrincipal}</h4>
        <p className={`stat-subtexto ${colorSubtexto}`}>{subtexto}</p>
      </div>
    </div>
  );
};