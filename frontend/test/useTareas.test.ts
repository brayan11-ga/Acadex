import { act, renderHook, waitFor } from "@testing-library/react";
import { beforeEach, expect, it, vi } from "vitest";
import { useTareas } from "../src/hooks/useTareas";
import { listarCategorias } from "../src/services/categorias";
import { eliminarTarea, listarTareas, type TareaBackend } from "../src/services/tareas";

vi.mock("../src/services/categorias", () => ({ listarCategorias: vi.fn() }));
vi.mock("../src/services/tareas", () => ({ eliminarTarea: vi.fn(), listarTareas: vi.fn() }));

const tareas: TareaBackend[] = Array.from({ length: 8 }, (_, indice) => ({
  id_tarea: indice + 1,
  nombre: `Tarea ${indice + 1}`,
  descripcion: null,
  fecha_entrega: "2026-10-20T12:00:00",
  estado: indice === 7 ? "Completada" : "Pendiente",
  dificultad_estimada: 3,
  tiempo_estimado: 30,
  prioridad: null,
  id_categoria: 1,
  id_usuario: 12,
  id_grupo: null,
  max_archivos: 3,
  total_archivos: 0,
  cronometro_activo: false,
  tiempo_acumulado: 0,
}));

beforeEach(() => {
  vi.resetAllMocks();
  vi.mocked(listarCategorias).mockResolvedValue([]);
  vi.mocked(listarTareas).mockResolvedValue(tareas);
});

it("vuelve a la primera página al filtrar y al eliminar una tarea", async () => {
  const { result } = renderHook(() => useTareas(0));
  await waitFor(() => expect(result.current.cargando).toBe(false));

  act(() => result.current.setPaginaActual(2));
  expect(result.current.tareasPaginadas.map((tarea) => tarea.id_tarea)).toEqual([7, 8]);
  act(() => result.current.setFiltroActivo("activas"));
  expect(result.current.paginaActual).toBe(1);
  expect(result.current.totalTareasFiltradas).toBe(7);

  act(() => result.current.setPaginaActual(2));
  act(() => result.current.solicitarEliminar(7));
  await act(() => result.current.confirmarEliminar());
  expect(eliminarTarea).toHaveBeenCalledWith(7);
  expect(result.current.paginaActual).toBe(1);
  expect(result.current.totalPaginas).toBe(1);
});

it("ignora el resultado de una recarga sustituida por otra", async () => {
  let resolverPrimera!: (datos: TareaBackend[]) => void;
  let resolverSegunda!: (datos: TareaBackend[]) => void;
  const primera = new Promise<TareaBackend[]>((resolver) => { resolverPrimera = resolver; });
  const segunda = new Promise<TareaBackend[]>((resolver) => { resolverSegunda = resolver; });
  vi.mocked(listarTareas)
    .mockReturnValueOnce(primera)
    .mockReturnValueOnce(segunda);
  const { result, rerender } = renderHook(({ clave }) => useTareas(clave), {
    initialProps: { clave: 0 },
  });

  rerender({ clave: 1 });
  expect(result.current.cargando).toBe(true);
  await act(async () => resolverSegunda(tareas.slice(0, 1)));
  expect(result.current.cargando).toBe(false);

  await act(async () => resolverPrimera(tareas));
  expect(result.current.totalTareas).toBe(1);
});
