import { describe, test, expect } from 'vitest';
import { JSDOM } from 'jsdom';
import fs from 'fs';
import path from 'path';

describe('CP-08 - Validación de contraseña obligatoria en Login', () => {

    test('El campo de contraseña debe ser obligatorio', () => {

        const loginPath = path.resolve('frontend/templates/login.html');
        const html = fs.readFileSync(loginPath, 'utf-8');
        const dom = new JSDOM(html);
        const document = dom.window.document;

        const password = document.querySelector('#password');

        expect(password).not.toBeNull();
        expect(password.type).toBe('password');
        expect(password.required).toBe(true);
    });

});