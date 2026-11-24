export function validarAsignados(idsSeleccionados: number[]): string | undefined {
  return idsSeleccionados.length === 0 ? "Elige al menos un integrante" : undefined;
}
