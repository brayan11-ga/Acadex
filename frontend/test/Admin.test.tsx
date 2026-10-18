import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react';
import { afterEach, beforeEach, describe, expect, test, vi } from 'vitest';
import { MemoryRouter } from 'react-router-dom';

import Admin from '../src/pages/Admin';

const { listarMock, eliminarMock, restablecerMock } = vi.hoisted(() => ({
  listarMock: vi.fn(),
  eliminarMock: vi.fn(),
  restablecerMock: vi.fn(),
}));

vi.mock('../src/services/adminapi', () => ({
  adminApi: {
    listar: listarMock,
    eliminar: eliminarMock,
    restablecerPassword: restablecerMock,
    resumen: vi.fn(),
  },
}));

vi.mock('../src/hooks/usePerfilActual', () => ({
  usePerfilActual: () => ({ perfil: { nombre_usuario: 'Administración' } }),
}));

vi.mock('../src/components/admin/Resumen', () => ({
  Resumen: () => <div>Resumen de prueba</div>,
}));

function renderPanel() {
  return render(
    <MemoryRouter>
      <Admin />
    </MemoryRouter>,
  );
}

describe('acciones del panel administrativo', () => {
  beforeEach(() => {
    listarMock.mockResolvedValue([]);
    eliminarMock.mockResolvedValue(null);
    restablecerMock.mockResolvedValue(null);
  });

  afterEach(() => {
    cleanup();
    vi.restoreAllMocks();
  });

  test('usuarios solo permite listar, eliminar y restablecer contraseña', async () => {
    listarMock.mockResolvedValueOnce([{
      id_usuario: 7,
      correo_electronico: 'estudiante@example.test',
      fecha_registro: '2026-10-17',
      es_admin: false,
    }]);
    renderPanel();

    fireEvent.click(screen.getByRole('button', { name: 'Usuarios' }));

    expect(await screen.findByText('estudiante@example.test')).toBeInTheDocument();
    expect(screen.queryByRole('button', { name: '+ Nuevo' })).not.toBeInTheDocument();
    expect(screen.queryByRole('button', { name: 'Editar' })).not.toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Eliminar' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Restablecer contraseña' })).toBeInTheDocument();
  });

  test('categorías se muestran en modo de solo lectura', async () => {
    listarMock.mockResolvedValueOnce([{
      id_categoria: 3,
      nombre_categoria: 'Lectura',
    }]);
    renderPanel();

    fireEvent.click(screen.getByRole('button', { name: 'Categorías' }));

    expect(await screen.findByText('Lectura')).toBeInTheDocument();
    expect(screen.queryByRole('button', { name: '+ Nuevo' })).not.toBeInTheDocument();
    expect(screen.queryByRole('button', { name: 'Editar' })).not.toBeInTheDocument();
    expect(screen.queryByRole('button', { name: 'Eliminar' })).not.toBeInTheDocument();
  });

  test('muestra solo el token temporal y su vencimiento al restablecer contraseña', async () => {
    listarMock.mockResolvedValueOnce([{
      id_usuario: 7,
      correo_electronico: 'estudiante@example.test',
      fecha_registro: '2026-10-17',
      es_admin: false,
    }]);
    restablecerMock.mockResolvedValueOnce({
      valor_token: 'token-sintetico-de-prueba',
      fecha_expiracion: '2026-10-17T15:00:00Z',
    });
    vi.spyOn(window, 'confirm').mockReturnValue(true);
    const prompt = vi.spyOn(window, 'prompt').mockReturnValue(null);
    renderPanel();

    fireEvent.click(screen.getByRole('button', { name: 'Usuarios' }));
    fireEvent.click(await screen.findByRole('button', { name: 'Restablecer contraseña' }));

    expect(restablecerMock).toHaveBeenCalledWith(7);
    await waitFor(() => {
      expect(prompt).toHaveBeenCalledWith(
        expect.stringContaining('Envíalo solo al usuario por un canal seguro.'),
        'token-sintetico-de-prueba',
      );
    });
  });
});
