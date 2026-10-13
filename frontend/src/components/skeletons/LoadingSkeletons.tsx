import { Skeleton, SkeletonStatus } from "../ui/Skeleton";

const cuatroElementos = [0, 1, 2, 3];
const tresElementos = [0, 1, 2];

export function PanelLoadingSkeleton() {
  return (
    <div className="panel-contenedor loading-panel">
      <SkeletonStatus label="Cargando el panel" className="loading-panel__content">
        <header className="loading-panel__header">
          <Skeleton width="12rem" height="1.8rem" />
          <Skeleton width="18rem" height="0.9rem" />
        </header>
        <div className="loading-panel__hero">
          <div className="loading-surface loading-panel__priority">
            <Skeleton width="7rem" height="1rem" variant="pill" />
            <Skeleton width="68%" height="1.2rem" />
            <Skeleton width="92%" />
            <Skeleton width="78%" />
            <Skeleton width="8rem" height="2.4rem" variant="block" />
          </div>
          <div className="loading-surface loading-panel__chart">
            <Skeleton width="42%" height="1rem" />
            <div className="loading-panel__bars">
              {[42, 70, 54, 88, 63, 78, 48].map((height, index) => (
                <Skeleton
                  key={index}
                  variant="block"
                  width="9%"
                  height={height + "%"}
                  className="loading-panel__bar"
                />
              ))}
            </div>
          </div>
        </div>
        <div className="loading-panel__section-heading">
          <Skeleton width="10rem" height="1rem" />
          <Skeleton width="6rem" height="0.8rem" />
        </div>
        <div className="loading-panel__tasks">
          {tresElementos.map((item) => (
            <div className="loading-surface loading-panel__task" key={item}>
              <Skeleton width="45%" />
              <Skeleton width="78%" />
              <Skeleton width="62%" />
            </div>
          ))}
        </div>
      </SkeletonStatus>
    </div>
  );
}

export function ProfileLoadingSkeleton() {
  return (
    <SkeletonStatus label="Cargando el perfil" className="pixel-perfil-main loading-profile">
      <header className="pixel-perfil-header">
        <div className="loading-profile__heading">
          <Skeleton width="10rem" height="1.2rem" />
          <Skeleton width="18rem" />
        </div>
      </header>
      <section className="pixel-perfil-card">
        <div className="pixel-perfil-foto-row">
          <Skeleton variant="circle" width="56px" height="56px" />
          <div className="loading-profile__avatar-copy">
            <Skeleton width="8rem" />
            <Skeleton width="6rem" height="2rem" variant="block" />
          </div>
        </div>
        <div className="pixel-perfil-grid">
          {tresElementos.slice(0, 2).map((item) => (
            <div className="loading-profile__field" key={item}>
              <Skeleton width="9rem" />
              <Skeleton height="2.5rem" variant="block" />
            </div>
          ))}
        </div>
        <div className="loading-profile__field">
          <Skeleton width="10rem" />
          <Skeleton height="4rem" variant="block" />
        </div>
      </section>
      <section className="pixel-perfil-card loading-profile__preferences">
        <Skeleton width="60%" />
        <Skeleton width="42%" />
      </section>
      <Skeleton width="9rem" height="2.6rem" variant="block" />
    </SkeletonStatus>
  );
}

export function GroupsLoadingSkeleton() {
  return (
    <SkeletonStatus label="Cargando los grupos" className="groups-view loading-groups">
      <header className="groups-header">
        <div className="loading-groups__heading">
          <Skeleton width="14rem" height="1.4rem" />
          <Skeleton width="19rem" />
        </div>
        <div className="loading-groups__actions">
          <Skeleton width="9rem" height="2.7rem" variant="block" />
          <Skeleton width="8rem" height="2.7rem" variant="block" />
        </div>
      </header>
      <ul className="groups-grid">
        {tresElementos.map((item) => (
          <li key={item}>
            <article className="loading-surface loading-groups__card">
              <div className="loading-groups__card-heading">
                <Skeleton width="56%" />
                <Skeleton width="4.5rem" height="1.4rem" variant="pill" />
              </div>
              <Skeleton width="92%" />
              <Skeleton width="70%" />
              <Skeleton width="5rem" />
            </article>
          </li>
        ))}
      </ul>
    </SkeletonStatus>
  );
}

export function GroupMembersLoadingSkeleton({ label = "Cargando integrantes del grupo" }: { label?: string }) {
  return (
    <SkeletonStatus label={label} className="detail-view loading-members">
      <Skeleton width="8rem" height="1rem" />
      <header className="detail-header">
        <div className="loading-members__heading">
          <Skeleton width="min(24rem, 80vw)" height="1.4rem" />
          <Skeleton width="min(32rem, 88vw)" />
          <Skeleton width="12rem" />
        </div>
        <Skeleton width="8rem" height="2.5rem" variant="block" />
      </header>
      <section className="detail-members-block">
        <Skeleton width="10rem" height="1rem" />
        <ul className="member-list">
          {cuatroElementos.map((item) => (
            <li className="member-row loading-members__row" key={item}>
              <div className="member-info">
                <Skeleton variant="circle" width="2.7rem" height="2.7rem" />
                <div className="loading-members__identity">
                  <Skeleton width="min(15rem, 45vw)" />
                  <Skeleton width="5rem" />
                </div>
              </div>
              <Skeleton width="5rem" height="2rem" variant="block" />
            </li>
          ))}
        </ul>
      </section>
    </SkeletonStatus>
  );
}

export function TaskListLoadingSkeleton() {
  return (
    <SkeletonStatus label="Cargando las tareas" className="loading-task-list">
      <section className="pixel-tareas-lista">
        {cuatroElementos.map((item) => (
          <article className="pixel-tarea-card loading-task-card" key={item}>
            <div className="pixel-tarea-info">
              <div className="loading-task-card__heading">
                <Skeleton width="min(16rem, 50vw)" height="1rem" />
                <Skeleton width="5rem" height="1.4rem" variant="pill" />
              </div>
              <Skeleton width="86%" />
              <Skeleton width="58%" />
            </div>
            <Skeleton width="7rem" height="2.4rem" variant="block" />
          </article>
        ))}
      </section>
    </SkeletonStatus>
  );
}

export function AttachmentsLoadingSkeleton() {
  return (
    <SkeletonStatus label="Cargando los adjuntos" className="loading-attachments">
      <ul className="pixel-adjuntos-lista loading-attachments-list">
        {tresElementos.map((item) => (
          <li className="pixel-adjunto-item loading-attachment-row" key={item}>
            <Skeleton width="2.5rem" height="2.5rem" variant="block" />
            <div className="loading-attachment-row__copy">
              <Skeleton width="min(18rem, 58vw)" />
              <Skeleton width="9rem" />
            </div>
            <Skeleton width="2rem" height="2rem" variant="circle" />
          </li>
        ))}
      </ul>
    </SkeletonStatus>
  );
}

export function StatisticsPageLoadingSkeleton() {
  return (
    <SkeletonStatus label="Cargando las estadísticas" className="stats-page loading-statistics-page">
      <header className="stats-header loading-statistics-header">
        <Skeleton width="min(24rem, 80vw)" height="1.4rem" />
        <Skeleton width="min(28rem, 82vw)" />
      </header>
      <div className="stats-grid-top">
        <div className="stat-card loading-stat-goal">
          <div className="stat-card-header"><Skeleton width="9rem" /><Skeleton width="2rem" height="2rem" variant="block" /></div>
          <Skeleton variant="circle" width="8rem" height="8rem" />
          <Skeleton width="70%" />
        </div>
      </div>
      <div className="stats-grid-middle">
        {tresElementos.map((item) => (
          <div className="stat-card loading-stat-card" key={item}>
            <div className="stat-card-header"><Skeleton width="8rem" /><Skeleton width="2rem" height="2rem" variant="block" /></div>
            <Skeleton width="55%" height="1.6rem" />
            <Skeleton width="78%" />
          </div>
        ))}
      </div>
      <div className="stats-grid-bottom">
        <div className="stat-card loading-stat-insight">
          <div className="stat-card-header"><Skeleton width="12rem" /></div>
          <Skeleton width="95%" /><Skeleton width="82%" /><Skeleton width="88%" />
        </div>
        <div className="stat-card loading-stat-insight">
          <div className="stat-card-header"><Skeleton width="9rem" /></div>
          <Skeleton width="93%" /><Skeleton width="72%" />
        </div>
      </div>
    </SkeletonStatus>
  );
}

export function AdminSummaryLoadingSkeleton() {
  return (
    <SkeletonStatus label="Cargando el resumen de administración" className="admin-resumen loading-admin-summary">
      <Skeleton width="17rem" height="1rem" />
      <div className="admin-resumen-grid">
        {tresElementos.map((item) => (
          <div className="stat-card admin-resumen-card" key={item}>
            <div className="stat-card-header"><Skeleton width="7rem" /><Skeleton width="2rem" height="2rem" variant="block" /></div>
            <Skeleton width="4rem" height="1.6rem" />
          </div>
        ))}
      </div>
    </SkeletonStatus>
  );
}

export function AdminTableLoadingSkeleton({
  columns,
  hasActions,
}: {
  columns: string[];
  hasActions: boolean;
}) {
  return (
    <SkeletonStatus label="Cargando los registros" className="loading-table-state">
      <div className="loading-table-scroll">
        <table className="tabla-admin">
          <thead>
            <tr>
              {columns.map((column, index) => <th key={column + index}>{column}</th>)}
              {hasActions && <th>Acciones</th>}
            </tr>
          </thead>
          <tbody>
            {cuatroElementos.map((row) => (
              <tr key={row}>
                {columns.map((column, index) => (
                  <td key={column + index}><Skeleton width={(48 + ((row + index) % 4) * 11) + "%"} /></td>
                ))}
                {hasActions && <td><Skeleton width="5rem" height="2rem" variant="block" /></td>}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </SkeletonStatus>
  );
}

export function ChartSummaryLoadingSkeleton() {
  return (
    <SkeletonStatus label="Cargando el resumen" className="loading-chart-summary">
      <div className="loading-chart-summary__metrics">
        {tresElementos.map((item) => (
          <div className="indicator-card" key={item}>
            <Skeleton width="70%" />
            <Skeleton width="45%" height="1.4rem" />
          </div>
        ))}
      </div>
      <div className="chart-container loading-chart-summary__chart">
        <div className="loading-chart-summary__bars">
          {[38, 66, 50, 82, 58, 74, 44].map((height, index) => (
            <Skeleton key={index} variant="block" width="8%" height={height + "%"} />
          ))}
        </div>
      </div>
    </SkeletonStatus>
  );
}
