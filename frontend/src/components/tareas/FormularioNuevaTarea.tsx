// Ruta: frontend/src/components/tareas/FormularioNuevaTarea.tsx
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
import {
  crearTarea,
  crearTareaConPdf,
  actualizarTarea,
  analizarDocumentoIA,
  subirArchivoTarea,
  crearTareaGrupal,
  type TareaBackend,
} from "../../services/tareas";
import { SeccionAdjuntosTarea } from "./SeccionAdjuntosTarea";
import { SelectorArchivosPendientes } from "./SelectorArchivosPendientes";
import { adjuntosHabilitados } from "../../config/featureFlags";
import {
  claveArchivo,
  TAMANO_MAXIMO_ADJUNTO,
} from "./validacionArchivosTarea";
import AsignarIntegrantes, {
  validarAsignados,
} from "../tareas-grupo/AsignarIntegrantes";
import type { IntegranteAsignable } from "../../types/tareaGrupo";

const NIVELES_DIFICULTAD = [
  { nivel: 1, icono: caraNivel1, etiqueta: "Muy fácil" },
  { nivel: 2, icono: caraNivel2, etiqueta: "Fácil" },
  { nivel: 3, icono: caraNivel3, etiqueta: "Moderada" },
  { nivel: 4, icono: caraNivel4, etiqueta: "Difícil" },
  { nivel: 5, icono: caraNivel5, etiqueta: "Muy difícil" },
];

interface FormularioProps {
  onDescartar: () => void;
  onTareaCreada: () => void;
  tareaAEditar?: TareaBackend | null;
  modo?: "individual" | "grupal";
  idGrupo?: number;
  integrantes?: IntegranteAsignable[];
  usuarioActualId?: number | null;
  embebidoEnModal?: boolean;
  enviandoExterno?: boolean;
  onEstadoEnvioChange?: (enviando: boolean) => void;
  formId?: string;
}

function FormularioNuevaTarea({
  onDescartar,
  onTareaCreada,
  tareaAEditar,
  modo = "individual",
  idGrupo,
  integrantes = [],
  usuarioActualId = null,
  embebidoEnModal = false,
  onEstadoEnvioChange,
  formId,
}: FormularioProps) {
  const esGrupal = modo === "grupal";
  const [categorias, setCategorias] = useState<Categoria[]>([]);
  const [titulo, setTitulo] = useState("");
  const [idCategoria, setIdCategoria] = useState<number | null>(null);
  const [fecha, setFecha] = useState("");
  const [dificultad, setDificultad] = useState(3);
  const [tiempoEstimado, setTiempoEstimado] = useState("");
  const [descripcion, setDescripcion] = useState("");
  const [enviando, setEnviando] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [errorSubidaAdjuntos, setErrorSubidaAdjuntos] = useState<string | null>(null);
  const [progresoAdjuntos, setProgresoAdjuntos] = useState<string | null>(null);
  const [archivosAdjuntosPendientes, setArchivosAdjuntosPendientes] = useState<File[]>([]);
  const [adjuntosGuardados, setAdjuntosGuardados] = useState(false);
  const [idTareaCreada, setIdTareaCreada] = useState<number | null>(null);
  const [asignados, setAsignados] = useState<number[]>([]);
  const [errorAsignados, setErrorAsignados] = useState<string | undefined>();

  const [archivoIA, setArchivoIA] = useState<File | null>(null);
  const [analizando, setAnalizando] = useState(false);
  const [avisoIA, setAvisoIA] = useState<string | null>(null);
  const [errorIA, setErrorIA] = useState<string | null>(null);

  const archivoEsPdf = Boolean(
    archivoIA
      && archivoIA.name.toLowerCase().endsWith(".pdf")
      && archivoIA.type === "application/pdf",
  );
  const archivoPdfAnalizable = Boolean(
    archivoIA
      && archivoEsPdf
      && archivoIA.size > 0
      && archivoIA.size <= TAMANO_MAXIMO_ADJUNTO,
  );
  const nivelActual = NIVELES_DIFICULTAD.find((n) => n.nivel === dificultad)!;

  const marcarEnviando = (valor: boolean) => {
    setEnviando(valor);
    onEstadoEnvioChange?.(valor);
  };

  const agregarArchivosPendientes = (nuevos: File[]) => {
    if (idTareaCreada !== null) setErrorSubidaAdjuntos(null);
    setAvisoIA(null);
    setErrorIA(null);
    setArchivosAdjuntosPendientes((actuales) => {
      const claves = new Set(actuales.map(claveArchivo));
      return [...actuales, ...nuevos.filter((archivo) => {
        const clave = claveArchivo(archivo);
        if (claves.has(clave)) return false;
        claves.add(clave);
        return true;
      })];
    });
  };

  const quitarArchivoPendiente = (archivo: File) => {
    const clave = claveArchivo(archivo);
    if (archivoIA && claveArchivo(archivoIA) === clave) {
      const restantes = archivosAdjuntosPendientes.filter((actual) => claveArchivo(actual) !== clave);
      setArchivoIA(restantes[restantes.length - 1] ?? null);
      setAvisoIA(null);
      setErrorIA(null);
    }
    setArchivosAdjuntosPendientes((actuales) => actuales.filter((actual) => claveArchivo(actual) !== clave));
    if (idTareaCreada !== null) setErrorSubidaAdjuntos(null);
  };

  const subirAdjuntosPendientes = async (idTarea: number, archivos: File[]): Promise<boolean> => {
    const fallidos: File[] = [];
    for (const [indice, archivo] of archivos.entries()) {
      setProgresoAdjuntos(`Subiendo archivo ${indice + 1} de ${archivos.length}: ${archivo.name}`);
      try {
        await subirArchivoTarea(idTarea, archivo);
      } catch {
        fallidos.push(archivo);
      }
    }

    setProgresoAdjuntos(null);
    setArchivosAdjuntosPendientes(fallidos);
    if (fallidos.length > 0) {
      setAdjuntosGuardados(false);
      setErrorSubidaAdjuntos(
        `La tarea se guardó, pero no se pudieron subir ${fallidos.length} archivo${fallidos.length === 1 ? "" : "s"}. Puedes reintentar sin crear otra tarea.`,
      );
      return false;
    }

    if (archivos.length > 0) setAdjuntosGuardados(true);
    setErrorSubidaAdjuntos(null);
    return true;
  };

  useEffect(() => {
    listarCategorias()
      .then((datos) => {
        setCategorias(datos);
        if (!tareaAEditar && datos.length > 0) {
          setIdCategoria(datos[0].id_categoria);
        }
      })
      .catch(() => setError("No se pudieron cargar las categorías"));
  }, [tareaAEditar]);

  useEffect(() => {
    if (tareaAEditar) {
      setTitulo(tareaAEditar.nombre);
      setIdCategoria(tareaAEditar.id_categoria);
      setFecha(tareaAEditar.fecha_entrega.slice(0, 16));
      setDificultad(tareaAEditar.dificultad_estimada);
      setTiempoEstimado(String(tareaAEditar.tiempo_estimado));
      setDescripcion(tareaAEditar.descripcion ?? "");
    }
  }, [tareaAEditar]);

  const manejarAutocompletadoIA = async () => {
    if (!archivoIA || !archivoIA.name.toLowerCase().endsWith(".pdf")) {
      setErrorIA(null);
      setAvisoIA("Para autocompletar con IA, elige un PDF. Pronto habrá más formatos.");
      return;
    }
    if (!archivoEsPdf) {
      setAvisoIA(null);
      setErrorIA("No pudimos validar el PDF. Elige otro archivo.");
      return;
    }
    if (archivoIA.size === 0) {
      setAvisoIA(null);
      setErrorIA("El PDF está vacío. Elige otro archivo.");
      return;
    }
    if (archivoIA.size > TAMANO_MAXIMO_ADJUNTO) {
      setAvisoIA(null);
      setErrorIA("El PDF supera 5 MB. Elige uno más pequeño.");
      return;
    }

    setAnalizando(true);
    setError(null);
    setErrorIA(null);
    setAvisoIA("Autocompletando con IA…");

    try {
      const propuesta = await analizarDocumentoIA(archivoIA);

      setTitulo(propuesta.titulo);
      setDescripcion(propuesta.descripcion);
      setDificultad(propuesta.dificultad_estimada);
      setTiempoEstimado(String(propuesta.tiempo_estimado));

      if (propuesta.id_categoria && categorias.some(c => c.id_categoria === propuesta.id_categoria)) {
        setIdCategoria(propuesta.id_categoria);
      }

      setAvisoIA(adjuntosHabilitados()
        ? "Listo. Completé los campos con sugerencias del PDF; se adjuntará al guardar."
        : "Listo. Completé los campos con sugerencias del PDF. El documento no se guardó como adjunto.");
    } catch (err) {
      setAvisoIA(null);
      setErrorIA(err instanceof Error ? err.message : "No se pudo analizar el PDF.");
    } finally {
      setAnalizando(false);
    }
  };

  const manejarCierreFormulario = () => {
    if (idTareaCreada !== null) {
      onTareaCreada();
      return;
    }
    onDescartar();
  };

  const manejarEnvio = async (evento: React.FormEvent) => {
    evento.preventDefault();
    setError(null);
    setErrorAsignados(undefined);

    if (!esGrupal && idTareaCreada !== null) {
      if (archivosAdjuntosPendientes.length === 0) {
        onTareaCreada();
        return;
      }
      marcarEnviando(true);
      try {
        const subidasCorrectas = await subirAdjuntosPendientes(idTareaCreada, archivosAdjuntosPendientes);
        if (subidasCorrectas) onTareaCreada();
      } finally {
        marcarEnviando(false);
      }
      return;
    }

    if (!titulo.trim() || !fecha || idCategoria === null) {
      setError("Completa título, fecha y categoría");
      return;
    }

    const tiempoEstimadoNum = Number(tiempoEstimado);
    if (!tiempoEstimado.trim() || !Number.isFinite(tiempoEstimadoNum) || tiempoEstimadoNum <= 0) {
      setError("El tiempo estimado debe ser un número mayor a 0 minutos");
      return;
    }

    if (esGrupal) {
      const errorAsignacion = validarAsignados(asignados);
      if (errorAsignacion) {
        setErrorAsignados(errorAsignacion);
        return;
      }
      if (idGrupo == null) {
        setError("Falta el grupo para crear la tarea.");
        return;
      }
    }

    marcarEnviando(true);
    try {
      if (esGrupal && idGrupo != null) {
        await crearTareaGrupal(idGrupo, {
          nombre: titulo,
          descripcion,
          fecha_entrega: fecha,
          dificultad_estimada: dificultad,
          tiempo_estimado: tiempoEstimadoNum,
          id_categoria: idCategoria,
          ids_usuarios: asignados,
        });
        onTareaCreada();
      } else if (tareaAEditar) {
        await actualizarTarea(tareaAEditar.id_tarea, {
          nombre: titulo,
          descripcion,
          fecha_entrega: fecha,
          dificultad_estimada: dificultad,
          tiempo_estimado: tiempoEstimadoNum,
          id_categoria: idCategoria,
        });
        onTareaCreada();
      } else {
        const datosTarea = {
          nombre: titulo,
          descripcion,
          fecha_entrega: fecha,
          dificultad_estimada: dificultad,
          tiempo_estimado: tiempoEstimadoNum,
          id_categoria: idCategoria,
        };
        const guardarPdfConTarea = Boolean(
          adjuntosHabilitados()
          && archivoPdfAnalizable
          && archivoIA
          && archivosAdjuntosPendientes.some(
            (archivo) => claveArchivo(archivo) === claveArchivo(archivoIA),
          ),
        );
        let nuevaTarea: TareaBackend;
        if (guardarPdfConTarea && archivoIA) {
          try {
            nuevaTarea = await crearTareaConPdf(datosTarea, archivoIA);
          } catch (err) {
            const detalle = err instanceof Error ? err.message : "Error al guardar el PDF.";
            setError(`No se pudo confirmar el guardado conjunto de la tarea y su PDF. ${detalle}`);
            return;
          }
        } else {
          nuevaTarea = await crearTarea(datosTarea);
        }
        setIdTareaCreada(nuevaTarea.id_tarea);
        const adjuntosRestantes = guardarPdfConTarea && archivoIA
          ? archivosAdjuntosPendientes.filter(
            (archivo) => claveArchivo(archivo) !== claveArchivo(archivoIA),
          )
          : archivosAdjuntosPendientes;
        if (guardarPdfConTarea) setArchivosAdjuntosPendientes(adjuntosRestantes);
        if (guardarPdfConTarea && adjuntosRestantes.length === 0) {
          setAdjuntosGuardados(true);
        }
        const subidasCorrectas = await subirAdjuntosPendientes(
          nuevaTarea.id_tarea,
          adjuntosRestantes,
        );
        if (!subidasCorrectas) return;
        onTareaCreada();
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error al guardar la tarea");
    } finally {
      marcarEnviando(false);
    }
  };

  const clasesForm = [
    "pixel-panel",
    embebidoEnModal ? "tareas-grupo-form-embebido" : "",
  ]
    .filter(Boolean)
    .join(" ");

  return (
    <form id={formId} className={clasesForm} onSubmit={manejarEnvio} noValidate>
      {!embebidoEnModal && (
        <div className="pixel-panel-header">
          <div>
            <h2 id="formulario-tarea-titulo" className="pixel-panel-title">
              {tareaAEditar ? "Editar tarea" : esGrupal ? "Nueva tarea grupal" : "Nueva tarea"}
            </h2>
            <p className="pixel-panel-subtitle">
              {esGrupal ? "Define el objetivo y a quién le toca." : "Define el objetivo de tu próxima sesión"}
            </p>
          </div>
          <button
            type="button"
            className="pixel-link-descartar"
            onClick={manejarCierreFormulario}
            disabled={enviando || (idTareaCreada !== null && archivosAdjuntosPendientes.length > 0)}
          >
            {idTareaCreada !== null ? "× Cerrar" : "× Descartar"}
          </button>
        </div>
      )}

      {error && <p className="pixel-error" role="alert">{error}</p>}

      <label className="pixel-field">
        <span className="pixel-field-label">Título</span>
        <input
          type="text"
          className="pixel-input"
          autoFocus
          disabled={idTareaCreada !== null}
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
            disabled={idTareaCreada !== null}
            onChange={(e) => setIdCategoria(Number(e.target.value))}
          >
            {categorias.map((cat) => (
              <option key={cat.id_categoria} value={cat.id_categoria}>
                {cat.nombre_categoria}
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
            type="datetime-local"
            className="pixel-input"
            value={fecha}
            disabled={idTareaCreada !== null}
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
                  disabled={idTareaCreada !== null}
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
            disabled={idTareaCreada !== null}
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
          disabled={idTareaCreada !== null}
          onChange={(e) => setDescripcion(e.target.value)}
        />
      </label>

      {esGrupal && (
        <AsignarIntegrantes
          integrantes={integrantes}
          seleccionados={asignados}
          onChange={(ids) => {
            setAsignados(ids);
            setErrorAsignados(undefined);
          }}
          error={errorAsignados}
          usuarioActualId={usuarioActualId}
        />
      )}

      {!esGrupal && !tareaAEditar && (
        <SelectorArchivosPendientes
          archivos={archivosAdjuntosPendientes}
          adjuntosHabilitados={adjuntosHabilitados()}
          archivoAnalisisIA={archivoPdfAnalizable ? archivoIA : null}
          analisisDisponible={archivoPdfAnalizable && idTareaCreada === null}
          analizando={analizando}
          avisoIA={avisoIA}
          errorIA={errorIA}
          disabled={enviando}
          disabledIA={idTareaCreada !== null}
          onAgregar={agregarArchivosPendientes}
          onQuitar={quitarArchivoPendiente}
          onSeleccionarArchivo={(archivo) => {
            const yaAdjuntado = archivo
              ? archivosAdjuntosPendientes.find((actual) => claveArchivo(actual) === claveArchivo(archivo))
              : null;
            setArchivoIA(yaAdjuntado ?? archivo);
            setAvisoIA(null);
            setErrorIA(null);
          }}
          onAnalizar={() => void manejarAutocompletadoIA()}
        />
      )}

      {!esGrupal && tareaAEditar && (
        <SeccionAdjuntosTarea
          key={tareaAEditar.id_tarea}
          idTarea={tareaAEditar.id_tarea}
          modo="edicion"
        />
      )}

      {!esGrupal && progresoAdjuntos && (
        <p className="pixel-form-progreso" role="status">{progresoAdjuntos}</p>
      )}
      {!esGrupal && errorSubidaAdjuntos && (
        <p className="pixel-error" role="alert">{errorSubidaAdjuntos}</p>
      )}
      {!esGrupal && idTareaCreada !== null && (
        <p className="pixel-form-tarea-guardada" role="status">
          {errorSubidaAdjuntos
            ? "La tarea está guardada, pero el PDF/archivo todavía no se subió. Reintenta antes de cerrar."
            : adjuntosGuardados
              ? "La tarea y sus archivos quedaron guardados."
              : "La tarea ya está guardada."}
        </p>
      )}

      {!embebidoEnModal && (
        <div className="pixel-panel-footer">
          {esGrupal && (
            <p className="tareas-grupo-nota">La prioridad se calcula automáticamente.</p>
          )}
          <button type="submit" className="pixel-btn-crear-tarea" disabled={enviando}>
            {enviando
              ? idTareaCreada !== null ? "Subiendo adjuntos…" : "Guardando…"
              : tareaAEditar
                ? "Guardar →"
                : idTareaCreada !== null
                  ? archivosAdjuntosPendientes.length > 0 ? "Reintentar adjuntos →" : "Finalizar →"
                  : esGrupal
                    ? "Crear tarea →"
                    : "Crear →"}
          </button>
        </div>
      )}
    </form>
  );
}

export default FormularioNuevaTarea;
