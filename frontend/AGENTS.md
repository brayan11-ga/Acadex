<!-- Ruta: frontend/AGENTS.md (dentro de la carpeta frontend/, aparte del AGENTS.md de la raíz) -->

# frontend/AGENTS.md — Reglas del frontend de Acadex

> Este archivo **complementa** al `AGENTS.md` de la raíz. Si algo choca, manda el de la raíz. Léelo antes de cualquier tarea de interfaz.

## 1. Stack y carpetas
React + TypeScript + Vite. Estado global con Redux (por ejemplo el slice de autenticación). Se ejecuta con `npm run dev` en `http://localhost:5173`.

```
frontend/src/
├── components/   # piezas reutilizables (tarjetas, modales, formularios)
├── pages/        # una página por pantalla
├── layouts/      # estructuras de página (AppLayout con Sidebar)
├── router/       # rutas; las protegidas van dentro de AppLayout
├── services/     # llamadas a la API (una función por endpoint)
├── types/        # tipos de TypeScript de lo que devuelve la API
├── contexts/  hooks/  store/  utils/
└── styles/       # un .css por componente o página + pixel-theme.css (variables de diseño)
```
Guías de diseño del equipo: `docs/DESIGN.md` y `docs/GUIA_FRONTEND.md`.

## 2. Reglas de estilo
- **Solo CSS normal** en archivos `.css` dentro de `src/styles/`. Prohibido Tailwind, shadcn/ui y cualquier cosa de Next.js.
- Colores, fuentes y espacios salen de las **variables de `pixel-theme.css`** (estilo pixel art, tema oscuro). No inventes colores sueltos.
- Reutiliza los componentes que ya existen antes de crear uno nuevo. Para una pantalla parecida a otra (por ejemplo, listas o detalles de grupos), **copia su patrón**.
- Cada archivo nuevo o modificado lleva arriba un comentario con su ruta: `// Ruta: frontend/src/pages/...` (en CSS: `/* Ruta: ... */`).

## 3. Cómo conectar una pantalla con el backend
1. La llamada a la API va en `src/services/` (no dentro del componente).
2. Los tipos de la respuesta van en `src/types/`.
3. La pantalla maneja siempre estos estados: **cargando**, **error**, **vacío** (sin datos) y **sin permisos**.
4. Las rutas protegidas van dentro de `AppLayout` en el router.
5. Ocultar un botón **no es seguridad**: el backend es quien valida los permisos. Si tocas una ruta de líder o de admin, avisa que también debe validarse en el backend.
6. Antes de implementar, lee el RF de esa función en `docs/RF/`. Sus escenarios (Dado/Cuando/Entonces) son los casos que la pantalla debe cubrir, incluidos los de error y los de lista vacía.

## 4. Receta: de un diseño de v0 a Acadex
Cuando Sam trae un diseño de v0, estará guardado en `frontend/_v0/` (carpeta temporal; **no se importa en la app**). Convierte cada pieza así:

1. Lee solo el archivo que Sam te indique; no explores toda la carpeta.
2. Quita todo lo de Next.js: `"use client"`, `next/link`, `next/image` y `next/navigation`. Usa `<a>`/`Link` de `react-router` y `<img>`, según lo que ya use el proyecto.
3. Quita Tailwind y shadcn/ui: pasa las clases a un archivo `.css` en `src/styles/` y reemplaza los componentes de shadcn por elementos o componentes propios que ya existan.
4. Cambia los colores y espacios por las variables de `pixel-theme.css`.
5. Si usa íconos, revisa qué librería de íconos ya usa el proyecto antes de agregar otra.
6. Reemplaza los datos de ejemplo (mock) por las llamadas reales de `src/services/`.
7. Muestra el plan antes de escribir código: qué archivos vas a crear o modificar.

Al terminar: indica qué archivo de `frontend/_v0/` ya se puede borrar y actualiza `memory.md`.

## 5. Para ahorrar tokens
- Una pantalla o componente por sesión.
- Trabaja solo con los archivos que Sam te nombre; no leas todo el repo.
- No pegues el código de v0 en el chat: léelo desde `frontend/_v0/`.
- No reescribas archivos completos para cambios pequeños.
