import { Routes, Route } from "react-router-dom";
import Inicio from "../pages/LandingPage";
import IniciarSesion from "../pages/Login";
import Registrarse from "../pages/Register";
import AppLayout from "../layouts/AppLayout";
import Tareas from "../pages/Tareas";
import { Panel } from "../pages/Panel";
import { RutaAdmin } from "./RutaAdmin";
import { AdminPage } from "../pages/Admin";

function AppRouter() {
  return (
    <Routes>
      {/* Rutas públicas */}
      <Route path="/" element={<Inicio />} />
      <Route path="/iniciarSesion" element={<IniciarSesion />} />
      <Route path="/registrarse" element={<Registrarse />} />

      {/* Rutas internas normales */}
      <Route element={<AppLayout />}>
        <Route path="/panel" element={<Panel />} />
        <Route path="/tareas" element={<Tareas />} />
      </Route>

      {/* Ruta protegida solo para admins */}
      <Route element={<RutaAdmin />}>
        <Route path="/admin" element={<AdminPage />} />
      </Route>
    </Routes>
  );
}

export default AppRouter;