import { describe, test, expect } from 'vitest';
import { JSDOM } from 'jsdom';
import fs from 'fs';
import path from 'path';

describe('CP-007 - Validación de correo obligatorio en Login', () => {

    test('El campo de correo debe ser obligatorio', () => {

        // Ruta del archivo login.html
        const loginPath = path.resolve(
            'frontend/templates/login.html'
        );

        // Leer el HTML
        const html = fs.readFileSync(loginPath, 'utf-8');

        // Crear un DOM simulado
        const dom = new JSDOM(html);

        const document = dom.window.document;

        // Buscar el campo de correo
        const email = document.querySelector('#email');

        // Verificar que el campo exista
        expect(email).not.toBeNull();

        // Verificar que sea de tipo email
        expect(email.type).toBe('email');

        // Verificar que sea obligatorio
        expect(email.required).toBe(true);
    });

});