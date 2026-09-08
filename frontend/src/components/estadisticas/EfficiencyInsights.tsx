// src/components/estadisticas/EfficiencyInsights.tsx
import React from 'react';
import { Lightbulb, Sparkles } from 'lucide-react';
import type { Insight } from '../../types/estadisticas';

interface Props {
  insights: Insight[];
  sugerenciaIa?: Insight | null;
}

export const EfficiencyInsights: React.FC<Props> = ({ insights, sugerenciaIa }) => {
  return (
    <div className="stats-grid-bottom">
      {/* Tarjeta de Insights de Eficiencia */}
      <div className="stat-card">
        <div className="stat-card-header">
          <h3 className="stat-card-title">Insights de Eficiencia</h3>
          <span className="stat-card-icon">
            <Lightbulb size={18} />
          </span>
        </div>

        <div className="insights-list">
          {insights.map((ins, idx) => (
            <div key={idx} className="insight-item">
              <div className="insight-content">
                <h5 className="insight-item-title">{ins.titulo}</h5>
                <p className="insight-item-desc">{ins.descripcion}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Tarjeta de Sugerencia IA */}
      <div className="stat-card ai-card">
        <div className="stat-card-header">
          <span className="ai-badge">Sugerencia de IA</span>
          <span className="stat-card-icon ai-icon">
            <Sparkles size={18} />
          </span>
        </div>

        <div className="ai-body">
          {sugerenciaIa ? (
            <div>
              <h4 className="ai-title">{sugerenciaIa.titulo}</h4>
              <p className="ai-desc">{sugerenciaIa.descripcion}</p>
            </div>
          ) : (
            <p className="ai-desc">Analizando patrones de rendimiento...</p>
          )}
        </div>
      </div>
    </div>
  );
};