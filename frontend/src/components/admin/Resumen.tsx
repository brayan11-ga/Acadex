import { useEffect, useState } from 'react';
import { adminApi } from '../../services/adminapi';
import { EstadisticasAdmin } from '../estadisticas/EstadisticasAdmin';
import type { ItemResumen } from '../estadisticas/EstadisticasAdmin';

export const Resumen = () => {
    const [items, setItems] = useState<ItemResumen[]>([]);
    const [cargando, setCargando] = useState(true);

    useEffect(() => {
    const cargar = async () => {
        setCargando(true);
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
        setCargando(false);
    };
    cargar();
    }, []);

    return <EstadisticasAdmin titulo="Resumen general de Acadex" items={items} cargando={cargando} />;
};

export default Resumen;