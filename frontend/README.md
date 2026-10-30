# Frontend de Acadex

Interfaz React, TypeScript y Vite. Usa la API FastAPI para cuentas, tareas, grupos, archivos y estadísticas.

Para instalar dependencias y ejecutar la interfaz junto con la API, sigue [Inicio manual](../docs/inicio-manual.md). La alternativa completa en contenedores está en [Inicio con Docker](../docs/inicio-docker.md).

## Configuración pública

Para el inicio manual, copia [.env.example](.env.example) a `.env.local` sin sobrescribir una configuración existente. La guía manual contiene los comandos de copia. Docker entrega el origen de la API mediante Compose.

| Variable | Uso |
| --- | --- |
| `VITE_API_URL` | Origen de la API, por ejemplo `http://localhost:8000`. El cliente añade `/api/v1`. |
| `VITE_ATTACHMENTS_ENABLED` | Habilita la interfaz de adjuntos. El backend debe habilitarlos también. Para el primer arranque conserva `false`. |

Las variables `VITE_*` se incluyen en el código del navegador: nunca contienen claves privadas. Reinicia Vite después de cambiar `.env.local`.

## Scripts disponibles

[package.json](package.json) fija pnpm 12.11.2. Ejecuta sus scripts desde `frontend/` con `corepack pnpm`:

| Script | Qué hace |
| --- | --- |
| `dev` | Inicia Vite para desarrollo |
| `build` | Comprueba TypeScript y genera `dist/` |
| `lint` | Analiza el código con Oxlint |
| `test --run` | Ejecuta Vitest una vez |
| `preview` | Sirve el build local; primero ejecuta `build` |

La secuencia de comprobaciones está en [Calidad y pruebas](../docs/calidad-y-pruebas.md). El workflow usa Node.js 22; el Dockerfile usa Node.js 24. La guía manual toma Node.js 24 como referencia.

El mapa de componentes está en [Arquitectura](../docs/arquitectura.md). Para estilos compartidos y tokens, consulta [Diseño frontend](../docs/diseno-frontend.md).
