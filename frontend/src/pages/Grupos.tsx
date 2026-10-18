// Ruta: frontend/src/pages/Grupos.tsx
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { MyGroups } from "../components/grupos/MyGroups";
import { CreateGroupModal } from "../components/grupos/CreateGroupModal";
import { JoinGroupModal } from "../components/grupos/JoinGroupModal";
import { GroupsLoadingSkeleton } from "../components/skeletons/LoadingSkeletons";
import {
  listarMisGrupos,
  crearGrupo,
  unirseAGrupo,
} from "../services/grupos";
import type { GrupoConRol, Grupo } from "../types/grupo";

function Grupos() {
  const navigate = useNavigate();
  const [grupos, setGrupos] = useState<GrupoConRol[]>([]);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [mostrarCrear, setMostrarCrear] = useState(false);
  const [mostrarUnirse, setMostrarUnirse] = useState(false);

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
    navigate(`/grupos/${idGrupo}/tareas`);
  };

  if (cargando) return <GroupsLoadingSkeleton />;
  if (error) return <p>{error}</p>;

  return (
    <>
      <MyGroups
        groups={grupos}
        onOpenGroup={handleOpenGroup}
        onCreateClick={() => setMostrarCrear(true)}
        onJoinClick={() => setMostrarUnirse(true)}
      />

      <CreateGroupModal isOpen={mostrarCrear} onClose={() => setMostrarCrear(false)} onCreate={handleCreate} />
      <JoinGroupModal isOpen={mostrarUnirse} onClose={() => setMostrarUnirse(false)} onJoin={handleJoin} />
    </>
  );
}

export default Grupos;
