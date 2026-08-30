import { useState } from "react";
import { Outlet } from "react-router-dom";
import Sidebar from "../components/layout/Sidebar";
import FormularioNuevaTarea from "../components/tareas/FormularioNuevaTarea";

import "../styles/pixel-theme.css";
import "../styles/layout.css";
import "../styles/tareas.css"; // Importamos los estilos del modal globalmente

function AppLayout() {
  // Estado global para el modal
  const [isModalOpen, setIsModalOpen] = useState(false);

  return (
    <div className="pixel-app">
      {/* Pasamos la función al Sidebar */}
      <Sidebar onCrearRapido={() => setIsModalOpen(true)} />
      
      <main className="pixel-content">
        {/* Usamos context para que las vistas (como Tareas) puedan usar la función */}
        <Outlet context={{ abrirModalGlobal: () => setIsModalOpen(true) }} />
      </main>

      {/* El modal renderizado a nivel global */}
      {isModalOpen && (
        <div className="pixel-modal-overlay">
          <div className="pixel-modal-content">
            <FormularioNuevaTarea onDescartar={() => setIsModalOpen(false)} />
          </div>
        </div>
      )}
    </div>
  );
}

export default AppLayout;