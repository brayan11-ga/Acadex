import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Provider } from 'react-redux';
import { MemoryRouter, Route, Routes, useLocation, useNavigationType } from 'react-router-dom';
import { describe, expect, test, vi } from 'vitest';
import { FormularioLogin } from '../src/components/login/FormularioLogin';

import { iniciarSesion } from '../src/services/authService';
import { adminApi } from '../src/services/adminapi';
import { store } from '../src/store/store';

vi.mock('../src/services/authService', () => ({
  iniciarSesion: vi.fn(),
}));

vi.mock('../src/services/adminapi', () => ({
  adminApi: {
    obtenerMe: vi.fn(),
  },
}));

describe('CP-2 - Inicio de sesión', () => {
  test('muestra el mensaje de registro después de limpiar el estado del historial', () => {
    function LoginConHistorial() {
      const { state } = useLocation();
      const tipo = useNavigationType();
      return (
        <>
          <FormularioLogin />
          <output aria-label="Historial">{tipo} {JSON.stringify(state)}</output>
        </>
      );
    }

    render(
      <Provider store={store}>
        <MemoryRouter initialEntries={[{
          pathname: '/iniciarSesion',
          state: { mensajeExito: 'Cuenta creada correctamente' },
        }]}>
          <LoginConHistorial />
        </MemoryRouter>
      </Provider>,
    );

    expect(screen.getByText('Cuenta creada correctamente')).toHaveAttribute('role', 'status');
    expect(screen.getByLabelText('Historial')).toHaveTextContent('REPLACE null');
  });

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
      <Provider store={store}>
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
      </Provider>
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
    <Provider store={store}>
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
    </Provider>
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
