// src/components/tareas/FormularioNuevaTarea.tsx
import { useState } from "react";

const CATEGORIAS = ["Backend", "Frontend", "Diseño", "Documentación"];
const NIVELES_DIFICULTAD = [1, 2, 3, 4, 5];
const ETIQUETAS_DIFICULTAD: Record<number, string> = {
  1: "Muy fácil",
  2: "Fácil",
  3: "Moderada",
  4: "Difícil",
  5: "Muy difícil",
};

const colorDificultad = (nivel: number) => {
  if (nivel <= 2) return "baja";
  if (nivel === 3) return "media";
  return "alta";
};

function FormularioNuevaTarea() {
  const [titulo, setTitulo] = useState("");
  const [categoria, setCategoria] = useState(CATEGORIAS[0]);
  const [fecha, setFecha] = useState("");
  const [dificultad, setDificultad] = useState(3);
  const [tiempoEstimado, setTiempoEstimado] = useState("");
  const [descripcion, setDescripcion] = useState("");

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
        <button type="button" className="pixel-link-descartar">
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
          <span className="pixel-field-label">Categoría</span>
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
          <span className="pixel-field-label">Fecha de entrega</span>
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
              {NIVELES_DIFICULTAD.map((nivel) => (
                <button
                  key={nivel}
                  type="button"
                  className={
                    dificultad === nivel
                      ? "pixel-dificultad-btn active"
                      : "pixel-dificultad-btn"
                  }
                  onClick={() => setDificultad(nivel)}
                >
                  {nivel}
                </button>
              ))}
            </div>
            <span className={`pixel-dificultad-hint hint-${colorDificultad(dificultad)}`}>
              {ETIQUETAS_DIFICULTAD[dificultad]}
            </span>
          </div>
        </div>

        <label className="pixel-field">
          <span className="pixel-field-label">Tiempo estimado (min)</span>
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