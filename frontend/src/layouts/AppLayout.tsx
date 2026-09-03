import { useState } from "react";
import { Outlet } from "react-router-dom";
import Sidebar from "../components/layout/Sidebar";
import FormularioNuevaTarea from "../components/tareas/FormularioNuevaTarea";

import "../styles/pixel-theme.css";
import "../styles/layout.css";
import "../styles/tareas.css";

function AppLayout() {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [refreshKey, setRefreshKey] = useState(0); // cambia cada vez que se crea una tarea

  const manejarTareaCreada = () => {
    setIsModalOpen(false);
    setRefreshKey((k) => k + 1);
  };

  return (
    <div className="pixel-app">
      <Sidebar onCrearRapido={() => setIsModalOpen(true)} />

      <main className="pixel-content">
        <Outlet
          context={{
            abrirModalGlobal: () => setIsModalOpen(true),
            refreshKey,
          }}
        />
      </main>

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
    </div>
  );
}

export default AppLayout;