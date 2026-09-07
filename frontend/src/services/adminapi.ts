const API_BASE = import.meta.env?.VITE_API_URL ?? 'http://localhost:8000/api/v1';

export function headersConToken(extra: Record<string, string> = {}): Record<string, string> {
    const token = localStorage.getItem('access_token');
    return {
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...extra,
    };
}

export async function fetchJSON<T>(path: string, options: RequestInit = {}): Promise<T | null> {
    try {
    const respuesta = await fetch(`${API_BASE}${path}`, options);
    if (!respuesta.ok) throw new Error(`Error ${respuesta.status}`);
    if (respuesta.status === 204) return null;
    return (await respuesta.json()) as T;
    } catch (error) {
    console.error('Error al conectar con la API:', error);
    return null;
    }
}

// ---------- Helpers genéricos por entidad ----------
export const adminApi = {
    listar: <T>(entidad: string) =>
    fetchJSON<T[]>(`/${entidad}`, { headers: headersConToken() }),

    eliminar: (entidad: string, id: number | string) =>
    fetchJSON<void>(`/${entidad}/${id}`, { method: 'DELETE', headers: headersConToken() }),

    actualizar: <T>(entidad: string, id: number | string, datos: Record<string, unknown>) =>
    fetchJSON<T>(`/${entidad}/${id}`, {
        method: 'PUT',
        headers: headersConToken({ 'Content-Type': 'application/json' }),
        body: JSON.stringify(datos),
    }),

    crear: <T>(entidad: string, datos: Record<string, unknown>) =>
    fetchJSON<T>(`/${entidad}`, {
        method: 'POST',
        headers: headersConToken({ 'Content-Type': 'application/json' }),
        body: JSON.stringify(datos),
    }),

    obtenerMe: <T>() => fetchJSON<T>('/usuarios/me', { headers: headersConToken() }),
};