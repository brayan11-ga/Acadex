import { useRef, useState } from "react";
import { FileImage, FileText, Paperclip, Sparkles, UploadCloud, X } from "lucide-react";
import { claveArchivo, validarArchivoAdjunto } from "./validacionArchivosTarea";

function mostrarTamano(tamano: number): string {
  if (tamano < 1024) return `${tamano} B`;
  if (tamano < 1024 * 1024) return `${(tamano / 1024).toFixed(1)} KB`;
  return `${(tamano / 1024 / 1024).toFixed(2)} MB`;
}

function IconoArchivo({ nombre }: { nombre: string }) {
  const extension = nombre.split(".").pop()?.toLowerCase();
  const Icono = ["png", "jpg", "jpeg"].includes(extension ?? "") ? FileImage : FileText;
  return <Icono aria-hidden="true" size={18} />;
}

interface SelectorArchivosPendientesProps {
  archivos: File[];
  archivoAnalisisIA: File | null;
  analisisDisponible: boolean;
  analizando: boolean;
  avisoIA: string | null;
  errorIA: string | null;
  disabled?: boolean;
  disabledIA?: boolean;
  adjuntosHabilitados?: boolean;
  onAgregar: (archivos: File[]) => void;
  onQuitar: (archivo: File) => void;
  onSeleccionarArchivo: (archivo: File | null) => void;
  onAnalizar: () => void;
}

export function SelectorArchivosPendientes({
  archivos,
  archivoAnalisisIA,
  analisisDisponible,
  analizando,
  avisoIA,
  errorIA,
  disabled = false,
  disabledIA = false,
  adjuntosHabilitados = false,
  onAgregar,
  onQuitar,
  onSeleccionarArchivo,
  onAnalizar,
}: SelectorArchivosPendientesProps) {
  const [arrastrando, setArrastrando] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const agregarArchivos = (seleccion: FileList | File[]) => {
    if (!adjuntosHabilitados) {
      const candidatos = Array.from(seleccion);
      const pdf = candidatos.at(-1);
      if (!pdf) {
        onSeleccionarArchivo(null);
        return;
      }
      const problema = validarArchivoAdjunto(pdf);
      if (problema) {
        onSeleccionarArchivo(null);
        setError(problema);
      } else if (
        !pdf.name.toLowerCase().endsWith(".pdf")
        || pdf.type !== "application/pdf"
      ) {
        onSeleccionarArchivo(null);
        setError("Para autocompletar con IA, elige un archivo PDF válido.");
      } else {
        onSeleccionarArchivo(pdf);
        setError(candidatos.length > 1 ? "Selecciona un solo PDF para el análisis." : null);
      }
      if (inputRef.current) inputRef.current.value = "";
      return;
    }

    const validos: File[] = [];
    const errores: string[] = [];
    const seleccionadosValidos: File[] = [];
    const existentes = new Set(archivos.map(claveArchivo));

    for (const archivo of Array.from(seleccion)) {
      const problema = validarArchivoAdjunto(archivo);
      if (problema) {
        errores.push(problema);
      } else {
        seleccionadosValidos.push(archivo);
        if (!existentes.has(claveArchivo(archivo))) {
          existentes.add(claveArchivo(archivo));
          validos.push(archivo);
        }
      }
    }

    onSeleccionarArchivo(seleccionadosValidos[seleccionadosValidos.length - 1] ?? null);
    if (validos.length > 0) onAgregar(validos);
    setError(errores.length > 0 ? errores.join(" ") : null);
    if (inputRef.current) inputRef.current.value = "";
  };

  const claveAnalisisIA = archivoAnalisisIA ? claveArchivo(archivoAnalisisIA) : null;
  const archivosMostrados = adjuntosHabilitados
    ? archivos
    : archivoAnalisisIA ? [archivoAnalisisIA] : [];

  return (
    <section className="pixel-form-adjuntos" aria-labelledby="titulo-adjuntos-pendientes">
      <div className="pixel-form-adjuntos-header">
        <div>
          <h3 id="titulo-adjuntos-pendientes">
            {adjuntosHabilitados ? <Paperclip aria-hidden="true" size={17} /> : <Sparkles aria-hidden="true" size={17} />}
            {adjuntosHabilitados ? "Archivos adjuntos" : "Autocompletar tarea con IA"}
          </h3>
          <p>{adjuntosHabilitados
            ? "Se guardarán junto con la tarea. PDF, DOCX, JPG o PNG; hasta 5 MB cada uno."
            : "Selecciona un PDF de hasta 5 MB. Se analizará para sugerir datos y no se guardará como adjunto."}</p>
        </div>
        <div className="pixel-form-adjuntos-meta">
          <span className="pixel-form-adjuntos-opcional">OPCIONAL</span>
          {adjuntosHabilitados && (
            <span className="pixel-form-adjuntos-contador" aria-label={`${archivos.length} archivos seleccionados`}>
              {archivos.length}
            </span>
          )}
          <div className="pixel-form-adjuntos-ia">
            <button
              type="button"
              className={`pixel-form-adjuntos-ia-boton${analisisDisponible ? " disponible" : ""}`}
              aria-disabled={!analisisDisponible}
              disabled={disabled || disabledIA || analizando}
              onClick={onAnalizar}
            >
              <Sparkles aria-hidden="true" size={15} />
              {analizando ? "Autocompletando…" : "Autocompletar con IA"}
            </button>
          </div>
        </div>
      </div>

      <p className="pixel-form-adjuntos-ia-aviso" role="status">
        <Sparkles aria-hidden="true" size={14} />
        {analisisDisponible
          ? "PDF listo: puedes autocompletar la tarea con IA."
          : adjuntosHabilitados
            ? "Solo puedes autocompletar con IA al adjuntar un PDF."
            : "Solo puedes autocompletar con IA al seleccionar un PDF."}
      </p>

      {adjuntosHabilitados ? <div
        className={`pixel-form-adjuntos-zona${arrastrando ? " activa" : ""}${disabled ? " ocupada" : ""}`}
        onDragOver={(evento) => {
          evento.preventDefault();
          if (!disabled) setArrastrando(true);
        }}
        onDragLeave={() => setArrastrando(false)}
        onDrop={(evento) => {
          evento.preventDefault();
          setArrastrando(false);
          if (!disabled) agregarArchivos(evento.dataTransfer.files);
        }}
      >
        <input
          ref={inputRef}
          type="file"
          multiple
          accept=".pdf,.docx,.jpg,.jpeg,.png"
          className="pixel-form-adjuntos-input"
          aria-label="Seleccionar archivos adjuntos de la tarea"
          tabIndex={-1}
          disabled={disabled}
          onChange={(evento) => agregarArchivos(evento.target.files ?? [])}
        />
        <UploadCloud aria-hidden="true" size={22} />
        <span>Arrastra archivos aquí o</span>
        <button
          type="button"
          className="pixel-form-adjuntos-boton"
          disabled={disabled}
          onClick={() => inputRef.current?.click()}
        >
          Seleccionar archivos
        </button>
      </div> : <div className="pixel-form-adjuntos-zona">
        <input
          ref={inputRef}
          type="file"
          accept=".pdf,application/pdf"
          className="pixel-form-adjuntos-input"
          aria-label="Seleccionar PDF para autocompletar"
          tabIndex={-1}
          disabled={disabled || disabledIA}
          onChange={(evento) => agregarArchivos(evento.target.files ?? [])}
        />
        <FileText aria-hidden="true" size={22} />
        <span>El PDF solo se usa para generar sugerencias.</span>
        <button
          type="button"
          className="pixel-form-adjuntos-boton"
          disabled={disabled || disabledIA}
          onClick={() => inputRef.current?.click()}
        >
          Seleccionar PDF
        </button>
      </div>}

      {error && <p className="pixel-error" role="alert">{error}</p>}

      {errorIA && <p className="pixel-ia-mensaje error" role="alert">{errorIA}</p>}
      {avisoIA && <p className="pixel-ia-mensaje" role="status">{avisoIA}</p>}

      {archivosMostrados.length === 0 ? (
        <p className="pixel-form-adjuntos-vacio">Aún no has seleccionado archivos.</p>
      ) : (
        <ul className="pixel-form-adjuntos-lista" aria-label={adjuntosHabilitados
          ? "Archivos que se adjuntarán al crear la tarea"
          : "PDF seleccionado para el análisis de IA"}>
          {archivosMostrados.map((archivo) => {
            const esAnalisisIA = claveAnalisisIA === claveArchivo(archivo);
            return (
              <li className="pixel-form-adjunto" key={claveArchivo(archivo)}>
                <span className="pixel-form-adjunto-icono"><IconoArchivo nombre={archivo.name} /></span>
                <span className="pixel-form-adjunto-info">
                  <strong title={archivo.name}>{archivo.name}</strong>
                  <span>
                    {mostrarTamano(archivo.size)}
                    {esAnalisisIA && <span className="pixel-form-adjunto-ia">
                      {adjuntosHabilitados ? " · Autocompletar + adjunto" : " · Solo análisis de IA"}
                    </span>}
                  </span>
                </span>
                <button
                  type="button"
                  className="pixel-form-adjunto-quitar"
                  aria-label={adjuntosHabilitados
                    ? `Quitar ${archivo.name} de los adjuntos`
                    : `Quitar ${archivo.name} del análisis`}
                  title={`Quitar ${archivo.name}`}
                  disabled={disabled}
                  onClick={() => {
                    setError(null);
                    onQuitar(archivo);
                  }}
                >
                  <X aria-hidden="true" size={17} />
                </button>
              </li>
            );
          })}
        </ul>
      )}
    </section>
  );
}
