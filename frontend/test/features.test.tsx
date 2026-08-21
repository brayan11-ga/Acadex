import { describe, test, expect } from 'vitest';
import { render, screen, within } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';

import Header from '../src/components/landing/Header';
import Features from '../src/components/landing/Features';

describe('CP-003 - Navegación hacia Funcionalidades', () => {
  test('El enlace Funcionalidades debe apuntar a la sección correspondiente', () => {
    render(
      <MemoryRouter>
        <Header />
        <Features />
      </MemoryRouter>
    );

    const navegacion = screen.getByRole('navigation');

    const enlaceFuncionalidades = within(navegacion).getByRole('link', {
      name: 'Funcionalidades',
    });

    expect(enlaceFuncionalidades).toBeInTheDocument();

    expect(enlaceFuncionalidades).toHaveAttribute(
      'href',
      '/#funcionalidades'
    );

    const seccionFuncionalidades = document.getElementById(
      'funcionalidades'
    );

    expect(seccionFuncionalidades).toBeInTheDocument();
  });
});