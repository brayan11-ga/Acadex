const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

interface ApiError {
    detail: string;
}

export async function registrarUsuario(email: string, username: string, password: string) {
    const res = await fetch(`${API_URL}/usuarios/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        correo_electronico: email,
        nombre_usuario: username,
        contrasena: password,
    }),
});

    if (!res.ok) {
    const error: ApiError = await res.json();
    throw new Error(error.detail || 'Error al registrar el usuario');
    }
    return res.json();
}

export async function iniciarSesion(email: string, password: string) {
    const res = await fetch(`${API_URL}/usuarios/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
    correo_electronico: email,
    contrasena: password,
    }),
});

    if (!res.ok) {
    const error: ApiError = await res.json();
    throw new Error(error.detail || 'Correo o contraseña incorrectos');
    }

  return res.json(); // { access_token, token_type }
}