// src/layouts/AppLayout.tsx
import { useEffect, useState } from "react";
import { Outlet, useNavigate } from "react-router-dom";
import Sidebar from "../components/layout/Sidebar";
import FormularioNuevaTarea from "../components/tareas/FormularioNuevaTarea";
import type { TareaBackend } from "../services/tareas";
import { ThemeToggle } from "../components/landing/ThemeToggle";
import { apiFetch } from "../services/api";
import { ModalConfirmacion } from "../components/layout/ModalConfirmacion";

// Importamos los componentes globales
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

  // 1. Estados de nuestros compañeros (Soporte para edición de tareas)
  const [tareaEditando, setTareaEditando] = useState<TareaBackend | null>(null);

  // 2. Nuestros estados globales (Perfil, sesión y errores)
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

  const cerrarModal = () => {
    setIsModalOpen(false);
    setTareaEditando(null);
  };

  const manejarTareaGuardada = () => {
    cerrarModal();
    setRefreshKey((k) => k + 1);
  };

  const ejecutarCierreSesion = () => {
    localStorage.removeItem('access_token');
    navigate('/iniciarSesion');
  };

  const abrirModalCrear = () => {
    setTareaEditando(null);
    setIsModalOpen(true);
  };

  const abrirModalEditar = (tarea: TareaBackend) => {
    setTareaEditando(tarea);
    setIsModalOpen(true);
  };

  const mostrarAvisoSinSesion = !token || errorPerfil;
  const nombreUsuario = perfil?.nombre_usuario || (token ? "Usuario Acadex" : "Invitado (Modo Pruebas)");
  const rolUsuario = "Estudiante ADSO"; 

  return (
    <div className="pixel-app">
      <Sidebar onCrearRapido={abrirModalCrear} />

      <main className="pixel-content">
        {/* Banner global si no hay sesión */}
        {mostrarAvisoSinSesion && <BannerModoPrueba />}
        
        {/* Barra superior global con datos de usuario */}
        <Topbar 
          nombreUsuario={nombreUsuario}
          rolUsuario={rolUsuario}
          token={token}
          onAbrirModalLogout={() => setModalLogoutAbierto(true)}
        />

        {/* Vistas dinámicas con el contexto unificado */}
        <Outlet
          context={{
            abrirModalGlobal: abrirModalCrear,
            abrirModalEditar,
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
              onDescartar={cerrarModal}
              onTareaCreada={manejarTareaGuardada}
              tareaAEditar={tareaEditando}
            />
          </div>
        </div>
      )}

      {/* Modal global de cierre de sesión */}
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