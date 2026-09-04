// src/services/api.ts
const BASE_URL = "http://localhost:8000/api/v1";

export async function apiFetch<T>(
  ruta: string,
  opciones: RequestInit = {}
): Promise<T> {
  // 1. Recuperamos el token JWT guardado en el login
  const token = localStorage.getItem('access_token');

  // 2. Construimos los headers incluyendo la autorización si el token existe
  const headers: HeadersInit = {
    "Content-Type": "application/json",
    ...(token ? { "Authorization": `Bearer ${token}` } : {}),
    ...opciones.headers,
  };

  const respuesta = await fetch(`${BASE_URL}${ruta}`, {
    ...opciones,
    headers, // <-- Pasamos los headers con el token integrado
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