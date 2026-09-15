import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import { describe, expect, test } from 'vitest';
import LandingPage from '../src/pages/LandingPage';
import { ThemeProvider } from '../src/contexts/ThemeContext';

describe('CP-1 - Página de inicio de Acadex', () => {
  const renderLandingPage = () => {
    render(
      <MemoryRouter>
        <ThemeProvider>
          <LandingPage />
        </ThemeProvider>
      </MemoryRouter>
    );
  };

  test('debe cargar correctamente la página principal', () => {
    renderLandingPage();

    expect(
      screen.getByText(/Organiza tus tareas, coordina tu equipo/i)
    ).toBeInTheDocument();
  });

  test('debe mostrar las secciones principales de la página', () => {
    renderLandingPage();

    expect(
      document.getElementById('funcionalidades')
    ).toBeInTheDocument();

    expect(
      document.getElementById('como-funciona')
    ).toBeInTheDocument();

    expect(
      document.getElementById('beneficios')
    ).toBeInTheDocument();
  });

  test('debe permitir cambiar entre modo claro y oscuro', async () => {
    const user = userEvent.setup();

    renderLandingPage();

    const themeToggle = screen.getByRole('checkbox') as HTMLInputElement;

    const initialState = themeToggle.checked;

    await user.click(themeToggle);

    expect(themeToggle.checked).toBe(!initialState);
  });

  test('debe permitir navegar a las diferentes secciones de la página', async () => {
  const user = userEvent.setup();

  renderLandingPage();

  const funcionalidadesLinks = screen.getAllByRole('link', {
    name: 'Funcionalidades',
  });

  const comoFuncionaLinks = screen.getAllByRole('link', {
    name: '¿Cómo funciona?',
  });

  const beneficiosLinks = screen.getAllByRole('link', {
    name: 'Beneficios',
  });

  await user.click(funcionalidadesLinks[0]);
  expect(window.location.hash).toBe('#funcionalidades');

  await user.click(comoFuncionaLinks[0]);
  expect(window.location.hash).toBe('#como-funciona');

  await user.click(beneficiosLinks[0]);
  expect(window.location.hash).toBe('#beneficios');
});
});