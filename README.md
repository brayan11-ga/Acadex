# Acadex

[![CI](https://github.com/brayan11-ga/Acadex/actions/workflows/ci.yml/badge.svg)](https://github.com/brayan11-ga/Acadex/actions/workflows/ci.yml)

Acadex es una aplicación web para apoyar la organización académica individual y colaborativa. El código actual incluye cuentas y perfiles, tareas y categorías, grupos e integrantes, cronómetro, panel y calendario, estadísticas, administración y adjuntos. Algunas capacidades opcionales, como análisis con IA, almacenamiento remoto y correo, dependen de configuración adicional.

Este README es el punto de entrada. Los procedimientos detallados y las reglas de colaboración viven en los documentos enlazados más abajo.

## Stack y arquitectura

| Área | Tecnologías verificadas |
| --- | --- |
| Frontend | React, TypeScript, Vite, React Router, Redux Toolkit, Vitest y Oxlint |
| Backend | Python, FastAPI, SQLAlchemy, Pydantic, JWT y pytest |
| Datos | PostgreSQL y Alembic |
| Desarrollo local | Docker Compose, Mailpit, Node.js/pnpm y Python para ejecución manual |

En desarrollo con Compose, el navegador consume el frontend de Vite, que llama a la API FastAPI bajo **/api/v1**. El backend usa PostgreSQL; el servicio **migrate** aplica las migraciones Alembic antes de iniciar la API. Consulta la [arquitectura](docs/arquitectura.md) para el diagrama, los directorios y las integraciones opcionales.

## Inicio rápido con Docker Compose

Esta es la ruta recomendada para un clon nuevo. Requiere Git y Docker Desktop con Docker Compose **v2.24.0 o superior**. No requiere instalar Node.js, Python ni PostgreSQL en el equipo anfitrión.

~~~sh
docker compose version
docker compose up --build
~~~

En un volumen nuevo, PostgreSQL crea la base local y **migrate** ejecuta **alembic upgrade head** antes de que FastAPI inicie. Mantén la terminal abierta para consultar los logs. Para iniciarlo en segundo plano, usa **docker compose up --build -d**.

Servicios locales predeterminados:

| Servicio | Dirección |
| --- | --- |
| Aplicación web | <http://localhost:5173/> |
| API y OpenAPI | <http://localhost:8000/docs> |
| Salud de la API | <http://localhost:8000/health/ready> |
| Bandeja local de Mailpit | <http://localhost:8025/> |
| PostgreSQL para herramientas locales | localhost:5433 |

Los puertos se exponen únicamente en **127.0.0.1**. Se pueden ajustar con **ACADEX_FRONTEND_PORT**, **ACADEX_API_PORT**, **ACADEX_DB_PORT**, **ACADEX_MAILPIT_UI_PORT** y **ACADEX_MAILPIT_SMTP_PORT** antes de levantar Compose.

~~~sh
docker compose ps
docker compose logs -f backend
docker compose stop
docker compose start
~~~

**docker compose down** conserva el volumen de PostgreSQL; no uses **docker compose down -v** para detener o actualizar el entorno, porque elimina los datos locales. Antes de usar una base ya existente o ejecutar una migración, sigue la [guía de base de datos](database/README.md).

## Configuración y secretos

Compose puede iniciar sin archivos **.env**: sus valores predeterminados son solo para desarrollo local. Hay tres ámbitos de configuración que no deben confundirse:

- **.env** en la raíz: Compose lo usa para interpolar variables como puertos y **DB_NAME**.
- **backend/.env**: configuración opcional del backend y las migraciones; parte de la plantilla [backend/.env.example](backend/.env.example).
- **frontend/.env.local**: configuración de Vite cuando se ejecuta fuera de Compose; parte de [frontend/.env.example](frontend/.env.example).

No subas archivos .env, claves JWT reales, tokens de Gemini o Supabase, contraseñas, bases de datos ni adjuntos. Las funciones de IA, almacenamiento Supabase y SMTP tienen configuración opcional y sus secretos pertenecen al entorno seguro donde se ejecuten, no al repositorio. La [guía del backend](backend/README.md) explica el alcance de las plantillas; la de [Alembic](docs/DESPLIEGUE_ALEMBIC.md) trata la adopción de una base existente.

## Comandos esenciales

Los comandos se ejecutan desde la raíz, salvo que se indique otra ubicación.

~~~sh
# Pruebas y compilación del frontend dentro del entorno Compose
docker compose exec -T frontend pnpm test --run
docker compose exec -T frontend pnpm build

# Pruebas aisladas con PostgreSQL efímero; ejecutar una suite a la vez
docker compose -f docker-compose.test.yml run --build --rm integration
docker compose -f docker-compose.test.yml run --build --rm api-tests
docker compose -f docker-compose.test.yml down
~~~

Para desarrollo manual, consulta [frontend/README.md](frontend/README.md) y [backend/README.md](backend/README.md). La lista de comandos, el alcance de cada prueba y lo que ejecuta CI están en [calidad y pruebas](docs/calidad-y-pruebas.md). La documentación OpenAPI en **/docs** es la referencia de endpoints disponibles en una instancia en ejecución; no se mantiene una lista duplicada aquí.

## Documentación

- [Índice de documentación](docs/README.md): mapa, responsables y fuentes canónicas.
- [Arquitectura](docs/arquitectura.md): componentes, flujos y estructura del repositorio.
- [Calidad y pruebas](docs/calidad-y-pruebas.md): comandos de lint, compilación, pruebas y CI.
- [Diseño frontend](docs/diseno-frontend.md): tokens y convenciones verificadas en los estilos actuales.
- [Base de datos](database/README.md): Alembic, seguridad de migraciones y pruebas PostgreSQL.
- [Adopción de Alembic en una base existente](docs/DESPLIEGUE_ALEMBIC.md): procedimiento excepcional y cautelas.
- [Requisitos funcionales](docs/RF/README.md) y [no funcionales](docs/RNF/README.md): fuente de alcance y criterios de producto.

## Colaborar

La fuente central del flujo de trabajo es [CONTRIBUTING.md](CONTRIBUTING.md). Antes de comenzar una funcionalidad o una corrección, revisa la Issue asociada, los requisitos que correspondan y su tarjeta en el GitHub Project existente de Acadex. El flujo documentado cubre planificación, rama, cambios, pruebas, Pull Request, revisión, integración y actualización de la documentación.

Las plantillas de Issue y Pull Request facilitan ese flujo, pero no sustituyen una descripción clara ni las validaciones técnicas.

## Límites de entorno

Esta documentación describe desarrollo local a partir de la configuración versionada. No constituye un procedimiento de despliegue ni confirma el estado de una base de producción, de Supabase o de otro proveedor externo. Cualquier cambio en datos existentes requiere identificar el destino, revisar su historial y contar con un respaldo recuperable antes de ejecutar una migración.
