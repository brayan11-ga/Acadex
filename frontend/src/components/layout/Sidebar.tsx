import { NavLink } from "react-router-dom";
import moonIcon from "../../assets/backgrounds/moon-icon.png";
import iconoTareas from "../../assets/icons/sidebar/tareas_sidebar.png";
import iconoCalendario from "../../assets/icons/sidebar/calendario_sidebar.png";
import iconoEstadisticas from "../../assets/icons/sidebar/estadisticas_sidebar.png";
import iconoAjustes from "../../assets/icons/sidebar/Ajustes_sidebar.png";

const enlaces = [
  { to: "/dashboard", label: "Panel", icono: null },
  { to: "/tareas", label: "Tareas", icono: iconoTareas },
  { to: "/calendario", label: "Calendario", icono: iconoCalendario },
  { to: "/stats", label: "Estadísticas", icono: iconoEstadisticas },
  { to: "/ajustes", label: "Ajustes", icono: iconoAjustes },
];

// 1. Definimos la prop para recibir la acción
interface SidebarProps {
  onCrearRapido: () => void;
}

// 2. Recibimos la prop
function Sidebar({ onCrearRapido }: SidebarProps) {
  return (
    <aside className="pixel-sidebar">
      <div className="pixel-sidebar-logo">
        <span className="pixel-sidebar-title">ACADEX</span>
        <img src={moonIcon} alt="" className="pixel-logo-moon" />
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

      {/* 3. Conectamos la función al evento onClick */}
      <button className="pixel-btn-crear" onClick={onCrearRapido}>
        + CREAR RÁPIDO
      </button>
    </aside>
  );
}

export default Sidebar;