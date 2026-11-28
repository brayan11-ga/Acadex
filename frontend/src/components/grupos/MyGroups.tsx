// frontend/src/components/grupos/MyGroups.tsx
import type { GrupoConRol } from "../../types/grupo";
import "../../styles/tarjetas.css";
import "../../styles/my-groups.css";
import { EmptyState } from "../ui/EmptyState";
import { ToggleVista } from "../ui/ToggleVista";
import { useModoVista } from "../../hooks/useModoVista";
import { TarjetaGrupo } from "./TarjetaGrupo";

interface MyGroupsProps {
  groups: GrupoConRol[];
  onOpenGroup: (idGrupo: number) => void;
  onCreateClick: () => void;
  onJoinClick: () => void;
}

export function MyGroups({ groups, onOpenGroup, onCreateClick, onJoinClick }: MyGroupsProps) {
  const [modoVista, setModoVista] = useModoVista("acadex:vista-grupos", "cuadricula");

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
          <button
            className="groups-btn groups-btn-primary"
            onClick={onCreateClick}
          >
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
        <>
          <div className="groups-toolbar">
            <ToggleVista valor={modoVista} onCambiar={setModoVista} />
          </div>
          <ul
            className={`tarjetas-lista ${modoVista === "cuadricula" ? "vista-cuadricula" : ""}`}
          >
            {groups.map((grupo) => (
              <li key={grupo.id_grupo}>
                <TarjetaGrupo grupo={grupo} onAbrir={onOpenGroup} />
              </li>
            ))}
          </ul>
        </>
      )}
    </section>
  );
}
