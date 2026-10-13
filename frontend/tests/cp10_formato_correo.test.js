import React from 'react';
import { fireEvent, render, screen } from '@testing-library/react';
import { Provider } from 'react-redux';
import { MemoryRouter } from 'react-router-dom';
import { describe, test, expect } from 'vitest';
import { store } from '../src/store/store';
import { FormularioLogin } from '../src/components/login/FormularioLogin';

function renderLogin() {
    render(React.createElement(Provider, { store },
      React.createElement(MemoryRouter, null, React.createElement(FormularioLogin))));
    return screen.getByLabelText(/correo electrónico/i);
}

describe('CP-10 - Validación de formato de correo electrónico en Login', () => {

    // Nota: 'samu@correo' (sin punto/extensión) NO se incluye porque
    // el estándar HTML5 lo considera válido, aunque no sea un dominio real.
    const casosInvalidos = [
        'samu@',
        'samu.com',
        'samu@@correo.com',
        '@correo.com',
        'samu correo.com'
    ];

    casosInvalidos.forEach((correo) => {
        test(`Rechaza el formato inválido: "${correo}"`, () => {
            const email = renderLogin();
            fireEvent.change(email, { target: { value: correo } });
            expect(email.checkValidity()).toBe(false);
            expect(email.validity.typeMismatch).toBe(true);
        });
    });

    test('Acepta un correo con formato válido', () => {
        const email = renderLogin();
        fireEvent.change(email, { target: { value: 'samu@correo.com' } });
        expect(email.checkValidity()).toBe(true);
    });

});
