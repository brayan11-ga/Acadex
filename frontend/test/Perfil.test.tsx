import { fireEvent, render, renderHook, screen, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { afterEach, beforeEach, expect, it, vi } from "vitest";
import { usePerfilActual } from "../src/hooks/usePerfilActual";
import Perfil from "../src/pages/Perfil";
import { actualizarMiPerfil, obtenerMiPerfil, type PerfilBackend } from "../src/services/perfil";

vi.mock("../src/services/perfil", () => ({
  actualizarMiPerfil: vi.fn(),
  obtenerMiPerfil: vi.fn(),
}));

const perfil: PerfilBackend = {
  id_perfil: 1,
  nombre_usuario: "Ana",
  telefono: null,
  foto_perfil: null,
  descripcion: null,
  notif_activas: true,
  limite_cronometro: 25,
  id_usuario: 12,
};

beforeEach(() => {
  vi.resetAllMocks();
  localStorage.clear();
  vi.mocked(obtenerMiPerfil).mockResolvedValue(perfil);
});

afterEach(() => {
  localStorage.clear();
});

it("deja de mostrar el perfil al retirar el token de sesión", async () => {
  localStorage.setItem("access_token", "token-prueba");
  const { result, rerender } = renderHook(usePerfilActual, { wrapper: MemoryRouter });
  await waitFor(() => expect(result.current.perfil).toEqual(perfil));

  localStorage.removeItem("access_token");
  rerender();
  expect(result.current).toEqual({ perfil: null, errorServidorCaido: false });
  expect(obtenerMiPerfil).toHaveBeenCalledTimes(1);

  localStorage.setItem("access_token", "token-prueba");
  rerender();
  expect(result.current.perfil).toBeNull();
  await waitFor(() => expect(result.current.perfil).toEqual(perfil));
});

it("carga el perfil y guarda los valores editados", async () => {
  vi.mocked(actualizarMiPerfil).mockResolvedValue({ ...perfil, nombre_usuario: "Ana María" });
  render(<Perfil />);

  fireEvent.change(await screen.findByDisplayValue("Ana"), {
    target: { value: "Ana María" },
  });
  fireEvent.click(screen.getByRole("button", { name: "Guardar cambios" }));
  await waitFor(() => expect(actualizarMiPerfil).toHaveBeenCalledWith({
    nombre_usuario: "Ana María",
    telefono: undefined,
    descripcion: undefined,
    notif_activas: true,
    limite_cronometro: 25,
  }));
  expect(await screen.findByRole("button", { name: "Guardar cambios" })).toBeEnabled();
});
