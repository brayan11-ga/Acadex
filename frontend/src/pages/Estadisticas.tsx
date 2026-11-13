// src/pages/Estadisticas.tsx
import React, { useEffect, useState } from 'react';
import { obtenerEstadisticas } from '../services/estadisticasService';
import type { ResumenEstadisticas } from '../types/estadisticas';
import { WeeklyGoalCard } from '../components/estadisticas/WeeklyGoalCard';
import { RendimientoCategorias } from '../components/estadisticas/RendimientoCategorias';
import { StatisticsPageLoadingSkeleton } from '../components/skeletons/LoadingSkeletons';

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
    return <StatisticsPageLoadingSkeleton />;
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
      
      <RendimientoCategorias categorias={data.categorias}/>

    </div>
  );
};
