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

Revisa primero las nuevas revisiones de `backend/alembic/versions/` y sigue el procedimiento de la guía de base de datos. Conserva tus cambios locales y crea un respaldo antes de modificar una base con información que necesites.

### Pruebas del backend

El trabajo backend del CI instala `backend/requirements.txt` y ejecuta desde `backend/`:

```sh
python -m pytest test tests -q
```

Este comando no habilita el acceso PostgreSQL; por eso las pruebas que necesitan esa base quedan omitidas en ese trabajo. El trabajo PostgreSQL del CI ejecuta Alembic y, en procesos separados, las suites que corresponden a los servicios `api-tests` e `integration` de abajo.

Las pruebas unitarias de la guarda PostgreSQL no requieren una base de datos y pueden ejecutarse en el contenedor backend.

Ejecuta estos comandos desde la raíz del repositorio y en este orden. El Compose de pruebas crea una base local efímera en una red interna; no usa la base de desarrollo ni servicios remotos. Las pruebas de PostgreSQL van en un proceso separado:

```sh
# backend/tests: pruebas unitarias y de seguridad; PostgreSQL queda omitido aquí.
docker compose -f docker-compose.test.yml run --build --rm -e ACADEX_RUN_POSTGRES_TESTS=0 api-tests python -m pytest tests -q

# backend/test: pruebas de API.
docker compose -f docker-compose.test.yml run --build --rm api-tests

# Integración PostgreSQL, por separado.
docker compose -f docker-compose.test.yml run --build --rm integration

# Detén y elimina contenedores y red de pruebas al terminar.
docker compose -f docker-compose.test.yml down
```

Los valores predeterminados de credenciales de ese Compose son exclusivamente locales para la base efímera; no los reutilices en producción. Puedes cambiar el identificador del proyecto y sus credenciales con `ACADEX_TEST_COMPOSE_PROJECT`, `ACADEX_TEST_DB_USER` y `ACADEX_TEST_DB_PASSWORD`. El identificador debe ser `acadex-test-` seguido de 8 a 32 caracteres hexadecimales. Consulta [database/README.md](database/README.md) para las barreras y el alcance de estas pruebas.

```sh
# backend/tests: pruebas unitarias y de seguridad; PostgreSQL queda omitido aquí.
docker compose -f docker-compose.test.yml run --build --rm -e ACADEX_RUN_POSTGRES_TESTS=0 api-tests python -m pytest tests -q

# backend/test: pruebas de API.
docker compose -f docker-compose.test.yml run --build --rm api-tests

# Integración PostgreSQL, por separado.
docker compose -f docker-compose.test.yml run --build --rm integration

# Detén y elimina contenedores y red de pruebas al terminar.
docker compose -f docker-compose.test.yml down
```

Los valores predeterminados de credenciales de ese Compose son exclusivamente locales para la base efímera; no los reutilices en producción. Puedes cambiar el identificador del proyecto y sus credenciales con `ACADEX_TEST_COMPOSE_PROJECT`, `ACADEX_TEST_DB_USER` y `ACADEX_TEST_DB_PASSWORD`. El identificador debe ser `acadex-test-` seguido de 8 a 32 caracteres hexadecimales. Consulta [database/README.md](database/README.md) para las barreras y el alcance de estas pruebas.

Para ejecutar las pruebas frontend sin instalar Node.js/pnpm en el anfitrión, con el servicio frontend iniciado:

```sh
docker compose exec -T frontend pnpm test --run
docker compose exec -T frontend pnpm build
```

### Verificar un clon limpio y aislado

Este procedimiento crea una base local nueva. Usa un nombre de proyecto Compose único: Compose agrega ese nombre a los contenedores y al volumen PostgreSQL, por lo que la prueba no reutiliza los datos del proyecto normal. Confirma que los puertos elegidos estén libres.

En PowerShell, ejecuta esto desde el repositorio fuente. Clona la rama actual desde la ruta local y copia las plantillas. Los archivos copiados son locales y están ignorados por Git; no pegues credenciales reales:

```powershell
$source = (Get-Location).Path
$branch = (git branch --show-current).Trim()
git clone --branch $branch --single-branch --no-hardlinks $source Acadex-prueba
cd Acadex-prueba
Copy-Item backend/.env.example backend/.env
Copy-Item frontend/.env.example frontend/.env.local
$project = "acadex-prueba-$([guid]::NewGuid().ToString('N').Substring(0,8))"
$env:ACADEX_FRONTEND_PORT = "28173"
$env:ACADEX_API_PORT = "28180"
$env:ACADEX_DB_PORT = "28543"
$env:ACADEX_MAILPIT_UI_PORT = "28025"
$env:ACADEX_MAILPIT_SMTP_PORT = "21025"
docker compose -p $project up --build -d
docker compose -p $project ps -a
$migrateId = docker compose -p $project ps -aq migrate
docker inspect $migrateId --format '{{.State.Status}} {{.State.ExitCode}}'
Invoke-RestMethod http://localhost:28180/health/ready
```

La migración debe mostrar estado `exited` y código `0`; la verificación de salud debe responder correctamente. Abre `http://localhost:28180/docs` y usa la documentación interactiva para registrar una cuenta, iniciar sesión y crear una tarea con el token devuelto por el login. Los códigos esperados son 201 para registro, 200 para login y 201 para crear la tarea.

Al terminar, elimina solo este proyecto de prueba y su volumen nuevo:

```powershell
docker compose -p $project down --volumes --remove-orphans
```

Conserva el mismo `$project` en todos los comandos. No uses el nombre del proyecto normal para esta limpieza, porque `--volumes` borra su base PostgreSQL.

La validación de portabilidad de extremo a extremo también requiere comprobar la salud de los servicios y probar la persistencia tras un reinicio.

## Ejecución manual sin Docker Compose

Esta ruta es para desarrollo de frontend/backend directamente en el anfitrión. Requiere Node.js, pnpm, Python y una instancia PostgreSQL ya instalada y configurada; no es necesaria para el flujo recomendado con Compose.

1. Copia las plantillas sin sobrescribir configuraciones existentes:

   ```powershell
   if (-not (Test-Path .\backend\.env)) { Copy-Item .\backend\.env.example .\backend\.env }
   if (-not (Test-Path .\frontend\.env.local)) { Copy-Item .\frontend\.env.example .\frontend\.env.local }
   ```

   En macOS/Linux:

   ```sh
   test -f backend/.env || cp backend/.env.example backend/.env
   test -f frontend/.env.local || cp frontend/.env.example frontend/.env.local
   ```

2. Configura en `backend/.env` la conexión a PostgreSQL local, la clave de desarrollo y las opciones que vayas a utilizar. Mantén `VITE_API_URL` del frontend apuntando al origen de la API.
3. Instala dependencias e inicia backend y frontend en terminales separadas:

   ```sh
   cd backend
   python -m venv .venv
   # Activa el entorno virtual para tu sistema operativo.
   pip install -r requirements.txt
   uvicorn app.main:app --reload
   ```

   ```sh
   cd frontend
   corepack enable
   corepack pnpm --version
   corepack pnpm install --frozen-lockfile
   corepack pnpm dev
   ```

   `corepack pnpm --version` debe mostrar la versión fijada por `packageManager` en `frontend/package.json` (actualmente `12.11.2`). Desde `frontend/`, los demás comandos disponibles son:

   ```sh
   corepack pnpm build
   corepack pnpm test --run
   corepack pnpm lint
   ```

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
