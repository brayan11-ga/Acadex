// adminApi
import { API_BASE_URL } from './api';

export function headersConToken(extra: Record<string, string> = {}): Record<string, string> {
    const token = localStorage.getItem('access_token');
    return {
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...extra,
    };
}

export class ApiRequestError extends Error {
    constructor(public readonly status: number, message: string) {
        super(message);
        this.name = 'ApiRequestError';
    }
}

export async function fetchJSON<T>(path: string, options: RequestInit = {}): Promise<T | null> {
    try {
    const respuesta = await fetch(`${API_BASE_URL}${path}`, options);
    if (!respuesta.ok) throw new Error(`Error ${respuesta.status}`);
    if (respuesta.status === 204) return null;
    return (await respuesta.json()) as T;
    } catch (error) {
    console.error(`Error al conectar con la API (${options.method ?? 'GET'} ${path}):`, error);
    return null;
    }
}


// ---------- Helpers genéricos por entidad ----------
export const adminApi = {
    listar: <T>(entidad: string) =>
    fetchJSON<T[]>(`/${entidad}`, { headers: headersConToken() }),

    eliminar: (entidad: string, id: number | string) =>
    fetchJSON<void>(`/${entidad}/${id}`, { method: 'DELETE', headers: headersConToken() }),

    // restablecer contraseña hasheada
    restablecerPassword: <T>(id: number | string) =>
    fetchJSON<T>(`/usuarios/${id}/restablecer-password`, {
        method: 'POST',
        headers: headersConToken(),
    }),
    
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

    obtenerMe: async <T>() => {
        const respuesta = await fetch(`${API_BASE_URL}/usuarios/me`, {
            headers: headersConToken(),
        });
        if (!respuesta.ok) {
            throw new ApiRequestError(respuesta.status, 'No se pudo verificar la sesión.');
        }
        return (await respuesta.json()) as T;
    },
    resumen: <T>() => fetchJSON<T>('/admin/resumen', { headers: headersConToken() }),
};

