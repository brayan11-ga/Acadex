// Ruta: frontend/src/pages/TareasGrupoPage.tsx
import { useCallback, useEffect, useState } from "react";
import { Link, Navigate, useNavigate, useParams } from "react-router-dom";
import ModalNuevaTareaGrupal from "../components/tareas-grupo/ModalNuevaTareaGrupal";
import { listarCategorias, type Categoria } from "../services/categorias";
import { listarMisGrupos, obtenerIntegrantes } from "../services/grupos";
import {
  listarAsignadosTarea,
  listarTareasAsignadasMias,
  listarTareasDeGrupo,
  type IntegranteAsignadoBackend,
  type TareaBackend,
} from "../services/tareas";
import type { GrupoConRol, Integrante } from "../types/grupo";
import type { IntegranteAsignable } from "../types/tareaGrupo";
import { obtenerIdUsuarioActual } from "../utils/jwt";
import "../styles/tareas-grupo.css";

type EstadoPantalla = "cargando" | "lista" | "vacio" | "error" | "sin-permisos";
type PrioridadChip = "baja" | "media" | "alta";

const formateadorFecha = new Intl.DateTimeFormat("es-CO", {
  day: "numeric",
  month: "short",
  hour: "numeric",
  minute: "2-digit",
});

const ETIQUETAS_ESTADO: Record<string, string> = {
  pendiente: "pendiente",
  "en-progreso": "en progreso",
  "en progreso": "en progreso",
  completada: "completada",
};

const ETIQUETAS_PRIORIDAD: Record<PrioridadChip, string> = {
  baja: "Prioridad baja",
  media: "Prioridad media",
  alta: "Prioridad alta",
};

function formatearFecha(fechaIso: string): string {
  const fecha = new Date(fechaIso);
  return Number.isNaN(fecha.getTime()) ? "Sin fecha" : formateadorFecha.format(fecha);
}

function normalizarEstado(estado: string): string {
  return estado.trim().toLowerCase().replace(/\s+/g, "-");
}

function mapearPrioridad(prioridad: number | null): PrioridadChip | null {
  if (prioridad == null) return null;
  if (prioridad <= 1) return "alta";
  if (prioridad === 2) return "media";
  return "baja";
}

function estaVencida(tarea: TareaBackend, ahora: Date): boolean {
  return normalizarEstado(tarea.estado) !== "completada"
    && new Date(tarea.fecha_entrega).getTime() < ahora.getTime();
}

function textoCantidadTareas(cantidad: number): string {
  return cantidad === 1 ? "1 tarea" : `${cantidad} tareas`;
}

function aIntegranteAsignable(integrante: Integrante): IntegranteAsignable {
  return {
    id_usuario: integrante.id_usuario,
    correo_electronico: integrante.correo_electronico,
    rol: integrante.rol,
  };
}

function obtenerInicial(correo: string): string {
  return correo.charAt(0).toUpperCase() || "?";
}

function TareasGrupoPage() {
  const { idGrupo } = useParams();
  const id = Number(idGrupo);
  const navigate = useNavigate();
  const idUsuarioActual = obtenerIdUsuarioActual();
  const [ahora] = useState(() => new Date());

  const [grupo, setGrupo] = useState<GrupoConRol | null>(null);
  const [tareas, setTareas] = useState<TareaBackend[]>([]);
  const [integrantes, setIntegrantes] = useState<IntegranteAsignable[]>([]);
  const [idsTareasMias, setIdsTareasMias] = useState<Set<number>>(new Set());
  const [categorias, setCategorias] = useState<Categoria[]>([]);
  const [estado, setEstado] = useState<EstadoPantalla>("cargando");
  const [modalAbierto, setModalAbierto] = useState(false);
  const [avisoVisible, setAvisoVisible] = useState(false);
  const [asignadosAbiertos, setAsignadosAbiertos] = useState<number[]>([]);
  const [cacheAsignados, setCacheAsignados] = useState<Record<number, IntegranteAsignadoBackend[]>>({});
  const [cargandoAsignados, setCargandoAsignados] = useState<Record<number, boolean>>({});
  const [errorAsignados, setErrorAsignados] = useState<Record<number, string>>({});

  const esLider = grupo?.rol === "lider";

  const nombreCategoria = useCallback(
    (idCategoria: number) =>
      categorias.find((c) => c.id_categoria === idCategoria)?.nombre_categoria ?? "Sin categoría",
    [categorias],
  );

  const cargar = useCallback(async () => {
    setEstado("cargando");
    try {
      const misGrupos = await listarMisGrupos();
      const encontrado = misGrupos.find((g) => g.id_grupo === id) ?? null;
      if (!encontrado) {
        setGrupo(null);
        setEstado("sin-permisos");
        return;
      }
      setGrupo(encontrado);

      const [listaTareas, miembros, categoriasDatos, asignadasMias] = await Promise.all([
        listarTareasDeGrupo(id),
        obtenerIntegrantes(id),
        listarCategorias(),
        listarTareasAsignadasMias().catch(() => [] as TareaBackend[]),
      ]);

      setTareas(listaTareas);
      setIntegrantes(miembros.map(aIntegranteAsignable));
      setCategorias(categoriasDatos);
      setIdsTareasMias(new Set(asignadasMias.map((t) => t.id_tarea)));
      setEstado(listaTareas.length === 0 ? "vacio" : "lista");
    } catch (err) {
      const mensaje = (err instanceof Error ? err.message : "").toLowerCase();
      if (mensaje.includes("permiso") || mensaje.includes("403") || mensaje.includes("forbidden")) {
        setEstado("sin-permisos");
      } else {
        setEstado("error");
      }
    }
  }, [id]);

  useEffect(() => {
    if (!Number.isNaN(id)) cargar();
  }, [cargar, id]);

  async function alternarAsignados(idTarea: number) {
    const yaAbierto = asignadosAbiertos.includes(idTarea);
    if (yaAbierto) {
      setAsignadosAbiertos((abiertos) => abiertos.filter((actual) => actual !== idTarea));
      return;
    }

    setAsignadosAbiertos((abiertos) => [...abiertos, idTarea]);

    if (cacheAsignados[idTarea] || cargandoAsignados[idTarea]) return;

    setCargandoAsignados((prev) => ({ ...prev, [idTarea]: true }));
    setErrorAsignados((prev) => {
      const siguiente = { ...prev };
      delete siguiente[idTarea];
      return siguiente;
    });

    try {
      const asignados = await listarAsignadosTarea(idTarea);
      setCacheAsignados((prev) => ({ ...prev, [idTarea]: asignados }));
    } catch (err) {
      const mensaje = err instanceof Error ? err.message : "No se pudieron cargar los asignados.";
      setErrorAsignados((prev) => ({
        ...prev,
        [idTarea]: mensaje.includes("403") || mensaje.toLowerCase().includes("permiso")
          ? "No tienes permiso para ver los asignados de esta tarea."
          : "No se pudieron cargar los asignados.",
      }));
    } finally {
      setCargandoAsignados((prev) => ({ ...prev, [idTarea]: false }));
    }
  }

  function manejarTareaCreada() {
    setModalAbierto(false);
    setAvisoVisible(true);
    void cargar();
  }

  if (Number.isNaN(id)) return <Navigate to="/grupos" replace />;

  if (estado === "sin-permisos") {
    return (
      <div className="tareas-grupo-pagina">
        <div className="tareas-grupo-contenido">
          <section className="tareas-grupo-estado" aria-labelledby="tareas-grupo-sin-permisos">
            <span className="tareas-grupo-estado-icono" aria-hidden="true">!</span>
            <h1 id="tareas-grupo-sin-permisos" className="tareas-grupo-estado-titulo">
              No perteneces a este grupo
            </h1>
            <p className="tareas-grupo-estado-texto">
              Pide al líder un código de acceso para unirte y ver sus tareas.
            </p>
            <Link to="/grupos" className="tareas-grupo-volver">
              ← Volver a Mis Grupos
            </Link>
          </section>
        </div>
      </div>
    );
  }

  return (
    <div className="tareas-grupo-pagina">
      <div className="tareas-grupo-contenido">
        {grupo && (
          <header className="tareas-grupo-encabezado">
            <div className="tareas-grupo-encabezado-info">
              <Link to="/grupos" className="tareas-grupo-volver">
                ← Volver a Mis Grupos
              </Link>
              <h1 className="tareas-grupo-titulo">{grupo.nombre_grupo}</h1>
              <p className="tareas-grupo-descripcion">
                {grupo.descripcion?.trim() || "Sin descripción."}
              </p>
              {(estado === "lista" || estado === "vacio") && (
                <span className="tareas-grupo-contador">{textoCantidadTareas(tareas.length)}</span>
              )}
            </div>

            <div className="tareas-grupo-acciones">
              <button
                type="button"
                className="tareas-grupo-boton tareas-grupo-boton--secundario"
                onClick={() => navigate(`/grupos/${id}`)}
              >
                Integrantes
              </button>
              {esLider && (
                <>
                  <button
                    type="button"
                    className="tareas-grupo-boton tareas-grupo-boton--secundario"
                    onClick={() => navigate(`/grupos/${id}/lider`)}
                  >
                    Panel de líder
                  </button>
                  <button
                    type="button"
                    className="tareas-grupo-boton tareas-grupo-boton--primario"
                    onClick={() => {
                      setAvisoVisible(false);
                      setModalAbierto(true);
                    }}
                  >
                    + Nueva tarea
                  </button>
                </>
              )}
            </div>
          </header>
        )}

        {avisoVisible && (
          <div className="tareas-grupo-aviso" role="status">
            <span className="tareas-grupo-aviso-icono" aria-hidden="true">✓</span>
            <p>Tarea creada y asignada</p>
            <button
              type="button"
              className="tareas-grupo-boton-icono"
              onClick={() => setAvisoVisible(false)}
              aria-label="Cerrar aviso"
            >
              ✕
            </button>
          </div>
        )}

        {estado === "cargando" && (
          <div>
            <p className="tareas-grupo-sr-only" role="status">Cargando tareas…</p>
            <ul className="tareas-grupo-lista" aria-hidden="true">
              {[0, 1, 2].map((indice) => (
                <li key={indice} className="tareas-grupo-tarjeta tareas-grupo-skeleton-tarjeta">
                  <div className="tareas-grupo-tarjeta-principal">
                    <span className="tareas-grupo-skeleton tareas-grupo-skeleton--titulo" />
                    <span className="tareas-grupo-skeleton tareas-grupo-skeleton--linea" />
                  </div>
                  <div className="tareas-grupo-tarjeta-lado">
                    <span className="tareas-grupo-skeleton tareas-grupo-skeleton--chip" />
                    <span className="tareas-grupo-skeleton tareas-grupo-skeleton--chip" />
                  </div>
                </li>
              ))}
            </ul>
          </div>
        )}

        {estado === "error" && (
          <section className="tareas-grupo-estado tareas-grupo-estado--error" role="alert">
            <span className="tareas-grupo-estado-icono" aria-hidden="true">✕</span>
            <h2 className="tareas-grupo-estado-titulo">No pudimos cargar las tareas</h2>
            <p className="tareas-grupo-estado-texto">Revisa tu conexión e inténtalo de nuevo.</p>
            <button
              type="button"
              className="tareas-grupo-boton tareas-grupo-boton--primario"
              onClick={() => void cargar()}
            >
              Reintentar
            </button>
          </section>
        )}

        {estado === "vacio" && (
          <section className="tareas-grupo-estado" aria-labelledby="tareas-grupo-estado-vacio">
            <span className="tareas-grupo-estado-icono" aria-hidden="true">+</span>
            <h2 id="tareas-grupo-estado-vacio" className="tareas-grupo-estado-titulo">
              Aún no hay tareas en este grupo
            </h2>
            <p className="tareas-grupo-estado-texto">
              {esLider
                ? "Crea la primera tarea para que tu equipo pueda empezar a trabajar."
                : "Cuando el líder cree una tarea, aparecerá aquí para que puedas verla."}
            </p>
          </section>
        )}

        {estado === "lista" && grupo && (
          <ul className="tareas-grupo-lista" aria-label={`Tareas de ${grupo.nombre_grupo}`}>
            {tareas.map((tarea) => {
              const estadoNorm = normalizarEstado(tarea.estado);
              const prioridad = mapearPrioridad(tarea.prioridad);
              const vencida = estaVencida(tarea, ahora);
              const esTuya = idsTareasMias.has(tarea.id_tarea);
              const abierto = asignadosAbiertos.includes(tarea.id_tarea);
              const asignados = cacheAsignados[tarea.id_tarea] ?? [];
              const idPanel = `tareas-grupo-asignados-${tarea.id_tarea}`;
              const clases = [
                "tareas-grupo-tarjeta",
                vencida && "tareas-grupo-tarjeta--vencida",
                estadoNorm === "completada" && "tareas-grupo-tarjeta--completada",
              ]
                .filter(Boolean)
                .join(" ");

              return (
                <li key={tarea.id_tarea} className={clases}>
                  <div className="tareas-grupo-tarjeta-principal">
                    <div className="tareas-grupo-tarjeta-titulo-fila">
                      <h3 className="tareas-grupo-tarjeta-titulo">{tarea.nombre}</h3>
                      <span className={`tareas-grupo-nivel tareas-grupo-nivel--${tarea.dificultad_estimada}`}>
                        Nivel {tarea.dificultad_estimada}
                      </span>
                      {esTuya && <span className="tareas-grupo-etiqueta-tuya">Tuya</span>}
                      {vencida && <span className="tareas-grupo-etiqueta-vencida">Vencida</span>}
                    </div>
                    <dl className="tareas-grupo-meta">
                      <div className={vencida ? "tareas-grupo-meta-item tareas-grupo-meta-item--vencida" : "tareas-grupo-meta-item"}>
                        <dt>Entrega</dt>
                        <dd>
                          <time dateTime={tarea.fecha_entrega}>{formatearFecha(tarea.fecha_entrega)}</time>
                        </dd>
                      </div>
                      <div className="tareas-grupo-meta-item">
                        <dt>Categoría</dt>
                        <dd>{nombreCategoria(tarea.id_categoria)}</dd>
                      </div>
                    </dl>
                  </div>

                  <div className="tareas-grupo-tarjeta-lado">
                    <span className={`tareas-grupo-chip tareas-grupo-estado--${estadoNorm}`}>
                      <span className="tareas-grupo-sr-only">Estado: </span>
                      {ETIQUETAS_ESTADO[estadoNorm] ?? estadoNorm}
                    </span>
                    {prioridad && (
                      <span className={`tareas-grupo-chip tareas-grupo-prioridad tareas-grupo-prioridad--${prioridad}`}>
                        {ETIQUETAS_PRIORIDAD[prioridad]}
                      </span>
                    )}
                  </div>

                  <div className="tareas-grupo-tarjeta-pie">
                    <button
                      type="button"
                      className="tareas-grupo-boton tareas-grupo-boton--secundario tareas-grupo-boton--pequeno"
                      aria-expanded={abierto}
                      aria-controls={idPanel}
                      onClick={() => void alternarAsignados(tarea.id_tarea)}
                    >
                      {abierto ? "Ocultar asignados" : "Ver asignados"}
                      {cacheAsignados[tarea.id_tarea] && (
                        <span
                          className="tareas-grupo-boton-contador"
                          aria-label={`${asignados.length} asignados`}
                        >
                          {asignados.length}
                        </span>
                      )}
                    </button>
                  </div>

                  {abierto && (
                    <div id={idPanel} className="tareas-grupo-asignados">
                      {cargandoAsignados[tarea.id_tarea] && (
                        <p className="tareas-grupo-asignados-vacio" role="status">Cargando asignados…</p>
                      )}
                      {errorAsignados[tarea.id_tarea] && (
                        <p className="tareas-grupo-error-campo" role="alert">
                          <span aria-hidden="true">✕</span> {errorAsignados[tarea.id_tarea]}
                        </p>
                      )}
                      {!cargandoAsignados[tarea.id_tarea] && !errorAsignados[tarea.id_tarea] && (
                        asignados.length === 0 ? (
                          <p className="tareas-grupo-asignados-vacio">Sin asignados</p>
                        ) : (
                          <ul className="tareas-grupo-asignados-lista">
                            {asignados.map((persona) => (
                              <li key={persona.id_usuario} className="tareas-grupo-asignado">
                                <span className="tareas-grupo-avatar" aria-hidden="true">
                                  {obtenerInicial(persona.correo_electronico)}
                                </span>
                                <span className="tareas-grupo-truncar">{persona.correo_electronico}</span>
                                {persona.id_usuario === idUsuarioActual && (
                                  <span className="tareas-grupo-etiqueta-tu">TÚ</span>
                                )}
                              </li>
                            ))}
                          </ul>
                        )
                      )}
                    </div>
                  )}
                </li>
              );
            })}
          </ul>
        )}
      </div>

      {modalAbierto && esLider && grupo && (
        <ModalNuevaTareaGrupal
          idGrupo={id}
          integrantes={integrantes}
          usuarioActualId={idUsuarioActual}
          onCerrar={() => setModalAbierto(false)}
          onCreada={manejarTareaCreada}
        />
      )}
    </div>
  );
}

export default TareasGrupoPage;
