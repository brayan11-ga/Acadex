import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { obtenerMiPerfil, type PerfilBackend } from "../services/perfil";

export function usePerfilActual() {
  const [resultado, setResultado] = useState<{
    token: string;
    perfil: PerfilBackend | null;
    errorServidorCaido: boolean;
  } | null>(null);
  const token = localStorage.getItem("access_token");
  const navigate = useNavigate();

  if (resultado && resultado.token !== token) setResultado(null);

  useEffect(() => {
    if (!token) return;

    let cancelado = false;

    obtenerMiPerfil()
      .then((datos) => {
        if (cancelado) return;
        setResultado({ token, perfil: datos, errorServidorCaido: false });
      })
      .catch((error: unknown) => {
        if (cancelado) return;

        console.error("Error al cargar perfil:", error);
        const mensaje = error instanceof Error ? error.message : "";

        if (mensaje.includes("401")) {
          localStorage.removeItem("access_token");
          navigate("/iniciarSesion");
        } else {
          setResultado((anterior) => ({
            token,
            perfil: anterior?.token === token ? anterior.perfil : null,
            errorServidorCaido: mensaje.includes("Failed to fetch"),
          }));
        }
      });

    return () => {
      cancelado = true;
    };
  }, [token, navigate]);

  const resultadoActual = resultado?.token === token ? resultado : null;
  return {
    perfil: resultadoActual?.perfil ?? null,
    errorServidorCaido: resultadoActual?.errorServidorCaido ?? false,
  };
}
