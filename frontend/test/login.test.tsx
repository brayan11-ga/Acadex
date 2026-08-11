import { describe, test, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import FormularioLogin from '../src/components/login/FormularioLogin';

describe('CP-007 - Validación de correo obligatorio en Login', () => {
  test('El campo de correo debe ser obligatorio', () => {
    render(<FormularioLogin />);

    const email = screen.getByLabelText(/correo electrónico/i);

    expect(email).toBeInTheDocument();
    expect(email).toHaveAttribute('type', 'email');
    expect(email).toBeRequired();
  });
});