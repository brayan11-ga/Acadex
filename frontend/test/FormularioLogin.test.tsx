import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { describe, expect, test, vi } from 'vitest';
import { FormularioLogin } from '../src/components/login/FormularioLogin';

import { iniciarSesion } from '../src/services/authService';
import { adminApi } from '../src/services/adminapi';

vi.mock('../src/services/authService', () => ({
  iniciarSesion: vi.fn(),
}));

vi.mock('../src/services/adminapi', () => ({
  adminApi: {
    obtenerMe: vi.fn(),
  },
}));

describe('CP-2 - Inicio de sesión', () => {
  test('debe iniciar sesión correctamente y redirigir al panel', async () => {
    const user = userEvent.setup();

    vi.mocked(iniciarSesion).mockResolvedValue({
      access_token: 'token-prueba',
      token_type: 'bearer',
    });

    vi.mocked(adminApi.obtenerMe).mockResolvedValue({
      es_admin: false,
    });

    render(
      <MemoryRouter initialEntries={['/iniciarSesion']}>
        <Routes>
          <Route
            path="/iniciarSesion"
            element={<FormularioLogin />}
          />

          <Route
            path="/panel"
            element={<h1>Panel de Acadex</h1>}
          />
        </Routes>
      </MemoryRouter>
    );

    await user.type(
      screen.getByLabelText('Correo electrónico'),
      'prueba@acadex.com'
    );

    await user.type(
      screen.getByLabelText('Contraseña'),
      'Prueba123'
    );

    await user.click(
      screen.getByRole('button', { name: 'Iniciar sesión' })
    );

    expect(iniciarSesion).toHaveBeenCalledWith(
      'prueba@acadex.com',
      'Prueba123'
    );

    expect(localStorage.getItem('access_token')).toBe(
      'token-prueba'
    );

    expect(adminApi.obtenerMe).toHaveBeenCalled();

    expect(
      await screen.findByRole('heading', {
        name: 'Panel de Acadex',
      })
    ).toBeInTheDocument();
  });

  test('debe mostrar un error cuando las credenciales son incorrectas', async () => {
  const user = userEvent.setup();

  vi.clearAllMocks();
  localStorage.clear();

  vi.mocked(iniciarSesion).mockRejectedValue(
    new Error('Correo o contraseña incorrectos')
  );

  render(
    <MemoryRouter initialEntries={['/iniciarSesion']}>
      <Routes>
        <Route
          path="/iniciarSesion"
          element={<FormularioLogin />}
        />

        <Route
          path="/panel"
          element={<h1>Panel de Acadex</h1>}
        />
      </Routes>
    </MemoryRouter>
  );

  await user.type(
    screen.getByLabelText('Correo electrónico'),
    'usuario@incorrecto.com'
  );

  await user.type(
    screen.getByLabelText('Contraseña'),
    'ContraseñaIncorrecta'
  );

  await user.click(
    screen.getByRole('button', { name: 'Iniciar sesión' })
  );

  expect(
    await screen.findByRole('alert')
  ).toHaveTextContent('Correo o contraseña incorrectos');

  expect(iniciarSesion).toHaveBeenCalledWith(
    'usuario@incorrecto.com',
    'ContraseñaIncorrecta'
  );

  expect(localStorage.getItem('access_token')).toBeNull();

  expect(
    screen.queryByRole('heading', {
      name: 'Panel de Acadex',
    })
  ).not.toBeInTheDocument();
});
});