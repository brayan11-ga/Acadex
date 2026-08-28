import { useState } from 'react';
import '../../styles/sidebar.css';

interface NavItem {
  id: string;
  label: string;
  icon: string;
}
 
interface SidebarProps {
  /** Nombre mostrado en la cabecera del sidebar */
  appName?: string;
  /** Id del item activo por defecto (uso no controlado) */
  defaultActiveId?: string;
  /** Se llama cuando el usuario hace clic en un item de navegación */
  onNavigate?: (id: string) => void;
  /** Se llama cuando el usuario hace clic en el botón "Quick Create" */
  onQuickCreate?: () => void;
}
 
const NAV_ITEMS: NavItem[] = [
  { id: 'dashboard', label: 'Dashboard', icon: 'bi-speedometer2' },
  { id: 'tareas', label: 'Tareas', icon: 'bi-list-task' },
  { id: 'calendario', label: 'Calendario', icon: 'bi-calendar3-fill' },
  { id: 'estadisticas', label: 'Estadísticas', icon: 'bi-bar-chart-fill' },
  { id: 'ajustes', label: 'Ajustes', icon: 'bi-gear-fill' },
];
 
/* ---------------------------------------------------------- */
/* Component                                                    */
/* ---------------------------------------------------------- */
 
function Sidebar({
  appName = 'Acadex',
  defaultActiveId = 'tareas',
  onNavigate,
  onQuickCreate,
}: SidebarProps) {
  const [activeId, setActiveId] = useState<string>(defaultActiveId);
 
  const handleNavClick = (id: string) => {
    setActiveId(id);
    onNavigate?.(id);
  };
 
  return (
    <aside className="sidebar">
      <div className="sidebar__header">
        <h1 className="sidebar__title">{appName}</h1>
      </div>
 
      <nav className="sidebar__nav" aria-label="Main navigation">
        <ul className="sidebar__list">
          {NAV_ITEMS.map((item) => (
            <li key={item.id}>
              <button
                type="button"
                className={`sidebar__item${activeId === item.id ? ' sidebar__item--active' : ''}`}
                onClick={() => handleNavClick(item.id)}
                aria-current={activeId === item.id ? 'page' : undefined}
              >
                <span className="sidebar__icon">
                  <i className={`bi ${item.icon}`} aria-hidden="true" />
                </span>
                <span className="sidebar__label">{item.label}</span>
              </button>
            </li>
          ))}
        </ul>
      </nav>
 
      <div className="sidebar__footer">
        <button type="button" className="sidebar__quick-create" onClick={onQuickCreate}>
          <i className="bi bi-plus-lg" aria-hidden="true" />
          <span>Crear Tarea Rápido</span>
        </button>
      </div>
    </aside>
  );
}
 
export default Sidebar;