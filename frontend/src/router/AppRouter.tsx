import { Routes, Route } from "react-router-dom";

// Importar páginas
import Inicio from "../pages/LandingPage";
import IniciarSesion from "../pages/Login";
import Registrarse from "../pages/Register";

function AppRouter () {
    return(
        <Routes>
        <Route path="/" element={<Inicio />} />
        <Route path="/iniciarSesion" element={<IniciarSesion />} />
        <Route path="/registrarse" element={<Registrarse />} />
        </Routes>
    );
}

export default AppRouter;