// src/pages/Estadisticas.tsx
import React, { useEffect, useState } from 'react';
import { obtenerEstadisticas } from '../services/estadisticasService';
import type { ResumenEstadisticas } from '../types/estadisticas';

import { WeeklyGoalCard } from '../components/estadisticas/WeeklyGoalCard';
import { StatCard } from '../components/estadisticas/StatCard';
import { EfficiencyInsights } from '../components/estadisticas/EfficiencyInsights';

// Importamos los estilos independientes
import '../styles/estadisticas.css';

export const Estadisticas: React.FC = () => {
  const [data, setData] = useState<ResumenEstadisticas | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    obtenerEstadisticas()
      .then((res) => {
        setData(res);
        setLoading(false);
      })
      .catch((err) => {
        setError('No se pudieron cargar las estadísticas.');
        setLoading(false);
        console.error(err);
      });
  }, []);

  if (loading) {
    return (
      <div className="stats-page stats-state-container">
        <div className="stats-spinner"></div>
        <span className="stats-loading-text">Cargando estadísticas de Acadex...</span>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="stats-page stats-state-container stats-error-text">
        {error || 'Error al cargar datos'}
      </div>
    );
  }

  return (
    <div className="stats-page">
      <header className="stats-header">
        <h1>Estadísticas de Acadex</h1>
        <p>Analítica de rendimiento para Acadex esta semana.</p>
      </header>

      <div className="stats-grid-top">
        <WeeklyGoalCard data={data.meta_semanal} />
      </div>

      <div className="stats-grid-middle">
        <StatCard 
          titulo="Focus Score" 
          valorPrincipal={`${data.focus_score.puntaje}/100`} 
          subtexto={data.focus_score.nivel} 
          icono="zap"
          colorSubtexto="positive"
        />
        <StatCard 
          titulo="Top Category" 
          valorPrincipal={data.categoria_top.nombre} 
          subtexto={`${data.categoria_top.horas_dedicadas} hrs logged`} 
          icono="rocket"
          colorSubtexto="neutral"
        />
        <StatCard 
          titulo="Avg. Completion" 
          valorPrincipal={`${data.promedio_tiempo.minutos} min`} 
          subtexto={data.promedio_tiempo.tendencia} 
          icono="clock"
          colorSubtexto="positive"
        />
      </div>

      <EfficiencyInsights 
        insights={data.insights} 
        sugerenciaIa={data.sugerencia_ia} 
      />
    </div>
  );
};