// frontend/src/utils/jwt.ts
export function obtenerIdUsuarioActual(): number | null {
  const token = localStorage.getItem("access_token");
  if (!token) return null;

  try {
    const payload = token.split(".")[1];
    const decodificado = JSON.parse(atob(payload));
    return Number(decodificado.sub);
  } catch {
    return null;
  }
}