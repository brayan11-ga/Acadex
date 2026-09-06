// src/router/AppRouter.tsx
import { Routes, Route, Navigate } from "react-router-dom";
import Inicio from "../pages/LandingPage";
import IniciarSesion from "../pages/Login";
import Registrarse from "../pages/Register";

// Layout y páginas internas
import AppLayout from "../layouts/AppLayout";
import Tareas from "../pages/Tareas";
import Perfil from "../pages/Perfil";
import { Panel } from "../pages/Panel";
import { AdminPage } from "../pages/Admin";
import { Calendario } from "../pages/Calendario";

// Rutas de seguridad / control de acceso
import { ProtectedRoute } from "./ProtectedRoute";
import { RutaAdmin } from "./RutaAdmin";

function AppRouter() {
  return (
    <Routes>
      {/* Rutas públicas */}
      <Route path="/" element={<Inicio />} />
      <Route path="/iniciarSesion" element={<IniciarSesion />} />
      <Route path="/registrarse" element={<Registrarse />} />

      {/* Rutas protegidas generales (Panel, Tareas y Perfil con AppLayout) */}
      <Route element={<ProtectedRoute />}>
        <Route element={<AppLayout />}>
          <Route path="/panel" element={<Panel />} />
          <Route path="/tareas" element={<Tareas />} />
          <Route path="/perfil" element={<Perfil />} />
          <Route path="/calendario" element={<Calendario />} />
        </Route>
      </Route>

      {/* Ruta protegida exclusiva para administradores */}
      <Route element={<RutaAdmin />}>
        <Route path="/admin" element={<AdminPage />} />
      </Route>

      {/* Redirección por defecto si la ruta no existe */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

export default AppRouter;