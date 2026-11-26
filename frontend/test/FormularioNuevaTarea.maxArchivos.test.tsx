// Ruta: frontend/test/FormularioNuevaTarea.maxArchivos.test.tsx
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

const servicios = vi.hoisted(() => ({
  listar: vi.fn(),
  subir: vi.fn(),
  descargar: vi.fn(),
  eliminar: vi.fn(),
  listarCategorias: vi.fn(),
  actualizar: vi.fn(),
  crear: vi.fn(),
  crearConPdf: vi.fn(),
  analizar: vi.fn(),
  crearGrupal: vi.fn(),
}));

vi.mock("../src/services/tareas", () => ({
  listarArchivosTarea: servicios.listar,
  subirArchivoTarea: servicios.subir,
  descargarArchivoTarea: servicios.descargar,
  eliminarArchivoTarea: servicios.eliminar,
  crearTarea: servicios.crear,
  crearTareaConPdf: servicios.crearConPdf,
  actualizarTarea: servicios.actualizar,
  analizarDocumentoIA: servicios.analizar,
  crearTareaGrupal: servicios.crearGrupal,
}));

vi.mock("../src/services/categorias", () => ({
  listarCategorias: servicios.listarCategorias,
}));

vi.mock("../src/config/featureFlags", () => ({
  adjuntosHabilitados: () => true,
}));

import FormularioNuevaTarea from "../src/components/tareas/FormularioNuevaTarea";
import type { TareaBackend } from "../src/services/tareas";

const tareaGrupal: TareaBackend = {
  id_tarea: 40,
  nombre: "Tarea grupal",
  descripcion: "Detalle de la tarea",
  fecha_entrega: "2026-10-20T12:00:00",
  estado: "en progreso",
  dificultad_estimada: 3,
  tiempo_estimado: 60,
  prioridad: null,
  id_categoria: 4,
  id_usuario: null,
  id_grupo: 7,
  max_archivos: 5,
  total_archivos: 2,
  cronometro_activo: false,
  tiempo_acumulado: 0,
};

const tareaIndividual: TareaBackend = {
  ...tareaGrupal,
  id_tarea: 41,
  id_usuario: 12,
  id_grupo: null,
};

function renderEdicion(tarea: TareaBackend, onTareaCreada = vi.fn()) {
  const esGrupal = tarea.id_grupo !== null;
  render(
    <FormularioNuevaTarea
      modo={esGrupal ? "grupal" : "individual"}
      idGrupo={tarea.id_grupo ?? undefined}
      tareaAEditar={tarea}
      onDescartar={() => undefined}
      onTareaCreada={onTareaCreada}
    />,
  );
  return onTareaCreada;
}

describe("max_archivos en la edición de tarea grupal", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    servicios.listar.mockResolvedValue([]);
    servicios.listarCategorias.mockResolvedValue([
      { id_categoria: 4, nombre_categoria: "Lectura" },
    ]);
    servicios.actualizar.mockResolvedValue(tareaGrupal);
  });

  it("muestra el máximo actual en la edición grupal", async () => {
    renderEdicion(tareaGrupal);
    const campo = await screen.findByLabelText("Máximo de archivos");
    expect(campo).toHaveValue(5);
    expect(campo).toHaveAttribute("min", "1");
    expect(campo).toHaveAttribute("max", "10");
  });

  it("reinicia los campos de edición al recibir otra tarea", async () => {
    const callbacks = { onDescartar: vi.fn(), onTareaCreada: vi.fn() };
    const { rerender } = render(
      <FormularioNuevaTarea {...callbacks} modo="grupal" idGrupo={7} tareaAEditar={tareaGrupal} />,
    );
    fireEvent.change(await screen.findByDisplayValue(tareaGrupal.nombre), {
      target: { value: "Borrador" },
    });

    const otra = { ...tareaGrupal, id_tarea: 50, nombre: "Otra tarea", max_archivos: 2 };
    rerender(<FormularioNuevaTarea {...callbacks} modo="grupal" idGrupo={7} tareaAEditar={otra} />);
    expect(screen.getByDisplayValue(otra.nombre)).toBeInTheDocument();
    expect(screen.getByLabelText("Máximo de archivos")).toHaveValue(2);
    await waitFor(() => expect(servicios.listarCategorias).toHaveBeenCalledTimes(2));
  });

  it("envía el nuevo max_archivos al guardar la edición grupal", async () => {
    const onTareaCreada = renderEdicion(tareaGrupal);
    fireEvent.change(await screen.findByLabelText("Máximo de archivos"), {
      target: { value: "8" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Guardar →" }));

    await waitFor(() =>
      expect(servicios.actualizar).toHaveBeenCalledWith(
        tareaGrupal.id_tarea,
        expect.objectContaining({ max_archivos: 8 }),
      ),
    );
    expect(onTareaCreada).toHaveBeenCalledTimes(1);
  });

  it("muestra dentro del formulario el 400 del backend cuando baja de los archivos subidos", async () => {
    servicios.actualizar.mockRejectedValueOnce(
      new Error(
        "No puedes fijar el máximo en 2: la tarea ya tiene 3 archivos.",
      ),
    );
    renderEdicion(tareaGrupal);
    fireEvent.change(await screen.findByLabelText("Máximo de archivos"), {
      target: { value: "2" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Guardar →" }));

    expect(
      await screen.findByRole("alert"),
    ).toHaveTextContent("No puedes fijar el máximo en 2: la tarea ya tiene 3 archivos.");
    expect(servicios.actualizar).toHaveBeenCalledWith(
      tareaGrupal.id_tarea,
      expect.objectContaining({ max_archivos: 2 }),
    );
  });

  it("rechaza en el cliente un valor fuera del rango 1 a 10", async () => {
    renderEdicion(tareaGrupal);
    fireEvent.change(await screen.findByLabelText("Máximo de archivos"), {
      target: { value: "11" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Guardar →" }));

    expect(
      await screen.findByRole("alert"),
    ).toHaveTextContent("El máximo de archivos debe ser un número entero entre 1 y 10");
    expect(servicios.actualizar).not.toHaveBeenCalled();
  });

  it("no muestra ni envía max_archivos en la edición individual", async () => {
    renderEdicion(tareaIndividual);

    await waitFor(() => expect(servicios.listarCategorias).toHaveBeenCalled());
    expect(
      screen.queryByLabelText("Máximo de archivos"),
    ).not.toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: "Guardar →" }));
    await waitFor(() => expect(servicios.actualizar).toHaveBeenCalled());

    const payload = servicios.actualizar.mock.calls[0][1];
    expect(payload).not.toHaveProperty("max_archivos");
  });
});
