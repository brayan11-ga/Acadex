import { Routes, Route } from "react-router-dom";

// Importar páginas
import Inicio from "../pages/LandingPage";
import IniciarSesion from "../pages/Login";
<<<<<<< Updated upstream
import Registrarse from "../pages/register";
=======
import Registrarse from "../pages/Register";
import Tareas from "../pages/Tareas";
>>>>>>> Stashed changes

function AppRouter () {
    return(
        <Routes>
        <Route path="/" element={<Inicio />} />
        <Route path="/iniciarSesion" element={<IniciarSesion />} />
        <Route path="/registrarse" element={<Registrarse />} />
        <Route path="/tareas" element={<Tareas />} />
        </Routes>
    );
}

export default AppRouter;