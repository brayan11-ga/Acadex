// src/pages/Perfil.tsx
import { useState, useEffect } from "react";
import "../styles/perfil.css";
import { ProfileLoadingSkeleton } from "../components/skeletons/LoadingSkeletons";
import {
  obtenerMiPerfil,
  actualizarMiPerfil,
  type PerfilBackend,
} from "../services/perfil";

const LIMITE_DEFECTO_SEG = 1800;
const LIMITE_MINIMO_SEG = 10;

function Perfil() {
  const [perfil, setPerfil] = useState<PerfilBackend | null>(null);
  const [cargando, setCargando] = useState(true);
  const [guardando, setGuardando] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [nombreUsuario, setNombreUsuario] = useState("");
  const [telefono, setTelefono] = useState("");
  const [descripcion, setDescripcion] = useState("");
  const [notifActivas, setNotifActivas] = useState(true);
  const [limiteMin, setLimiteMin] = useState<number | "">("");
  const [limiteSeg, setLimiteSeg] = useState<number | "">("");

  useEffect(() => {
    setCargando(true);
    obtenerMiPerfil()
      .then((datos) => {
        setPerfil(datos);
        setNombreUsuario(datos.nombre_usuario);
        setTelefono(datos.telefono ?? "");
        setDescripcion(datos.descripcion ?? "");
        setNotifActivas(datos.notif_activas);
        const total = datos.limite_cronometro ?? LIMITE_DEFECTO_SEG;
        setLimiteMin(Math.floor(total / 60));
        setLimiteSeg(total % 60);
        setError(null);
      })
      .catch(() => setError("No se pudo cargar el perfil"))
      .finally(() => setCargando(false));
  }, []);

  const manejarGuardar = async () => {
    const min = Number(limiteMin || 0);
    const seg = Number(limiteSeg || 0);
    const totalSeg = min * 60 + seg;
    if (
      !Number.isInteger(min) ||
      !Number.isInteger(seg) ||
      min < 0 ||
      seg < 0 ||
      seg > 59 ||
      totalSeg < LIMITE_MINIMO_SEG
    ) {
      setError(
        `El límite debe ser de al menos ${LIMITE_MINIMO_SEG} segundos y los segundos entre 0 y 59.`
      );
      return;
    }
    setGuardando(true);
    try {
      const actualizado = await actualizarMiPerfil({
        nombre_usuario: nombreUsuario,
        telefono: telefono || undefined,
        descripcion: descripcion || undefined,
        notif_activas: notifActivas,
        limite_cronometro: totalSeg,
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
    return <ProfileLoadingSkeleton />;
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
              Tiempo máximo seguido antes de pausarse solo.
            </p>
          </div>
          <div className="pixel-perfil-limite">
            <input
              type="number"
              min={0}
              value={limiteMin}
              onChange={(e) =>
                setLimiteMin(e.target.value === "" ? "" : Number(e.target.value))
              }
              className="pixel-perfil-input pixel-perfil-input-corto"
              aria-label="Minutos"
            />{" "}
            min{" "}
            <input
              type="number"
              min={0}
              max={59}
              value={limiteSeg}
              onChange={(e) =>
                setLimiteSeg(e.target.value === "" ? "" : Number(e.target.value))
              }
              className="pixel-perfil-input pixel-perfil-input-corto"
              aria-label="Segundos"
            />{" "}
            s
          </div>
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