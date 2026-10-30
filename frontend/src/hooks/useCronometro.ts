import { useCallback, useEffect, useRef, useState } from "react";
import {
  confirmarContinuar,
  iniciarSesion,
  obtenerEstadoCronometro,
  pausarSesion,
  reiniciarCronometro,
  verificarLimite,
  type EstadoCronometroTarea,
} from "../services/sesionesCronometro";
import { sonarAlarma } from "../utils/alarma";

const INTERVALO_VERIFICACION_MS = 30_000;
const mensajeDe = (e: unknown, defecto: string) =>
  e instanceof Error ? e.message : defecto;

export function useCronometro(idTarea: number) {
  const [segundos, setSegundos] = useState(0);
  const [limiteSegundos, setLimiteSegundos] = useState(0);
  const [idSesion, setIdSesion] = useState<number | null>(null);
  const [pausadoPorLimite, setPausadoPorLimite] = useState(false);
  const [segundosGracia, setSegundosGracia] = useState<number | null>(null);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const avisoSonado = useRef(false);
  const ventanaRef = useRef(0);
  const limiteRef = useRef(0);
  
  const corriendo = idSesion !== null;

  const aplicarEstado = useCallback((e: EstadoCronometroTarea) => {
    setSegundos(e.segundos_acumulados + e.segundos_sesion_actual);
    setLimiteSegundos(e.limite_segundos);
    setIdSesion(e.sesion?.id_sesion ?? null);
    ventanaRef.current = e.sesion ? e.segundos_ventana : 0;
    limiteRef.current = e.limite_segundos;
  }, []);

  

  const cargar = useCallback(async () => {
    const estado = await obtenerEstadoCronometro(idTarea);
    aplicarEstado(estado);
    return estado;
  }, [idTarea, aplicarEstado]);

  const revisar = useCallback(
    async (id: number) => {
      const r = await verificarLimite(id);
      if (r.estado === "aviso") {
        setSegundosGracia(r.segundos_gracia_restantes);
        if (!avisoSonado.current) {
          avisoSonado.current = true;
          sonarAlarma();
        }
        return;
      }
      setSegundosGracia(null);
      avisoSonado.current = false;
      if (r.estado === "pausada_automaticamente") {
        setPausadoPorLimite(true);
        sonarAlarma();
        await cargar();
      } else if (r.estado === "cerrada") {
        await cargar();
      }
    },
    [cargar]
  );

  // Carga inicial (y al cambiar de tarea). Si ya hay una sesión abierta, se revisa el límite de una vez.
  useEffect(() => {
    let vigente = true;
    try {
      localStorage.removeItem(`cronometro:tarea:${idTarea}`); // limpia el estado viejo local
    } catch {
      // sin acceso a localStorage
    }

    const iniciarCarga = async () => {
      setCargando(true);
      setError(null);
      setPausadoPorLimite(false);
      setSegundosGracia(null);
      avisoSonado.current = false;
      try {
        const estado = await cargar();
        if (vigente && estado.sesion) await revisar(estado.sesion.id_sesion);
      } catch (e) {
        if (vigente) setError(mensajeDe(e, "No se pudo cargar el cronómetro"));
      } finally {
        if (vigente) setCargando(false);
      }
    };
    void iniciarCarga();

    return () => {
      vigente = false;
    };
  }, [idTarea, cargar, revisar]);

  // Avance visual por segundo mientras hay una sesión abierta
  useEffect(() => {
    if (!corriendo || idSesion===null) return;
    const id = window.setInterval(() => {
      const limite=limiteRef.current;
      if (limite>0 && ventanaRef.current >=limite) return;//congela el limite
      ventanaRef.current+=1;
      setSegundos((s) => s + 1);
      setSegundosGracia((g) => (g === null ? null : Math.max(0, g - 1)));

      const avisoEn=limite- Math.min(60,Math.floor(limite/2));
      if (limite>0 && (ventanaRef.current ===avisoEn || ventanaRef.current>=limite)){
        window.setTimeout(()=>{
          revisar(idSesion).catch((e)=>
          setError(mensajeDe(e,"no se pudo verificar el limite"))
        );
        },1000);
      }
    }, 1000);
    return () => window.clearInterval(id);
  }, [corriendo, idSesion, revisar]);

  // Consulta periódica del límite al backend
  useEffect(() => {
    if (idSesion === null) return;
    const id = window.setInterval(() => {
      revisar(idSesion).catch((e) =>
        setError(mensajeDe(e, "No se pudo verificar el límite"))
      );
    }, INTERVALO_VERIFICACION_MS);
    return () => window.clearInterval(id);
  }, [idSesion, revisar]);

  const ejecutar = async (accion: () => Promise<void>, defecto: string) => {
    setError(null);
    try {
      await accion();
    } catch (e) {
      setError(mensajeDe(e, defecto));
    }
  };

  const iniciar = () =>
    ejecutar(async () => {
      setPausadoPorLimite(false);
      const sesion = await iniciarSesion(idTarea);
      setIdSesion(sesion.id_sesion);
    }, "No se pudo iniciar el cronómetro");

  const pausar = () =>
    ejecutar(async () => {
      if (idSesion === null) return;
      await pausarSesion(idSesion);
      setSegundosGracia(null);
      avisoSonado.current = false;
      await cargar(); // sincroniza con lo que guardó el backend
    }, "No se pudo pausar el cronómetro");

  const alternar = () => (corriendo ? pausar() : iniciar());
  
  const confirmar = () =>
    ejecutar(async () => {
      if (idSesion === null) return;
      await confirmarContinuar(idSesion);
      setSegundosGracia(null);
      avisoSonado.current = false;
    }, "No se pudo confirmar");

  const reiniciar = () =>
    ejecutar(async () => {
      const estado = await reiniciarCronometro(idTarea);
      aplicarEstado(estado);
      setPausadoPorLimite(false);
      setSegundosGracia(null);
      avisoSonado.current = false;
    }, "No se pudo reiniciar el cronómetro");

  return {
    segundos,
    corriendo,
    cargando,
    error,
    pausadoPorLimite,
    segundosGracia,
    limiteSegundos,
    alternar,
    confirmar,
    reiniciar,
  };
}