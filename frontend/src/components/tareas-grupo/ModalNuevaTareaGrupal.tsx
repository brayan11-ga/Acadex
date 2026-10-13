// Ruta: frontend/src/components/tareas-grupo/ModalNuevaTareaGrupal.tsx
import { useEffect, useState } from "react";
import FormularioNuevaTarea from "../tareas/FormularioNuevaTarea";
import type { IntegranteAsignable } from "../../types/tareaGrupo";
import "../../styles/tareas-grupo.css";

const FORM_ID = "formulario-tarea-grupal-modal";

interface ModalNuevaTareaGrupalProps {
  idGrupo: number;
  integrantes: IntegranteAsignable[];
  usuarioActualId: number | null;
  onCerrar: () => void;
  onCreada: () => void;
}

export default function ModalNuevaTareaGrupal({
  idGrupo,
  integrantes,
  usuarioActualId,
  onCerrar,
  onCreada,
}: ModalNuevaTareaGrupalProps) {
  const [enviando, setEnviando] = useState(false);
  const [confirmandoDescarte, setConfirmandoDescarte] = useState(false);

  function solicitarCierre() {
    if (enviando) return;
    setConfirmandoDescarte(true);
  }

  useEffect(() => {
    function alPulsarTecla(evento: KeyboardEvent) {
      if (evento.key !== "Escape" || enviando) return;
      if (confirmandoDescarte) setConfirmandoDescarte(false);
      else setConfirmandoDescarte(true);
    }
    document.addEventListener("keydown", alPulsarTecla);
    return () => document.removeEventListener("keydown", alPulsarTecla);
  }, [enviando, confirmandoDescarte]);

  useEffect(() => {
    const desbordeAnterior = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    return () => {
      document.body.style.overflow = desbordeAnterior;
    };
  }, []);

  return (
    <div
      className="tareas-grupo-overlay"
      onMouseDown={(evento) => {
        if (evento.target === evento.currentTarget) solicitarCierre();
      }}
    >
      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby="tareas-grupo-modal-titulo"
        aria-describedby="tareas-grupo-modal-subtitulo"
        className="tareas-grupo-modal"
      >
        <header className="tareas-grupo-modal-cabecera">
          <div>
            <h2 id="tareas-grupo-modal-titulo" className="tareas-grupo-modal-titulo">
              Nueva tarea grupal
            </h2>
            <p id="tareas-grupo-modal-subtitulo" className="tareas-grupo-modal-subtitulo">
              Define el objetivo y a quién le toca.
            </p>
          </div>
          <button
            type="button"
            className="tareas-grupo-boton tareas-grupo-boton--descartar"
            onClick={solicitarCierre}
            disabled={enviando}
          >
            ✕ Descartar
          </button>
        </header>

        {confirmandoDescarte && (
          <div className="tareas-grupo-confirmar" role="alertdialog" aria-labelledby="tareas-grupo-confirmar-texto">
            <p id="tareas-grupo-confirmar-texto">¿Descartar los cambios?</p>
            <div className="tareas-grupo-confirmar-acciones">
              <button
                type="button"
                className="tareas-grupo-boton tareas-grupo-boton--secundario tareas-grupo-boton--pequeno"
                autoFocus
                onClick={() => setConfirmandoDescarte(false)}
              >
                Seguir editando
              </button>
              <button
                type="button"
                className="tareas-grupo-boton tareas-grupo-boton--descartar tareas-grupo-boton--pequeno"
                onClick={onCerrar}
              >
                Sí, descartar
              </button>
            </div>
          </div>
        )}

        <fieldset className="tareas-grupo-fieldset" disabled={enviando}>
          <FormularioNuevaTarea
            formId={FORM_ID}
            modo="grupal"
            idGrupo={idGrupo}
            integrantes={integrantes}
            usuarioActualId={usuarioActualId}
            embebidoEnModal
            onDescartar={onCerrar}
            onTareaCreada={onCreada}
            onEstadoEnvioChange={setEnviando}
          />
        </fieldset>

        <div className="tareas-grupo-modal-pie">
          <p className="tareas-grupo-nota">La prioridad se calcula automáticamente.</p>
          <button
            type="submit"
            form={FORM_ID}
            className="tareas-grupo-boton tareas-grupo-boton--primario tareas-grupo-boton--display"
            disabled={enviando}
          >
            {enviando ? "Creando…" : "Crear tarea →"}
          </button>
        </div>
      </div>
    </div>
  );
}
