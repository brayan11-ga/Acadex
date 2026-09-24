import { useEffect, useState } from 'react';
import { adminApi } from '../../services/adminapi';
import { EstadisticasAdmin } from '../estadisticas/RankingCard';
import type { ItemResumen } from '../estadisticas/RankingCard';

export const Resumen = () => {
    const [items, setItems] = useState<ItemResumen[]>([]);
    const [cargando, setCargando] = useState(true);

// src/components/panel/Resumen.tsx (o donde esté)
useEffect(() => {
  const cargar = async () => {
    setCargando(true);
    try {
      const [usuarios, categorias, grupos, tareas, integrantes] = await Promise.all([
        adminApi.listar<any>('usuarios'),
        adminApi.listar<any>('categorias'),
        adminApi.listar<any>('grupos'),
        adminApi.listar<any>('tareas'),
        adminApi.listar<any>('integrantes'),
      ]);

      setItems([
        { label: 'Usuarios', valor: usuarios?.length ?? 0 },
        { label: 'Categorías', valor: categorias?.length ?? 0 },
        { label: 'Grupos', valor: grupos?.length ?? 0 },
        { label: 'Tareas', valor: tareas?.length ?? 0 },
        { label: 'Integrantes', valor: integrantes?.length ?? 0 },
      ]);
    } catch (error) {
      console.error('Error cargando resumen admin:', error);
      // opcional: setError(true) si luego quieres mostrar un mensaje
    } finally {
      setCargando(false);
    }
  };
  cargar();
}, []);
    return <EstadisticasAdmin titulo="Resumen general de Acadex" items={items} cargando={cargando} />;
};

export default Resumen;