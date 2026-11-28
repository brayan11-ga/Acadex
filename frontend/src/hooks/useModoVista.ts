import { useState } from "react";
import type { ModoVista } from "../components/ui/ToggleVista";

export function useModoVista(clave: string, inicial: ModoVista = "lista") {
    const [modo, setModo] = useState<ModoVista>(() => {
    try {
        const guardado = localStorage.getItem(clave);
        return guardado === "lista" || guardado === "cuadricula" ? guardado : inicial;
    } catch {
        return inicial;
    }
    });

    const cambiar = (nuevo: ModoVista) => {
    setModo(nuevo);
    try {
        localStorage.setItem(clave, nuevo);
    } catch {
      /* sin almacenamiento: la vista solo dura la sesión */
    }
    };

    return [modo, cambiar] as const;
}