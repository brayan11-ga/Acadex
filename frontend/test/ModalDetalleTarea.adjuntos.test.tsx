import { fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

const servicios = vi.hoisted(() => ({
  listar: vi.fn(),
  subir: vi.fn(),
  descargar: vi.fn(),
  eliminar: vi.fn(),
  listarCategorias: vi.fn(),
  crear: vi.fn(),
  actualizar: vi.fn(),
  analizar: vi.fn(),
}));

const docxRenderer = vi.hoisted(() => ({
  render: vi.fn(),
}));

vi.mock("../src/services/tareas", () => ({
  listarArchivosTarea: servicios.listar,
  subirArchivoTarea: servicios.subir,
  descargarArchivoTarea: servicios.descargar,
  eliminarArchivoTarea: servicios.eliminar,
  crearTarea: servicios.crear,
  actualizarTarea: servicios.actualizar,
  analizarDocumentoIA: servicios.analizar,
}));

vi.mock("../src/services/categorias", () => ({
  listarCategorias: servicios.listarCategorias,
}));

vi.mock("docx-preview", () => ({
  renderAsync: docxRenderer.render,
}));

import FormularioNuevaTarea from "../src/components/tareas/FormularioNuevaTarea";
import { ModalDetalleTarea } from "../src/components/tareas/ModalDetalleTarea";
import type { ArchivoTarea, TareaBackend } from "../src/services/tareas";

const tarea: TareaBackend = {
  id_tarea: 31,
  nombre: "Leer capítulo",
  descripcion: null,
  fecha_entrega: "2026-10-20T12:00:00",
  estado: "pendiente",
  dificultad_estimada: 2,
  tiempo_estimado: 60,
  prioridad: null,
  id_categoria: 4,
  id_usuario: 12,
  id_grupo: null,
};

const adjunto: ArchivoTarea = {
  id_archivo: 8,
  nombre: "guia.pdf",
  tamano: 1024,
  tipo: "PDF",
  fecha_adjuncion: "2026-10-10T09:00:00",
  id_tarea: 31,
  puede_eliminar: true,
};

function renderModalDetalle() {
  return render(
    <ModalDetalleTarea
      tarea={tarea}
      nombreCategoria={() => "Lectura"}
      formatearFecha={() => "20 oct. 2026"}
      onCerrar={() => undefined}
    />,
  );
}

function renderFormularioEdicion() {
  return render(
    <FormularioNuevaTarea
      tareaAEditar={tarea}
      onDescartar={() => undefined}
      onTareaCreada={() => undefined}
    />,
  );
}

describe("adjuntos de tareas", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    servicios.listar.mockResolvedValue([adjunto]);
    servicios.subir.mockResolvedValue(adjunto);
    servicios.descargar.mockResolvedValue(new Blob(["archivo"]));
    servicios.eliminar.mockResolvedValue(undefined);
    servicios.listarCategorias.mockResolvedValue([
      { id_categoria: 4, nombre_categoria: "Lectura" },
    ]);
    docxRenderer.render.mockImplementation(async (_blob: Blob, contenedor: HTMLElement) => {
      const texto = document.createElement("p");
      texto.textContent = "Contenido de Word";
      contenedor.appendChild(texto);
    });
  });

  it("muestra adjuntos en la edición y permite cargarlos desde ese formulario", async () => {
    renderFormularioEdicion();

    expect(await screen.findByText("guia.pdf")).toBeInTheDocument();
    expect(screen.getByLabelText("Seleccionar adjuntos")).toBeInTheDocument();

    const archivos = [
      new File(["%PDF-1.7"], "uno.pdf", { type: "application/pdf" }),
      new File(["imagen"], "dos.png", { type: "image/png" }),
    ];
    fireEvent.change(screen.getByLabelText("Seleccionar adjuntos"), {
      target: { files: archivos },
    });
    expect(screen.getByRole("button", { name: "Subir adjuntos" })).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Subir adjuntos" }));

    expect(await screen.findByRole("status")).toHaveTextContent("Se subieron 2 adjuntos.");
    expect(servicios.subir).toHaveBeenCalledTimes(2);
    expect(servicios.subir).toHaveBeenNthCalledWith(1, tarea.id_tarea, archivos[0]);
    expect(servicios.listar).toHaveBeenCalledTimes(2);
  });

  it("mantiene ver detalles en modo de consulta", async () => {
    servicios.listar.mockResolvedValue([
      adjunto,
      { ...adjunto, id_archivo: 9, nombre: "de-otro.pdf", puede_eliminar: false },
    ]);

    renderModalDetalle();

    expect(await screen.findByText("guia.pdf")).toBeInTheDocument();
    expect(screen.getByText("de-otro.pdf")).toBeInTheDocument();
    expect(screen.queryByLabelText("Seleccionar adjuntos")).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Eliminar" })).not.toBeInTheDocument();
    expect(screen.getAllByRole("button", { name: "Descargar" })).toHaveLength(2);
  });

  it("confirma y elimina un archivo desde la edición", async () => {
    renderFormularioEdicion();
    await screen.findByText("guia.pdf");

    fireEvent.click(screen.getByRole("button", { name: "Eliminar" }));
    const dialog = screen.getByRole("alertdialog", { name: "¿Eliminar adjunto?" });
    expect(within(dialog).getByText(/guia\.pdf/)).toBeInTheDocument();
    fireEvent.click(within(dialog).getByRole("button", { name: "Confirmar" }));

    await waitFor(() => expect(servicios.eliminar).toHaveBeenCalledWith(tarea.id_tarea, adjunto.id_archivo));
    expect(await screen.findByRole("status")).toHaveTextContent("Adjunto eliminado.");
    expect(screen.queryByText("guia.pdf")).not.toBeInTheDocument();
  });

  it("descarga los archivos desde la vista de detalles", async () => {
    const clickAncla = vi.spyOn(HTMLAnchorElement.prototype, "click").mockImplementation(() => undefined);
    Object.defineProperty(URL, "createObjectURL", { configurable: true, value: vi.fn(() => "blob:test") });
    Object.defineProperty(URL, "revokeObjectURL", { configurable: true, value: vi.fn() });

    renderModalDetalle();
    await screen.findByText("guia.pdf");
    fireEvent.click(screen.getByRole("button", { name: "Descargar" }));

    await waitFor(() => expect(servicios.descargar).toHaveBeenCalledWith(tarea.id_tarea, adjunto.id_archivo));
    expect(clickAncla).toHaveBeenCalled();
  });

  it("abre los PDF en la vista previa integrada", async () => {
    servicios.descargar.mockResolvedValue(new Blob(["%PDF-1.7"], { type: "application/pdf" }));
    renderModalDetalle();
    await screen.findByText("guia.pdf");

    fireEvent.click(screen.getByRole("button", { name: "guia.pdf" }));

    expect(await screen.findByTitle("Vista previa de guia.pdf")).toBeInTheDocument();
    expect(servicios.descargar).toHaveBeenCalledWith(tarea.id_tarea, adjunto.id_archivo);
  });

  it("muestra imágenes en la vista previa integrada", async () => {
    servicios.listar.mockResolvedValue([{ ...adjunto, nombre: "apunte.png", tipo: "PNG" }]);
    servicios.descargar.mockResolvedValue(new Blob(["imagen"], { type: "image/png" }));
    Object.defineProperty(URL, "createObjectURL", { configurable: true, value: vi.fn(() => "blob:imagen") });
    Object.defineProperty(URL, "revokeObjectURL", { configurable: true, value: vi.fn() });
    renderModalDetalle();
    await screen.findByText("apunte.png");

    fireEvent.click(screen.getByRole("button", { name: "apunte.png" }));

    expect(await screen.findByRole("img", { name: "apunte.png" })).toHaveAttribute("src", "blob:imagen");
  });

  it("renderiza DOCX en el visor y permite descargar el original", async () => {
    servicios.listar.mockResolvedValue([{ ...adjunto, nombre: "guia.docx", tipo: "DOCX" }]);
    servicios.descargar.mockResolvedValue(
      new Blob(["docx"], {
        type: "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
      }),
    );
    renderModalDetalle();
    await screen.findByText("guia.docx");

    fireEvent.click(screen.getByRole("button", { name: "guia.docx" }));

    const dialog = await screen.findByRole("dialog", { name: "Vista previa de guia.docx" });
    expect(await screen.findByText("Contenido de Word")).toBeInTheDocument();
    expect(docxRenderer.render).toHaveBeenCalled();
    expect(within(dialog).getByRole("button", { name: "Descargar" })).toBeInTheDocument();
  });
});
