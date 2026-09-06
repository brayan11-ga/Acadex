// src/pages/Perfil.tsx
import { useState, useEffect } from "react";
import "../styles/perfil.css";
import {
  obtenerMiPerfil,
  actualizarMiPerfil,
  type PerfilBackend,
} from "../services/perfil";

function Perfil() {
  const [perfil, setPerfil] = useState<PerfilBackend | null>(null);
  const [cargando, setCargando] = useState(true);
  const [guardando, setGuardando] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Campos del formulario, separados del "perfil" original
  // para que el usuario pueda escribir sin que se guarde todavía
  const [nombreUsuario, setNombreUsuario] = useState("");
  const [telefono, setTelefono] = useState("");
  const [descripcion, setDescripcion] = useState("");
  const [notifActivas, setNotifActivas] = useState(true);
  const [limiteCronometro, setLimiteCronometro] = useState<number | "">("");

  useEffect(() => {
    setCargando(true);
    obtenerMiPerfil()
      .then((datos) => {
        setPerfil(datos);
        setNombreUsuario(datos.nombre_usuario);
        setTelefono(datos.telefono ?? "");
        setDescripcion(datos.descripcion ?? "");
        setNotifActivas(datos.notif_activas);
        setLimiteCronometro(datos.limite_cronometro ?? "");
        setError(null);
      })
      .catch(() => setError("No se pudo cargar el perfil"))
      .finally(() => setCargando(false));
  }, []);

  const manejarGuardar = async () => {
    setGuardando(true);
    try {
      const actualizado = await actualizarMiPerfil({
        nombre_usuario: nombreUsuario,
        telefono: telefono || undefined,
        descripcion: descripcion || undefined,
        notif_activas: notifActivas,
        limite_cronometro:
          limiteCronometro === "" ? undefined : Number(limiteCronometro),
      });
      setPerfil(actualizado);
      setError(null);
    } catch {
      setError("No se pudieron guardar los cambios");
    } finally {
      setGuardando(false);
    }
  };

  if (cargando) {
    return <p className="pixel-tareas-subtitle">Cargando perfil...</p>;
  }

  if (!perfil) {
    return <p className="pixel-error">{error ?? "No se encontró el perfil"}</p>;
  }

  return (
    <main className="pixel-perfil-main">
      <header className="pixel-perfil-header">
        <div>
          <h1 className="pixel-perfil-title">Perfil</h1>
          <p className="pixel-perfil-subtitle">
            Gestiona la información de tu cuenta.
          </p>
        </div>
      </header>

      {error && <p className="pixel-error">{error}</p>}

      <section className="pixel-perfil-card">
        <div className="pixel-perfil-foto-row">
          <div className="pixel-perfil-avatar">👤</div>
          <div>
            <span className="pixel-perfil-label">Foto de perfil</span>
            <button type="button" className="pixel-btn-icono">
              Cambiar foto
            </button>
          </div>
        </div>

        <div className="pixel-perfil-grid">
          <div className="pixel-perfil-campo">
            <label className="pixel-perfil-label">Nombre de usuario</label>
            <input
              type="text"
              value={nombreUsuario}
              onChange={(e) => setNombreUsuario(e.target.value)}
              className="pixel-perfil-input"
            />
          </div>
          <div className="pixel-perfil-campo">
            <label className="pixel-perfil-label">Teléfono</label>
            <input
              type="text"
              value={telefono}
              placeholder="opcional"
              onChange={(e) => setTelefono(e.target.value)}
              className="pixel-perfil-input"
            />
          </div>
        </div>

        <div className="pixel-perfil-campo">
          <label className="pixel-perfil-label">Descripción personal</label>
          <textarea
            rows={2}
            value={descripcion}
            placeholder="Cuéntanos algo sobre ti..."
            onChange={(e) => setDescripcion(e.target.value)}
            className="pixel-perfil-textarea"
          />
        </div>
      </section>

      <section className="pixel-perfil-card">
        <div className="pixel-perfil-switch-row">
          <div>
            <p className="pixel-perfil-item-title">Notificaciones de priorización</p>
            <p className="pixel-perfil-item-desc">
              Avisos cuando una tarea sube de prioridad.
            </p>
          </div>
          <label className="pixel-switch">
            <input
              type="checkbox"
              checked={notifActivas}
              onChange={(e) => setNotifActivas(e.target.checked)}
            />
            <span className="pixel-switch-slider"></span>
          </label>
        </div>

        <div className="pixel-perfil-switch-row pixel-perfil-divisor">
          <div>
            <p className="pixel-perfil-item-title">Límite del cronómetro</p>
            <p className="pixel-perfil-item-desc">
              Minutos antes de pausarse solo.
            </p>
          </div>
          <input
            type="number"
            value={limiteCronometro}
            onChange={(e) =>
              setLimiteCronometro(
                e.target.value === "" ? "" : Number(e.target.value)
              )
            }
            className="pixel-perfil-input pixel-perfil-input-corto"
          />
        </div>
      </section>

      <div className="pixel-perfil-acciones">
        <button
          type="button"
          className="pixel-btn-primario"
          onClick={manejarGuardar}
          disabled={guardando}
        >
          {guardando ? "Guardando..." : "Guardar cambios"}
        </button>
      </div>
    </main>
  );
}

export default Perfil;