import { fireEvent, render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { describe, expect, test, vi } from 'vitest';
import { FormularioRegistro } from '../src/components/register/Formularioregister';
import { LONGITUD_MINIMA_CONTRASENA } from '../src/utils/contrasena';

import { registrarUsuario } from '../src/services/authService';

vi.mock('../src/services/authService', () => ({
  registrarUsuario: vi.fn(),
}));

async function completarConsentimientos(user: ReturnType<typeof userEvent.setup>) {
  await user.click(screen.getByRole('checkbox', { name: /Política de tratamiento de datos/i }));
  await user.click(screen.getByRole('checkbox', { name: /aviso de cookies y almacenamiento local/i }));
}

describe('CP-2 - Registro de usuario', () => {
  test('no permite registrar si faltan las confirmaciones obligatorias', async () => {
    const user = userEvent.setup();
    render(<MemoryRouter><FormularioRegistro /></MemoryRouter>);

    await user.type(screen.getByLabelText('Correo electrónico'), 'prueba@acadex.com');
    await user.type(screen.getByLabelText('Nombre de usuario'), 'Usuario Prueba');
    await user.type(screen.getByLabelText('Contraseña'), 'Prueba123');
    await user.type(screen.getByLabelText('Confirmar contraseña'), 'Prueba123');

    expect(screen.getByRole('button', { name: 'Registrarse' })).toBeDisabled();
    expect(registrarUsuario).not.toHaveBeenCalled();
  });

  test('registra el nombre y las dos confirmaciones, y redirige al inicio de sesión', async () => {
    const user = userEvent.setup();
    vi.mocked(registrarUsuario).mockResolvedValue({
      id_usuario: 1,
      correo_electronico: 'prueba@acadex.com',
    });

    render(
      <MemoryRouter initialEntries={['/registrarse']}>
        <Routes>
          <Route path="/registrarse" element={<FormularioRegistro />} />
          <Route path="/iniciarSesion" element={<h1>Página de inicio de sesión</h1>} />
        </Routes>
      </MemoryRouter>
    );

    await user.type(screen.getByLabelText('Correo electrónico'), 'prueba@acadex.com');
    await user.type(screen.getByLabelText('Nombre de usuario'), 'Usuario Prueba');
    await user.type(screen.getByLabelText('Contraseña'), 'Prueba123');
    await user.type(screen.getByLabelText('Confirmar contraseña'), 'Prueba123');
    await completarConsentimientos(user);
    await user.click(screen.getByRole('button', { name: 'Registrarse' }));

    expect(registrarUsuario).toHaveBeenCalledWith(
      'prueba@acadex.com', 'Usuario Prueba', 'Prueba123', true, true, ''
    );
    expect(await screen.findByRole('heading', { name: 'Página de inicio de sesión' }))
      .toBeInTheDocument();
  });

  test('muestra un error cuando las contraseñas no coinciden', async () => {
    const user = userEvent.setup();
    vi.clearAllMocks();
    render(<MemoryRouter><FormularioRegistro /></MemoryRouter>);

    await user.type(screen.getByLabelText('Correo electrónico'), 'prueba@acadex.com');
    await user.type(screen.getByLabelText('Nombre de usuario'), 'Usuario Prueba');
    await user.type(screen.getByLabelText('Contraseña'), 'Prueba123');
    await user.type(screen.getByLabelText('Confirmar contraseña'), 'Otra1234');
    await completarConsentimientos(user);
    await user.click(screen.getByRole('button', { name: 'Registrarse' }));

    expect(screen.getByRole('alert')).toHaveTextContent('Las contraseñas no coinciden');
    expect(registrarUsuario).not.toHaveBeenCalled();
  });

  test('rechaza una contraseña menor a ocho caracteres', async () => {
    const user = userEvent.setup();
    vi.clearAllMocks();
    render(<MemoryRouter><FormularioRegistro /></MemoryRouter>);

    await user.type(screen.getByLabelText('Correo electrónico'), 'prueba@acadex.com');
    await user.type(screen.getByLabelText('Nombre de usuario'), 'Usuario Prueba');
    const password = screen.getByLabelText('Contraseña');
    await user.type(password, '1234567');
    await user.type(screen.getByLabelText('Confirmar contraseña'), '1234567');
    await completarConsentimientos(user);

    expect(password).toHaveAttribute('minlength', '8');
    fireEvent.submit(document.querySelector('form')!);
    expect(screen.getByRole('alert')).toHaveTextContent(
      'La contraseña debe tener al menos 8 caracteres'
    );
    expect(registrarUsuario).not.toHaveBeenCalled();
  });

  test('acepta una contraseña de exactamente ocho caracteres', async () => {
    const user = userEvent.setup();
    vi.clearAllMocks();
    vi.mocked(registrarUsuario).mockResolvedValue({
      id_usuario: 1,
      correo_electronico: 'prueba@acadex.com',
    });
    const password = 'x'.repeat(LONGITUD_MINIMA_CONTRASENA);

    render(<MemoryRouter><FormularioRegistro /></MemoryRouter>);
    await user.type(screen.getByLabelText('Correo electrónico'), 'prueba@acadex.com');
    await user.type(screen.getByLabelText('Nombre de usuario'), 'Usuario Prueba');
    await user.type(screen.getByLabelText('Contraseña'), password);
    await user.type(screen.getByLabelText('Confirmar contraseña'), password);
    await completarConsentimientos(user);
    await user.click(screen.getByRole('button', { name: 'Registrarse' }));

    expect(registrarUsuario).toHaveBeenCalledWith(
      'prueba@acadex.com', 'Usuario Prueba', password, true, true, ''
    );
  });

  test('muestra un error cuando el correo ya está registrado', async () => {
    const user = userEvent.setup();
    vi.clearAllMocks();
    vi.mocked(registrarUsuario).mockRejectedValue(new Error('El correo ya está registrado'));
    render(<MemoryRouter><FormularioRegistro /></MemoryRouter>);

    await user.type(screen.getByLabelText('Correo electrónico'), 'usuario@existente.com');
    await user.type(screen.getByLabelText('Nombre de usuario'), 'Usuario Existente');
    await user.type(screen.getByLabelText('Contraseña'), 'Prueba123');
    await user.type(screen.getByLabelText('Confirmar contraseña'), 'Prueba123');
    await completarConsentimientos(user);
    await user.click(screen.getByRole('button', { name: 'Registrarse' }));

    expect(await screen.findByRole('alert')).toHaveTextContent('El correo ya está registrado');
    expect(registrarUsuario).toHaveBeenCalledWith(
      'usuario@existente.com', 'Usuario Existente', 'Prueba123', true, true, ''
    );
  });
});
