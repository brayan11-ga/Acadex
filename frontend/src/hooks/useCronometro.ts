import { useEffect, useRef, useState } from 'react';

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

export function useCronometro(idTarea: number, limiteSegundos = 25 * 60) {
  const [segundos, setSegundos] = useState(0);
  const [corriendo, setCorriendo] = useState(false);
  const [pausadoPorLimite, setPausadoPorLimite] = useState(false);
  const intervaloRef = useRef<number | null>(null);

  // Al montar o cambiar de tarea: recuperar estado guardado y
  // sumar el tiempo que pasó mientras la app estuvo cerrada (si estaba corriendo)
  useEffect(() => {
    let segundosBase = 0;
    let corriendoBase = false;

    try {
      const guardado = localStorage.getItem(construirClave(idTarea));
      if (guardado) {
        const estado: EstadoPersistido = JSON.parse(guardado);
        segundosBase = estado.segundosAcumulados;
        corriendoBase = estado.corriendo;
        if (estado.corriendo && estado.ultimaMarcaTiempo) {
          const transcurridoMientrasCerrado = Math.floor(
            (Date.now() - estado.ultimaMarcaTiempo) / 1000
          );
          segundosBase += Math.max(0, transcurridoMientrasCerrado);
        }
      }
    } catch {
    }

    if (segundosBase >= limiteSegundos) {
      segundosBase = limiteSegundos;
      corriendoBase = false;
      setPausadoPorLimite(true);
    } else {
      setPausadoPorLimite(false);
    }

    setSegundos(segundosBase);
    setCorriendo(corriendoBase);
  }, [idTarea, limiteSegundos]);

  // Tick del cronómetro mientras está corriendo
  useEffect(() => {
    if (!corriendo) return;

    intervaloRef.current = window.setInterval(() => {
      setSegundos((previo) => {
        const siguiente = previo + 1;

        if (siguiente >= limiteSegundos) {
          setCorriendo(false);
          setPausadoPorLimite(true);
          persistirEstado(idTarea, {
            segundosAcumulados: siguiente,
            corriendo: false,
            ultimaMarcaTiempo: null,
          });
          return siguiente;
        }

        persistirEstado(idTarea, {
          segundosAcumulados: siguiente,
          corriendo: true,
          ultimaMarcaTiempo: Date.now(),
        });
        return siguiente;
      });
    }, 1000);

    return () => {
      if (intervaloRef.current) {
        clearInterval(intervaloRef.current);
        intervaloRef.current = null;
      }
    };
  }, [corriendo, idTarea, limiteSegundos]);

  const iniciar = () => {
    if (segundos >= limiteSegundos) return;
    setPausadoPorLimite(false);
    setCorriendo(true);
    persistirEstado(idTarea, {
      segundosAcumulados: segundos,
      corriendo: true,
      ultimaMarcaTiempo: Date.now(),
    });
  };

  const pausar = () => {
    setCorriendo(false);
    persistirEstado(idTarea, {
      segundosAcumulados: segundos,
      corriendo: false,
      ultimaMarcaTiempo: null,
    });
  };

  const alternar = () => (corriendo ? pausar() : iniciar());

  const reiniciar = () => {
    setSegundos(0);
    setCorriendo(false);
    setPausadoPorLimite(false);
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