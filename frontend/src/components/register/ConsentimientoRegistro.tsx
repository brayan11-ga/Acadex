import { Link } from 'react-router-dom';

interface ConsentimientoRegistroProps {
  aceptaTratamiento: boolean;
  confirmaAviso: boolean;
  onTratamientoChange: (value: boolean) => void;
  onAvisoChange: (value: boolean) => void;
}

export default function ConsentimientoRegistro({
  aceptaTratamiento,
  confirmaAviso,
  onTratamientoChange,
  onAvisoChange,
}: ConsentimientoRegistroProps) {
  return (
    <fieldset className="register-consents">
      <legend>Privacidad y datos</legend>
      <label className="register-consent-option">
        <input
          type="checkbox"
          checked={aceptaTratamiento}
          onChange={(event) => onTratamientoChange(event.target.checked)}
          required
        />
        <span>
          Leí la <Link to="/politica-privacidad" target="_blank" rel="noopener noreferrer">Política de tratamiento de datos</Link> y autorizo el uso de mis datos para operar mi cuenta.
        </span>
      </label>
      <label className="register-consent-option">
        <input
          type="checkbox"
          checked={confirmaAviso}
          onChange={(event) => onAvisoChange(event.target.checked)}
          required
        />
        <span>
          Leí el <Link to="/politica-cookies" target="_blank" rel="noopener noreferrer">aviso de cookies y almacenamiento local</Link>.
        </span>
      </label>
    </fieldset>
  );
}
