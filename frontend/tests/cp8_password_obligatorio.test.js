import React from 'react';
import { render, screen } from '@testing-library/react';
import { Provider } from 'react-redux';
import { MemoryRouter } from 'react-router-dom';
import { describe, test, expect } from 'vitest';
import { store } from '../src/store/store';
import { FormularioLogin } from '../src/components/login/FormularioLogin';

describe('CP-08 - Validación de contraseña obligatoria en Login', () => {

  test('El formulario React marca la contraseña como obligatoria', () => {
    render(React.createElement(Provider, { store },
      React.createElement(MemoryRouter, null, React.createElement(FormularioLogin))));
    const password = screen.getByLabelText(/contraseña/i);
    expect(password).toHaveAttribute('type', 'password');
    expect(password).toBeRequired();
    });

});
