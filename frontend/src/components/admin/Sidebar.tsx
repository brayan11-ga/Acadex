import type { LucideIcon } from 'lucide-react';
import { LayoutDashboard, Users, UsersRound, Tag, UserCog } from 'lucide-react';

export interface TabAdmin {
  clave: string;
  titulo: string;
}

interface Props {
  tabs: TabAdmin[];
  tabActivo: string;
  onCambiarTab: (clave: string) => void;
}

const ICONOS: Record<string, LucideIcon> = {
  resumen: LayoutDashboard,
  usuarios: Users,
  grupos: UsersRound,
  categorias: Tag,
  integrantes: UserCog,
};

export const Sidebar = ({ tabs, tabActivo, onCambiarTab }: Props) => {
  return (
    <aside className="admin-sidebar">
      <div className="admin-sidebar-header">
        <span className="admin-sidebar-logo">Acadex</span>
        <span className="admin-sidebar-subtitulo">Panel Admin</span>
      </div>

      <nav className="admin-sidebar-nav">
        {tabs.map((tab) => {
          const Icono = ICONOS[tab.clave] ?? LayoutDashboard;
          const activo = tab.clave === tabActivo;
          return (
            <button
              key={tab.clave}
              className={`admin-sidebar-link ${activo ? 'activo' : ''}`}
              onClick={() => onCambiarTab(tab.clave)}
              aria-current={activo ? 'page' : undefined}
            >
              <Icono size={18} />
              <span>{tab.titulo}</span>
            </button>
          );
        })}
      </nav>
    </aside>
  );
};

export default Sidebar;