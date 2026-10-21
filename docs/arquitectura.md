# Arquitectura de Acadex

Esta guía describe la arquitectura observada en el código y la configuración versionados. No sustituye la documentación OpenAPI que ofrece una instancia de la API en **/docs**.

## Componentes y responsabilidades

| Componente | Responsabilidad verificada |
| --- | --- |
| frontend | Interfaz React/TypeScript, rutas de la aplicación, estado del cliente y consumo de la API |
| backend | API FastAPI, autenticación, reglas de aplicación, acceso a datos y servicios integrados |
| PostgreSQL | Persistencia relacional de la aplicación |
| Alembic | Evolución versionada del esquema desde backend/alembic/versions |
| Docker Compose | Entorno local con PostgreSQL, migraciones, API, frontend y Mailpit |
| Mailpit | Captura local de correo cuando se habilitan funciones que lo envían |

~~~mermaid
flowchart LR
    U[Navegador] --> F[Frontend Vite :5173]
    F -->|HTTP /api/v1| A[FastAPI :8000]
    A --> S[Servicios y repositorios]
    S --> P[(PostgreSQL)]
    M[Servicio migrate] -->|alembic upgrade head| P
    A -. configuración opcional .-> G[Gemini]
    A -. configuración opcional .-> SS[Supabase Storage]
    A -. correo local .-> MP[Mailpit]
~~~

El diagrama representa desarrollo local con los puertos predeterminados. Gemini, almacenamiento Supabase y SMTP externo requieren variables de configuración y no son necesarios para que Compose levante las funciones básicas. Mailpit sustituye el servidor SMTP externo en el entorno Compose.

## Flujo de una petición

1. El navegador carga la aplicación servida por Vite.
2. Los servicios del frontend toman VITE_API_URL y llaman a la API con prefijo /api/v1; las rutas protegidas envían el token de autenticación cuando corresponde.
3. backend/app/main.py crea FastAPI, configura CORS e incorpora los routers de la API.
4. Los endpoints delegan en servicios, repositorios, modelos y esquemas según el módulo.
5. SQLAlchemy accede a PostgreSQL. El esquema se crea o evoluciona mediante Alembic, no desde FastAPI durante una petición.

Los endpoints disponibles, sus modelos y respuestas se consultan en OpenAPI (en /docs) en una instancia ejecutándose.

## Organización relevante

~~~text
Acadex/
├── frontend/
│   └── src/
│       ├── components/  contexts/  hooks/  layouts/  pages/
│       ├── router/  services/  store/  styles/  types/  utils/
├── backend/
│   ├── app/
│   │   ├── api/  config/  core/  db/  dependencies/  middlewares/
│   │   ├── models/  repositories/  schemas/  services/  testing/  utils/
│   ├── alembic/versions/
│   ├── test/  tests/
│   └── scripts/
├── database/
├── docs/
├── docker-compose.yml
└── docker-compose.test.yml
~~~

Los directorios anteriores son una orientación de alto nivel, no un contrato para forzar nuevas carpetas. Consulta el archivo cercano al cambio antes de añadir una capa o mover código.

## Configuración y entornos

- docker-compose.yml define el entorno local y mapea los servicios en 127.0.0.1.
- El archivo .env de la raíz sirve a la interpolación de Compose. backend/.env es opcional para backend y migraciones; frontend/.env.local es para Vite ejecutado manualmente.
- backend/app/config/settings.py valida configuración de CORS, almacenamiento y correo según el entorno.
- La fuente vigente del esquema es Alembic. Los SQL de database y backend/migrations que la guía de datos identifica como históricos no son el procedimiento de arranque.

Los detalles operativos están en el [README raíz](../README.md), [backend/README.md](../backend/README.md), [frontend/README.md](../frontend/README.md) y [database/README.md](../database/README.md).
