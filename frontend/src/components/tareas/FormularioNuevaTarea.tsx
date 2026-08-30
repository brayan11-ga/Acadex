// src/components/tareas/FormularioNuevaTarea.tsx
import { useState } from "react";
import caraNivel1 from "../../assets/icons/dificultad/1.png";
import caraNivel2 from "../../assets/icons/dificultad/2.png";
import caraNivel3 from "../../assets/icons/dificultad/3.png";
import caraNivel4 from "../../assets/icons/dificultad/4.png";
import caraNivel5 from "../../assets/icons/dificultad/5.png";
import iconoCategorias from "../../assets/icons/ui/categorias.png";
import iconoCalendario from "../../assets/icons/ui/calendario.png";
import iconoReloj from "../../assets/icons/ui/reloj.png";

const CATEGORIAS = ["Backend", "Frontend", "Diseño", "Documentación"];

const NIVELES_DIFICULTAD = [
  { nivel: 1, icono: caraNivel1, etiqueta: "Muy fácil" },
  { nivel: 2, icono: caraNivel2, etiqueta: "Fácil" },
  { nivel: 3, icono: caraNivel3, etiqueta: "Moderada" },
  { nivel: 4, icono: caraNivel4, etiqueta: "Difícil" },
  { nivel: 5, icono: caraNivel5, etiqueta: "Muy difícil" },
];

// 1. Definimos la interfaz para que TypeScript reconozca la prop
interface FormularioProps {
  onDescartar: () => void;
}

// 2. Agregamos la prop al componente
function FormularioNuevaTarea({ onDescartar }: FormularioProps) {
  const [titulo, setTitulo] = useState("");
  const [categoria, setCategoria] = useState(CATEGORIAS[0]);
  const [fecha, setFecha] = useState("");
  const [dificultad, setDificultad] = useState(3);
  const [tiempoEstimado, setTiempoEstimado] = useState("");
  const [descripcion, setDescripcion] = useState("");

  const nivelActual = NIVELES_DIFICULTAD.find((n) => n.nivel === dificultad)!;

  const manejarEnvio = (evento: React.FormEvent) => {
    evento.preventDefault();
    console.log({ titulo, categoria, fecha, dificultad, tiempoEstimado, descripcion });
  };

  return (
    <form className="pixel-panel" onSubmit={manejarEnvio}>
      <div className="pixel-panel-header">
        <div>
          <h2 className="pixel-panel-title">Nueva tarea</h2>
          <p className="pixel-panel-subtitle">Define el objetivo de tu próxima sesión</p>
        </div>
        {/* 3. Conectamos la prop al evento onClick del botón */}
        <button type="button" className="pixel-link-descartar" onClick={onDescartar}>
          × Descartar
        </button>
      </div>

      <label className="pixel-field">
        <span className="pixel-field-label">Título</span>
        <input
          type="text"
          className="pixel-input"
          placeholder="¿Qué hay que hacer?"
          value={titulo}
          onChange={(e) => setTitulo(e.target.value)}
        />
      </label>

      <div className="pixel-field-row">
        <label className="pixel-field">
          <span className="pixel-field-label">
            <img src={iconoCategorias} alt="" className="pixel-field-icono" />
            Categoría
          </span>
          <select
            className="pixel-input"
            value={categoria}
            onChange={(e) => setCategoria(e.target.value)}
          >
            {CATEGORIAS.map((cat) => (
              <option key={cat} value={cat}>
                {cat}
              </option>
            ))}
          </select>
        </label>

        <label className="pixel-field">
          <span className="pixel-field-label">
            <img src={iconoCalendario} alt="" className="pixel-field-icono" />
            Fecha de entrega
          </span>
          <input
            type="date"
            className="pixel-input"
            value={fecha}
            onChange={(e) => setFecha(e.target.value)}
          />
        </label>
      </div>

      <div className="pixel-field-row">
        <div className="pixel-field">
          <span className="pixel-field-label">Dificultad estimada</span>
          <div className="pixel-dificultad-row">
            <div className="pixel-dificultad-group">
              {NIVELES_DIFICULTAD.map(({ nivel, icono }) => (
                <button
                  key={nivel}
                  type="button"
                  aria-label={`Dificultad ${nivel}`}
                  className={
                    dificultad === nivel
                      ? `pixel-dificultad-btn nivel-${nivel} active`
                      : `pixel-dificultad-btn nivel-${nivel}`
                  }
                  onClick={() => setDificultad(nivel)}
                >
                  <img src={icono} alt="" className="pixel-dificultad-icono" />
                </button>
              ))}
            </div>
            <span className={`pixel-dificultad-hint nivel-${dificultad}`}>
              {nivelActual.etiqueta}
            </span>
          </div>
        </div>

        <label className="pixel-field">
          <span className="pixel-field-label">
            <img src={iconoReloj} alt="" className="pixel-field-icono" />
            Tiempo estimado (min)
          </span>
          <input
            type="number"
            min="1"
            className="pixel-input"
            placeholder="120"
            value={tiempoEstimado}
            onChange={(e) => setTiempoEstimado(e.target.value)}
          />
        </label>
      </div>

      <label className="pixel-field pixel-field-grow">
        <span className="pixel-field-label">Descripción</span>
        <textarea
          className="pixel-input pixel-textarea"
          placeholder="Detalla los objetivos y restricciones..."
          value={descripcion}
          onChange={(e) => setDescripcion(e.target.value)}
        />
      </label>

      <div className="pixel-panel-footer">
        <button type="submit" className="pixel-btn-crear-tarea">
          Crear →
        </button>
      </div>
    </form>
  );
}

export default FormularioNuevaTarea;