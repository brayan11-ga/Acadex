import { Routes, Route } from "react-router-dom";

// Importar páginas
import Inicio from "../pages/LandingPage";
import IniciarSesion from "../pages/Login";
import Registrarse from "../pages/Register";
import Tareas from "../pages/Tareas";
import DetalleTarea from "../pages/DetalleTarea";

function AppRouter() {
return (
<Routes>
<Route path="/" element={<Inicio />} />
<Route path="/iniciarSesion" element={<IniciarSesion />} />
<Route path="/registrarse" element={<Registrarse />} />

        {/* Tareas */}
        <Route path="/tareas" element={<Tareas />} />
        <Route path="/tareas/:id" element={<DetalleTarea />} />
    </Routes>
);

}

export default AppRouter;