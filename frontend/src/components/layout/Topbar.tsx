// src/components/layout/Topbar.tsx
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { PanelNotificaciones } from '../common/PanelNotificaciones'; 
import '../../styles/Topbar.css';

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
        <div className="user-profile">
          {/* Aquí insertamos el componente global conectado a Redux y a la API */}
          <PanelNotificaciones />

          <button className="user-profile-clickable" onClick={() => setMenuAbierto(!menuAbierto)} style={{ background: 'none', border: 'none', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '12px' }}>
            <div className="user-info" style={{ textAlign: 'right' }}>
              <span className="user-name">{nombreUsuario}</span>
              <span className="user-role">{rolUsuario}</span>
            </div>
            <div className="user-avatar pixel-avatar"></div>
          </button>
        </div>

        {menuAbierto && (
          <div className="user-dropdown-menu">
            {token ? (
              <>
                <button 
                  onClick={() => { 
                    setMenuAbierto(false); 
                    navigate('/perfil'); 
                  }} 
                  className="btn-dropdown-opcion"
                >
                  ⚙️ Configuración
                </button>
                <button 
                  onClick={() => { 
                    setMenuAbierto(false); 
                    onAbrirModalLogout(); 
                  }} 
                  className="btn-cerrar-sesion"
                >
                  🚪 Cerrar Sesión
                </button>
              </>
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