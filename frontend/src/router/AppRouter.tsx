import { Routes, Route, Navigate } from "react-router-dom";
import Inicio from "../pages/LandingPage";
import IniciarSesion from "../pages/Login";
import Registrarse from "../pages/Register";

import AppLayout from "../layouts/AppLayout";
import Tareas from "../pages/Tareas";
import Perfil from "../pages/Perfil";
import { Panel } from "../pages/Panel";
import { Admin } from "../pages/Admin";
import { Lider } from "../pages/Lider";
import { Estadisticas } from "../pages/Estadisticas";
import { Calendario } from "../pages/Calendario";

import { ProtectedRoute } from "./ProtectedRoute";
import { RutaAdmin } from "./RutaAdmin";
import { RutaLider } from "./RutaLider";

function AppRouter() {
  return (
    <Routes>
      {/* Rutas públicas */}
      <Route path="/" element={<Inicio />} />
      <Route path="/iniciarSesion" element={<IniciarSesion />} />
      <Route path="/registrarse" element={<Registrarse />} />

      {/* Rutas protegidas generales */}
      <Route element={<ProtectedRoute />}>
        <Route element={<AppLayout />}>
          <Route path="/panel" element={<Panel />} />
          <Route path="/tareas" element={<Tareas />} />
          <Route path="/perfil" element={<Perfil />} />
          <Route path="/calendario" element={<Calendario />} />
          <Route path="/estadisticas" element={<Estadisticas />} />
        </Route>
      </Route>

      {/* Ruta protegida exclusiva de líder */}
      <Route element={<RutaLider />}>
        <Route path="/lider" element={<Lider />} />
      </Route>

      {/* Ruta protegida exclusiva para administradores */}
      <Route element={<RutaAdmin />}>
        <Route path="/admin" element={<Admin />} />
      </Route>

      {/* Redirección por defecto si la ruta no existe */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

export default AppRouter;