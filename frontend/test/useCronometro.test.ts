import { act, renderHook } from "@testing-library/react";
import { afterEach, beforeEach, expect, it, vi } from "vitest";
import { useCronometro } from "../src/hooks/useCronometro";

beforeEach(() => {
  vi.useFakeTimers();
  localStorage.clear();
});

afterEach(() => {
  vi.useRealTimers();
  localStorage.clear();
});

it("recupera una sesión en marcha y se detiene al llegar al límite", () => {
  const clave = "cronometro:tarea:40";
  localStorage.setItem(clave, JSON.stringify({
    segundosAcumulados: 2,
    corriendo: true,
    ultimaMarcaTiempo: Date.now() - 3000,
  }));

  const { result } = renderHook(() => useCronometro(40, 7));
  expect(result.current).toMatchObject({ segundos: 5, corriendo: true });

  act(() => vi.advanceTimersByTime(5000));
  expect(result.current).toMatchObject({
    segundos: 7,
    corriendo: false,
    pausadoPorLimite: true,
  });
  expect(JSON.parse(localStorage.getItem(clave)!)).toEqual({
    segundosAcumulados: 7,
    corriendo: false,
    ultimaMarcaTiempo: null,
  });
});

it("restaura cada tarea al cambiar de ID o límite y permite pausar y reiniciar", () => {
  const { result, rerender } = renderHook(
    ({ id, limite }) => useCronometro(id, limite),
    { initialProps: { id: 40, limite: 60 } },
  );

  act(() => result.current.iniciar());
  act(() => vi.advanceTimersByTime(2000));
  act(() => result.current.pausar());
  expect(result.current).toMatchObject({ segundos: 2, corriendo: false });

  rerender({ id: 41, limite: 60 });
  expect(result.current).toMatchObject({ segundos: 0, corriendo: false });
  rerender({ id: 40, limite: 1 });
  expect(result.current).toMatchObject({ segundos: 1, pausadoPorLimite: true });

  act(() => result.current.reiniciar());
  expect(result.current).toMatchObject({
    segundos: 0,
    corriendo: false,
    pausadoPorLimite: false,
  });
  expect(JSON.parse(localStorage.getItem("cronometro:tarea:40")!).segundosAcumulados).toBe(0);
});
