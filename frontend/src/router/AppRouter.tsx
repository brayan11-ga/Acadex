// src/router/AppRouter.tsx
import { Routes, Route } from "react-router-dom";

// Páginas públicas
import Inicio from "../pages/LandingPage";
import IniciarSesion from "../pages/Login";
import Registrarse from "../pages/Register";

// Layout y páginas internas
import AppLayout from "../layouts/AppLayout";
import Tareas from "../pages/Tareas";

function AppRouter() {
  return (
    <Routes>
      {/* Rutas públicas */}
      <Route path="/" element={<Inicio />} />
      <Route path="/iniciarSesion" element={<IniciarSesion />} />
      <Route path="/registrarse" element={<Registrarse />} />

      {/* Rutas internas, todas comparten el sidebar de AppLayout */}
      <Route element={<AppLayout />}>
        <Route path="/tareas" element={<Tareas />} />
      </Route>
    </Routes>
  );
}

export default AppRouter;