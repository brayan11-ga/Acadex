// Ruta: frontend/src/pages/GrupoIntegrantesPage.tsx
import { useCallback, useEffect, useState } from "react";
import { Navigate, useNavigate, useParams } from "react-router-dom";
import { GroupDetail } from "../components/grupos/GroupDetail";
import {
  expulsarIntegrante,
  listarMisGrupos,
  obtenerIntegrantes,
  salirDeGrupo,
} from "../services/grupos";
import type { GrupoConRol, Integrante } from "../types/grupo";
import { obtenerIdUsuarioActual } from "../utils/jwt";

function GrupoIntegrantesPage() {
  const { idGrupo } = useParams();
  const id = Number(idGrupo);
  const navigate = useNavigate();
  const idUsuarioActual = obtenerIdUsuarioActual();

  const [grupo, setGrupo] = useState<GrupoConRol | null>(null);
  const [integrantes, setIntegrantes] = useState<Integrante[]>([]);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [sinPermisos, setSinPermisos] = useState(false);

  const cargar = useCallback(async () => {
    setCargando(true);
    try {
      const misGrupos = await listarMisGrupos();
      const encontrado = misGrupos.find((g) => g.id_grupo === id) ?? null;
      if (!encontrado) {
        setSinPermisos(true);
        setGrupo(null);
        setIntegrantes([]);
        setError(null);
        return;
      }
      const miembros = await obtenerIntegrantes(id);
      setGrupo(encontrado);
      setIntegrantes(miembros);
      setSinPermisos(false);
      setError(null);
    } catch (err) {
      const mensaje = (err instanceof Error ? err.message : "").toLowerCase();
      if (mensaje.includes("permiso") || mensaje.includes("403") || mensaje.includes("forbidden")) {
        setSinPermisos(true);
        setError(null);
      } else {
        setError("No se pudieron cargar los integrantes.");
      }
    } finally {
      setCargando(false);
    }
  }, [id]);

  useEffect(() => {
    if (!Number.isNaN(id)) cargar();
  }, [cargar, id]);

  const handleKick = async (idUsuario: number) => {
    if (!window.confirm("¿Expulsar a este integrante del grupo?")) return;
    try {
      await expulsarIntegrante(id, idUsuario);
      await cargar();
    } catch {
      setError("No se pudo expulsar al integrante.");
    }
  };

  const handleLeave = async () => {
    if (!window.confirm("¿Seguro que quieres salir de este grupo?")) return;
    try {
      await salirDeGrupo(id);
      navigate("/grupos");
    } catch {
      setError("No se pudo salir del grupo.");
    }
  };

  if (Number.isNaN(id)) return <Navigate to="/grupos" replace />;
  if (cargando) return <p>Cargando integrantes...</p>;
  if (sinPermisos) {
    return (
      <section>
        <p>No perteneces a este grupo.</p>
        <button type="button" onClick={() => navigate("/grupos")}>
          ← Volver a Mis Grupos
        </button>
      </section>
    );
  }
  if (error) return <p>{error}</p>;
  if (!grupo) return <Navigate to="/grupos" replace />;

  return (
    <GroupDetail
      group={grupo}
      members={integrantes}
      currentUserId={idUsuarioActual}
      textoVolver="← Volver a tareas del grupo"
      onBack={() => navigate(`/grupos/${id}/tareas`)}
      onKickMember={handleKick}
      onLeaveGroup={handleLeave}
    />
  );
}

export default GrupoIntegrantesPage;
