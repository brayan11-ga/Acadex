import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { describe, expect, test, vi } from 'vitest';
import { FormularioRegistro } from '../src/components/register/Formularioregister';

import { registrarUsuario } from '../src/services/authService';

vi.mock('../src/services/authService', () => ({
  registrarUsuario: vi.fn(),
}));

describe('CP-2 - Registro de usuario', () => {
  test('debe registrar correctamente un usuario y redirigir al inicio de sesión', async () => {
    const user = userEvent.setup();

    vi.mocked(registrarUsuario).mockResolvedValue({
      id_usuario: 1,
      correo_electronico: 'prueba@acadex.com',
    });

    render(
      <MemoryRouter initialEntries={['/registrarse']}>
        <Routes>
          <Route
            path="/registrarse"
            element={<FormularioRegistro />}
          />

          <Route
            path="/iniciarSesion"
            element={<h1>Página de inicio de sesión</h1>}
          />
        </Routes>
      </MemoryRouter>
    );

    const email = screen.getByLabelText('Correo electrónico');
    const username = screen.getByLabelText('Nombre de usuario');
    const password = screen.getByLabelText('Contraseña');
    const confirmPassword = screen.getByLabelText('Confirmar contraseña');

    await user.type(email, 'prueba@acadex.com');
    await user.type(username, 'Usuario Prueba');
    await user.type(password, 'Prueba123');
    await user.type(confirmPassword, 'Prueba123');

    await user.click(
      screen.getByRole('button', { name: 'Registrarse' })
    );

    expect(registrarUsuario).toHaveBeenCalledWith(
      'prueba@acadex.com',
      'Usuario Prueba',
      'Prueba123'
    );

    expect(
      await screen.findByRole('heading', {
        name: 'Página de inicio de sesión',
      })
    ).toBeInTheDocument();
  });

  test('debe mostrar un error cuando las contraseñas no coinciden', async () => {
    const user = userEvent.setup();

    vi.clearAllMocks();

    render(
      <MemoryRouter>
        <FormularioRegistro />
      </MemoryRouter>
    );

    await user.type(
      screen.getByLabelText('Correo electrónico'),
      'prueba@acadex.com'
    );

    await user.type(
      screen.getByLabelText('Nombre de usuario'),
      'Usuario Prueba'
    );

    await user.type(
      screen.getByLabelText('Contraseña'),
      'Prueba123'
    );

    await user.type(
      screen.getByLabelText('Confirmar contraseña'),
      'Otra1234'
    );

    await user.click(
      screen.getByRole('button', { name: 'Registrarse' })
    );

    expect(screen.getByRole('alert')).toHaveTextContent(
      'Las contraseñas no coinciden'
    );

    expect(registrarUsuario).not.toHaveBeenCalled();
  });

  test('debe mostrar un error cuando la contraseña tiene menos de 8 caracteres', async () => {
  const user = userEvent.setup();

  vi.clearAllMocks();

  render(
    <MemoryRouter>
      <FormularioRegistro />
    </MemoryRouter>
  );

  await user.type(
    screen.getByLabelText('Correo electrónico'),
    'prueba@acadex.com'
  );

  await user.type(
    screen.getByLabelText('Nombre de usuario'),
    'Usuario Prueba'
  );

  await user.type(
    screen.getByLabelText('Contraseña'),
    '1234567'
  );

  await user.type(
    screen.getByLabelText('Confirmar contraseña'),
    '1234567'
  );

  await user.click(
    screen.getByRole('button', { name: 'Registrarse' })
  );

  expect(screen.getByRole('alert')).toHaveTextContent(
    'La contraseña debe tener al menos 8 caracteres'
  );

  expect(registrarUsuario).not.toHaveBeenCalled();
});

test('debe mostrar un error cuando el correo ya está registrado', async () => {
  const user = userEvent.setup();

  vi.clearAllMocks();

  vi.mocked(registrarUsuario).mockRejectedValue(
    new Error('El correo ya está registrado')
  );

  render(
    <MemoryRouter>
      <FormularioRegistro />
    </MemoryRouter>
  );

  await user.type(
    screen.getByLabelText('Correo electrónico'),
    'usuario@existente.com'
  );

  await user.type(
    screen.getByLabelText('Nombre de usuario'),
    'Usuario Existente'
  );

  await user.type(
    screen.getByLabelText('Contraseña'),
    'Prueba123'
  );

  await user.type(
    screen.getByLabelText('Confirmar contraseña'),
    'Prueba123'
  );

  await user.click(
    screen.getByRole('button', { name: 'Registrarse' })
  );

  expect(
    await screen.findByRole('alert')
  ).toHaveTextContent('El correo ya está registrado');

  expect(registrarUsuario).toHaveBeenCalledWith(
    'usuario@existente.com',
    'Usuario Existente',
    'Prueba123'
  );
});
});