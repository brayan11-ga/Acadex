import { useState } from 'react';
import { useCronometro } from '../../hooks/useCronometro';
import { PixelHourglass } from './PixelHourglass';
import '../../styles/Cronometro.css';

interface CronometroProps {
  idTarea: number;
}

const formatearTiempo = (totalSegundos: number) => {
  const minutos = Math.floor(totalSegundos / 60);
  const segundos = totalSegundos % 60;
  return `${String(minutos).padStart(2, '0')}:${String(segundos).padStart(2, '0')}`;
};

export const Cronometro = ({ idTarea }: CronometroProps) => {
  const {
    segundos, corriendo, cargando, error, pausadoPorLimite,
    segundosGracia, limiteSegundos, alternar, confirmar, reiniciar,
  } = useCronometro(idTarea);
  const [mostrarConfirmacion, setMostrarConfirmacion] = useState(false);

  const confirmarReinicio = () => {
    void reiniciar();
    setMostrarConfirmacion(false);
  };

  const hayAviso = segundosGracia !== null;

  return (
    <div className="cronometro-contenedor">
      {corriendo && <PixelHourglass />}

      <div className="cronometro-tiempo">{formatearTiempo(segundos)}</div>

      <p className="cronometro-estado">
        {corriendo
          ? hayAviso
            ? '¿Sigues trabajando?'
            : 'Cronómetro activo'
          : pausadoPorLimite
          ? 'Pausado automáticamente por inactividad'
          : segundos > 0
          ? 'En pausa'
          : 'Cronómetro detenido'}
      </p>

      {error && <p className="pixel-error">{error}</p>}

      {hayAviso && (
        <div className="cronometro-confirmacion" role="alert">
          <p>
            Llevas {formatearTiempo(limiteSegundos)} seguidos. Se pausara en{' '}
            {formatearTiempo(segundosGracia)}.
          </p>
          <button type="button" className="pixel-btn-play" onClick={() => void confirmar()}>
            Sigo trabajando
          </button>
        </div>
      )}

      <div className="cronometro-acciones">
        <button
          type="button"
          className="pixel-btn-play"
          onClick={() => void alternar()}
          disabled={cargando}
        >
          <span className="icon">{corriendo ? '❚❚' : '▶'}</span>
          {corriendo ? 'Pausar' : 'Iniciar'}
        </button>
        <button
          type="button"
          className="pixel-btn-outline"
          onClick={() => setMostrarConfirmacion(true)}
          disabled={cargando}
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