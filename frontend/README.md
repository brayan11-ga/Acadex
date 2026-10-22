# Frontend de Acadex

Interfaz web de Acadex, construida con React, TypeScript y Vite. Se comunica con la API FastAPI del backend para gestionar cuentas, tareas, grupos, archivos y estadísticas.

Para levantar el sistema completo por primera vez, sigue el [README raíz](../README.md) con Docker Compose. Esta guía cubre la ejecución manual del frontend; el mapa de componentes está en [docs/arquitectura.md](../docs/arquitectura.md) y las validaciones se describen en [docs/calidad-y-pruebas.md](../docs/calidad-y-pruebas.md).

## Requisitos

- Node.js 20.19 o superior, o 22.12 o superior.
- Corepack y pnpm 12.11.2, fijado por el campo `packageManager` de `package.json`.

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
corepack pnpm --version
corepack pnpm install --frozen-lockfile
corepack pnpm dev
```

`corepack pnpm --version` confirma la versión seleccionada desde `package.json`. Debe mostrar `12.11.2`. Vite muestra la dirección local al iniciar. En otra terminal, ejecuta las verificaciones desde `frontend/`:

```sh
corepack pnpm test --run
corepack pnpm lint
corepack pnpm build
```

- `test --run`: ejecuta la suite completa de Vitest y termina al finalizar.
- `lint`: revisa el código con Oxlint.
- `build`: comprueba TypeScript y genera el sitio optimizado en `dist/`.
- `preview`: sirve localmente el resultado ya compilado; primero ejecuta `corepack pnpm build`.

Para probar el build:

```sh
corepack pnpm preview
```

Los tokens y convenciones visuales que existen hoy se documentan en [docs/diseno-frontend.md](../docs/diseno-frontend.md). No incluyas secretos en archivos VITE: sus valores se incorporan al código que recibe el navegador.
