import React from 'react';
import { render, screen } from '@testing-library/react';
import { Provider } from 'react-redux';
import { MemoryRouter } from 'react-router-dom';
import { describe, test, expect } from 'vitest';
import { store } from '../src/store/store';
import { FormularioLogin } from '../src/components/login/FormularioLogin';

describe('CP-07 - Validación de correo obligatorio en Login', () => {

  test('El formulario React marca el correo como obligatorio', () => {
    render(React.createElement(Provider, { store },
      React.createElement(MemoryRouter, null, React.createElement(FormularioLogin))));
    const email = screen.getByLabelText(/correo electrónico/i);
    expect(email).toHaveAttribute('type', 'email');
    expect(email).toBeRequired();
    });

});
