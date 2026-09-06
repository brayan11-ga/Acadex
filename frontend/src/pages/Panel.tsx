// src/pages/Panel.tsx
import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAppDispatch, useAppSelector } from '../hooks/hooks';
import { fetchPanelData } from '../store/panelSlice';
import { apiFetch } from '../services/api';
import { ModalConfirmacion } from '../components/layout/ModalConfirmacion';

// Componentes hijos organizados
import { PanelBannerModoPrueba } from '../components/panel/PanelBannerModoPrueba';
import { PanelTopbar } from '../components/panel/PanelTopbar';
import { PanelHero } from '../components/panel/PanelHero';
import { PanelTareasRecientes } from '../components/panel/PanelTareasRecientes';

import '../styles/Panel.css'; 

interface PerfilUsuario {
  nombre_usuario: string;
  telefono?: string;
  descripcion?: string;
}

export const Panel = () => {
  const dispatch = useAppDispatch();
  const navigate = useNavigate();
  
  const { data: datos, loading: cargando, error } = useAppSelector((state) => state.panel);

  const [perfil, setPerfil] = useState<PerfilUsuario | null>(null);
  const [modalLogoutAbierto, setModalLogoutAbierto] = useState(false);

  const token = localStorage.getItem('access_token');

  useEffect(() => {
    dispatch(fetchPanelData());

    if (token) {
      apiFetch<PerfilUsuario>('/perfiles/me')
        .then((data) => setPerfil(data))
        .catch((err) => console.error("Error al cargar perfil:", err));
    }
  }, [dispatch, token]);

  const ejecutarCierreSesion = () => {
    localStorage.removeItem('access_token');
    navigate('/iniciarSesion');
  };

  if (cargando) {
    return (
      <div className="panel-contenedor panel-estado-container">
        <div className="pixel-panel panel-mensaje-cargando">
          <p className="pixel-text">Cargando tu panel...</p>
        </div>
      </div>
    );
  }

  const mostrarAvisoSinSesion = !token || error;
  const { tareaPrioritaria, progreso, proximasTareas } = datos || {};
  const nombreUsuario = perfil?.nombre_usuario || (token ? "Usuario Acadex" : "Invitado (Modo Pruebas)");
  const rolUsuario = "Estudiante ADSO";

  return (
    <div className="panel-contenedor">
      {mostrarAvisoSinSesion && <PanelBannerModoPrueba />}

      <PanelTopbar 
        nombreUsuario={nombreUsuario}
        rolUsuario={rolUsuario}
        token={token}
        onAbrirModalLogout={() => setModalLogoutAbierto(true)}
      />

      <section className="panel-header-titulos">
        <h1 className="pixel-title-main">Panel</h1>
        <p className="pixel-subtitle">Concéntrate en lo que importa hoy.</p>
      </section>

      <PanelHero tareaPrioritaria={tareaPrioritaria} progreso={progreso} />

      <PanelTareasRecientes proximasTareas={proximasTareas} />

      <ModalConfirmacion
        isOpen={modalLogoutAbierto}
        title="¿Cerrar sesión?"
        message="¿Estás seguro de que deseas salir de Acadex?"
        onConfirm={ejecutarCierreSesion}
        onCancel={() => setModalLogoutAbierto(false)}
      />
    </div>
  );
};

export default Panel;