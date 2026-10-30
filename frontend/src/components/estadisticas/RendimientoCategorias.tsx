import React from "react";
import { BarChart2, TrendingDown, TrendingUp, Minus } from "lucide-react";
import type{MejoraTiempo, RecomendacionDificultad, RendimientoCategoria} from '../../types/estadisticas';
import { EmptyState } from '../ui/EmptyState';

const ETIQUETA_ESTADO={
    eficiente:'Eficiente',
    deficiente:'Con deficiencia',
    insuficiente:"Datos insuficientes",
} as const;

const ETIQUETA_MEJORA:Record<MejoraTiempo, string>={
    mejora:"Mejoraste en tiempo",
    estable:'Tiempo estable',
    empeora:'Tarda mas que antes',
};

const TEXTO_RECOMENDACION:Record<RecomendacionDificultad, string>={
    subir:'puedes subir la dificultad en esta categoria',
    mantener:'manten el nivel de dificultad actual',
    bajar:'conviene bajar la dificultad y reforzar el tema',
    sin_datos:'Completa al menos 3 tareas con cronometro para recibir una recomendacion',
}

const ICONO_MEJORA:Record<MejoraTiempo, React.ReactNode>={
    mejora:<TrendingDown size={16}/>,
    estable:<Minus size={16}/>,
    empeora:<TrendingUp size={16}/>,
}

const CategoriaCard:React.FC<{item:RendimientoCategoria}>=({item})=>(
    <div className="stat-card category-card">
        <div className="stat-card-header">
            <h3 className="stat-card-title">{item.categoria}</h3>
            <span className={'category-badge category-badge--${item.estado}'}>
                {ETIQUETA_ESTADO[item.estado]}
            </span>
        </div>
        <div className="category-metrics">
            <div>
                <p className="category-metric-label">Tiempo real / estimado</p>
                <p className="category-metric-value">{item.dificultad_real_prom?? '-'}/{item.dificultad_estimada_prom}</p>
            </div>
        </div>

        {item.mejora_tiempo &&(
            <p className="category-trend">
                {ICONO_MEJORA[item.mejora_tiempo]}{ETIQUETA_MEJORA[item.mejora_tiempo]}
                {item.variacion_tiempo_pct !== null && `(${item.variacion_tiempo_pct>0?'+':''}${item.variacion_tiempo_pct}%)`}
            </p>
        )}
        <p className="category-recommendation">{TEXTO_RECOMENDACION[item.recomendacion]}</p>
    </div>
);

interface Props{
    categorias:RendimientoCategoria[];
}

export const RendimientoCategorias:React.FC<Props>=({categorias})=>{
    if (categorias.length===0){
        return(
            <EmptyState className="empty-state--statics" headingLevel={4} title="Aun no hay suficientes datos" description="Completa tareas con el cronómetro para ver tu rendimiento por categoría."/>
        );
    }
    
    return (
    <section>
    <div className="stat-card-header">
        <h2 className="stat-card-title">Rendimiento por categoría</h2>
        <span className="stat-card-icon"><BarChart2 size={18} /></span>
    </div>
    <div className="category-grid">
        {categorias.map((c) => (
        <CategoriaCard key={c.categoria} item={c} />
        ))}
    </div>
    </section>
    );
}