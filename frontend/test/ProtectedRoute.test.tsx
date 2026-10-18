import { configureStore } from '@reduxjs/toolkit';
import { Provider } from 'react-redux';
import { fireEvent, render, screen } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { afterEach, describe, expect, test, vi } from 'vitest';

import { ProtectedRoute } from '../src/router/ProtectedRoute';
import authReducer from '../src/store/authSlice';
import { adminApi, ApiRequestError } from '../src/services/adminapi';

vi.mock('../src/services/adminapi', async (importOriginal) => {
  const original = await importOriginal<typeof import('../src/services/adminapi')>();
  return {
    ...original,
    adminApi: {
      obtenerMe: vi.fn(),
    },
  };
});

function renderRutasProtegidas() {
  const store = configureStore({ reducer: { auth: authReducer } });
  return render(
    <Provider store={store}>
      <MemoryRouter initialEntries={['/privado']}>
        <Routes>
          <Route element={<ProtectedRoute />}>
            <Route path="/privado" element={<h1>Contenido privado</h1>} />
          </Route>
          <Route path="/iniciarSesion" element={<h1>Inicio de sesión</h1>} />
        </Routes>
      </MemoryRouter>
    </Provider>
  );
}

describe('ProtectedRoute', () => {
  afterEach(() => {
    localStorage.clear();
    vi.resetAllMocks();
  });

  test('redirige cuando no hay token', async () => {
    renderRutasProtegidas();

    expect(await screen.findByRole('heading', { name: 'Inicio de sesión' }))
      .toBeInTheDocument();
    expect(adminApi.obtenerMe).not.toHaveBeenCalled();
  });

  test('redirige cuando el servidor rechaza la sesión', async () => {
    localStorage.setItem('access_token', crypto.randomUUID());
    vi.mocked(adminApi.obtenerMe).mockRejectedValue(
      new ApiRequestError(401, 'No se pudo verificar la sesión.'),
    );

    renderRutasProtegidas();

    expect(await screen.findByRole('heading', { name: 'Inicio de sesión' }))
      .toBeInTheDocument();
    expect(localStorage.getItem('access_token')).toBeNull();
  });

  test('mantiene sesión y permite reintentar ante un error de red', async () => {
    const token = crypto.randomUUID();
    localStorage.setItem('access_token', token);
    vi.mocked(adminApi.obtenerMe)
      .mockRejectedValueOnce(new TypeError('Network request failed'))
      .mockResolvedValue({
        id_ususario: 1,
        correo_electronico: 'persona@example.com',
        es_admin: false,
      });

    renderRutasProtegidas();

    expect(await screen.findByRole('alert')).toHaveTextContent(/Revisa tu conexión/);
    expect(localStorage.getItem('access_token')).toBe(token);
    expect(screen.queryByRole('heading', { name: 'Inicio de sesión' })).not.toBeInTheDocument();

    fireEvent.click(screen.getByRole('button', { name: 'Reintentar' }));

    expect(await screen.findByRole('heading', { name: 'Contenido privado' }))
      .toBeInTheDocument();
    expect(localStorage.getItem('access_token')).toBe(token);
  });

  test('mantiene sesión ante una respuesta 5xx', async () => {
    const token = crypto.randomUUID();
    localStorage.setItem('access_token', token);
    vi.mocked(adminApi.obtenerMe).mockRejectedValue(
      new ApiRequestError(503, 'No se pudo verificar la sesión.'),
    );

    renderRutasProtegidas();

    expect(await screen.findByRole('alert')).toHaveTextContent(/Revisa tu conexión/);
    expect(localStorage.getItem('access_token')).toBe(token);
    expect(screen.queryByRole('heading', { name: 'Inicio de sesión' })).not.toBeInTheDocument();
  });

  test('muestra la ruta si el servidor confirma la sesión', async () => {
    localStorage.setItem('access_token', crypto.randomUUID());
    vi.mocked(adminApi.obtenerMe).mockResolvedValue({
      id_ususario: 1,
      correo_electronico: 'persona@example.com',
      es_admin: false,
    });

    renderRutasProtegidas();

    expect(await screen.findByRole('heading', { name: 'Contenido privado' }))
      .toBeInTheDocument();
  });
});
