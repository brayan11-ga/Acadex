// src/components/tareas/FormularioNuevaTarea.tsx
import { useState, useEffect } from "react";
import caraNivel1 from "../../assets/icons/dificultad/1.png";
import caraNivel2 from "../../assets/icons/dificultad/2.png";
import caraNivel3 from "../../assets/icons/dificultad/3.png";
import caraNivel4 from "../../assets/icons/dificultad/4.png";
import caraNivel5 from "../../assets/icons/dificultad/5.png";
import iconoCategorias from "../../assets/icons/ui/categorias.png";
import iconoCalendario from "../../assets/icons/ui/calendario.png";
import iconoReloj from "../../assets/icons/ui/reloj.png";
import { listarCategorias, type Categoria } from "../../services/categorias";
import { crearTarea } from "../../services/tareas";

const NIVELES_DIFICULTAD = [
  { nivel: 1, icono: caraNivel1, etiqueta: "Muy fácil" },
  { nivel: 2, icono: caraNivel2, etiqueta: "Fácil" },
  { nivel: 3, icono: caraNivel3, etiqueta: "Moderada" },
  { nivel: 4, icono: caraNivel4, etiqueta: "Difícil" },
  { nivel: 5, icono: caraNivel5, etiqueta: "Muy difícil" },
];

interface FormularioProps {
  onDescartar: () => void;
  onTareaCreada: () => void; // avisa al padre para refrescar la lista
}

function FormularioNuevaTarea({ onDescartar, onTareaCreada }: FormularioProps) {
  const [categorias, setCategorias] = useState<Categoria[]>([]);
  const [titulo, setTitulo] = useState("");
  const [idCategoria, setIdCategoria] = useState<number | null>(null);
  const [fecha, setFecha] = useState("");
  const [dificultad, setDificultad] = useState(3);
  const [tiempoEstimado, setTiempoEstimado] = useState("");
  const [descripcion, setDescripcion] = useState("");
  const [enviando, setEnviando] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const nivelActual = NIVELES_DIFICULTAD.find((n) => n.nivel === dificultad)!;

  // Al montar el componente, traemos las categorías reales de la BD
  useEffect(() => {
    listarCategorias()
      .then((datos) => {
        setCategorias(datos);
        if (datos.length > 0) setIdCategoria(datos[0].id_categoria);
      })
      .catch(() => setError("No se pudieron cargar las categorías"));
  }, []);

  const manejarEnvio = async (evento: React.FormEvent) => {
    evento.preventDefault();
    setError(null);

    if (!titulo.trim() || !fecha || idCategoria === null) {
      setError("Completa título, fecha y categoría");
      return;
    }

    setEnviando(true);
    try {
      await crearTarea({
        nombre: titulo,
        descripcion,
        fecha_entrega: `${fecha}T00:00:00`, // el input date solo da la fecha; completamos la hora
        dificultad_estimada: dificultad,
        tiempo_estimado: Number(tiempoEstimado) || 0,
        id_categoria: idCategoria,
        id_usuario: 1, // TODO: reemplazar por el id del usuario logueado
      });
      onTareaCreada();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error al crear la tarea");
    } finally {
      setEnviando(false);
    }
  };

  return (
    <form className="pixel-panel" onSubmit={manejarEnvio}>
      <div className="pixel-panel-header">
        <div>
          <h2 className="pixel-panel-title">Nueva tarea</h2>
          <p className="pixel-panel-subtitle">Define el objetivo de tu próxima sesión</p>
        </div>
        <button type="button" className="pixel-link-descartar" onClick={onDescartar}>
          × Descartar
        </button>
      </div>

      {error && <p className="pixel-error">{error}</p>}

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
            value={idCategoria ?? ""}
            onChange={(e) => setIdCategoria(Number(e.target.value))}
          >
            {categorias.map((cat) => (
              <option key={cat.id_categoria} value={cat.id_categoria}>
                {cat.nombre}
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
        <button type="submit" className="pixel-btn-crear-tarea" disabled={enviando}>
          {enviando ? "Creando..." : "Crear →"}
        </button>
      </div>
    </form>
  );
}

export default FormularioNuevaTarea;