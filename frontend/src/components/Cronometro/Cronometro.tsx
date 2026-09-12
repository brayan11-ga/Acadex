import { useState } from 'react';
import { useCronometro } from '../../hooks/useCronometro';
import { PixelHourglass } from './Pixelhourglass';
import '../../styles/Cronometro.css';

interface CronometroProps {
  idTarea: number;
  limiteSegundos?: number; //(default 25 min)
}

const formatearTiempo = (totalSegundos: number) => {
  const minutos = Math.floor(totalSegundos / 60);
  const segundos = totalSegundos % 60;
  return `${String(minutos).padStart(2, '0')}:${String(segundos).padStart(2, '0')}`;
};

export const Cronometro = ({ idTarea, limiteSegundos = 25 * 60 }: CronometroProps) => {
  const { segundos, corriendo, pausadoPorLimite, alternar, reiniciar } =
    useCronometro(idTarea, limiteSegundos);
  const [mostrarConfirmacion, setMostrarConfirmacion] = useState(false);

  const porcentajeLimite = Math.min(100, Math.round((segundos / limiteSegundos) * 100));

  const confirmarReinicio = () => {
    reiniciar();
    setMostrarConfirmacion(false);
  };

  return (
    <div className="cronometro-contenedor">
      {corriendo && <PixelHourglass />}

      <div className="cronometro-tiempo">{formatearTiempo(segundos)}</div>

      <p className="cronometro-estado">
        {corriendo
          ? 'Cronómetro activo'
          : pausadoPorLimite
          ? 'Pausado automáticamente (límite alcanzado)'
          : segundos > 0
          ? 'En pausa'
          : 'Cronómetro detenido'}
      </p>

      <div className="cronometro-barra-limite">
        <div className="cronometro-barra-relleno" style={{ width: `${porcentajeLimite}%` }} />
      </div>

      <div className="cronometro-acciones">
        <button type="button" className="pixel-btn-play" onClick={alternar}>
          <span className="icon">{corriendo ? '❚❚' : '▶'}</span>
          {corriendo ? 'Pausar' : 'Iniciar'}
        </button>
        <button
          type="button"
          className="pixel-btn-outline"
          onClick={() => setMostrarConfirmacion(true)}
          aria-label="Reiniciar cronómetro"
        >
          ↺
        </button>
      </div>

      {mostrarConfirmacion && (
        <div className="cronometro-confirmacion">
          <p>¿Reiniciar el tiempo acumulado a cero?</p>
          <div className="cronometro-confirmacion-acciones">
            <button type="button" className="pixel-btn-danger" onClick={confirmarReinicio}>
              Sí, reiniciar
            </button>
            <button
              type="button"
              className="pixel-btn-outline"
              onClick={() => setMostrarConfirmacion(false)}
            >
              Cancelar
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default Cronometro;