// src/components/common/PanelNotificaciones.tsx
import { useEffect, useState, useRef } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import type { RootState, AppDispatch } from '../../store/store';
import { obtenerNotificaciones } from '../../store/notificacionesSlice';

export function PanelNotificaciones() {
  const dispatch = useDispatch<AppDispatch>();
  const { lista, cargando } = useSelector((state: RootState) => state.notificaciones);
  const [panelAbierto, setPanelAbierto] = useState(false);
  const refContenedor = useRef<HTMLDivElement>(null);

  // Disparamos la petición a la API al montar el componente globalmente
  useEffect(() => {
    dispatch(obtenerNotificaciones());
  }, [dispatch]);

  // Contamos cuántas notificaciones no han sido leídas (estado === false)
  const noLeidas = lista.filter((n) => !n.estado).length;

  // Opcional: Cerrar el panel si se hace clic fuera de él
  useEffect(() => {
    const manejarClickFuera = (event: MouseEvent) => {
      if (refContenedor.current && !refContenedor.current.contains(event.target as Node)) {
        setPanelAbierto(false);
      }
    };
    document.addEventListener('mousedown', manejarClickFuera);
    return () => document.removeEventListener('mousedown', manejarClickFuera);
  }, []);

  return (
    <div ref={refContenedor} style={{ position: 'relative', display: 'inline-block' }}>
      {/* Botón de la campanita integrado al estilo del Topbar */}
      <button 
        className="btn-notificacion" 
        onClick={() => setPanelAbierto(!panelAbierto)}
        aria-label="Notificaciones"
        style={{ background: 'none', border: 'none', cursor: 'pointer', position: 'relative', fontSize: '1.2rem', padding: '4px' }}
      >
        🔔
        {noLeidas > 0 && (
          <span style={{
            position: 'absolute',
            top: '0',
            right: '0',
            background: '#ff4d4d',
            color: 'white',
            borderRadius: '50%',
            padding: '1px 5px',
            fontSize: '0.65rem',
            fontWeight: 'bold',
            fontFamily: 'var(--pixel-font-display)'
          }}>
            {noLeidas}
          </span>
        )}
      </button>

      {/* Menú desplegable del panel */}
      {panelAbierto && (
        <div className="pixel-panel" style={{
          position: 'absolute',
          right: 0,
          top: '120%',
          width: '320px',
          background: 'var(--pixel-panel, #fff)',
          border: '2px solid var(--pixel-border-strong, #ccc)',
          padding: '14px',
          zIndex: 1100,
          boxShadow: '0 8px 24px rgba(0,0,0,0.2)'
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px', borderBottom: '1px solid var(--pixel-border, #eee)', paddingBottom: '8px' }}>
            <span style={{ fontFamily: 'var(--pixel-font-display)', fontSize: '0.8rem', fontWeight: 'bold' }}>NOTIFICACIONES</span>
            <span style={{ fontSize: '0.75rem', color: 'var(--pixel-ink-faint, #777)' }}>{lista.length} total</span>
          </div>

          {cargando && <p style={{ fontSize: '0.85rem', textAlign: 'center', margin: '15px 0' }}>Sincronizando alertas...</p>}
          
          {!cargando && lista.length === 0 && (
            <p style={{ fontSize: '0.82rem', textAlign: 'center', color: 'var(--pixel-ink-faint, #777)', margin: '15px 0' }}>
              No hay notificaciones registradas.
            </p>
          )}

          <ul style={{ listStyle: 'none', padding: 0, margin: 0, maxHeight: '260px', overflowY: 'auto' }}>
            {lista.map((notif) => (
              <li key={notif.id_notificacion} style={{ 
                padding: '10px 8px', 
                borderBottom: '1px solid var(--pixel-border, #f0f0f0)',
                backgroundColor: notif.estado ? 'transparent' : 'rgba(124, 92, 255, 0.05)'
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline' }}>
                  <strong style={{ fontSize: '0.85rem', color: 'var(--pixel-ink, #222)' }}>{notif.titulo}</strong>
                  <span style={{ fontSize: '0.65rem', color: 'var(--pixel-ink-faint, #888)' }}>{notif.fecha_envio?.slice(5, 10)}</span>
                </div>
                <p style={{ margin: '4px 0 0 0', fontSize: '0.78rem', color: 'var(--pixel-ink-soft, #555)', lineHeight: '1.3' }}>
                  {notif.detalles}
                </p>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}