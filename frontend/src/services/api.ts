// src/services/api.ts
const BASE_URL = "http://localhost:8000/api/v1";

export async function apiFetch<T>(
  ruta: string,
  opciones: RequestInit = {}
): Promise<T> {
  const respuesta = await fetch(`${BASE_URL}${ruta}`, {
    headers: {
      "Content-Type": "application/json",
      ...opciones.headers,
    },
    ...opciones,
  });

  if (!respuesta.ok) {
    const detalle = await respuesta.text();
    throw new Error(`Error ${respuesta.status}: ${detalle}`);
  }

  if (respuesta.status === 204) {
    return undefined as T;
  }

  return respuesta.json();
}