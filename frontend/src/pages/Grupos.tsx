// frontend/src/pages/Grupos.tsx
import { useEffect, useState } from "react";
import { MyGroups } from "../components/grupos/MyGroups";
import { GroupDetail } from "../components/grupos/GroupDetail";
import { CreateGroupModal } from "../components/grupos/CreateGroupModal";
import { JoinGroupModal } from "../components/grupos/JoinGroupModal";
import {
  listarMisGrupos,
  crearGrupo,
  unirseAGrupo,
  obtenerIntegrantes,
  salirDeGrupo,
  expulsarIntegrante,
  eliminarGrupo,
} from "../services/grupos";
import type { GrupoConRol, Grupo, Integrante } from "../types/grupo";
import { obtenerIdUsuarioActual } from "../utils/jwt";

function Grupos() {
  const [grupos, setGrupos] = useState<GrupoConRol[]>([]);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [mostrarCrear, setMostrarCrear] = useState(false);
  const [mostrarUnirse, setMostrarUnirse] = useState(false);

  const [idGrupoAbierto, setIdGrupoAbierto] = useState<number | null>(null);
  const [integrantes, setIntegrantes] = useState<Integrante[]>([]);
  const [cargandoDetalle, setCargandoDetalle] = useState(false);

  const idUsuarioActual = obtenerIdUsuarioActual();
  const grupoAbierto = grupos.find((g) => g.id_grupo === idGrupoAbierto) ?? null;

  const cargarGrupos = async () => {
    try {
      const datos = await listarMisGrupos();
      setGrupos(datos);
      setError(null);
    } catch {
      setError("No se pudieron cargar tus grupos.");
    } finally {
      setCargando(false);
    }
  };

  useEffect(() => {
    cargarGrupos();
  }, []);

  const cargarIntegrantes = async (idGrupo: number) => {
    setCargandoDetalle(true);
    try {
      const datos = await obtenerIntegrantes(idGrupo);
      setIntegrantes(datos);
    } catch {
      setError("No se pudieron cargar los integrantes.");
    } finally {
      setCargandoDetalle(false);
    }
  };

  const handleCreate = async (datos: { nombre_grupo: string; descripcion: string }): Promise<Grupo> => {
    const nuevoGrupo = await crearGrupo(datos);
    await cargarGrupos();
    return nuevoGrupo;
  };

  const handleJoin = async (codigo: string): Promise<void> => {
    await unirseAGrupo(codigo);
    await cargarGrupos();
    setMostrarUnirse(false);
  };

  const handleOpenGroup = (idGrupo: number) => {
    setIdGrupoAbierto(idGrupo);
    cargarIntegrantes(idGrupo);
  };

  const handleBack = () => {
    setIdGrupoAbierto(null);
    setIntegrantes([]);
  };

  const handleKick = async (idUsuario: number) => {
    if (!idGrupoAbierto) return;
    if (!window.confirm("¿Expulsar a este integrante del grupo?")) return;
    try {
      await expulsarIntegrante(idGrupoAbierto, idUsuario);
      await cargarIntegrantes(idGrupoAbierto);
    } catch {
      setError("No se pudo expulsar al integrante.");
    }
  };

  const handleDelete = async () => {
    if (!idGrupoAbierto) return;
    if (!window.confirm("¿Eliminar este grupo? Esta acción no se puede deshacer.")) return;
    try {
      await eliminarGrupo(idGrupoAbierto);
      handleBack();
      await cargarGrupos();
    } catch {
      setError("No se pudo eliminar el grupo.");
    }
  };

  const handleLeave = async () => {
    if (!idGrupoAbierto) return;
    if (!window.confirm("¿Seguro que quieres salir de este grupo?")) return;
    try {
      await salirDeGrupo(idGrupoAbierto);
      handleBack();
      await cargarGrupos();
    } catch {
      setError("No se pudo salir del grupo.");
    }
  };

  if (cargando) return <p>Cargando grupos...</p>;
  if (error) return <p>{error}</p>;

  return (
    <>
      {grupoAbierto ? (
        cargandoDetalle ? (
          <p>Cargando integrantes...</p>
        ) : (
          <GroupDetail
            group={grupoAbierto}
            members={integrantes}
            currentUserId={idUsuarioActual}
            onBack={handleBack}
            onKickMember={handleKick}
            onDeleteGroup={handleDelete}
            onLeaveGroup={handleLeave}
          />
        )
      ) : (
        <MyGroups
          groups={grupos}
          onOpenGroup={handleOpenGroup}
          onCreateClick={() => setMostrarCrear(true)}
          onJoinClick={() => setMostrarUnirse(true)}
        />
      )}

      <CreateGroupModal isOpen={mostrarCrear} onClose={() => setMostrarCrear(false)} onCreate={handleCreate} />
      <JoinGroupModal isOpen={mostrarUnirse} onClose={() => setMostrarUnirse(false)} onJoin={handleJoin} />
    </>
  );
}

export default Grupos;