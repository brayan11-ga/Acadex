import { describe, test, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import LandingPage from '../src/pages/LandingPage';

describe('CP-001 - Carga de la página principal', () => {
  test('La página principal de Acadex debe renderizarse correctamente', () => {
    render(
      <MemoryRouter>
        <LandingPage />
      </MemoryRouter>
    );

    expect(screen.getByRole('banner')).toBeInTheDocument();
    expect(screen.getByRole('main')).toBeInTheDocument();
    expect(screen.getByRole('contentinfo')).toBeInTheDocument();
  });
});