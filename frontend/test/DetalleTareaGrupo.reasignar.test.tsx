// Ruta: frontend/test/DetalleTareaGrupo.reasignar.test.tsx
import {
  fireEvent,
  render,
  screen,
  waitFor,
  within,
} from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { beforeAll, beforeEach, describe, expect, it, vi } from "vitest";

const servicios = vi.hoisted(() => ({
  listarMisGrupos: vi.fn(),
  obtenerIntegrantes: vi.fn(),
  obtenerTarea: vi.fn(),
  listarAsignados: vi.fn(),
  listarArchivos: vi.fn(),
  listarCategorias: vi.fn(),
  listarSesiones: vi.fn(),
  reasignar: vi.fn(),
  // Usados por el formulario de edición, que aquí no se abre.
  crear: vi.fn(),
  crearConPdf: vi.fn(),
  actualizar: vi.fn(),
  analizar: vi.fn(),
  subir: vi.fn(),
  crearGrupal: vi.fn(),
  descargar: vi.fn(),
  eliminarArchivo: vi.fn(),
  eliminarTarea: vi.fn(),
  reabrir: vi.fn(),
  completar: vi.fn(),
  iniciarCrono: vi.fn(),
  finalizarCrono: vi.fn(),
  reiniciarCrono: vi.fn(),
}));

vi.mock("../src/services/grupos", () => ({
  listarMisGrupos: servicios.listarMisGrupos,
  obtenerIntegrantes: servicios.obtenerIntegrantes,
}));

vi.mock("../src/services/tareas", () => ({
  completarParteTarea: servicios.completar,
  descargarArchivoTarea: servicios.descargar,
  eliminarArchivoTarea: servicios.eliminarArchivo,
  eliminarTarea: servicios.eliminarTarea,
  listarArchivosTarea: servicios.listarArchivos,
  listarAsignadosTarea: servicios.listarAsignados,
  obtenerTarea: servicios.obtenerTarea,
  reabrirTarea: servicios.reabrir,
  reasignarAsignadosTarea: servicios.reasignar,
  subirArchivoTarea: servicios.subir,
  crearTarea: servicios.crear,
  crearTareaConPdf: servicios.crearConPdf,
  actualizarTarea: servicios.actualizar,
  analizarDocumentoIA: servicios.analizar,
  crearTareaGrupal: servicios.crearGrupal,
}));

vi.mock("../src/services/categorias", () => ({
  listarCategorias: servicios.listarCategorias,
}));

vi.mock("../src/services/sesionesCronometro", () => ({
  finalizarSesionCronometro: servicios.finalizarCrono,
  iniciarSesionCronometro: servicios.iniciarCrono,
  listarSesionesUsuario: servicios.listarSesiones,
  reiniciarSesionesCronometro: servicios.reiniciarCrono,
}));

vi.mock("../src/utils/jwt", () => ({
  obtenerIdUsuarioActual: () => 12,
}));

vi.mock("../src/config/featureFlags", () => ({
  adjuntosHabilitados: () => true,
}));

import DetalleTareaGrupoPage from "../src/pages/DetalleTareaGrupoPage";

const grupo = {
  id_grupo: 7,
  nombre_grupo: "Grupo 7",
  descripcion: null,
  codigo_acceso: null,
  fecha_expiracion_codigo: null,
  segundos_restantes_codigo: null,
  fecha_creacion: "2026-01-01T00:00:00",
  rol: "lider",
};

const tarea = {
  id_tarea: 40,
  nombre: "Tarea grupal",
  descripcion: "Detalle",
  fecha_entrega: "2026-12-31T12:00:00",
  estado: "en progreso",
  dificultad_estimada: 3,
  tiempo_estimado: 60,
  prioridad: null,
  id_categoria: 4,
  id_usuario: null,
  id_grupo: 7,
  max_archivos: 5,
  total_archivos: 0,
  cronometro_activo: false,
  tiempo_acumulado: 0,
};

const asignados = [
  {
    id_usuario: 12,
    correo_electronico: "lider@correo.com",
    completado: true,
  },
  {
    id_usuario: 13,
    correo_electronico: "ana@correo.com",
    completado: false,
  },
];

const integrantes = [
  {
    id_integrante: 1,
    id_usuario: 12,
    correo_electronico: "lider@correo.com",
    rol: "lider",
    fecha_ingreso: "2026-01-01T00:00:00",
  },
  {
    id_integrante: 2,
    id_usuario: 13,
    correo_electronico: "ana@correo.com",
    rol: "miembro",
    fecha_ingreso: "2026-01-02T00:00:00",
  },
  {
    id_integrante: 3,
    id_usuario: 14,
    correo_electronico: "carlos@correo.com",
    rol: "miembro",
    fecha_ingreso: "2026-01-03T00:00:00",
  },
];

beforeAll(() => {
  // jsdom no implementa <dialog>; lo mínimo para que el modal se abra.
  HTMLDialogElement.prototype.showModal = function (this: HTMLDialogElement) {
    this.setAttribute("open", "");
  };
  HTMLDialogElement.prototype.close = function (this: HTMLDialogElement) {
    this.removeAttribute("open");
    this.dispatchEvent(new Event("close"));
  };
});

beforeEach(() => {
  vi.resetAllMocks();
  servicios.listarMisGrupos.mockResolvedValue([grupo]);
  servicios.obtenerIntegrantes.mockResolvedValue(integrantes);
  servicios.obtenerTarea.mockResolvedValue(tarea);
  servicios.listarAsignados.mockResolvedValue(asignados);
  servicios.listarArchivos.mockResolvedValue([]);
  servicios.listarCategorias.mockResolvedValue([
    { id_categoria: 4, nombre_categoria: "Lectura" },
  ]);
  servicios.listarSesiones.mockResolvedValue([]);
  servicios.reasignar.mockResolvedValue(tarea);
});

function renderPagina() {
  return render(
    <MemoryRouter initialEntries={["/grupos/7/tareas/40"]}>
      <Routes>
        <Route
          path="/grupos/:idGrupo/tareas/:idTarea"
          element={<DetalleTareaGrupoPage />}
        />
      </Routes>
    </MemoryRouter>,
  );
}

function casilla(correo: string) {
  return screen.getByRole("checkbox", {
    name: new RegExp(correo.replace(/\./g, "\\.")),
  });
}

async function abrirModal() {
  renderPagina();
  fireEvent.click(
    await screen.findByRole("button", { name: "Reasignar integrantes" }),
  );
  await screen.findByText("Integrantes del grupo");
}

describe("Reasignar integrantes de una tarea grupal", () => {
  it("marca los asignados actuales, conserva la marca de completado y deshabilita Confirmar sin cambios", async () => {
    await abrirModal();

    expect(casilla("lider@correo.com")).toBeChecked();
    expect(casilla("ana@correo.com")).toBeChecked();
    expect(casilla("carlos@correo.com")).not.toBeChecked();
    const dialogo = screen.getByRole("dialog", {
      name: "Reasignar integrantes",
    });
    expect(within(dialogo).getByText("Completó")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Confirmar" })).toBeDisabled();
  });

  it("bloquea Confirmar y avisa cuando la selección queda vacía", async () => {
    await abrirModal();

    fireEvent.click(casilla("lider@correo.com"));
    fireEvent.click(casilla("ana@correo.com"));

    expect(
      await screen.findByText("La tarea necesita al menos un asignado."),
    ).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Confirmar" })).toBeDisabled();
    expect(servicios.reasignar).not.toHaveBeenCalled();
  });

  it("pide confirmación al quitar a alguien y envía solo los que quedan", async () => {
    await abrirModal();

    fireEvent.click(casilla("ana@correo.com"));
    fireEvent.click(screen.getByRole("button", { name: "Confirmar" }));

    const dialogo = await screen.findByRole("dialog", {
      name: "Quitar integrantes",
    });
    expect(within(dialogo).getByText("ana@correo.com")).toBeInTheDocument();
    expect(
      within(dialogo).getByText(/se borrarán sus archivos subidos/i),
    ).toBeInTheDocument();

    fireEvent.click(
      within(dialogo).getByRole("button", { name: "Quitar y guardar" }),
    );

    await waitFor(() =>
      expect(servicios.reasignar).toHaveBeenCalledWith(40, [12]),
    );
  });

  it("avisa si la persona que sale ya había completado su parte", async () => {
    await abrirModal();

    fireEvent.click(casilla("lider@correo.com"));
    fireEvent.click(screen.getByRole("button", { name: "Confirmar" }));

    const dialogo = await screen.findByRole("dialog", {
      name: "Quitar integrantes",
    });
    expect(
      within(dialogo).getByText(/ya había completado su parte/),
    ).toBeInTheDocument();

    fireEvent.click(within(dialogo).getByRole("button", { name: "Cancelar" }));
    expect(servicios.reasignar).not.toHaveBeenCalled();
  });

  it("agrega integrantes sin pedir confirmación y muestra el error 409 dentro del modal", async () => {
    servicios.reasignar.mockRejectedValueOnce(new Error("Reábrela primero."));
    await abrirModal();

    fireEvent.click(casilla("carlos@correo.com"));
    fireEvent.click(screen.getByRole("button", { name: "Confirmar" }));

    expect(
      await screen.findByText("La tarea está completada. Reábrela para editarla."),
    ).toBeInTheDocument();
    expect(servicios.reasignar).toHaveBeenCalledWith(40, [12, 13, 14]);
    expect(screen.queryByRole("dialog", { name: "Quitar integrantes" })).toBeNull();
  });

  it("deshabilita Reasignar integrantes cuando la tarea está completada", async () => {
    servicios.obtenerTarea.mockResolvedValueOnce({
      ...tarea,
      estado: "completada",
    });
    renderPagina();

    const boton = await screen.findByRole("button", {
      name: "Reasignar integrantes",
    });
    expect(boton).toBeDisabled();
    expect(
      screen.getByText("Esta tarea está completada. Reábrela para editarla."),
    ).toBeInTheDocument();
  });
});
