// frontend/src/components/grupos/JoinGroupModal.tsx
import { useState } from "react";
import "../../styles/join-group-modal.css";

interface JoinGroupModalProps {
  isOpen: boolean;
  onClose: () => void;
  onJoin: (codigo: string) => Promise<void>;
}

export function JoinGroupModal({ isOpen, onClose, onJoin }: JoinGroupModalProps) {
  const [code, setCode] = useState("");
  const [enviando, setEnviando] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const trimmed = code.trim().toUpperCase();
    if (trimmed.length < 8) return;

    setEnviando(true);
    setError(null);
    try {
      await onJoin(trimmed);
      setCode("");
    } catch {
      setError("Código inválido o ya perteneces a este grupo.");
    } finally {
      setEnviando(false);
    }
  };

  const handleClose = () => {
    setCode("");
    setError(null);
    onClose();
  };

  return (
    <div className="join-overlay" onClick={handleClose} role="presentation">
      <div
        className="join-card"
        role="dialog"
        aria-modal="true"
        aria-labelledby="join-group-title"
        onClick={(e) => e.stopPropagation()}
      >
        <button className="join-close" onClick={handleClose} aria-label="Cerrar">
          ✕
        </button>
        <h2 id="join-group-title" className="join-title">Unirse a un grupo</h2>
        <p className="join-subtitle">Ingresa el código de acceso de 8 caracteres que te compartieron.</p>
        <form className="join-form" onSubmit={handleSubmit}>
          <label className="join-field">
            <span className="join-field-label">Código de acceso</span>
            <input
              className="join-code-input"
              type="text"
              value={code}
              onChange={(e) => setCode(e.target.value.toUpperCase())}
              placeholder="XXXXXXXX"
              maxLength={8}
              autoFocus
              autoComplete="off"
              spellCheck={false}
            />
          </label>
          {error && <p className="join-field-error">{error}</p>}
          <div className="join-actions">
            <button type="button" className="join-btn join-btn-ghost" onClick={handleClose}>
              Cancelar
            </button>
            <button type="submit" className="join-btn join-btn-primary" disabled={code.trim().length < 8 || enviando}>
              {enviando ? "Uniendo..." : "Unirse"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}