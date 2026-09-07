// src/components/layout/Sidebar.tsx
import { useState } from "react";
import { NavLink } from "react-router-dom";
import moonIcon from "../../assets/backgrounds/moon-icon.png";
import iconoTareas from "../../assets/icons/sidebar/tareas_sidebar.png";
import iconoCalendario from "../../assets/icons/sidebar/calendario_sidebar.png";
import iconoEstadisticas from "../../assets/icons/sidebar/estadisticas_sidebar.png";
import logoAcadex from "../../assets/logos/logo_acadex.png";

const enlaces = [
  { to: "/panel", label: "Panel", icono: null },
  { to: "/tareas", label: "Tareas", icono: iconoTareas },
  { to: "/calendario", label: "Calendario", icono: iconoCalendario },
  { to: "/estadisticas", label: "Estadísticas", icono: iconoEstadisticas },
];

interface SidebarProps {
  onCrearRapido: () => void;
}

function Sidebar({ onCrearRapido }: SidebarProps) {
  const [isCollapsed, setIsCollapsed] = useState(false);

  return (
    <aside className={`pixel-sidebar ${isCollapsed ? "collapsed" : ""}`}>
      {/* Botón de toggle con Bootstrap Icons y estilo para pixel-art */}
      <button 
        className="btn-toggle-sidebar" 
        onClick={() => setIsCollapsed(!isCollapsed)}
        title={isCollapsed ? "Expandir menú" : "Colapsar menú"}
      >
        <i className={`bi ${isCollapsed ? "bi-caret-right-fill" : "bi-caret-left-fill"}`}></i>
      </button>

      <div className="pixel-sidebar-logo">
        <div className="pixel-brand-container">
          <img src={logoAcadex} alt="Acadex Logo" className="pixel-brand-icon" />
          {!isCollapsed && <span className="pixel-sidebar-title">ACADEX</span>}
        </div>

        {!isCollapsed && (
          <>
            <img src={moonIcon} alt="Modo Enfoque Luna" className="pixel-logo-moon" />
            <span className="pixel-sidebar-subtitle">Modo Enfoque</span>
          </>
        )}
      </div>

      <nav className="pixel-sidebar-nav">
        {enlaces.map((enlace) => (
          <NavLink
            key={enlace.to}
            to={enlace.to}
            className={({ isActive }) =>
              isActive ? "pixel-nav-link active" : "pixel-nav-link"
            }
          >
            {enlace.icono ? (
              <img src={enlace.icono} alt="" className="pixel-nav-icono" />
            ) : (
              <span className="pixel-grid-icono" aria-hidden="true">
                <span></span><span></span><span></span><span></span>
              </span>
            )}
            
            {!isCollapsed && <span className="nav-text">{enlace.label}</span>}
            {isCollapsed && <span className="pixel-tooltip">{enlace.label}</span>}
          </NavLink>
        ))}
      </nav>

      <button className="pixel-btn-crear" onClick={onCrearRapido} title="Crear Rápido">
        {isCollapsed ? "+" : "+ CREAR RÁPIDO"}
      </button>
    </aside>
  );
}

export default Sidebar;