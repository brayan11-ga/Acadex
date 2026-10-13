// frontend/src/components/grupos/MyGroups.tsx
import type { GrupoConRol } from "../../types/grupo";
import "../../styles/my-groups.css";
import { EmptyState } from "../ui/EmptyState";

interface MyGroupsProps {
  groups: GrupoConRol[];
  onOpenGroup: (idGrupo: number) => void;
  onCreateClick: () => void;
  onJoinClick: () => void;
}

export function MyGroups({ groups, onOpenGroup, onCreateClick, onJoinClick }: MyGroupsProps) {
  return (
    <section className="groups-view">
      <header className="groups-header">
        <div>
          <h1 className="groups-title">Mis Grupos</h1>
          <p className="groups-subtitle">
            {groups.length === 0
              ? "Organiza tus actividades y estudia en equipo."
              : `Perteneces a ${groups.length} ${groups.length === 1 ? "grupo" : "grupos"} de estudio.`}
          </p>
        </div>
        <div className="groups-header-actions">
          <button className="groups-btn groups-btn-ghost" onClick={onJoinClick}>
            Unirse con código
          </button>
          <button className="groups-btn groups-btn-primary" onClick={onCreateClick}>
            + Crear grupo
          </button>
        </div>
      </header>
      {groups.length === 0 ? (
        <EmptyState
          className="empty-state--groups"
          title="Aún no tienes grupos de estudio"
          description="Crea un grupo o únete con un código para empezar a colaborar."
        />
      ) : (
        <ul className="groups-grid">
          {groups.map((grupo) => (
            <li key={grupo.id_grupo}>
              <button
                type="button"
                className="group-card"
                onClick={() => onOpenGroup(grupo.id_grupo)}
                aria-label={`Abrir grupo ${grupo.nombre_grupo}`}
              >
                <div className="group-card-top">
                  <h2 className="group-card-name">{grupo.nombre_grupo}</h2>
                  <span className={`role-badge role-badge--${grupo.rol === "lider" ? "leader" : "member"}`}>
                    {grupo.rol === "lider" ? "Líder" : "Miembro"}
                  </span>
                </div>
                <p className="group-card-desc">{grupo.descripcion?.trim() || "Sin descripción."}</p>
                <div className="group-card-footer">
                  <span className="group-card-cta">Ver grupo →</span>
                </div>
              </button>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
