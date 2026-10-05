# Estructura del Proyecto

## backend/
- **app/**: Código principal.
  - **api/**: Endpoints y rutas.
  - **config/**: Configuración y variables de entorno.
  - **core/**: Lógica central y base.
  - **db/**: Conexión y configuración de base de datos.
  - **dependencies/**: Dependencias inyectables.
  - **middlewares/**: Middlewares (auth, CORS, logs).
  - **models/**: Modelos ORM.
  - **repositories/**: Acceso a datos (queries).
  - **schemas/**: Esquemas de validación (Pydantic).
  - **services/**: Lógica de negocio.
  - **utils/**: Funciones auxiliares.
  - **main.py**: Punto de entrada del servidor.
- **venv/**: Entorno virtual (no versionar).
- **requirements.txt**: Dependencias de Python.

## database/
- Scripts, migraciones o respaldos de la base de datos.

## docs/
- Documentación del proyecto.

## frontend/
- **src/**
  - **assets/**: Imágenes, fuentes y estáticos.
  - **components/**: Componentes por dominio.
    - **admin/**, **Cronometro/**, **estadisticas/**, **landing/**, **layout/**, **lider/**, **login/**, **panel/**, **register/**, **tareas/**
  - **contexts/**: Contextos de React.
  - **hooks/**: Custom hooks.
  - **layouts/**: Plantillas de diseño.
  - **pages/**: Vistas asociadas a rutas.
  - **router/**: Configuración de rutas.
  - **services/**: Llamadas a APIs y lógica de datos.
  - **store/**: Estado global.
  - **styles/**: Estilos globales y temas.
  - **types/**: Tipos e interfaces de TypeScript.
  - **utils/**: Funciones auxiliares.
  - **App.tsx**: Componente raíz.
  - **index.css**: Estilos base.
  - **main.tsx**: Punto de entrada de React.
  - **test/**, **tests/**: Pruebas.
- **.gitignore**, **.oxlintrc.json**, **index.html**
- **package.json**, **package-lock.json**
- **README.md**
- **tsconfig.json**, **tsconfig.app.json**, **tsconfig.node.json**
- **vite.config.mts**: Configuración de Vite.

## Convenciones
- Nuevos componentes por dominio → `frontend/src/components/<dominio>/`
- Nuevas vistas → `frontend/src/pages/`
- Nuevos tipos → `frontend/src/types/`
- Nuevos endpoints → `backend/app/api/`
- Nueva lógica de negocio → `backend/app/services/`

## Observaciones
- Carpetas posiblemente duplicadas: `contexts` vs. `context`, `layouts` vs. `layout`, `test` vs. `tests`. Conviene unificar.
- Mezcla de mayúsculas y minúsculas en `components/` (`Cronometro` vs. `admin`). Lo estándar es todo en minúscula.
- `components/` incluye vistas completas (`login`, `register`, `landing`, `panel`). Considera moverlas a `pages/`.