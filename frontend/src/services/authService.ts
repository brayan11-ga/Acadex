import { API_BASE_URL } from './api';

interface ApiError {
    detail?: string | Array<{ msg?: string }>;
}

async function obtenerMensajeError(res: Response, predeterminado: string): Promise<string> {
    try {
        const error = await res.json() as ApiError;
        if (typeof error.detail === 'string') return error.detail;
        if (Array.isArray(error.detail)) {
            return error.detail.map((item) => item.msg).filter(Boolean).join('. ') || predeterminado;
        }
    } catch {
        return predeterminado;
    }
    return predeterminado;
}

export async function registrarUsuario(
    email: string,
    username: string,
    password: string,
    aceptaTratamientoDatos: boolean,
    confirmaAvisoAlmacenamiento: boolean,
    honeypot: string,
) {
    const res = await fetch(`${API_BASE_URL}/usuarios/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        correo_electronico: email,
        nombre_usuario: username,
        contrasena: password,
        acepta_tratamiento_datos: aceptaTratamientoDatos,
        confirma_aviso_almacenamiento: confirmaAvisoAlmacenamiento,
        sitio_web: honeypot,
    }),
});

    if (!res.ok) {
    throw new Error(await obtenerMensajeError(res, 'Error al registrar el usuario'));
    }
    return res.json();
}

export async function iniciarSesion(email: string, password: string) {
    const res = await fetch(`${API_BASE_URL}/usuarios/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
    correo_electronico: email,
    contrasena: password,
    }),
});

    if (!res.ok) {
    throw new Error(await obtenerMensajeError(res, 'Correo o contraseña incorrectos'));
    }

  return res.json(); // { access_token, token_type }
}
