import { describe, test, expect } from 'vitest';
import { JSDOM } from 'jsdom';
import fs from 'fs';
import path from 'path';

describe('CP-10 - Validación de formato de correo electrónico en Login', () => {

    const loginPath = path.resolve('frontend/templates/login.html');
    const html = fs.readFileSync(loginPath, 'utf-8');

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
        test(`Debe rechazar el formato inválido: "${correo}"`, () => {

            const dom = new JSDOM(html);
            const document = dom.window.document;
            const email = document.querySelector('#email');

            email.value = correo;

            expect(email.checkValidity()).toBe(false);
            expect(email.validity.typeMismatch).toBe(true);
        });
    });

    test('Debe aceptar un correo con formato válido', () => {

        const dom = new JSDOM(html);
        const document = dom.window.document;
        const email = document.querySelector('#email');

        email.value = 'samu@correo.com';

        expect(email.checkValidity()).toBe(true);
    });

});