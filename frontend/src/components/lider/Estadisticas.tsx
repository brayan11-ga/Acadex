import { useEffect, useRef } from 'react';
import Chart from 'chart.js/auto';

export interface ItemResumen {
    label: string;
    valor: number;
    color?: string;
}

interface EstadisticasProps {
    titulo: string;
    items: ItemResumen[];
    cargando?: boolean;
}

const PALETA_DEFECTO = [
    { bg: 'rgba(124, 92, 255, 0.6)', border: 'rgba(124, 92, 255, 1)' },
    { bg: 'rgba(69, 224, 168, 0.6)', border: 'rgba(69, 224, 168, 1)' },
    { bg: 'rgba(255, 111, 165, 0.6)', border: 'rgba(255, 111, 165, 1)' },
    { bg: 'rgba(62, 203, 240, 0.6)', border: 'rgba(62, 203, 240, 1)' },
    { bg: 'rgba(242, 163, 62, 0.6)', border: 'rgba(242, 163, 62, 1)' },
];

export const Estadisticas = ({ titulo, items, cargando = false }: EstadisticasProps) => {
    const canvasRef = useRef<HTMLCanvasElement>(null);
    const chartRef = useRef<Chart | null>(null);

    useEffect(() => {
    if (cargando || !canvasRef.current || items.length === 0) return;

    if (chartRef.current) {
        chartRef.current.destroy();
    }

    chartRef.current = new Chart(canvasRef.current, {
        type: 'bar',
        data: {labels: items.map((i) => i.label),
        datasets: [
            {label: titulo,data: items.map((i) => i.valor),backgroundColor: items.map((i, idx) => i.color ?? PALETA_DEFECTO[idx % PALETA_DEFECTO.length].bg),borderColor: items.map((i, idx) => i.color ?? PALETA_DEFECTO[idx % PALETA_DEFECTO.length].border),borderWidth: 1,},
            ],
        },
        options: {responsive: true,maintainAspectRatio: false,
        scales: {
            y: { beginAtZero: true, ticks: { color: '#b9aee0' } },
            x: { ticks: { color: '#b9aee0' } },
            },
            plugins: {
            legend: { display: false },
            title: { display: true, text: titulo, color: '#f1eaff', font: { size: 16 } },
            },
        },
    });

    return () => {
        chartRef.current?.destroy();
    };
    }, [items, titulo, cargando]);

    if (cargando) return <p>Cargando resumen...</p>;

    return (
    <div className="resumen-estadisticas">
        <div className="indicator-row">
        {items.map((item) => (
            <div className="indicator-card" key={item.label}>
            <p className="indicator-title">{item.label}</p>
            <p className="indicator-value">{item.valor}</p>
            </div>
        ))}
        </div>

        <div className="chart-container">
        <canvas ref={canvasRef}></canvas>
        </div>
    </div>
    );
};

export default Estadisticas;