// Ruta: frontend/src/components/grupos/GroupDetail.tsx
import type { GrupoConRol, Integrante } from "../../types/grupo";
import "../../styles/group-detail.css";
import { useNavigate } from "react-router-dom";
import { EmptyState } from "../ui/EmptyState";

interface GroupDetailProps {
  group: GrupoConRol;
  members: Integrante[];
  currentUserId: number | null;
  onBack: () => void;
  onKickMember: (idUsuario: number) => void;
  onLeaveGroup: () => void;
  textoVolver?: string;
}

export function GroupDetail({
  group,
  members,
  currentUserId,
  onBack,
  onKickMember,
  onLeaveGroup,
  textoVolver = "← Volver a Mis Grupos",
}: GroupDetailProps) {
  const isLeader = group.rol === "lider";
  const navigate = useNavigate();

  return (
    <section className="detail-view">
      <button className="detail-back" onClick={onBack}>
        {textoVolver}
      </button>
      <header className="detail-header">
        <div className="detail-header-info">
          <h1 className="detail-title">{group.nombre_grupo}</h1>
          <p className="detail-desc">{group.descripcion?.trim() || "Sin descripción."}</p>
        </div>

        {isLeader && (
          <div className="detail-header-actiion">
          <button className="detail-btn" onClick={()=>navigate(`/grupos/${group.id_grupo}/lider`)}>
            Panel de Lider
          </button>
          </div>
        )}
      </header>
      <div className="detail-members-block">
        <h2 className="detail-section-title">
          Integrantes <span className="detail-count">{members.length}</span>
        </h2>
        {members.length === 0 ? (
          <EmptyState
            className="empty-state--compact"
            headingLevel={3}
            title="Aún no hay integrantes en este grupo"
            description="Invita a tus compañeros para que puedan colaborar aquí."
            action={
              isLeader
                ? {
                    label: "Ir al panel de líder",
                    onClick: () => navigate("/grupos/" + group.id_grupo + "/lider"),
                  }
                : undefined
            }
          />
        ) : (
        <ul className="member-list">
          {members.map((member) => {
            const isSelf = member.id_usuario === currentUserId;
            return (
              <li key={member.id_integrante} className="member-row">
                <div className="member-info">
                  <span className="member-avatar" aria-hidden="true">
                    {member.correo_electronico.charAt(0).toUpperCase()}
                  </span>
                  <div className="member-text">
                    <span className="member-email">
                      {member.correo_electronico}
                      {isSelf && <span className="member-you">Tú</span>}
                    </span>
                    <span className={`member-role member-role--${member.rol === "lider" ? "leader" : "member"}`}>
                      {member.rol === "lider" ? "Líder" : "Miembro"}
                    </span>
                  </div>
                </div>
                {isLeader && !isSelf && (
                  <button className="member-kick" onClick={() => onKickMember(member.id_usuario)}>
                    Expulsar
                  </button>
                )}
              </li>
            );
          })}
        </ul>
        )}
      </div>
      {!isLeader && (
        <div className="detail-footer">
          <button className="detail-btn detail-btn-danger" onClick={onLeaveGroup}>
            Salir del grupo
          </button>
        </div>
      )}
    </section>
  );
}
