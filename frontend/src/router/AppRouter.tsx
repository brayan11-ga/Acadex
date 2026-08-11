import { Routes, Route } from "react-router-dom";

// Importar páginas
import Inicio from "../pages/LandingPage";
import IniciarSesion from "../pages/Login";

function AppRouter () {
    return(
        <Routes>
        <Route path="/" element={<Inicio />} />
        <Route path="/iniciarSesion" element={<IniciarSesion />} />
        </Routes>
    );
}

export default AppRouter;