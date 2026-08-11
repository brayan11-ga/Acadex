import { describe, test, expect } from 'vitest';
import { JSDOM } from 'jsdom';
import fs from 'fs';
import path from 'path';

describe('CP-001 - Carga de la página principal', () => {

    test('La página principal de Acadex debe cargar correctamente', () => {

        // Ruta del archivo index.html
        const indexPath = path.resolve(
            'frontend/templates/index.html'
        );

        // Leer el archivo HTML
        const html = fs.readFileSync(indexPath, 'utf-8');

        // Verificar que el archivo tenga contenido
        expect(html.length).toBeGreaterThan(0);

        // Crear un DOM simulado a partir del HTML
        const dom = new JSDOM(html);

        const document = dom.window.document;

        // Verificar que exista la estructura HTML principal
        expect(document.documentElement).not.toBeNull();
        expect(document.head).not.toBeNull();
        expect(document.body).not.toBeNull();

        // Verificar que exista un título
        const title = document.querySelector('title');

        expect(title).not.toBeNull();
        expect(title.textContent.trim().length).toBeGreaterThan(0);

        // Verificar que exista el encabezado
        const header = document.querySelector('header');

        expect(header).not.toBeNull();

        // Verificar que exista el contenido principal
        const main = document.querySelector('main');

        expect(main).not.toBeNull();

        // Verificar que exista el pie de página
        const footer = document.querySelector('footer');

        expect(footer).not.toBeNull();
    });

});