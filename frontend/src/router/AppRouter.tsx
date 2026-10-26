// Ruta: frontend/src/router/AppRouter.tsx
import { Routes, Route, Navigate } from "react-router-dom";
import Inicio from "../pages/LandingPage";
import IniciarSesion from "../pages/Login";
import Registrarse from "../pages/Register";
import AppLayout from "../layouts/AppLayout";
import Tareas from "../pages/Tareas";
import Perfil from "../pages/Perfil";
import { Panel } from "../pages/Panel";
import { Admin } from "../pages/Admin";
import Lider from "../pages/Lider";
import { Estadisticas } from "../pages/Estadisticas";
import { Calendario } from "../pages/Calendario";
import Grupos from "../pages/Grupos";
import TareasGrupoPage from "../pages/TareasGrupoPage";
import DetalleTareaGrupoPage from "../pages/DetalleTareaGrupoPage";
import GrupoIntegrantesPage from "../pages/GrupoIntegrantesPage";
import { ProtectedRoute } from "./ProtectedRoute";
import { RutaAdmin } from "./RutaAdmin";
import LegalInformation from "../pages/LegalInformation";
import OlvideContrasena from "../pages/OlvideContrasena";
import RestablecerContrasena from "../pages/RestablecerContrasena";

function AppRouter() {
  return (
    <Routes>
      {/* Rutas públicas */}
      <Route path="/" element={<Inicio />} />
      <Route path="/iniciarSesion" element={<IniciarSesion />} />
      <Route path="/olvide-contrasena" element={<OlvideContrasena />} />
      <Route path="/restablecer-contrasena" element={<RestablecerContrasena />} />
      <Route path="/registrarse" element={<Registrarse />} />
      <Route path="/politica-privacidad" element={<LegalInformation type="privacy" />} />
      <Route path="/politica-cookies" element={<LegalInformation type="cookies" />} />

      {/* Rutas protegidas generales */}
      <Route element={<ProtectedRoute />}>
        <Route element={<AppLayout />}>
          <Route path="/panel" element={<Panel />} />
          <Route path="/tareas" element={<Tareas />} />
          <Route path="/perfil" element={<Perfil />} />
          <Route path="/calendario" element={<Calendario />} />
          <Route path="/estadisticas" element={<Estadisticas />} />
          <Route path="/grupos" element={<Grupos />} />
          <Route path="/grupos/:idGrupo/tareas" element={<TareasGrupoPage />} />
          <Route
            path="/grupos/:idGrupo/tareas/:idTarea"
            element={<DetalleTareaGrupoPage />}
          />
          <Route path="/grupos/:idGrupo" element={<GrupoIntegrantesPage />} />
          <Route path="/grupos/:idGrupo/lider" element={<Lider />} />
        </Route>
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
