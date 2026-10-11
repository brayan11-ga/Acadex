export const TAMANO_MAXIMO_ADJUNTO = 5 * 1024 * 1024;

const EXTENSIONES_ADMITIDAS = new Set([".pdf", ".docx", ".jpg", ".jpeg", ".png"]);

export function claveArchivo(archivo: File): string {
  return `${archivo.name}\u0000${archivo.size}\u0000${archivo.lastModified}`;
}

export function validarArchivoAdjunto(archivo: File): string | null {
  const extension = `.${archivo.name.split(".").pop()?.toLowerCase() ?? ""}`;
  if (!EXTENSIONES_ADMITIDAS.has(extension)) {
    return `${archivo.name}: formato no admitido. Usa PDF, DOCX, JPG o PNG.`;
  }
  if (archivo.size === 0) return `${archivo.name}: el archivo está vacío.`;
  if (archivo.size > TAMANO_MAXIMO_ADJUNTO) return `${archivo.name}: supera el límite de 5 MB.`;
  return null;
}
