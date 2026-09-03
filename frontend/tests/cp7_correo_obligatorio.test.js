import { describe, test, expect } from 'vitest';
import { JSDOM } from 'jsdom';
import fs from 'fs';
import path from 'path';

describe('CP-07 - Validación de correo obligatorio en Login', () => {

    test('El campo de correo debe ser obligatorio', () => {

        const loginPath = path.resolve('frontend/templates/login.html');
        const html = fs.readFileSync(loginPath, 'utf-8');
        const dom = new JSDOM(html);
        const document = dom.window.document;

        const email = document.querySelector('#email');

        expect(email).not.toBeNull();
        expect(email.type).toBe('email');
        expect(email.required).toBe(true);
    });

});