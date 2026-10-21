# Calidad y pruebas

Los comandos de esta guía están tomados de frontend/package.json, la configuración Docker y el workflow [CI](../.github/workflows/ci.yml). Esta guía describe qué está configurado; no afirma que una suite haya pasado en una máquina concreta.

## Validaciones disponibles

| Área | Comando | Qué verifica |
| --- | --- | --- |
| Frontend | pnpm lint desde frontend | Análisis estático con Oxlint |
| Frontend | pnpm build desde frontend | Compilación TypeScript y build de Vite |
| Frontend | pnpm test --run desde frontend | Suite Vitest en una ejecución |
| Backend | python -m pytest test tests -q desde backend | Suites backend que no habilitan PostgreSQL aislado |
| Seguridad de pruebas PostgreSQL | docker compose exec -T backend python -m pytest tests/test_postgres_safety.py -q | Guardas que evitan destinos PostgreSQL no autorizados |
| Integración PostgreSQL | docker compose -f docker-compose.test.yml run --build --rm integration | Migraciones y tests/test_postgres_integration.py en una base efímera |
| API con PostgreSQL | docker compose -f docker-compose.test.yml run --build --rm api-tests | Suite test en el Compose de pruebas aislado |

Para los comandos de frontend fuera de Docker, activa Corepack e instala las dependencias fijadas:

~~~sh
cd frontend
corepack enable
pnpm install --frozen-lockfile
pnpm lint
pnpm build
pnpm test --run
~~~

El Compose de pruebas no publica PostgreSQL, usa acadex_test y un almacenamiento temporal. Ejecuta integration y api-tests por separado; después libera sus recursos:

~~~sh
docker compose -f docker-compose.test.yml down
~~~

No establezcas las variables de habilitación de estas pruebas contra el Compose habitual, una base compartida, Supabase ni producción. Consulta la explicación de sus guardas en la [guía de base de datos](../database/README.md).

## Tipos de prueba

Las pruebas que no habilitan PostgreSQL aislado validan unidades y comportamiento backend que puede ejecutarse sin esa dependencia. Las pruebas de integración levantan una base efímera, aplican Alembic y verifican la interacción real con PostgreSQL o con la API. No son intercambiables: una prueba unitaria rápida no demuestra que una migración ni una consulta funcionen sobre PostgreSQL.

## Qué ejecuta CI

El workflow actual se ejecuta en Pull Requests dirigidos a develop o main y tiene tres trabajos:

1. **frontend**: Node 22, Corepack con pnpm 12.11.2, instalación bloqueada, lint, build y Vitest.
2. **backend**: Python 3.14, instalación de requirements.txt y python -m pytest test tests -q.
3. **backend-postgres**: PostgreSQL 17, migraciones Alembic y las suites API e integración en un entorno aislado.

El workflow versionado es una validación automática. La política de revisión, protección de ramas y Squash and merge está definida en [CONTRIBUTING.md](../CONTRIBUTING.md), pero su activación efectiva depende de la configuración administrativa de GitHub y no puede verificarse desde el repositorio local.

## Validación según el cambio

| Cambio | Validación mínima razonable |
| --- | --- |
| Componente, estilo o ruta frontend | Lint, build y pruebas afectadas; comprobar visualmente los estados modificados |
| Endpoint, esquema o servicio backend | Pruebas backend pertinentes y casos de error del cambio |
| Migración, modelo o consulta PostgreSQL | Revisión de migración y suites aisladas de PostgreSQL |
| Docker, variables o arranque local | docker compose config y arranque o healthcheck pertinente, sin usar secretos |
| Documentación | Enlaces relativos, comandos contra configuración y revisión del diff |

Registra en el Pull Request el comando y el resultado real. Si no se ejecutó una validación, explica el motivo, riesgo y seguimiento previsto.
