// src/components/panel/PanelBannerModoPrueba.tsx
import { useNavigate } from 'react-router-dom';

export const PanelBannerModoPrueba = () => {
  const navigate = useNavigate();

  return (
    <div className="pixel-panel panel-banner-aviso">
      <span className="panel-banner-texto">
        ⚠️ <strong>Modo de prueba:</strong> No hay sesión activa o el servidor está apagado. Puedes explorar libremente.
      </span>
      <div className="panel-banner-acciones">
        <button onClick={() => navigate('/iniciarSesion')} className="pixel-btn-play panel-btn-chico">
          Iniciar Sesión
        </button>
        <button onClick={() => navigate('/registrarse')} className="pixel-btn-outline-success panel-btn-chico">
          Registrarse
        </button>
      </div>
    </div>
  );
};