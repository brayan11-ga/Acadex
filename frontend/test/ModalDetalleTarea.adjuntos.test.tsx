// Ruta: frontend/test/ModalDetalleTarea.adjuntos.test.tsx
import { fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

const servicios = vi.hoisted(() => ({
  listar: vi.fn(),
  subir: vi.fn(),
  descargar: vi.fn(),
  eliminar: vi.fn(),
  listarCategorias: vi.fn(),
  crear: vi.fn(),
  crearConPdf: vi.fn(),
  actualizar: vi.fn(),
  analizar: vi.fn(),
}));

const docxRenderer = vi.hoisted(() => ({
  render: vi.fn(),
}));

const entornoPruebas = vi.hoisted(() => ({
  VITE_ATTACHMENTS_ENABLED: "true",
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
}));

vi.mock("../src/services/categorias", () => ({
  listarCategorias: servicios.listarCategorias,
}));

vi.mock("../src/config/featureFlags", () => ({
  adjuntosHabilitados: () => entornoPruebas.VITE_ATTACHMENTS_ENABLED === "true",
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
  max_archivos: 3,
  total_archivos: 0,
  cronometro_activo: false,
  tiempo_acumulado: 0,
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

function renderFormularioCreacion(onTareaCreada = vi.fn()) {
  render(
    <FormularioNuevaTarea
      onDescartar={() => undefined}
      onTareaCreada={onTareaCreada}
    />,
  );
  return onTareaCreada;
}

async function completarDatosDeTarea() {
  await screen.findByRole("option", { name: "Lectura" });
  fireEvent.change(screen.getByPlaceholderText("¿Qué hay que hacer?"), {
    target: { value: "Entrega del capítulo" },
  });
  fireEvent.change(screen.getByLabelText(/Categoría/), { target: { value: "4" } });
  fireEvent.change(screen.getByLabelText(/Fecha de entrega/), {
    target: { value: "2026-10-20T12:00" },
  });
  fireEvent.change(screen.getByPlaceholderText("120"), { target: { value: "60" } });
}

describe("adjuntos de tareas", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    entornoPruebas.VITE_ATTACHMENTS_ENABLED = "true";
    servicios.listar.mockResolvedValue([adjunto]);
    servicios.subir.mockResolvedValue(adjunto);
    servicios.descargar.mockResolvedValue(new Blob(["archivo"]));
    servicios.eliminar.mockResolvedValue(undefined);
    servicios.listarCategorias.mockResolvedValue([
      { id_categoria: 4, nombre_categoria: "Lectura" },
    ]);
    servicios.crear.mockResolvedValue(tarea);
    servicios.crearConPdf.mockResolvedValue(tarea);
    servicios.analizar.mockResolvedValue({
      titulo: "Entrega sugerida",
      descripcion: "Resolver ejercicios del capítulo.",
      dificultad_estimada: 3,
      tiempo_estimado: 60,
      id_categoria: 4,
    });
    docxRenderer.render.mockImplementation(async (_blob: Blob, contenedor: HTMLElement) => {
      const texto = document.createElement("p");
      texto.textContent = "Contenido de Word";
      contenedor.appendChild(texto);
    });
  });

  it("oculta adjuntos y mantiene el análisis Gemini sin conservar el PDF", async () => {
    entornoPruebas.VITE_ATTACHMENTS_ENABLED = "false";
    renderModalDetalle();
    expect(screen.queryByRole("heading", { name: /adjuntos de la tarea/i })).not.toBeInTheDocument();
    expect(servicios.listar).not.toHaveBeenCalled();

    renderFormularioCreacion();
    const pdf = new File(["%PDF-1.7"], "guia.pdf", { type: "application/pdf" });
    fireEvent.change(screen.getByLabelText("Seleccionar PDF para autocompletar"), {
      target: { files: [pdf] },
    });
    fireEvent.click(screen.getByRole("button", { name: /Autocompletar con IA/ }));

    expect(await screen.findByText(/El documento no se guardó como adjunto/)).toBeInTheDocument();
    expect(servicios.analizar).toHaveBeenCalledWith(pdf);
    expect(servicios.subir).not.toHaveBeenCalled();
  });

  it("usa un solo selector de adjuntos y muestra la IA como opcional", async () => {
    renderFormularioCreacion();

    expect(await screen.findByText("OPCIONAL")).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Archivos adjuntos" })).toBeInTheDocument();
    expect(screen.getByLabelText("Seleccionar archivos adjuntos de la tarea")).toBeInTheDocument();
    expect(screen.getAllByRole("button", { name: /Autocompletar con IA/ })).toHaveLength(1);
    expect(screen.getByText("Solo puedes autocompletar con IA al adjuntar un PDF.")).toBeInTheDocument();
    expect(screen.getAllByLabelText(/Seleccionar.*archivos?/)).toHaveLength(1);
  });

  it("adjunta DOCX desde el selector único y avisa que la IA requiere PDF", async () => {
    const onTareaCreada = renderFormularioCreacion();
    const docx = new File(["documento"], "guia.docx", {
      type: "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    });

    fireEvent.change(screen.getByLabelText("Seleccionar archivos adjuntos de la tarea"), {
      target: { files: [docx] },
    });
    const botonAnalisis = screen.getByRole("button", { name: /Autocompletar con IA/ });
    expect(botonAnalisis).toHaveAttribute("aria-disabled", "true");
    expect(botonAnalisis).not.toBeDisabled();
    expect(await screen.findByRole("list", { name: "Archivos que se adjuntarán al crear la tarea" })).toHaveTextContent("guia.docx");

    fireEvent.click(botonAnalisis);
    expect(await screen.findByText(
      "Para autocompletar con IA, elige un PDF. Pronto habrá más formatos.",
    )).toBeInTheDocument();
    expect(servicios.analizar).not.toHaveBeenCalled();

    await completarDatosDeTarea();
    fireEvent.click(screen.getByRole("button", { name: "Crear →" }));

    await waitFor(() => expect(servicios.subir).toHaveBeenCalledWith(tarea.id_tarea, docx));
    expect(servicios.crear).toHaveBeenCalledTimes(1);
    expect(onTareaCreada).toHaveBeenCalledTimes(1);
  });

  it("permite autocompletar con el PDF seleccionado y lo adjunta al crear la tarea", async () => {
    const onTareaCreada = renderFormularioCreacion();
    const pdf = new File(["%PDF-1.7"], "guia.pdf", { type: "application/pdf" });
    fireEvent.change(screen.getByLabelText("Seleccionar archivos adjuntos de la tarea"), {
      target: { files: [pdf] },
    });

    const botonAnalisis = screen.getByRole("button", { name: /Autocompletar con IA/ });
    expect(botonAnalisis).toHaveAttribute("aria-disabled", "false");
    expect(await screen.findByText("PDF listo: puedes autocompletar la tarea con IA.")).toBeInTheDocument();
    expect(await screen.findByText(/Autocompletar \+ adjunto/)).toBeInTheDocument();
    fireEvent.click(botonAnalisis);

    expect(await screen.findByText("Listo. Completé los campos con sugerencias del PDF; se adjuntará al guardar.")).toBeInTheDocument();
    expect(servicios.analizar).toHaveBeenCalledWith(pdf);
    expect(servicios.subir).not.toHaveBeenCalled();

    await completarDatosDeTarea();
    fireEvent.click(screen.getByRole("button", { name: "Crear →" }));

    await waitFor(() => expect(servicios.crearConPdf).toHaveBeenCalledWith(expect.objectContaining({
      nombre: "Entrega del capítulo",
      descripcion: "Resolver ejercicios del capítulo.",
    }), pdf));
    expect(servicios.crear).not.toHaveBeenCalled();
    expect(servicios.subir).not.toHaveBeenCalled();
    expect(onTareaCreada).toHaveBeenCalledTimes(1);
  });

  it("no crea la tarea si no se pudo guardar primero el PDF analizado", async () => {
    servicios.crearConPdf.mockRejectedValueOnce(new Error("El almacenamiento no está disponible"));
    renderFormularioCreacion();
    const pdf = new File(["%PDF-1.7"], "guia.pdf", { type: "application/pdf" });
    fireEvent.change(screen.getByLabelText("Seleccionar archivos adjuntos de la tarea"), {
      target: { files: [pdf] },
    });
    fireEvent.click(screen.getByRole("button", { name: /Autocompletar con IA/ }));
    expect(await screen.findByText("Listo. Completé los campos con sugerencias del PDF; se adjuntará al guardar.")).toBeInTheDocument();

    await completarDatosDeTarea();
    fireEvent.click(screen.getByRole("button", { name: "Crear →" }));

    expect(await screen.findByText(
      "No se pudo confirmar el guardado conjunto de la tarea y su PDF. El almacenamiento no está disponible",
    )).toBeInTheDocument();
    expect(servicios.crearConPdf).toHaveBeenCalledWith(expect.any(Object), pdf);
    expect(servicios.crear).not.toHaveBeenCalled();
    expect(servicios.subir).not.toHaveBeenCalled();
    expect(screen.getByPlaceholderText("¿Qué hay que hacer?")).not.toBeDisabled();
  });

  it("permite reintentar adjuntos fallidos sin volver a crear la tarea", async () => {
    const onTareaCreada = renderFormularioCreacion();
    const archivo = new File(["imagen"], "apunte.png", { type: "image/png" });
    servicios.subir
      .mockRejectedValueOnce(new Error("El almacenamiento no está disponible"))
      .mockResolvedValueOnce(adjunto);

    fireEvent.change(screen.getByLabelText("Seleccionar archivos adjuntos de la tarea"), {
      target: { files: [archivo] },
    });
    await completarDatosDeTarea();
    fireEvent.click(screen.getByRole("button", { name: "Crear →" }));

    expect(await screen.findByRole("alert")).toHaveTextContent(
      "La tarea se guardó, pero no se pudieron subir 1 archivo",
    );
    expect(screen.getByRole("button", { name: /Cerrar/ })).toBeDisabled();
    expect(screen.getByText(/La tarea está guardada, pero el PDF\/archivo todavía no/)).toBeInTheDocument();
    expect(servicios.crear).toHaveBeenCalledTimes(1);
    expect(onTareaCreada).not.toHaveBeenCalled();

    fireEvent.click(screen.getByRole("button", { name: "Reintentar adjuntos →" }));

    await waitFor(() => expect(servicios.subir).toHaveBeenCalledTimes(2));
    expect(servicios.subir).toHaveBeenLastCalledWith(tarea.id_tarea, archivo);
    expect(servicios.crear).toHaveBeenCalledTimes(1);
    expect(onTareaCreada).toHaveBeenCalledTimes(1);
    expect(screen.getByText("La tarea y sus archivos quedaron guardados.")).toBeInTheDocument();
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
