import { describe, test, expect } from 'vitest';
import { render, screen, within } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { ThemeProvider } from '../src/contexts/ThemeContext';

import Header from '../src/components/landing/Header';
import Workflow from '../src/components/landing/Workflow';
import Benefits from '../src/components/landing/Benefits';

describe('CP-004 - Navegación hacia Cómo funciona y Beneficios', () => {
  test('Los enlaces Cómo funciona y Beneficios deben apuntar a sus secciones correspondientes', () => {
    render(
      <MemoryRouter>
        <ThemeProvider>
          <Header />
          <Workflow />
          <Benefits />
        </ThemeProvider>
      </MemoryRouter>
    );

    const navegacion = screen.getByRole('navigation');

    const enlaceComoFunciona = within(navegacion).getByRole('link', {
      name: '¿Cómo funciona?',
    });

    const enlaceBeneficios = within(navegacion).getByRole('link', {
      name: 'Beneficios',
    });

    expect(enlaceComoFunciona).toBeInTheDocument();
    expect(enlaceBeneficios).toBeInTheDocument();

    expect(enlaceComoFunciona).toHaveAttribute(
      'href',
      '/#como-funciona'
    );

    expect(enlaceBeneficios).toHaveAttribute(
      'href',
      '/#beneficios'
    );

    const seccionComoFunciona = document.getElementById(
      'como-funciona'
    );

    const seccionBeneficios = document.getElementById(
      'beneficios'
    );

    expect(seccionComoFunciona).toBeInTheDocument();
    expect(seccionBeneficios).toBeInTheDocument();
  });
});
