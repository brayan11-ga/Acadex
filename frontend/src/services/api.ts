// src/services/api.ts
// VITE_API_URL is the API origin (for example, http://localhost:8000).
const API_ORIGIN = import.meta.env.VITE_API_URL?.trim();

if (!API_ORIGIN) {
  throw new Error("Falta configurar VITE_API_URL en el entorno del frontend.");
}

export const API_BASE_URL = `${API_ORIGIN.replace(/\/+$/, "")}/api/v1`;

async function mensajeDeRespuestaError(respuesta: Response): Promise<string> {
  const detalle = await respuesta.text();
  try {
    const parsed = JSON.parse(detalle);
    if (parsed.detail) {
      return typeof parsed.detail === "string" ? parsed.detail : JSON.stringify(parsed.detail);
    }
  } catch {
    // Si no es JSON, conserva el texto del servidor.
  }
  return detalle;
}

export async function apiFetch<T>(
  ruta: string,
  opciones: RequestInit = {}
): Promise<T> {
  // 1. Recuperamos el token JWT guardado en el login
  const token = localStorage.getItem('access_token');

  // Detectamos si estamos enviando un archivo (FormData)
  const esFormData = opciones.body instanceof FormData;


  // 2. Construimos los headers incluyendo la autorización si el token existe
  const headers: HeadersInit = {
    // Solo ponemos application/json si NO es FormData
    ...(esFormData ? {} : { "Content-Type": "application/json" }),
    ...(token ? { "Authorization": `Bearer ${token}` } : {}),
    ...opciones.headers,
  };

  const respuesta = await fetch(`${API_BASE_URL}${ruta}`, {
    ...opciones,
    headers, // <-- Pasamos los headers con el token integrado
  });

  if (!respuesta.ok) {
    throw new Error(await mensajeDeRespuestaError(respuesta));
  }

  if (respuesta.status === 204) {
    return undefined as T;
  }

  return respuesta.json();
}

export async function apiFetchBlob(
  ruta: string,
  opciones: RequestInit = {}
): Promise<Blob> {
  const token = localStorage.getItem('access_token');
  const respuesta = await fetch(`${API_BASE_URL}${ruta}`, {
    ...opciones,
    headers: {
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...opciones.headers,
    },
  });

  if (!respuesta.ok) {
    throw new Error(await mensajeDeRespuestaError(respuesta));
  }

  return respuesta.blob();
}
