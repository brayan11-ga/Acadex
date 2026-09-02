// src/components/layout/Sidebar.tsx
import { NavLink } from "react-router-dom";
import moonIcon from "../../assets/backgrounds/moon-icon.png";
import iconoTareas from "../../assets/icons/sidebar/tareas_sidebar.png";
import iconoCalendario from "../../assets/icons/sidebar/calendario_sidebar.png";
import iconoEstadisticas from "../../assets/icons/sidebar/estadisticas_sidebar.png";
import iconoAjustes from "../../assets/icons/sidebar/Ajustes_sidebar.png";
import logoAcadex from "../../assets/logos/logo_acadex.png";

const enlaces = [
  { to: "/panel", label: "Panel", icono: null },
  { to: "/tareas", label: "Tareas", icono: iconoTareas },
  { to: "/calendario", label: "Calendario", icono: iconoCalendario },
  { to: "/stats", label: "Estadísticas", icono: iconoEstadisticas },
  { to: "/ajustes", label: "Ajustes", icono: iconoAjustes },
];

interface SidebarProps {
  onCrearRapido: () => void;
}

function Sidebar({ onCrearRapido }: SidebarProps) {
  return (
    <aside className="pixel-sidebar">
      <div className="pixel-sidebar-logo">
        {/* Logo principal grande y reconocible */}
        <div className="pixel-brand-container">
          <img src={logoAcadex} alt="Acadex Logo" className="pixel-brand-icon" />
          <span className="pixel-sidebar-title">ACADEX</span>
        </div>

        {/* Imagen de la luna decorativa */}
        <img src={moonIcon} alt="Modo Enfoque Luna" className="pixel-logo-moon" />
        
        <span className="pixel-sidebar-subtitle">Modo Enfoque</span>
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
            {enlace.label}
          </NavLink>
        ))}
      </nav>

      <button className="pixel-btn-crear" onClick={onCrearRapido}>
        + CREAR RÁPIDO
      </button>
    </aside>
  );
}

export default Sidebar;