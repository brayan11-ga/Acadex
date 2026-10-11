// src/components/ModalConfirmacion.tsx
import React, { useEffect, useId, useRef } from 'react';
import { createPortal } from 'react-dom';
import '../../styles/ModalConfirmacion.css';

interface ModalConfirmacionProps {
  isOpen: boolean;
  title: string;
  message: string;
  onConfirm: () => void;
  onCancel: () => void;
}

export const ModalConfirmacion: React.FC<ModalConfirmacionProps> = ({
  isOpen,
  title,
  message,
  onConfirm,
  onCancel,
}) => {
  const titleId = useId();
  const messageId = useId();
  const dialogRef = useRef<HTMLDivElement>(null);
  const cancelButtonRef = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    if (!isOpen) return;

    const previouslyFocused = document.activeElement instanceof HTMLElement
      ? document.activeElement
      : null;
    cancelButtonRef.current?.focus();

    return () => previouslyFocused?.focus();
  }, [isOpen]);

  if (!isOpen) return null;

  const manejarTeclado = (event: React.KeyboardEvent<HTMLDivElement>) => {
    if (event.key === 'Escape') {
      event.preventDefault();
      onCancel();
      return;
    }

    if (event.key !== 'Tab') return;

    const elementosEnfocables = dialogRef.current?.querySelectorAll<HTMLElement>(
      'button:not(:disabled), [href], input:not(:disabled), select:not(:disabled), textarea:not(:disabled), [tabindex]:not([tabindex="-1"])',
    );
    if (!elementosEnfocables?.length) {
      event.preventDefault();
      return;
    }

    const primero = elementosEnfocables[0];
    const ultimo = elementosEnfocables[elementosEnfocables.length - 1];

    if (event.shiftKey && document.activeElement === primero) {
      event.preventDefault();
      ultimo.focus();
    } else if (!event.shiftKey && document.activeElement === ultimo) {
      event.preventDefault();
      primero.focus();
    }
  };

  return createPortal(
    <div className="confirmacion-overlay">
      <div
        ref={dialogRef}
        className="confirmacion-content"
        role="alertdialog"
        aria-modal="true"
        aria-labelledby={titleId}
        aria-describedby={messageId}
        tabIndex={-1}
        onKeyDown={manejarTeclado}
      >
        <h3 id={titleId} className="confirmacion-title">{title}</h3>
        <p id={messageId} className="confirmacion-message">{message}</p>
        <div className="confirmacion-actions">
          <button
            ref={cancelButtonRef}
            type="button"
            onClick={onCancel}
            className="confirmacion-button confirmacion-button-cancel"
          >
            Cancelar
          </button>
          <button
            type="button"
            onClick={onConfirm}
            className="confirmacion-button confirmacion-button-confirm"
          >
            Confirmar
          </button>
        </div>
      </div>
    </div>,
    document.body,
  );
};
