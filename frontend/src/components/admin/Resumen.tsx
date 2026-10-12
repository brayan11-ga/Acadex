import { useEffect, useState } from 'react';
import { adminApi } from '../../services/adminapi';
import { EstadisticasAdmin } from '../estadisticas/RankingCard';
import type { ItemResumen } from '../estadisticas/RankingCard';

interface ResumenAdminData{
  usuarios:number;
  categorias:number;
  grupos:number;
  tareas:number;
  integrantes:number;
}

export const Resumen = () => {
    const [items, setItems] = useState<ItemResumen[]>([]);
    const [cargando, setCargando] = useState(true);

// src/components/panel/Resumen.tsx (o donde esté)
      useEffect(() => {
        const cargar = async () => {
          setCargando(true);
          const datos=await adminApi.resumen<ResumenAdminData>()
          if(datos){
      setItems([
        { label: 'Usuarios', valor: datos.usuarios},
        { label: 'Categorías', valor: datos.categorias},
        { label: 'Grupos', valor: datos.grupos},
        { label: 'Tareas', valor: datos.tareas},
        { label: 'Integrantes', valor: datos.integrantes},
      ]);
    }
      setCargando(false);
  };
  cargar();
}, []);
    return <EstadisticasAdmin titulo="Resumen general de Acadex" items={items} cargando={cargando} />;
};

export default Resumen;