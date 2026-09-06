// src/layouts/AppLayout.tsx
import { useState } from "react";
import { Outlet } from "react-router-dom";
import Sidebar from "../components/layout/Sidebar";
import FormularioNuevaTarea from "../components/tareas/FormularioNuevaTarea";
import type { TareaBackend } from "../services/tareas";

import "../styles/pixel-theme.css";
import "../styles/layout.css";
import "../styles/tareas.css";

function AppLayout() {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [tareaEditando, setTareaEditando] = useState<TareaBackend | null>(null);
  const [refreshKey, setRefreshKey] = useState(0);

  const cerrarModal = () => {
    setIsModalOpen(false);
    setTareaEditando(null);
  };

  const manejarTareaGuardada = () => {
    cerrarModal();
    setRefreshKey((k) => k + 1);
  };

  const abrirModalCrear = () => {
    setTareaEditando(null);
    setIsModalOpen(true);
  };

  const abrirModalEditar = (tarea: TareaBackend) => {
    setTareaEditando(tarea);
    setIsModalOpen(true);
  };

  return (
    <div className="pixel-app">
      <Sidebar onCrearRapido={abrirModalCrear} />

      <main className="pixel-content">
        <Outlet
          context={{
            abrirModalGlobal: abrirModalCrear,
            abrirModalEditar,
            refreshKey,
          }}
        />
      </main>

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
    </div>
  );
}

export default AppLayout;