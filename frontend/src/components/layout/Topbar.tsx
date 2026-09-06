import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

// Le cambiamos el nombre a la interfaz para que sea genérica
interface TopbarProps {
  nombreUsuario: string;
  rolUsuario: string;
  token: string | null;
  onAbrirModalLogout: () => void;
}

export const Topbar = ({ nombreUsuario, rolUsuario, token, onAbrirModalLogout }: TopbarProps) => {
  const [menuAbierto, setMenuAbierto] = useState(false);
  const navigate = useNavigate();

  return (
    <header className="panel-topbar">
      <div className="search-container pixel-panel-flat">
        <span className="search-icon">🔍</span>
        <input type="text" placeholder="Buscar tareas o comandos..." className="pixel-input-search" />
      </div>
      
      <div className="user-profile-wrapper">
        <button className="user-profile-clickable" onClick={() => setMenuAbierto(!menuAbierto)}>
          <div className="user-profile">
            <div className="btn-notificacion" aria-label="Notificaciones">🔔</div>
            <div className="user-info">
              <span className="user-name">{nombreUsuario}</span>
              <span className="user-role">{rolUsuario}</span>
            </div>
            <div className="user-avatar pixel-avatar"></div>
          </div>
        </button>

        {menuAbierto && (
          <div className="user-dropdown-menu">
            {token ? (
              <button onClick={() => { setMenuAbierto(false); onAbrirModalLogout(); }} className="btn-cerrar-sesion">
                🚪 Cerrar Sesión
              </button>
            ) : (
              <button onClick={() => navigate('/iniciarSesion')} className="btn-cerrar-sesion btn-login-link">
                🔑 Iniciar Sesión
              </button>
            )}
          </div>
        )}
      </div>
    </header>
  );
};