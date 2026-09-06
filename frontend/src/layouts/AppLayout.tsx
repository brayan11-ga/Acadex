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
  const [errorServidorCaido, setErrorServidorCaido] = useState(false);

  const token = localStorage.getItem('access_token');

  useEffect(() => {
    if (token) {
      apiFetch<PerfilUsuario>('/perfiles/me')
        .then((data) => {
          setPerfil(data);
          setErrorServidorCaido(false);
        })
        .catch((err) => {
          console.error("Error al cargar perfil:", err);
          
          // Si el token es inválido o expiró (401), deslogueamos
          if (err.message && err.message.includes('401')) {
            localStorage.removeItem('access_token');
            navigate('/iniciarSesion');
          } else if (err.message && err.message.includes('Failed to fetch')) {
            // SOLO si el servidor está apagado activamos el banner de modo prueba
            setErrorServidorCaido(true);
          } else {
            // Cualquier otro error menor (como perfil vacío), el servidor sigue arriba y hay sesión
            setErrorServidorCaido(false);
          }
        });
    }
  }, [token, navigate]);

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

  // El banner solo se muestra si NO hay token O si el servidor se cayó por completo
  const mostrarAvisoSinSesion = !token || errorServidorCaido;
  const nombreUsuario = perfil?.nombre_usuario || (token ? "Usuario Acadex" : "Invitado (Modo Pruebas)");
  const rolUsuario = "Estudiante ADSO"; 

  return (
    <div className="pixel-app">
      <Sidebar onCrearRapido={abrirModalCrear} />

      <main className="pixel-content">
        {/* Banner global: solo aparece sin token o si FastAPI está apagado */}
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