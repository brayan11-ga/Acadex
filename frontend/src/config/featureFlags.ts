export function adjuntosHabilitados(): boolean {
  // En un build de producción, el backend debe iniciar solo si el almacenamiento
  // persistente está configurado. No mostramos una modalidad que pierda el PDF.
  if (import.meta.env.PROD) return true;
  return import.meta.env.VITE_ATTACHMENTS_ENABLED === "true";
}
