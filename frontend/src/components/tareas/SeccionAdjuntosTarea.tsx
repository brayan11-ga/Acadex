import { useCallback, useEffect, useRef, useState } from "react";
import { createPortal } from "react-dom";
import { Download, Eye, FileImage, FileText, Paperclip, Trash2, UploadCloud, X } from "lucide-react";
import { ModalConfirmacion } from "../layout/ModalConfirmacion";
import {
  descargarArchivoTarea,
  eliminarArchivoTarea,
  listarArchivosTarea,
  subirArchivoTarea,
  type ArchivoTarea,
} from "../../services/tareas";

const MAXIMO_BYTES = 5 * 1024 * 1024;
const EXTENSIONES_PERMITIDAS = new Set([".pdf", ".docx", ".jpg", ".jpeg", ".png"]);

interface SeccionAdjuntosTareaProps {
  idTarea: number;
  modo: "lectura" | "edicion";
}

interface EstadoVistaPrevia {
  archivo: ArchivoTarea;
  url?: string;
  documento?: Blob;
  cargando: boolean;
  error?: string;
}

function mensajeDeError(error: unknown): string {
  return error instanceof Error ? error.message : "Ocurrió un error con los adjuntos.";
}

function mostrarTamano(tamano: number | null): string {
  if (tamano === null) return "Tamaño desconocido";
  if (tamano < 1024) return `${tamano} B`;
  if (tamano < 1024 * 1024) return `${(tamano / 1024).toFixed(1)} KB`;
  return `${(tamano / 1024 / 1024).toFixed(2)} MB`;
}

function IconoArchivo({ nombre }: { nombre: string }) {
  const extension = nombre.split(".").pop()?.toLowerCase();
  const Icono = ["png", "jpg", "jpeg"].includes(extension ?? "") ? FileImage : FileText;
  return <Icono aria-hidden="true" size={19} strokeWidth={1.8} />;
}

export function SeccionAdjuntosTarea({ idTarea, modo }: SeccionAdjuntosTareaProps) {
  const esEditable = modo === "edicion";
  const [adjuntos, setAdjuntos] = useState<ArchivoTarea[]>([]);
  const [archivosSeleccionados, setArchivosSeleccionados] = useState<File[]>([]);
  const [cargandoAdjuntos, setCargandoAdjuntos] = useState(true);
  const [operando, setOperando] = useState(false);
  const [errorAdjuntos, setErrorAdjuntos] = useState<string | null>(null);
  const [mensaje, setMensaje] = useState<string | null>(null);
  const [arrastrando, setArrastrando] = useState(false);
  const [vistaPrevia, setVistaPrevia] = useState<EstadoVistaPrevia | null>(null);
  const [adjuntoAEliminar, setAdjuntoAEliminar] = useState<ArchivoTarea | null>(null);
  const inputArchivosRef = useRef<HTMLInputElement>(null);
  const contenedorDocxRef = useRef<HTMLDivElement>(null);
  const solicitudVistaRef = useRef(0);

  const seleccionarArchivos = (archivos: FileList | File[]) => {
    if (!esEditable) return;
    setArchivosSeleccionados(Array.from(archivos));
    if (inputArchivosRef.current) inputArchivosRef.current.value = "";
    setErrorAdjuntos(null);
    setMensaje(null);
  };

  const cargarAdjuntos = useCallback(async (limpiarError = true) => {
    try {
      const resultado = await listarArchivosTarea(idTarea);
      setAdjuntos(resultado);
      if (limpiarError) setErrorAdjuntos(null);
    } catch (error) {
      setErrorAdjuntos(mensajeDeError(error));
    } finally {
      setCargandoAdjuntos(false);
    }
  }, [idTarea]);

  useEffect(() => {
    let activo = true;
    void listarArchivosTarea(idTarea)
      .then((resultado) => {
        if (activo) setAdjuntos(resultado);
      })
      .catch((error: unknown) => {
        if (activo) setErrorAdjuntos(mensajeDeError(error));
      })
      .finally(() => {
        if (activo) setCargandoAdjuntos(false);
      });

    return () => {
      activo = false;
    };
  }, [idTarea]);

  useEffect(() => {
    const url = vistaPrevia?.url;
    return () => {
      if (url) URL.revokeObjectURL(url);
    };
  }, [vistaPrevia?.url]);

  useEffect(() => {
    const documento = vistaPrevia?.documento;
    const contenedor = contenedorDocxRef.current;
    if (!documento || !contenedor) return;

    let cancelado = false;
    contenedor.replaceChildren();
    const renderizarDocumento = async () => {
      try {
        const { renderAsync } = await import("docx-preview");
        if (cancelado) return;
        await renderAsync(documento, contenedor, contenedor, {
          className: "acadex-docx",
          inWrapper: true,
          ignoreWidth: true,
          ignoreHeight: true,
          breakPages: false,
          renderAltChunks: false,
          renderComments: false,
          renderChanges: false,
          useBase64URL: true,
        });
        for (const enlace of contenedor.querySelectorAll<HTMLAnchorElement>("a[href]")) {
          const destino = enlace.getAttribute("href") ?? "";
          if (!destino) {
            enlace.removeAttribute("href");
            continue;
          }
          if (destino.startsWith("#")) continue;
          try {
            const protocolo = new URL(destino, window.location.origin).protocol;
            if (!["http:", "https:", "mailto:"].includes(protocolo)) {
              enlace.removeAttribute("href");
              continue;
            }
            enlace.target = "_blank";
            enlace.rel = "noopener noreferrer";
          } catch {
            enlace.removeAttribute("href");
          }
        }
        if (!cancelado) {
          setVistaPrevia((actual) => actual?.documento === documento
            ? { ...actual, cargando: false }
            : actual);
        }
      } catch {
        if (!cancelado) {
          setVistaPrevia((actual) => actual?.documento === documento
            ? { ...actual, cargando: false, error: "No se pudo mostrar este documento Word." }
            : actual);
        }
      }
    };
    void renderizarDocumento();

    return () => {
      cancelado = true;
      contenedor.replaceChildren();
    };
  }, [vistaPrevia?.documento]);

  useEffect(() => () => {
    solicitudVistaRef.current += 1;
  }, []);

  const manejarSubida = async () => {
    if (!esEditable || archivosSeleccionados.length === 0) return;

    const invalido = archivosSeleccionados.find((archivo) => {
      const extension = `.${archivo.name.split(".").pop()?.toLowerCase() ?? ""}`;
      return !EXTENSIONES_PERMITIDAS.has(extension) || archivo.size === 0 || archivo.size > MAXIMO_BYTES;
    });
    if (invalido) {
      setErrorAdjuntos(
        invalido.size > MAXIMO_BYTES
          ? `${invalido.name} supera el límite de 5 MB.`
          : `El formato de ${invalido.name} no está admitido. Se admiten PDF, DOCX, JPG y PNG.`,
      );
      return;
    }

    setOperando(true);
    setErrorAdjuntos(null);
    setMensaje(null);
    let subidos = 0;
    try {
      for (const archivo of archivosSeleccionados) {
        await subirArchivoTarea(idTarea, archivo);
        subidos += 1;
      }
      setMensaje(subidos === 1 ? "Adjunto subido." : `Se subieron ${subidos} adjuntos.`);
    } catch (error) {
      const prefijo = subidos > 0 ? `Se subieron ${subidos}; ` : "";
      setErrorAdjuntos(`${prefijo}${mensajeDeError(error)}`);
    } finally {
      setOperando(false);
      setArchivosSeleccionados([]);
      if (inputArchivosRef.current) inputArchivosRef.current.value = "";
      await cargarAdjuntos(false);
    }
  };

  const manejarDescarga = async (adjunto: ArchivoTarea) => {
    setOperando(true);
    setErrorAdjuntos(null);
    setMensaje(null);
    try {
      const blob = await descargarArchivoTarea(idTarea, adjunto.id_archivo);
      const url = URL.createObjectURL(blob);
      const enlace = document.createElement("a");
      enlace.href = url;
      enlace.download = adjunto.nombre;
      document.body.appendChild(enlace);
      enlace.click();
      enlace.remove();
      window.setTimeout(() => URL.revokeObjectURL(url), 0);
    } catch (error) {
      setErrorAdjuntos(mensajeDeError(error));
    } finally {
      setOperando(false);
    }
  };

  const cerrarVistaPrevia = () => {
    solicitudVistaRef.current += 1;
    setVistaPrevia(null);
  };

  const manejarVistaPrevia = async (adjunto: ArchivoTarea) => {
    const solicitud = solicitudVistaRef.current + 1;
    solicitudVistaRef.current = solicitud;
    setVistaPrevia({ archivo: adjunto, cargando: true });

    try {
      const blob = await descargarArchivoTarea(idTarea, adjunto.id_archivo);
      if (solicitudVistaRef.current !== solicitud) return;
      if (adjunto.tipo === "DOCX") {
        setVistaPrevia({ archivo: adjunto, documento: blob, cargando: true });
        return;
      }
      const url = URL.createObjectURL(blob);
      if (solicitudVistaRef.current !== solicitud) {
        URL.revokeObjectURL(url);
        return;
      }
      setVistaPrevia({ archivo: adjunto, url, cargando: false });
    } catch (error) {
      if (solicitudVistaRef.current === solicitud) {
        setVistaPrevia({ archivo: adjunto, cargando: false, error: mensajeDeError(error) });
      }
    }
  };

  const confirmarEliminacion = async () => {
    if (!esEditable || !adjuntoAEliminar?.puede_eliminar) return;

    setOperando(true);
    setErrorAdjuntos(null);
    setMensaje(null);
    try {
      await eliminarArchivoTarea(idTarea, adjuntoAEliminar.id_archivo);
      setMensaje("Adjunto eliminado.");
      setAdjuntos((actuales) => actuales.filter((actual) => actual.id_archivo !== adjuntoAEliminar.id_archivo));
    } catch (error) {
      setErrorAdjuntos(mensajeDeError(error));
    } finally {
      setOperando(false);
      setAdjuntoAEliminar(null);
    }
  };

  const vistaPreviaPortal = vistaPrevia && typeof document !== "undefined"
    ? createPortal(
      <div
        className="pixel-adjunto-vista-overlay"
        onClick={(evento) => {
          evento.stopPropagation();
          cerrarVistaPrevia();
        }}
      >
        <section
          className="pixel-adjunto-vista"
          role="dialog"
          aria-modal="true"
          aria-label={`Vista previa de ${vistaPrevia.archivo.nombre}`}
          onClick={(evento) => evento.stopPropagation()}
        >
          <header className="pixel-adjunto-vista-header">
            <span className="pixel-adjunto-icono"><IconoArchivo nombre={vistaPrevia.archivo.nombre} /></span>
            <div className="pixel-adjunto-vista-titulo">
              <span>VISTA PREVIA</span>
              <strong title={vistaPrevia.archivo.nombre}>{vistaPrevia.archivo.nombre}</strong>
            </div>
            <button
              type="button"
              className="pixel-adjunto-vista-descargar"
              disabled={operando}
              onClick={() => void manejarDescarga(vistaPrevia.archivo)}
            >
              <Download aria-hidden="true" size={16} /> Descargar
            </button>
            <button
              type="button"
              className="pixel-adjunto-vista-cerrar"
              aria-label="Cerrar vista previa"
              onClick={cerrarVistaPrevia}
            >
              <X aria-hidden="true" size={19} />
            </button>
          </header>
          <div className="pixel-adjunto-vista-contenido">
            {vistaPrevia.error ? (
              <p className="pixel-error" role="alert">{vistaPrevia.error}</p>
            ) : vistaPrevia.archivo.tipo === "DOCX" && vistaPrevia.documento ? (
              <div className="pixel-adjunto-vista-docx">
                <p className="pixel-adjunto-vista-nota">
                  Vista previa en el navegador. El diseño puede variar ligeramente respecto a Microsoft Word.
                </p>
                {vistaPrevia.cargando && <p className="pixel-adjunto-vista-estado">Preparando documento…</p>}
                <div
                  ref={contenedorDocxRef}
                  className="pixel-adjunto-docx-render"
                  aria-label={`Contenido de ${vistaPrevia.archivo.nombre}`}
                />
              </div>
            ) : vistaPrevia.cargando ? (
              <p className="pixel-adjunto-vista-estado">Preparando documento…</p>
            ) : vistaPrevia.archivo.tipo === "PDF" && vistaPrevia.url ? (
              <iframe
                className="pixel-adjunto-vista-pdf"
                src={vistaPrevia.url}
                title={`Vista previa de ${vistaPrevia.archivo.nombre}`}
              />
            ) : ["JPG", "PNG"].includes(vistaPrevia.archivo.tipo) && vistaPrevia.url ? (
              <div className="pixel-adjunto-vista-imagen-fondo">
                <img src={vistaPrevia.url} alt={vistaPrevia.archivo.nombre} />
              </div>
            ) : (
              <p className="pixel-adjunto-vista-estado">No se pudo mostrar la vista previa de este formato.</p>
            )}
          </div>
        </section>
      </div>,
      document.body,
    )
    : null;

  return (
    <>
      <section className="pixel-adjuntos" aria-labelledby={`titulo-adjuntos-${idTarea}`}>
        <div className="pixel-adjuntos-encabezado">
          <h3 id={`titulo-adjuntos-${idTarea}`}>
            <Paperclip aria-hidden="true" size={17} /> Adjuntos de la tarea
          </h3>
          {!cargandoAdjuntos && <span className="pixel-adjuntos-contador">{adjuntos.length}</span>}
        </div>
        <p className="pixel-tareas-subtitle">
          {esEditable
            ? "Añade archivos a esta tarea. PDF, DOCX, JPG o PNG, hasta 5 MB cada uno."
            : "Abre un archivo para previsualizarlo o descárgalo."}
        </p>

        {esEditable && (
          <>
            <div
              className={`pixel-adjuntos-zona${arrastrando ? " pixel-adjuntos-zona-activa" : ""}${operando ? " pixel-adjuntos-zona-ocupada" : ""}`}
              onDragOver={(evento) => {
                evento.preventDefault();
                if (!operando) setArrastrando(true);
              }}
              onDragLeave={() => setArrastrando(false)}
              onDrop={(evento) => {
                evento.preventDefault();
                setArrastrando(false);
                if (!operando) seleccionarArchivos(evento.dataTransfer.files);
              }}
            >
              <input
                ref={inputArchivosRef}
                id={`seleccionar-adjuntos-${idTarea}`}
                type="file"
                multiple
                accept=".pdf,.docx,.jpg,.jpeg,.png"
                className="pixel-adjuntos-input"
                aria-label="Seleccionar adjuntos"
                disabled={operando}
                onChange={(evento) => seleccionarArchivos(evento.target.files ?? [])}
              />
              <span className="pixel-adjuntos-icono-subida"><UploadCloud aria-hidden="true" size={23} /></span>
              <strong>Arrastra tus archivos aquí</strong>
              <span className="pixel-adjuntos-o">o</span>
              <button
                type="button"
                className="pixel-adjuntos-boton"
                disabled={operando}
                onClick={() => inputArchivosRef.current?.click()}
              >
                <UploadCloud aria-hidden="true" size={16} />
                <span>SELECCIONAR ARCHIVOS</span>
              </button>
              <span className="pixel-adjuntos-formatos">PDF · DOCX · JPG · PNG</span>
            </div>

            {archivosSeleccionados.length > 0 && (
              <div className="pixel-adjuntos-pendientes" aria-label="Archivos listos para subir">
                <div className="pixel-adjuntos-pendientes-titulo">
                  <strong>
                    {archivosSeleccionados.length === 1
                      ? "Archivo seleccionado"
                      : `${archivosSeleccionados.length} archivos seleccionados`}
                  </strong>
                  <span>Listos para adjuntar</span>
                </div>
                <ul className="pixel-adjuntos-seleccionados">
                  {archivosSeleccionados.map((archivo, indice) => (
                    <li className="pixel-adjunto-seleccionado" key={`${archivo.name}-${archivo.lastModified}-${indice}`}>
                      <span className="pixel-adjunto-icono"><IconoArchivo nombre={archivo.name} /></span>
                      <span className="pixel-adjunto-seleccionado-info">
                        <strong title={archivo.name}>{archivo.name}</strong>
                        <span>{mostrarTamano(archivo.size)}</span>
                      </span>
                      <button
                        type="button"
                        className="pixel-adjunto-quitar"
                        aria-label={`Quitar ${archivo.name}`}
                        title={`Quitar ${archivo.name}`}
                        disabled={operando}
                        onClick={() => {
                          setArchivosSeleccionados((actuales) => actuales.filter((_, i) => i !== indice));
                          if (inputArchivosRef.current) inputArchivosRef.current.value = "";
                        }}
                      >
                        <X aria-hidden="true" size={16} />
                      </button>
                    </li>
                  ))}
                </ul>
                <button
                  type="button"
                  className="pixel-btn-primario pixel-adjuntos-subir"
                  disabled={operando}
                  onClick={() => void manejarSubida()}
                >
                  <UploadCloud aria-hidden="true" size={17} />
                  {operando ? "Subiendo…" : "Subir adjuntos"}
                </button>
              </div>
            )}
          </>
        )}

        {errorAdjuntos && <p className="pixel-error" role="alert">{errorAdjuntos}</p>}
        {mensaje && <p className="pixel-adjuntos-exito" role="status">{mensaje}</p>}
        {cargandoAdjuntos ? (
          <p className="pixel-tareas-subtitle">Cargando adjuntos…</p>
        ) : adjuntos.length === 0 ? (
          <p className="pixel-tareas-subtitle">
            {esEditable ? "Esta tarea aún no tiene adjuntos." : "Esta tarea no tiene adjuntos."}
          </p>
        ) : (
          <ul className="pixel-adjuntos-lista">
            {adjuntos.map((adjunto) => (
              <li className="pixel-adjunto-item" key={adjunto.id_archivo}>
                <span className="pixel-adjunto-icono"><IconoArchivo nombre={adjunto.nombre} /></span>
                <div className="pixel-adjunto-info">
                  <button
                    type="button"
                    className="pixel-adjunto-nombre"
                    title={`Ver ${adjunto.nombre}`}
                    onClick={() => void manejarVistaPrevia(adjunto)}
                  >
                    <Eye aria-hidden="true" size={15} />
                    <span>{adjunto.nombre}</span>
                  </button>
                  <span>
                    <span className="pixel-adjunto-tipo">{adjunto.tipo}</span>
                    <span className="pixel-adjunto-meta">
                      {mostrarTamano(adjunto.tamano)} · {new Date(adjunto.fecha_adjuncion).toLocaleDateString("es-CO")}
                    </span>
                  </span>
                </div>
                <div className="pixel-adjunto-acciones">
                  <button
                    type="button"
                    className="pixel-btn-icono"
                    disabled={operando}
                    onClick={() => void manejarDescarga(adjunto)}
                  >
                    <Download aria-hidden="true" size={15} /> Descargar
                  </button>
                  {esEditable && adjunto.puede_eliminar && (
                    <button
                      type="button"
                      className="pixel-btn-icono pixel-btn-peligro"
                      disabled={operando}
                      onClick={() => setAdjuntoAEliminar(adjunto)}
                    >
                      <Trash2 aria-hidden="true" size={15} /> Eliminar
                    </button>
                  )}
                </div>
              </li>
            ))}
          </ul>
        )}
      </section>

      {esEditable && (
        <ModalConfirmacion
          isOpen={adjuntoAEliminar !== null}
          title="¿Eliminar adjunto?"
          message={adjuntoAEliminar ? `Se eliminará “${adjuntoAEliminar.nombre}”. Esta acción no se puede deshacer.` : ""}
          onConfirm={() => void confirmarEliminacion()}
          onCancel={() => setAdjuntoAEliminar(null)}
        />
      )}

      {vistaPreviaPortal}
    </>
  );
}
