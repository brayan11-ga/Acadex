import { useEffect, useState } from 'react';
import { apiFetch } from '../services/api';
import { Estadisticas as GraficaEstadisticas } from '../components/estadisticas/Estadisticas';
import '../styles/admin.css';

interface EstadisticaCategoria {
    nombre_categoria: string;
    promedio_tiempo: number | null;
    promedio_dificultad: number | null;
    total_tareas: number | null;
}

export const Estadisticas = () => {
    const [datos, setDatos] = useState<EstadisticaCategoria[]>([]);
    const [cargando, setCargando] = useState(true);

    useEffect(() => {
    const cargar = async () => {
        setCargando(true);
        const resultado = await apiFetch<EstadisticaCategoria[]>('/estadisticas/me');
        setDatos(resultado ?? []);
        setCargando(false);
    };
    cargar();
    }, []);

    const itemsTotalTareas = datos.map((d) => ({
    label: d.nombre_categoria,
    valor: d.total_tareas ?? 0,
    }));

    return (
    <div className="admin-page">
        <h1>Mis Estadísticas por Categoría</h1>

        <GraficaEstadisticas
        titulo="Total de tareas por categoría"
        items={itemsTotalTareas}
        cargando={cargando}
        />

        {!cargando && datos.length > 0 && (
        <table className="tabla-admin" style={{ marginTop: '2rem' }}>
            <thead>
            <tr>
                <th>Categoría</th>
                <th>Promedio tiempo (min)</th>
                <th>Promedio dificultad</th>
                <th>Total tareas</th>
            </tr>
            </thead>
            <tbody>
            {datos.map((d) => (
                <tr key={d.nombre_categoria}>
                <td>{d.nombre_categoria}</td>
                <td>{d.promedio_tiempo?.toFixed(1) ?? '-'}</td>
                <td>{d.promedio_dificultad?.toFixed(1) ?? '-'}</td>
                <td>{d.total_tareas ?? 0}</td>
                </tr>
            ))}
            </tbody>
        </table>
        )}

        {!cargando && datos.length === 0 && (
        <p>Aún no tienes estadísticas registradas. ¡Completa algunas tareas primero!</p>
        )}
    </div>
    );
};

export default Estadisticas;