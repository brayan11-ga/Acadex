import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { obtenerMiPerfil, type PerfilBackend } from "../services/perfil";

export function usePerfilActual() {
  const [perfil, setPerfil] = useState<PerfilBackend | null>(null);
  const [errorServidorCaido, setErrorServidorCaido] = useState(false);
  const token = localStorage.getItem("access_token");
  const navigate = useNavigate();

  useEffect(() => {
    if (!token) {
      setPerfil(null);
      setErrorServidorCaido(false);
      return;
    }

    let cancelado = false;

    obtenerMiPerfil()
      .then((datos) => {
        if (cancelado) return;
        setPerfil(datos);
        setErrorServidorCaido(false);
      })
      .catch((error: unknown) => {
        if (cancelado) return;

        console.error("Error al cargar perfil:", error);
        const mensaje = error instanceof Error ? error.message : "";

        if (mensaje.includes("401")) {
          localStorage.removeItem("access_token");
          navigate("/iniciarSesion");
        } else if (mensaje.includes("Failed to fetch")) {
          setErrorServidorCaido(true);
        } else {
          setErrorServidorCaido(false);
        }
      });

    return () => {
      cancelado = true;
    };
  }, [token, navigate]);

  return { perfil, errorServidorCaido };
}
