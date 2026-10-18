import type { TareaBackend } from "../services/tareas";

export interface AppLayoutContext {
  abrirModalGlobal: () => void;
  abrirModalEditar: (tarea: TareaBackend) => void;
  refreshKey: number;
  nombreUsuario: string | null;
}
