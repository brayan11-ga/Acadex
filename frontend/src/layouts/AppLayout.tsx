// src/layouts/AppLayout.tsx
import { useEffect, useState } from "react";
import { Outlet, useNavigate } from "react-router-dom";
import Sidebar from "../components/layout/Sidebar";
import FormularioNuevaTarea from "../components/tareas/FormularioNuevaTarea";
import { ThemeToggle } from "../components/landing/ThemeToggle";
import { apiFetch } from "../services/api";
import { ModalConfirmacion } from "../components/layout/ModalConfirmacion";

// Importamos los componentes que ahora son globales (Te sugiero moverlos a layout después)
import { BannerModoPrueba } from '../components/layout/BannerModoPrueba';
import { Topbar } from '../components/layout/Topbar';

import "../styles/pixel-theme.css";
import "../styles/layout.css";
import "../styles/tareas.css";

interface PerfilUsuario {
  nombre_usuario: string;
  telefono?: string;
  descripcion?: string;
}

function AppLayout() {
  const navigate = useNavigate();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [refreshKey, setRefreshKey] = useState(0);

  // Estados globales para el perfil y sesión
  const [perfil, setPerfil] = useState<PerfilUsuario | null>(null);
  const [modalLogoutAbierto, setModalLogoutAbierto] = useState(false);
  const [errorPerfil, setErrorPerfil] = useState(false);

  const token = localStorage.getItem('access_token');

  useEffect(() => {
    if (token) {
      apiFetch<PerfilUsuario>('/perfiles/me')
        .then((data) => setPerfil(data))
        .catch((err) => {
          console.error("Error al cargar perfil:", err);
          setErrorPerfil(true);
        });
    }
  }, [token]);

  const manejarTareaCreada = () => {
    setIsModalOpen(false);
    setRefreshKey((k) => k + 1);
  };

  const ejecutarCierreSesion = () => {
    localStorage.removeItem('access_token');
    navigate('/iniciarSesion');
  };

  const mostrarAvisoSinSesion = !token || errorPerfil;
  const nombreUsuario = perfil?.nombre_usuario || (token ? "Usuario Acadex" : "Invitado (Modo Pruebas)");
  const rolUsuario = "Estudiante ADSO"; 

  return (
    <div className="pixel-app">
      <Sidebar onCrearRapido={() => setIsModalOpen(true)} />

      <main className="pixel-content">
        {/* 1. Elementos globales superiores */}
        {mostrarAvisoSinSesion && <BannerModoPrueba />}
        
        <Topbar 
          nombreUsuario={nombreUsuario}
          rolUsuario={rolUsuario}
          token={token}
          onAbrirModalLogout={() => setModalLogoutAbierto(true)}
        />

        {/* 2. Aquí se inyectan las vistas dinámicas (Panel, Tareas, y pronto Estadísticas) */}
        <Outlet
          context={{
            abrirModalGlobal: () => setIsModalOpen(true),
            refreshKey,
          }}
        />
      </main>

      <div className="floating-theme-toggle">
        <ThemeToggle />
      </div>

      {isModalOpen && (
        <div className="pixel-modal-overlay">
          <div className="pixel-modal-content">
            <FormularioNuevaTarea
              onDescartar={() => setIsModalOpen(false)}
              onTareaCreada={manejarTareaCreada}
            />
          </div>
        </div>
      )}

      {/* Modal de cierre de sesión movido a nivel global */}
      <ModalConfirmacion
        isOpen={modalLogoutAbierto}
        title="¿Cerrar sesión?"
        message="¿Estás seguro de que deseas salir de Acadex?"
        onConfirm={ejecutarCierreSesion}
        onCancel={() => setModalLogoutAbierto(false)}
      />
    </div>
  );
}

export default AppLayout;