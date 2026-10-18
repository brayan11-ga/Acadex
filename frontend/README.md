# Frontend de Acadex

Interfaz web de Acadex, construida con React, TypeScript y Vite. Se comunica con la API FastAPI del backend para gestionar cuentas, tareas, grupos, archivos y estadísticas.

## Requisitos

- Node.js 20.19 o superior, o 22.12 o superior.
- pnpm 12.11.2, fijado por el campo `packageManager` de `package.json`. Corepack puede seleccionar esa versión.

## Configuración local

Desde esta carpeta, copia `.env.example` a `.env.local` y ajusta la dirección de la API según el entorno:

```sh
cp .env.example .env.local
```

En PowerShell:

```powershell
Copy-Item .env.example .env.local
```

Variables disponibles:

| Variable | Uso |
| --- | --- |
| `VITE_API_URL` | Origen HTTP de la API FastAPI, por ejemplo `http://localhost:8000`. |
| `VITE_ATTACHMENTS_ENABLED` | Activa la interfaz de adjuntos cuando el backend también los tiene configurados. Usa `false` para desarrollo local sin almacenamiento remoto. |

Las variables `VITE_*` se incorporan al código que recibe el navegador; no guardes contraseñas, tokens ni claves privadas en ellas.

## Instalar, desarrollar y verificar

```sh
corepack enable
pnpm install --frozen-lockfile
pnpm dev
```

Vite muestra la dirección local al iniciar. En otra terminal, ejecuta las verificaciones desde `frontend/`:

```sh
pnpm test --run
pnpm lint
pnpm build
```

- `test --run`: ejecuta la suite completa de Vitest y termina al finalizar.
- `lint`: revisa el código con Oxlint.
- `build`: comprueba TypeScript y genera el sitio optimizado en `dist/`.
- `preview`: sirve localmente el resultado ya compilado; primero ejecuta `pnpm build`.

Para probar el build:

```sh
pnpm preview
```
