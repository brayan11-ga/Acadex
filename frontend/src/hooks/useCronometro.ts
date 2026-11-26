import { useEffect, useState } from 'react';

interface EstadoPersistido {
  segundosAcumulados: number;
  corriendo: boolean;
  ultimaMarcaTiempo: number | null;
}

const construirClave = (idTarea: number) => `cronometro:tarea:${idTarea}`;

const persistirEstado = (idTarea: number, estado: EstadoPersistido) => {
  try {
    localStorage.setItem(construirClave(idTarea), JSON.stringify(estado));
  } catch {
  }
};

// Al montar o cambiar de tarea: recuperar estado guardado y
// sumar el tiempo que pasó mientras la app estuvo cerrada (si estaba corriendo)
function recuperarEstado(idTarea: number, limiteSegundos: number) {
  let segundos = 0;
  let corriendo = false;

  try {
    const guardado = localStorage.getItem(construirClave(idTarea));
    if (guardado) {
      const estado: EstadoPersistido = JSON.parse(guardado);
      segundos = estado.segundosAcumulados;
      corriendo = estado.corriendo;
      if (corriendo && estado.ultimaMarcaTiempo) {
        const transcurrido = Math.floor((Date.now() - estado.ultimaMarcaTiempo) / 1000);
        segundos += Math.max(0, transcurrido);
      }
    }
  } catch {
  }

  const pausadoPorLimite = segundos >= limiteSegundos;
  return {
    idTarea,
    limiteSegundos,
    segundos: pausadoPorLimite ? limiteSegundos : segundos,
    corriendo: corriendo && !pausadoPorLimite,
    pausadoPorLimite,
    tickPendiente: null as EstadoPersistido | null,
  };
}

export function useCronometro(idTarea: number, limiteSegundos = 25 * 60) {
  const [estado, setEstado] = useState(() => recuperarEstado(idTarea, limiteSegundos));
  const { segundos, corriendo, pausadoPorLimite, tickPendiente } = estado;

  if (!Object.is(estado.idTarea, idTarea) || !Object.is(estado.limiteSegundos, limiteSegundos)) {
    setEstado(recuperarEstado(idTarea, limiteSegundos));
  }

  useEffect(() => {
    if (tickPendiente) persistirEstado(idTarea, tickPendiente);
  }, [idTarea, tickPendiente]);

  // Tick del cronómetro mientras está corriendo
  useEffect(() => {
    if (!corriendo) return;

    const intervalo = window.setInterval(() => {
      const marca = Date.now();
      setEstado((previo) => {
        if (!previo.corriendo || !Object.is(previo.idTarea, idTarea) || !Object.is(previo.limiteSegundos, limiteSegundos)) {
          return previo;
        }
        const siguiente = previo.segundos + 1;
        const alcanzoLimite = siguiente >= limiteSegundos;
        return {
          ...previo,
          segundos: siguiente,
          corriendo: !alcanzoLimite,
          pausadoPorLimite: alcanzoLimite,
          tickPendiente: {
            segundosAcumulados: siguiente,
            corriendo: !alcanzoLimite,
            ultimaMarcaTiempo: alcanzoLimite ? null : marca,
          },
        };
      });
    }, 1000);

    return () => window.clearInterval(intervalo);
  }, [corriendo, idTarea, limiteSegundos]);

  const iniciar = () => {
    if (segundos >= limiteSegundos) return;
    setEstado((previo) => ({ ...previo, pausadoPorLimite: false, corriendo: true, tickPendiente: null }));
    persistirEstado(idTarea, {
      segundosAcumulados: segundos,
      corriendo: true,
      ultimaMarcaTiempo: Date.now(),
    });
  };

  const pausar = () => {
    setEstado((previo) => ({ ...previo, corriendo: false, tickPendiente: null }));
    persistirEstado(idTarea, {
      segundosAcumulados: segundos,
      corriendo: false,
      ultimaMarcaTiempo: null,
    });
  };

  const alternar = () => (corriendo ? pausar() : iniciar());

  const reiniciar = () => {
    setEstado((previo) => ({
      ...previo,
      segundos: 0,
      corriendo: false,
      pausadoPorLimite: false,
      tickPendiente: null,
    }));
    persistirEstado(idTarea, {
      segundosAcumulados: 0,
      corriendo: false,
      ultimaMarcaTiempo: null,
    });
  };

  return {
    segundos,
    corriendo,
    pausadoPorLimite,
    limiteSegundos,
    iniciar,
    pausar,
    alternar,
    reiniciar,
  };
}
