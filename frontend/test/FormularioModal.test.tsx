import { fireEvent, render, screen } from "@testing-library/react";
import { expect, it, vi } from "vitest";
import FormularioAdmin from "../src/components/admin/FormularioModal";
import FormularioLider from "../src/components/lider/FormularioModal";

it.each([
  ["administración", FormularioAdmin],
  ["liderazgo", FormularioLider],
] as const)("reinicia el formulario de %s al reabrir o cambiar sus valores iniciales", (_, Formulario) => {
  const props = {
    titulo: "Editar registro",
    campos: [{ name: "nombre", type: "text" as const, label: "Nombre" }],
    valoresIniciales: { nombre: "Original" },
    onCerrar: vi.fn(),
    onGuardar: vi.fn(),
  };
  const { rerender } = render(<Formulario {...props} abierto />);
  fireEvent.change(screen.getByLabelText("Nombre"), { target: { value: "Borrador" } });
  rerender(<Formulario {...props} abierto />);
  expect(screen.getByLabelText("Nombre")).toHaveValue("Borrador");

  rerender(<Formulario {...props} abierto={false} />);
  expect(screen.queryByLabelText("Nombre")).toBeNull();
  rerender(<Formulario {...props} abierto />);
  expect(screen.getByLabelText("Nombre")).toHaveValue("Original");

  rerender(<Formulario {...props} valoresIniciales={{ nombre: "Otro registro" }} abierto />);
  fireEvent.click(screen.getByRole("button", { name: "Guardar Cambios" }));
  expect(props.onGuardar).toHaveBeenCalledWith({ nombre: "Otro registro" });
});
