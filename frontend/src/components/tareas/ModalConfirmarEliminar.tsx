// ModalConfirmarEliminar.tsx
interface ModalConfirmarEliminar{
    onConfirmar:()=>void
    onCancelar:()=>void
}

export const ModalConfirmarEliminar=({
    onConfirmar,
    onCancelar,
}:ModalConfirmarEliminar)=>(
    <div className="pixel-modal-overlay" onClick={onCancelar}>
        <div className="pixel-modal-content" onClick={(e)=>e.stopPropagation()}>
            <div className="pixel-panel">
                <div className="pixel-panel-header">
                    <h2 className="pixel-panel-title">Eliminiar Tarea</h2>
                </div>
                <p>¿Seguro que quieres eliminar esta tarea?</p>
                <div style={{display:"flex", gap:"0.8rem", justifyContent:"flex-end", marginTop:"1.5rem"}}>
                    <button type="button" className="pixel-btn-icono pixel-btn-peligro" onClick={onConfirmar}>
                        Cancelar
                    </button>
                    <button type="button" className="pixel-btn-icono pixel-btn-peligro" onClick={onConfirmar}>
                        Eliminar
                    </button>
                </div>
            </div>
        </div>
    </div>
);