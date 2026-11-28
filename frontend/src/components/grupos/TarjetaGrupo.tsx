import { ChevronRight } from "lucide-react";
import type { GrupoConRol } from "../../types/grupo";
import { useDesbordado } from "../../hooks/useDesbordado";
import "../../styles/tarjetas.css";
import "../../styles/tareas-grupo.css";
import "../../styles/difuminado.css";

interface TarjetaGrupoProps {
    grupo: GrupoConRol;
    onAbrir: (idGrupo: number) => void;
}

export const TarjetaGrupo = ({ grupo, onAbrir }: TarjetaGrupoProps) => {
    const esLider = grupo.rol === "lider";
    const descripcion = grupo.descripcion?.trim() || "Sin descripción.";
    const [nombreRef, nombreDesborda] = useDesbordado<HTMLHeadingElement>(grupo.nombre_grupo);
    const [descRef, descDesborda] = useDesbordado<HTMLParagraphElement>(descripcion);

    return (
    <article
        className={`tareas-grupo-tarjeta tarjeta-clicable${esLider ? " tareas-grupo-tarjeta--lider" : ""}`}
        onClick={() => onAbrir(grupo.id_grupo)}
    >
        <div className="tareas-grupo-tarjeta-principal">
        <div className="tareas-grupo-tarjeta-titulo-fila">
            <h3
            ref={nombreRef}
            className={`tareas-grupo-tarjeta-titulo texto-difuminado ${nombreDesborda ? "texto-difuminado--desborda" : ""}`}
            title={grupo.nombre_grupo}
            >
            {grupo.nombre_grupo}
            </h3>
            <span className={`tareas-grupo-chip tareas-grupo-chip--${esLider ? "lider" : "miembro"}`}>
            {esLider ? "Líder" : "Miembro"}
            </span>
        </div>
        <p
            ref={descRef}
            className={`tareas-grupo-desc texto-difuminado ${descDesborda ? "texto-difuminado--desborda" : ""}`}
            title={descripcion}
        >
            {descripcion}
        </p>
        </div>

        <div className="tareas-grupo-tarjeta-lado">
        <button
            type="button"
            className="tareas-grupo-boton tareas-grupo-boton--secundario tareas-grupo-boton--pequeno"
            aria-label={`Abrir grupo ${grupo.nombre_grupo}`}
        >
            Ver grupo <ChevronRight size={14} />
        </button>
        </div>
    </article>
    );
};