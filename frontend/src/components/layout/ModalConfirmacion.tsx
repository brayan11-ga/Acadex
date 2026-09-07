// src/components/ModalConfirmacion.tsx
import React from 'react';
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
  if (!isOpen) return null;

  return (
    <div className="modal-overlay">
      <div className="modal-content pixel-panel">
        <h3 className="modal-title">{title}</h3>
        <p className="modal-message">{message}</p>
        <div className="modal-actions">
          <button onClick={onCancel} className="pixel-btn-outline">
            Cancelar
          </button>
          <button onClick={onConfirm} className="pixel-btn-danger">
            Confirmar
          </button>
        </div>
      </div>
    </div>
  );
};