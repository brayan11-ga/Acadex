// src/components/layout/Sidebar.tsx
import { NavLink } from "react-router-dom";
import moonIcon from "../../assets/backgrounds/moon-icon.png";

const enlaces = [
  { to: "/dashboard", label: "Panel", icon: "▦" },
  { to: "/tareas", label: "Tareas", icon: "✓" },
  { to: "/calendario", label: "Calendario", icon: "▤" },
  { to: "/stats", label: "Estadísticas", icon: "▲" },
  { to: "/ajustes", label: "Ajustes", icon: "●" },
];

function Sidebar() {
  return (
    <aside className="pixel-sidebar">
      <div className="pixel-sidebar-logo">
        <div className="pixel-logo-row">
          <span className="pixel-sidebar-title">ACADEX</span>
          <img src={moonIcon} alt="" className="pixel-logo-moon" />
        </div>
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
            <span className="pixel-nav-icon">{enlace.icon}</span>
            {enlace.label}
          </NavLink>
        ))}
      </nav>

      <button className="pixel-btn-crear">+ CREAR</button>
    </aside>
  );
}

export default Sidebar;