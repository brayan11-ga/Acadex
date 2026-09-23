// frontend/src/components/grupos/GroupDetail.tsx
import type { GrupoConRol, Integrante } from "../../types/grupo";
import "../../styles/group-detail.css";

interface GroupDetailProps {
  group: GrupoConRol;
  members: Integrante[];
  currentUserId: number | null;
  onBack: () => void;
  onKickMember: (idUsuario: number) => void;
  onDeleteGroup: () => void;
  onLeaveGroup: () => void;
}

export function GroupDetail({
  group,
  members,
  currentUserId,
  onBack,
  onKickMember,
  onDeleteGroup,
  onLeaveGroup,
}: GroupDetailProps) {
  const isLeader = group.rol === "lider";

  return (
    <section className="detail-view">
      <button className="detail-back" onClick={onBack}>
        ← Volver a Mis Grupos
      </button>
      <header className="detail-header">
        <div className="detail-header-info">
          <h1 className="detail-title">{group.nombre_grupo}</h1>
          <p className="detail-desc">{group.descripcion?.trim() || "Sin descripción."}</p>
        </div>
        {isLeader && (
          <button className="detail-btn detail-btn-danger" onClick={onDeleteGroup}>
            Eliminar grupo
          </button>
        )}
      </header>
      <div className="detail-members-block">
        <h2 className="detail-section-title">
          Integrantes <span className="detail-count">{members.length}</span>
        </h2>
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