// Ruta: frontend/src/pages/DetalleTareaGrupoPage.tsx
import {
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
  type ReactNode,
} from "react";
import { Link, Navigate, useParams } from "react-router-dom";
import { listarCategorias, type Categoria } from "../services/categorias";
import { listarMisGrupos } from "../services/grupos";
import {
  descargarArchivoTarea,
  listarArchivosTarea,
  listarAsignadosTarea,
  obtenerTarea,
  type ArchivoTarea,
  type IntegranteAsignadoBackend,
  type TareaBackend,
} from "../services/tareas";
import {
  listarSesionesUsuario,
  type SesionCronometroBackend,
} from "../services/sesionesCronometro";
import type { GrupoConRol } from "../types/grupo";
import { obtenerIdUsuarioActual } from "../utils/jwt";
import "../styles/detalle-tarea-grupo.css";

type EstadoPantalla =
  | "cargando"
  | "lista"
  | "error"
  | "sin-permisos"
  | "no-encontrada";
type PrioridadChip = "baja" | "media" | "alta";

const NIVELES = [
  "Muy fácil",
  "Fácil",
  "Moderada",
  "Difícil",
  "Muy difícil",
] as const;

const formateadorFecha = new Intl.DateTimeFormat("es-CO", {
  day: "numeric",
  month: "short",
  hour: "numeric",
  minute: "2-digit",
});

const FORMA_CARITA = [
  "..oooooo..",
  ".oooooooo.",
  "oooooooooo",
  "oooooooooo",
  "oooooooooo",
  "oooooooooo",
  "oooooooooo",
  "oooooooooo",
  ".oooooooo.",
  "..oooooo..",
];

const OJOS: [number, number][] = [
  [3, 3],
  [6, 3],
];
const RASGOS: Record<number, [number, number][]> = {
  1: [
    ...OJOS,
    [2, 5],
    [7, 5],
    [3, 6],
    [4, 6],
    [5, 6],
    [6, 6],
    [4, 7],
    [5, 7],
  ],
  2: [
    ...OJOS,
    [2, 5],
    [7, 5],
    [3, 6],
    [4, 6],
    [5, 6],
    [6, 6],
  ],
  3: [
    ...OJOS,
    [3, 6],
    [4, 6],
    [5, 6],
    [6, 6],
  ],
  4: [
    ...OJOS,
    [3, 6],
    [4, 6],
    [5, 6],
    [6, 6],
    [2, 7],
    [7, 7],
  ],
  5: [
    ...OJOS,
    [2, 2],
    [7, 2],
    [3, 6],
    [4, 6],
    [5, 6],
    [6, 6],
    [2, 7],
    [7, 7],
  ],
};

function formatearFecha(fechaIso: string): string {
  const fecha = new Date(fechaIso);
  return Number.isNaN(fecha.getTime())
    ? "Sin fecha"
    : formateadorFecha.format(fecha);
}

function formatearDuracion(minutos: number): string {
  const horas = Math.floor(minutos / 60);
  const mins = Math.round(minutos % 60);
  if (horas === 0) return `${mins} min`;
  return mins === 0 ? `${horas} h` : `${horas} h ${mins} min`;
}

function formatearCronometro(totalSegundos: number): string {
  const horas = Math.floor(totalSegundos / 3600);
  const minutos = Math.floor((totalSegundos % 3600) / 60);
  const segundos = totalSegundos % 60;
  return [horas, minutos, segundos]
    .map((numero) => String(numero).padStart(2, "0"))
    .join(":");
}

function formatearTamano(bytes: number | null): string {
  if (bytes == null) return "Tamaño desconocido";
  if (bytes < 1024 * 1024) return `${Math.max(1, Math.round(bytes / 1024))} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
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

function nivelValido(nivel: number): number {
  return Math.min(Math.max(nivel, 1), 5);
}

function estaVencida(tarea: TareaBackend): boolean {
  return (
    normalizarEstado(tarea.estado) !== "completada" &&
    new Date(tarea.fecha_entrega).getTime() < Date.now()
  );
}

function obtenerInicial(correo: string): string {
  return correo.charAt(0).toUpperCase() || "?";
}

function CaritaPixel({ nivel }: { nivel: number }) {
  return (
    <svg
      className="detalle-tarea-carita"
      viewBox="0 0 10 10"
      shapeRendering="crispEdges"
      aria-hidden="true"
    >
      {FORMA_CARITA.flatMap((fila, y) =>
        fila
          .split("")
          .map((caracter, x) =>
            caracter === "o" ? (
              <rect
                key={`${x}-${y}`}
                x={x}
                y={y}
                width="1"
                height="1"
                className="detalle-tarea-carita-piel"
              />
            ) : null,
          ),
      )}
      {RASGOS[nivel].map(([x, y]) => (
        <rect
          key={`r-${x}-${y}`}
          x={x}
          y={y}
          width="1"
          height="1"
          className="detalle-tarea-carita-rasgo"
        />
      ))}
    </svg>
  );
}

function InsigniaNivel({ nivel }: { nivel: number }) {
  return (
    <span
      className={`detalle-tarea-insignia detalle-tarea-insignia-nivel detalle-tarea-nivel-${nivel}`}
    >
      NIVEL {nivel}
    </span>
  );
}

function PildoraEstado({ estado }: { estado: string }) {
  const normalizado = normalizarEstado(estado);
  const etiqueta = normalizado === "en-progreso" ? "en progreso" : normalizado;
  return (
    <span
      className={`detalle-tarea-pildora detalle-tarea-pildora-${normalizado}`}
    >
      {etiqueta}
    </span>
  );
}

function Avatar({ correo }: { correo: string }) {
  return (
    <span className="detalle-tarea-avatar" aria-hidden="true">
      {obtenerInicial(correo)}
    </span>
  );
}

function Tarjeta({
  titulo,
  extra,
  children,
  className = "",
}: {
  titulo: string;
  extra?: ReactNode;
  children: ReactNode;
  className?: string;
}) {
  return (
    <section className={`detalle-tarea-tarjeta ${className}`} aria-label={titulo}>
      <header className="detalle-tarea-tarjeta-cabecera">
        <h2 className="detalle-tarea-tarjeta-titulo">{titulo}</h2>
        {extra}
      </header>
      {children}
    </section>
  );
}

function Modal({
  abierto,
  onCerrar,
  titulo,
  children,
  pequeno = false,
}: {
  abierto: boolean;
  onCerrar: () => void;
  titulo: string;
  children: ReactNode;
  pequeno?: boolean;
}) {
  const ref = useRef<HTMLDialogElement>(null);

  useEffect(() => {
    const dialogo = ref.current;
    if (!dialogo) return;
    if (abierto && !dialogo.open) dialogo.showModal();
    if (!abierto && dialogo.open) dialogo.close();
  }, [abierto]);

  return (
    <dialog
      ref={ref}
      className={`detalle-tarea-modal ${pequeno ? "detalle-tarea-modal-pequeno" : ""}`}
      aria-label={titulo}
      onClose={onCerrar}
      onClick={(evento) => {
        if (evento.target === ref.current) onCerrar();
      }}
    >
      {abierto && (
        <div className="detalle-tarea-modal-contenido">
          <h2 className="detalle-tarea-modal-titulo">{titulo}</h2>
          {children}
        </div>
      )}
    </dialog>
  );
}

function DialogoConfirmacion({
  abierto,
  titulo,
  mensaje,
  textoConfirmar,
  peligro = false,
  deshabilitado = false,
  onConfirmar,
  onCancelar,
}: {
  abierto: boolean;
  titulo: string;
  mensaje: ReactNode;
  textoConfirmar: string;
  peligro?: boolean;
  deshabilitado?: boolean;
  onConfirmar: () => void;
  onCancelar: () => void;
}) {
  return (
    <Modal abierto={abierto} onCerrar={onCancelar} titulo={titulo} pequeno>
      <div className="detalle-tarea-modal-texto">{mensaje}</div>
      <div className="detalle-tarea-modal-acciones">
        <button
          type="button"
          className="detalle-tarea-boton detalle-tarea-boton-secundario"
          onClick={onCancelar}
        >
          Cancelar
        </button>
        <button
          type="button"
          className={`detalle-tarea-boton ${peligro ? "detalle-tarea-boton-peligro" : "detalle-tarea-boton-primario"}`}
          onClick={onConfirmar}
          disabled={deshabilitado}
          title={deshabilitado ? "Próximamente" : undefined}
        >
          {textoConfirmar}
        </button>
      </div>
    </Modal>
  );
}

function Encabezado({
  tarea,
  esTuya,
  sinArchivos,
}: {
  tarea: TareaBackend;
  esTuya: boolean;
  sinArchivos: boolean;
}) {
  const vencida = estaVencida(tarea);
  const nivel = nivelValido(tarea.dificultad_estimada);
  return (
    <header
      className={`detalle-tarea-encabezado ${vencida ? "detalle-tarea-vencida" : ""}`}
    >
      <div className="detalle-tarea-encabezado-fila">
        <div className="detalle-tarea-encabezado-nombre">
          <h1 className="detalle-tarea-titulo">{tarea.nombre}</h1>
          {sinArchivos && (
            <>
              {/* ÍCONO PENDIENTE: sin archivos */}
              <span className="detalle-tarea-icono-pendiente" aria-hidden="true" />
            </>
          )}
        </div>
        <PildoraEstado estado={tarea.estado} />
      </div>
      <div className="detalle-tarea-insignias">
        <InsigniaNivel nivel={nivel} />
        {esTuya && (
          <span className="detalle-tarea-insignia detalle-tarea-insignia-tuya">
            TUYA
          </span>
        )}
        {vencida && (
          <span className="detalle-tarea-insignia detalle-tarea-insignia-vencida">
            VENCIDA
          </span>
        )}
      </div>
    </header>
  );
}

function InfoTarea({
  tarea,
  categoria,
  prioridad,
}: {
  tarea: TareaBackend;
  categoria: string;
  prioridad: PrioridadChip | null;
}) {
  const vencida = estaVencida(tarea);
  const nivel = nivelValido(tarea.dificultad_estimada);
  return (
    <Tarjeta titulo="Información">
      <p className="detalle-tarea-descripcion">
        {tarea.descripcion?.trim() || "Sin descripción."}
      </p>
      <dl className="detalle-tarea-datos">
        <div className="detalle-tarea-dato">
          <dt>Categoría</dt>
          <dd>{categoria}</dd>
        </div>
        <div className="detalle-tarea-dato">
          <dt>Entrega</dt>
          <dd className={vencida ? "detalle-tarea-texto-peligro" : ""}>
            <time dateTime={tarea.fecha_entrega}>
              {formatearFecha(tarea.fecha_entrega)}
            </time>
          </dd>
        </div>
        <div className="detalle-tarea-dato">
          <dt>Tiempo estimado</dt>
          <dd>{tarea.tiempo_estimado} min</dd>
        </div>
        <div className="detalle-tarea-dato">
          <dt>Dificultad estimada</dt>
          <dd className="detalle-tarea-dato-dificultad">
            <span className={`detalle-tarea-mini-carita detalle-tarea-nivel-${nivel}`}>
              <CaritaPixel nivel={nivel} />
            </span>
            {nivel}/5 · {NIVELES[nivel - 1]}
          </dd>
        </div>
        <div className="detalle-tarea-dato">
          <dt>Prioridad</dt>
          <dd>
            {prioridad ? (
              <span
                className={`detalle-tarea-prioridad detalle-tarea-prioridad-${prioridad}`}
              >
                {prioridad}
              </span>
            ) : (
              <span className="detalle-tarea-prioridad detalle-tarea-prioridad-sin">
                Sin prioridad
              </span>
            )}
          </dd>
        </div>
      </dl>
    </Tarjeta>
  );
}

function Progreso({ asignados }: { asignados: IntegranteAsignadoBackend[] }) {
  const completados = asignados.filter((asignado) => asignado.completado).length;
  const total = asignados.length;
  const porcentaje = total === 0 ? 0 : Math.round((completados / total) * 100);
  return (
    <Tarjeta titulo="Progreso">
      <p className="detalle-tarea-progreso-texto">
        <strong>{completados}</strong> de <strong>{total}</strong> asignados
        completaron su parte
      </p>
      <div
        className="detalle-tarea-barra"
        role="progressbar"
        aria-valuemin={0}
        aria-valuemax={total}
        aria-valuenow={completados}
        aria-label="Progreso de la tarea"
      >
        <div
          className="detalle-tarea-barra-relleno"
          style={{ width: `${porcentaje}%` }}
        />
      </div>
    </Tarjeta>
  );
}

function ListaAsignados({
  asignados,
  idUsuarioActual,
}: {
  asignados: IntegranteAsignadoBackend[];
  idUsuarioActual: number | null;
}) {
  return (
    <Tarjeta
      titulo="Asignados"
      extra={<span className="detalle-tarea-contador">{asignados.length}</span>}
    >
      {asignados.length === 0 ? (
        <p className="detalle-tarea-vacio">Sin asignados.</p>
      ) : (
        <ul className="detalle-tarea-lista">
          {asignados.map((asignado) => (
            <li key={asignado.id_usuario} className="detalle-tarea-fila">
              <Avatar correo={asignado.correo_electronico} />
              <span className="detalle-tarea-correo">
                {asignado.correo_electronico}
              </span>
              {asignado.id_usuario === idUsuarioActual && (
                <span className="detalle-tarea-etiqueta-tu">Tú</span>
              )}
              <span
                className={`detalle-tarea-insignia-estado ${
                  asignado.completado
                    ? "detalle-tarea-insignia-completo"
                    : "detalle-tarea-insignia-pendiente"
                }`}
              >
                {asignado.completado ? "Completó" : "Pendiente"}
              </span>
            </li>
          ))}
        </ul>
      )}
    </Tarjeta>
  );
}

function TiemposIntegrantes({
  asignados,
  idUsuarioActual,
  tiempoPropioSegundos,
}: {
  asignados: IntegranteAsignadoBackend[];
  idUsuarioActual: number | null;
  tiempoPropioSegundos: number | null;
}) {
  const hayOtrosIntegrantes = asignados.some(
    (asignado) => asignado.id_usuario !== idUsuarioActual,
  );

  return (
    <Tarjeta titulo="Tiempo por integrante">
      {asignados.length === 0 ? (
        <p className="detalle-tarea-vacio">Sin asignados.</p>
      ) : (
        <ul className="detalle-tarea-lista">
          {asignados.map((asignado) => {
            const esUnoMismo = asignado.id_usuario === idUsuarioActual;
            const registrado =
              asignado.completado &&
              esUnoMismo &&
              tiempoPropioSegundos !== null;
            return (
              <li key={asignado.id_usuario} className="detalle-tarea-fila">
                <Avatar correo={asignado.correo_electronico} />
                <span className="detalle-tarea-correo">
                  {asignado.correo_electronico}
                </span>
                {esUnoMismo && (
                  <span className="detalle-tarea-etiqueta-tu">Tú</span>
                )}
                <span
                  className={
                    registrado
                      ? "detalle-tarea-tiempo"
                      : "detalle-tarea-tiempo-vacio"
                  }
                >
                  {registrado
                    ? formatearDuracion(
                        Math.round((tiempoPropioSegundos ?? 0) / 60),
                      )
                    : "Aún sin registrar"}
                </span>
              </li>
            );
          })}
        </ul>
      )}
      {hayOtrosIntegrantes && (
        <p className="detalle-tarea-nota">
          El tiempo de los demás integrantes estará disponible próximamente.
        </p>
      )}
    </Tarjeta>
  );
}

function MiCronometro() {
  return (
    <Tarjeta
      titulo="Mi cronómetro"
      className="detalle-tarea-cronometro"
      extra={
        <span className="detalle-tarea-etiqueta-personal">Personal</span>
      }
    >
      <p className="detalle-tarea-crono-tiempo" aria-live="off">
        {formatearCronometro(0)}
      </p>
      <p className="detalle-tarea-crono-estado" role="status">
        <span className="detalle-tarea-crono-punto" aria-hidden="true" />
        Cronómetro detenido
      </p>
      <div className="detalle-tarea-crono-botones">
        <button
          type="button"
          className="detalle-tarea-boton detalle-tarea-boton-primario"
          disabled
          title="Próximamente"
        >
          Iniciar
        </button>
        <button
          type="button"
          className="detalle-tarea-boton detalle-tarea-boton-secundario"
          disabled
          title="Próximamente"
        >
          Pausar
        </button>
        <button
          type="button"
          className="detalle-tarea-boton detalle-tarea-boton-secundario"
          disabled
          title="Próximamente"
        >
          Reiniciar
        </button>
      </div>
      <p className="detalle-tarea-nota">Solo tú ves y manejas este cronómetro.</p>
    </Tarjeta>
  );
}

function Archivos({
  archivos,
  maximo,
  puedeSubir,
  descargandoId,
  errorDescarga,
  onSubir,
  onEliminar,
  onDescargar,
}: {
  archivos: ArchivoTarea[];
  maximo: number;
  puedeSubir: boolean;
  descargandoId: number | null;
  errorDescarga: string | null;
  onSubir: () => void;
  onEliminar: (archivo: ArchivoTarea) => void;
  onDescargar: (archivo: ArchivoTarea) => void;
}) {
  const inputRef = useRef<HTMLInputElement>(null);
  const limite = archivos.length >= maximo;

  return (
    <Tarjeta
      titulo="Archivos"
      extra={
        <span className="detalle-tarea-contador">
          {archivos.length} de {maximo} archivos
        </span>
      }
    >
      {archivos.length === 0 ? (
        <p className="detalle-tarea-vacio">
          Todavía no hay archivos en esta tarea.
        </p>
      ) : (
        <ul className="detalle-tarea-lista">
          {archivos.map((archivo) => (
            <li key={archivo.id_archivo} className="detalle-tarea-archivo">
              <span
                className={`detalle-tarea-tipo detalle-tarea-tipo-${archivo.tipo.toLowerCase()}`}
              >
                {archivo.tipo}
              </span>
              <div className="detalle-tarea-archivo-info">
                <span className="detalle-tarea-archivo-nombre">
                  {archivo.nombre}
                </span>
                <span className="detalle-tarea-archivo-meta">
                  {formatearTamano(archivo.tamano)} ·{" "}
                  {formatearFecha(archivo.fecha_adjuncion)} ·{" "}
                  {archivo.puede_eliminar ? "Subido por ti" : "Autor desconocido"}
                </span>
              </div>
              <div className="detalle-tarea-archivo-acciones">
                <button
                  type="button"
                  className="detalle-tarea-boton detalle-tarea-boton-secundario detalle-tarea-boton-chico"
                  onClick={() => onDescargar(archivo)}
                  disabled={descargandoId === archivo.id_archivo}
                >
                  {descargandoId === archivo.id_archivo
                    ? "Descargando…"
                    : "Descargar"}
                </button>
                {archivo.puede_eliminar && (
                  <button
                    type="button"
                    className="detalle-tarea-boton detalle-tarea-boton-peligro-borde detalle-tarea-boton-chico"
                    onClick={() => onEliminar(archivo)}
                    disabled
                    title="Próximamente"
                  >
                    Eliminar
                  </button>
                )}
              </div>
            </li>
          ))}
        </ul>
      )}

      {errorDescarga && (
        <p className="detalle-tarea-error" role="alert">
          {errorDescarga}
        </p>
      )}

      {puedeSubir && (
        <div
          className={`detalle-tarea-subida ${limite ? "detalle-tarea-subida-deshabilitada" : ""}`}
        >
          <input
            ref={inputRef}
            type="file"
            className="detalle-tarea-oculto"
            accept=".pdf,.docx,.jpg,.jpeg,.png"
            onChange={onSubir}
            disabled
            tabIndex={-1}
            aria-hidden="true"
          />
          <button
            type="button"
            className="detalle-tarea-boton detalle-tarea-boton-primario"
            onClick={() => inputRef.current?.click()}
            disabled
            title="Próximamente"
            aria-describedby="detalle-tarea-aviso-subida"
          >
            Subir archivo
          </button>
          <p id="detalle-tarea-aviso-subida" className="detalle-tarea-nota">
            {limite
              ? `Esta tarea ya alcanzó el máximo de ${maximo} archivos.`
              : "PDF, DOCX, JPG o PNG, máximo 5 MB"}
          </p>
        </div>
      )}
    </Tarjeta>
  );
}

function SelectorDificultad({
  valor,
  onCambiar,
}: {
  valor: number;
  onCambiar: (nivel: number) => void;
}) {
  return (
    <fieldset className="detalle-tarea-selector">
      <legend className="detalle-tarea-etiqueta">Dificultad real</legend>
      <div className="detalle-tarea-selector-opciones">
        {NIVELES.map((nombre, indice) => {
          const nivel = indice + 1;
          return (
            <label
              key={nombre}
              className={`detalle-tarea-opcion detalle-tarea-nivel-${nivel} ${
                valor === nivel ? "detalle-tarea-opcion-activa" : ""
              }`}
            >
              <input
                type="radio"
                name="dificultad-real"
                value={nivel}
                checked={valor === nivel}
                onChange={() => onCambiar(nivel)}
                className="detalle-tarea-oculto-visual"
              />
              <CaritaPixel nivel={nivel} />
              <span className="detalle-tarea-oculto-visual">{nombre}</span>
            </label>
          );
        })}
        <span
          className={`detalle-tarea-selector-nombre detalle-tarea-nivel-${valor}`}
          aria-hidden="true"
        >
          {NIVELES[valor - 1]}
        </span>
      </div>
    </fieldset>
  );
}

function ModalCompletar({
  abierto,
  segundos,
  enCurso,
  sinArchivos,
  deshabilitado = false,
  onEntregar,
  onCerrar,
}: {
  abierto: boolean;
  segundos: number;
  enCurso: boolean;
  sinArchivos: boolean;
  deshabilitado?: boolean;
  onEntregar: (dificultad: number) => void;
  onCerrar: () => void;
}) {
  const [dificultad, setDificultad] = useState(3);
  const minutos = Math.floor(segundos / 60);
  const sinTiempo = segundos === 0;

  return (
    <Modal abierto={abierto} onCerrar={onCerrar} titulo="Completar mi parte">
      <p className="detalle-tarea-modal-subtitulo">
        Cuéntanos cómo te fue antes de entregar.
      </p>

      <div className="detalle-tarea-tiempo-registrado">
        <span className="detalle-tarea-etiqueta">Tiempo registrado</span>
        <output>{sinTiempo ? "0 min" : formatearDuracion(minutos || 1)}</output>
      </div>

      <SelectorDificultad valor={dificultad} onCambiar={setDificultad} />

      {enCurso && (
        <p className="detalle-tarea-error" role="alert">
          Pausa tu cronómetro antes de completar tu parte.
        </p>
      )}
      {!enCurso && sinTiempo && (
        <p className="detalle-tarea-aviso">
          No registraste tiempo en el cronómetro. ¿Completar de todos modos?
        </p>
      )}
      {sinArchivos && (
        <p className="detalle-tarea-aviso">
          Aún no has subido ningún archivo a esta tarea. ¿Quieres entregarla de
          todos modos?
        </p>
      )}

      <div className="detalle-tarea-modal-acciones">
        <button
          type="button"
          className="detalle-tarea-boton detalle-tarea-boton-secundario"
          onClick={onCerrar}
        >
          Volver
        </button>
        <button
          type="button"
          className="detalle-tarea-boton detalle-tarea-boton-primario"
          disabled={enCurso || deshabilitado}
          title={deshabilitado ? "Próximamente" : undefined}
          onClick={() => onEntregar(dificultad)}
        >
          {sinArchivos ? "Entregar sin archivos" : "Entregar"}
        </button>
      </div>
    </Modal>
  );
}

function AccionesLider({
  completada,
  onEditar,
  onEliminar,
  onReabrir,
}: {
  completada: boolean;
  onEditar: () => void;
  onEliminar: () => void;
  onReabrir: () => void;
}) {
  return (
    <Tarjeta
      titulo="Acciones del líder"
      extra={<span className="detalle-tarea-etiqueta-personal">Líder</span>}
    >
      <div className="detalle-tarea-acciones-lider">
        <button
          type="button"
          className="detalle-tarea-boton detalle-tarea-boton-secundario"
          disabled
          title="Próximamente"
          onClick={onEditar}
          aria-describedby={
            completada ? "detalle-tarea-nota-editar" : undefined
          }
        >
          Editar tarea
        </button>
        {completada && (
          <button
            type="button"
            className="detalle-tarea-boton detalle-tarea-boton-primario"
            disabled
            title="Próximamente"
            onClick={onReabrir}
          >
            Reabrir tarea
          </button>
        )}
        <button
          type="button"
          className="detalle-tarea-boton detalle-tarea-boton-peligro"
          disabled
          title="Próximamente"
          onClick={onEliminar}
        >
          Eliminar tarea
        </button>
      </div>
      {completada && (
        <p id="detalle-tarea-nota-editar" className="detalle-tarea-nota">
          Esta tarea está completada. Reábrela para editarla.
        </p>
      )}
    </Tarjeta>
  );
}

function Esqueleto() {
  return (
    <div
      className="detalle-tarea-esqueleto"
      aria-busy="true"
      aria-label="Cargando tarea"
    >
      <div className="detalle-tarea-esq-bloque detalle-tarea-esq-titulo" />
      <div className="detalle-tarea-esq-fila">
        <div className="detalle-tarea-esq-bloque detalle-tarea-esq-chip" />
        <div className="detalle-tarea-esq-bloque detalle-tarea-esq-chip" />
      </div>
      <div className="detalle-tarea-cuadricula">
        <div className="detalle-tarea-columna">
          <div className="detalle-tarea-esq-bloque detalle-tarea-esq-tarjeta" />
          <div className="detalle-tarea-esq-bloque detalle-tarea-esq-tarjeta-baja" />
          <div className="detalle-tarea-esq-bloque detalle-tarea-esq-tarjeta" />
        </div>
        <div className="detalle-tarea-columna">
          <div className="detalle-tarea-esq-bloque detalle-tarea-esq-tarjeta" />
        </div>
      </div>
    </div>
  );
}

function MensajeCentral({
  titulo,
  texto,
  accion,
}: {
  titulo: string;
  texto: string;
  accion?: ReactNode;
}) {
  return (
    <div className="detalle-tarea-mensaje-central" role="alert">
      <h1 className="detalle-tarea-mensaje-titulo">{titulo}</h1>
      <p>{texto}</p>
      {accion}
    </div>
  );
}

function DetalleTareaGrupoPage() {
  const { idGrupo, idTarea } = useParams();
  const idG = Number(idGrupo);
  const idT = Number(idTarea);
  const idUsuarioActual = obtenerIdUsuarioActual();

  const [grupo, setGrupo] = useState<GrupoConRol | null>(null);
  const [tarea, setTarea] = useState<TareaBackend | null>(null);
  const [asignados, setAsignados] = useState<IntegranteAsignadoBackend[]>([]);
  const [archivos, setArchivos] = useState<ArchivoTarea[]>([]);
  const [categorias, setCategorias] = useState<Categoria[]>([]);
  const [tiempoPropioSegundos, setTiempoPropioSegundos] = useState<
    number | null
  >(null);
  const [estado, setEstado] = useState<EstadoPantalla>("cargando");
  const [descargandoId, setDescargandoId] = useState<number | null>(null);
  const [errorDescarga, setErrorDescarga] = useState<string | null>(null);
  const [modalCompletar, setModalCompletar] = useState(false);
  const [confirmarEliminarTarea, setConfirmarEliminarTarea] = useState(false);
  const [confirmarReabrir, setConfirmarReabrir] = useState(false);
  const [archivoPorEliminar, setArchivoPorEliminar] =
    useState<ArchivoTarea | null>(null);

  const esLider = grupo?.rol === "lider";
  const yo = asignados.find((asignado) => asignado.id_usuario === idUsuarioActual) ?? null;
  const esAsignado = yo !== null;
  const completada = tarea ? normalizarEstado(tarea.estado) === "completada" : false;
  const puedeTrabajar = esAsignado && !yo?.completado && !completada;
  const sinArchivosPropios = archivos.filter((archivo) => archivo.puede_eliminar).length === 0;

  const nombreCategoria = useMemo(() => {
    if (!tarea) return "Sin categoría";
    return (
      categorias.find((categoria) => categoria.id_categoria === tarea.id_categoria)
        ?.nombre_categoria ?? "Sin categoría"
    );
  }, [categorias, tarea]);

  const cargar = useCallback(async () => {
    setEstado("cargando");
    try {
      const misGrupos = await listarMisGrupos();
      const grupoEncontrado =
        misGrupos.find((grupoActual) => grupoActual.id_grupo === idG) ?? null;
      if (!grupoEncontrado) {
        setGrupo(null);
        setEstado("sin-permisos");
        return;
      }
      setGrupo(grupoEncontrado);

      const [tareaDatos, asignadosDatos, archivosDatos, categoriasDatos, sesiones] =
        await Promise.all([
          obtenerTarea(idT),
          listarAsignadosTarea(idT),
          listarArchivosTarea(idT),
          listarCategorias().catch(() => [] as Categoria[]),
          idUsuarioActual != null
            ? listarSesionesUsuario(idUsuarioActual).catch(() => null)
            : Promise.resolve(null as SesionCronometroBackend[] | null),
        ]);

      if (tareaDatos.id_grupo !== idG) {
        setEstado("no-encontrada");
        return;
      }

      setTarea(tareaDatos);
      setAsignados(asignadosDatos);
      setArchivos(archivosDatos);
      setCategorias(categoriasDatos);
      setTiempoPropioSegundos(
        sesiones
          ? sesiones
              .filter(
                (sesion) =>
                  sesion.id_tarea === idT && sesion.duracion != null,
              )
              .reduce(
                (total, sesion) => total + (sesion.duracion ?? 0),
                0,
              )
          : null,
      );
      setEstado("lista");
    } catch (err) {
      const mensaje = (err instanceof Error ? err.message : "").toLowerCase();
      if (
        mensaje.includes("permiso") ||
        mensaje.includes("403") ||
        mensaje.includes("forbidden")
      ) {
        setEstado("sin-permisos");
      } else if (
        mensaje.includes("no encontrada") ||
        mensaje.includes("404")
      ) {
        setEstado("no-encontrada");
      } else {
        setEstado("error");
      }
    }
  }, [idG, idT, idUsuarioActual]);

  useEffect(() => {
    if (!Number.isNaN(idG) && !Number.isNaN(idT)) void cargar();
  }, [cargar, idG, idT]);

  async function descargar(archivo: ArchivoTarea) {
    setErrorDescarga(null);
    setDescargandoId(archivo.id_archivo);
    try {
      const blob = await descargarArchivoTarea(idT, archivo.id_archivo);
      const url = URL.createObjectURL(blob);
      const enlace = document.createElement("a");
      enlace.href = url;
      enlace.download = archivo.nombre;
      document.body.appendChild(enlace);
      enlace.click();
      enlace.remove();
      window.setTimeout(() => URL.revokeObjectURL(url), 0);
    } catch (err) {
      const mensaje = (err instanceof Error ? err.message : "").toLowerCase();
      setErrorDescarga(
        mensaje.includes("permiso") ||
          mensaje.includes("403") ||
          mensaje.includes("forbidden")
          ? "No tienes permiso para descargar este archivo."
          : "No se pudo descargar el archivo.",
      );
    } finally {
      setDescargandoId(null);
    }
  }

  if (Number.isNaN(idG) || Number.isNaN(idT)) {
    return <Navigate to="/grupos" replace />;
  }

  if (estado === "cargando") {
    return (
      <div className="detalle-tarea-pagina">
        <div className="detalle-tarea-contenedor">
          <Esqueleto />
        </div>
      </div>
    );
  }

  if (estado === "sin-permisos") {
    return (
      <div className="detalle-tarea-pagina">
        <div className="detalle-tarea-contenedor">
          <MensajeCentral
            titulo="Sin acceso"
            texto="No perteneces a este grupo."
            accion={
              <Link to="/grupos" className="detalle-tarea-volver">
                ← Volver a Mis Grupos
              </Link>
            }
          />
        </div>
      </div>
    );
  }

  if (estado === "no-encontrada") {
    return (
      <div className="detalle-tarea-pagina">
        <div className="detalle-tarea-contenedor">
          <MensajeCentral
            titulo="Tarea no encontrada"
            texto="La tarea que buscas no existe o fue eliminada."
            accion={
              <Link
                to={`/grupos/${idG}/tareas`}
                className="detalle-tarea-volver"
              >
                ← Volver a las tareas del grupo
              </Link>
            }
          />
        </div>
      </div>
    );
  }

  if (estado === "error" || !tarea || !grupo) {
    return (
      <div className="detalle-tarea-pagina">
        <div className="detalle-tarea-contenedor">
          <MensajeCentral
            titulo="No pudimos cargar la tarea"
            texto="Revisa tu conexión e inténtalo otra vez."
            accion={
              <button
                type="button"
                className="detalle-tarea-boton detalle-tarea-boton-primario"
                onClick={() => void cargar()}
              >
                Reintentar
              </button>
            }
          />
        </div>
      </div>
    );
  }

  return (
    <div className="detalle-tarea-pagina">
      <div className="detalle-tarea-contenedor">
        <Link to={`/grupos/${idG}/tareas`} className="detalle-tarea-volver">
          <span aria-hidden="true">←</span> Volver a las tareas del grupo
        </Link>

        {completada && (
          <div className="detalle-tarea-banner" role="status">
            <span className="detalle-tarea-banner-marca" aria-hidden="true" />
            Esta tarea está completada
          </div>
        )}

        <Encabezado
          tarea={tarea}
          esTuya={esAsignado}
          sinArchivos={archivos.length === 0}
        />

        {!esAsignado && (
          <p className="detalle-tarea-solo-lectura">
            No estás asignado a esta tarea. Solo puedes consultarla.
          </p>
        )}

        <div className="detalle-tarea-cuadricula">
          <div className="detalle-tarea-columna">
            <InfoTarea
              tarea={tarea}
              categoria={nombreCategoria}
              prioridad={mapearPrioridad(tarea.prioridad)}
            />
            <Progreso asignados={asignados} />
            <ListaAsignados
              asignados={asignados}
              idUsuarioActual={idUsuarioActual}
            />
            <TiemposIntegrantes
              asignados={asignados}
              idUsuarioActual={idUsuarioActual}
              tiempoPropioSegundos={tiempoPropioSegundos}
            />
          </div>

          <aside className="detalle-tarea-columna" aria-label="Acciones">
            {puedeTrabajar && <MiCronometro />}

            {esAsignado && !completada && (
              <div className="detalle-tarea-completar">
                {yo?.completado ? (
                  <p className="detalle-tarea-completado-ok" role="status">
                    <span
                      className="detalle-tarea-check"
                      aria-hidden="true"
                    />
                    Tu parte está completada
                  </p>
                ) : (
                  <button
                    type="button"
                    className="detalle-tarea-boton detalle-tarea-boton-primario detalle-tarea-boton-grande"
                    disabled
                    title="Próximamente"
                    onClick={() => setModalCompletar(true)}
                  >
                    Completar mi parte
                  </button>
                )}
              </div>
            )}

            <Archivos
              archivos={archivos}
              maximo={tarea.max_archivos}
              puedeSubir={puedeTrabajar}
              descargandoId={descargandoId}
              errorDescarga={errorDescarga}
              onSubir={() => {}}
              onEliminar={(archivo) => setArchivoPorEliminar(archivo)}
              onDescargar={(archivo) => void descargar(archivo)}
            />

            {esLider && (
              <AccionesLider
                completada={completada}
                onEditar={() => {}}
                onEliminar={() => setConfirmarEliminarTarea(true)}
                onReabrir={() => setConfirmarReabrir(true)}
              />
            )}
          </aside>
        </div>

        <ModalCompletar
          abierto={modalCompletar && puedeTrabajar}
          segundos={0}
          enCurso={false}
          sinArchivos={sinArchivosPropios}
          deshabilitado
          onEntregar={() => {}}
          onCerrar={() => setModalCompletar(false)}
        />

        <DialogoConfirmacion
          abierto={confirmarEliminarTarea}
          titulo="Eliminar tarea"
          peligro
          textoConfirmar="Eliminar"
          deshabilitado
          mensaje={
            <>
              <p>
                ¿Eliminar «{tarea.nombre}»? Se borrarán sus archivos, tiempos y
                asignaciones para todos. No se puede deshacer.
              </p>
              {completada && (
                <p>Como está completada, también saldrá del historial.</p>
              )}
            </>
          }
          onConfirmar={() => setConfirmarEliminarTarea(false)}
          onCancelar={() => setConfirmarEliminarTarea(false)}
        />

        <DialogoConfirmacion
          abierto={confirmarReabrir}
          titulo="Reabrir tarea"
          textoConfirmar="Reabrir"
          deshabilitado
          mensaje={
            <p>
              ¿Reabrir esta tarea? Se borrarán las entregas de todos los
              asignados (dificultad y tiempo registrados) y tendrán que
              completar su parte otra vez. Los archivos se conservan.
            </p>
          }
          onConfirmar={() => setConfirmarReabrir(false)}
          onCancelar={() => setConfirmarReabrir(false)}
        />

        <DialogoConfirmacion
          abierto={archivoPorEliminar !== null}
          titulo="Eliminar archivo"
          peligro
          textoConfirmar="Eliminar"
          deshabilitado
          mensaje={<p>¿Eliminar este archivo? No se puede deshacer.</p>}
          onConfirmar={() => setArchivoPorEliminar(null)}
          onCancelar={() => setArchivoPorEliminar(null)}
        />
      </div>
    </div>
  );
}

export default DetalleTareaGrupoPage;
