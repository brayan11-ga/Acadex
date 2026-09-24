// frontend/src/components/grupos/CreateGroupModal.tsx
import { useState } from "react";
import type { Grupo } from "../../types/grupo";
import "../../styles/create-group-modal.css";

interface CreateGroupModalProps {
  isOpen: boolean;
  onClose: () => void;
  onCreate: (datos: { nombre_grupo: string; descripcion: string }) => Promise<Grupo>;
}

export function CreateGroupModal({ isOpen, onClose, onCreate }: CreateGroupModalProps) {
  const [nombre, setNombre] = useState("");
  const [descripcion, setDescripcion] = useState("");
  const [createdCode, setCreatedCode] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);
  const [enviando, setEnviando] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const trimmed = nombre.trim();
    if (!trimmed) return;

    setEnviando(true);
    setError(null);
    try {
      const grupo = await onCreate({ nombre_grupo: trimmed, descripcion: descripcion.trim() });
      setCreatedCode(grupo.codigo_acceso);
    } catch (err) {
      setError("No se pudo crear el grupo. Intenta de nuevo.");
    } finally {
      setEnviando(false);
    }
  };

  const handleCopy = async () => {
    if (!createdCode) return;
    try {
      await navigator.clipboard.writeText(createdCode);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      setCopied(false);
    }
  };

  const handleClose = () => {
    setNombre("");
    setDescripcion("");
    setCreatedCode(null);
    setCopied(false);
    setError(null);
    onClose();
  };

  return (
    <div className="modal-overlay" onClick={handleClose} role="presentation">
      <div
        className="modal-card"
        role="dialog"
        aria-modal="true"
        aria-labelledby="create-group-title"
        onClick={(e) => e.stopPropagation()}
      >
        <button className="modal-close" onClick={handleClose} aria-label="Cerrar">
          ✕
        </button>

        {createdCode === null ? (
          <>
            <h2 id="create-group-title" className="modal-title">Crear grupo</h2>
            <p className="modal-subtitle">Crea un grupo de estudio y comparte el código con tus compañeros.</p>

            <form className="modal-form" onSubmit={handleSubmit}>
              <label className="field">
                <span className="field-label">Nombre del grupo</span>
                <input
                  className="field-input"
                  type="text"
                  value={nombre}
                  onChange={(e) => setNombre(e.target.value)}
                  placeholder="Ej. Cálculo I - Grupo de estudio"
                  maxLength={60}
                  autoFocus
                />
              </label>

              <label className="field">
                <span className="field-label">
                  Descripción <span className="field-optional">(opcional)</span>
                </span>
                <textarea
                  className="field-input field-textarea"
                  value={descripcion}
                  onChange={(e) => setDescripcion(e.target.value)}
                  placeholder="¿De qué trata el grupo?"
                  rows={3}
                  maxLength={200}
                />
              </label>

              {error && <p className="field-error">{error}</p>}

              <div className="modal-actions">
                <button type="button" className="btn btn-ghost" onClick={handleClose}>
                  Cancelar
                </button>
                <button type="submit" className="btn btn-primary" disabled={!nombre.trim() || enviando}>
                  {enviando ? "Creando..." : "Crear"}
                </button>
              </div>
            </form>
          </>
        ) : (
          <div className="success-view">
            <div className="success-check" aria-hidden="true">✓</div>
            <h2 className="modal-title">¡Grupo creado!</h2>
            <p className="modal-subtitle">Comparte este código de acceso para que otros se unan.</p>

            <div className="code-box">
              <span className="code-value">{createdCode}</span>
              <button className="btn btn-primary code-copy" onClick={handleCopy}>
                {copied ? "¡Copiado!" : "Copiar"}
              </button>
            </div>

            <div className="modal-actions modal-actions-center">
              <button className="btn btn-ghost" onClick={handleClose}>Listo</button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}