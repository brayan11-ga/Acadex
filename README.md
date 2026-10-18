# ACADEX

Aplicación web académica colaborativa para organizar tareas, grupos, integrantes, archivos y progreso de proyectos. Usa React, TypeScript y Vite; FastAPI y SQLAlchemy; y PostgreSQL.

## Inicio rápido con Docker Compose

Esta es la ruta recomendada para probar ACADEX desde un computador limpio. Solo necesitas **Git** y **Docker Desktop** con Docker Compose v2.24.0 o superior. No necesitas instalar Node.js, Python, PostgreSQL ni npm en el computador anfitrión.

Comprueba Docker Compose y que el motor esté iniciado:

```sh
docker compose version
docker info
```

Clona la rama predeterminada configurada en GitHub y entra al repositorio. El comando sigue la rama predeterminada del servidor; no requiere elegir una rama `docker`:

```sh
git clone https://github.com/brayan11-ga/Acadex.git
cd Acadex
```

En un clon nuevo, inicia toda la aplicación con un solo comando:

```sh
docker compose up --build
```

Compose inicia PostgreSQL (`db`), el servicio de migraciones (`migrate`), Mailpit, FastAPI y Vite. PostgreSQL crea la base `acadex` al inicializar un volumen vacío. Cuando PostgreSQL está saludable, `migrate` ejecuta `alembic upgrade head`; FastAPI espera a que termine correctamente. Si una migración falla, FastAPI no inicia. Alembic registra las revisiones aplicadas y no las repite en reinicios normales. FastAPI no ejecuta DDL por su cuenta.

Si ya existe una base, sigue primero las comprobaciones de [database/README.md](database/README.md); no ejecutes una actualización hasta confirmar el destino y su estado.

El comando mantiene los logs en esa terminal; déjala abierta mientras uses la aplicación. Para consultar el estado desde otra terminal, ejecuta `docker compose ps`. Si prefieres dejar el stack en segundo plano, usa `docker compose up --build -d` y consulta los logs con `docker compose logs -f`.

El arranque normal inicia cinco servicios: PostgreSQL (`db`), migraciones (`migrate`), Mailpit (`mailpit`), FastAPI (`backend`) y Vite (`frontend`). PostgreSQL crea la base al preparar un volumen vacío; Alembic crea el esquema. No existe un perfil `schema` que debas activar. El backend espera a PostgreSQL y a que `migrate` termine con código cero. El frontend espera a que el backend esté listo.

Accede desde el navegador del computador anfitrión:

- Aplicación: <http://localhost:5173/>
- API y documentación interactiva: <http://localhost:8000/docs>
- Verificación de disponibilidad del backend: <http://localhost:8000/health/ready>
- Bandeja local de correo de prueba (Mailpit): <http://localhost:8025/>

El navegador usa `http://localhost:8000` para la API. Dentro de la red de Compose, el backend llega a PostgreSQL por `db:5432`; `localhost` dentro de un contenedor se refiere a ese mismo contenedor. PostgreSQL se publica en el anfitrión como `localhost:5433` para herramientas locales, pero el backend no usa ese puerto publicado. Para pgAdmin instalado en el computador, usa host `localhost`, puerto `5433` y base `acadex`. Usa el usuario y la contraseña locales configurados para Compose; no uses credenciales de producción.

### Configuración y archivos `.env`

El stack Compose puede arrancar sin crear ningún archivo `.env`. Los valores predeterminados del Compose son de **desarrollo local solamente**; no son credenciales ni configuración de producción.

Hay varios mecanismos distintos:

1. **`.env` en la raíz:** Compose lo lee automáticamente para interpolar expresiones `${VARIABLE}` del archivo Compose. También puede recibir esas variables del entorno de la terminal. `DB_NAME` en este archivo configura el nombre de la base para PostgreSQL, Alembic y FastAPI. Este archivo no se entrega automáticamente a los contenedores; Compose solo pasa las variables declaradas bajo `environment` o las incluidas en `env_file`.
2. **`env_file` de backend:** `backend/.env` es opcional en Compose. Sus variables se incorporan al entorno de los contenedores de backend y migraciones. Una clave declarada también bajo `environment` toma el valor de `environment`, incluso cuando `backend/.env` tenga otro valor. En particular, `backend/.env` no reemplaza `DB_NAME` declarado por Compose ni cambia el nombre de la base que PostgreSQL inicializa.
3. **`environment`:** `docker-compose.yml` define las variables de ejecución del stack, entre ellas conexión a PostgreSQL, clave local de desarrollo, origen CORS, URL de navegador y Mailpit. Las expresiones `${VAR:-valor}` usan el valor de la terminal o del `.env` raíz y recurren al valor indicado si falta o está vacío.
4. **Configuración de la aplicación:** Pydantic en el backend lee primero las variables del proceso y puede leer `.env` desde su directorio de trabajo cuando ese archivo existe. El contexto Docker excluye archivos `.env` personales; Compose inyecta las variables declaradas. Vite recibe `VITE_API_URL` desde Compose. `frontend/.env.local` se usa para Vite ejecutado manualmente, no es necesario para Compose.
5. **Plantillas `.env.example`:** son guías versionadas para ejecución manual o configuración adicional. No se copian automáticamente ni contienen credenciales personales. `.gitignore` excluye `.env` y `.env.*`, pero conserva `.env.example`.

Valores y funciones locales:

- PostgreSQL, la clave JWT local, CORS y los puertos tienen valores predeterminados de desarrollo en Compose. Cambia la clave JWT antes de cualquier despliegue y configura producción mediante el mecanismo seguro de ese entorno.
- Gemini es opcional para iniciar y usar las funciones básicas. Sin `GEMINI_API_KEY`, la operación de análisis con IA devuelve un error de servicio no disponible, pero no bloquea el arranque.
- Los adjuntos están desactivados por defecto y no requieren credenciales Supabase en desarrollo. La configuración de Supabase solo corresponde a un despliegue que habilite almacenamiento remoto.
- Mailpit está disponible para capturar correo local cuando se habilita una función que lo envía. La recuperación de contraseña está desactivada de forma predeterminada. No se requiere SMTP externo ni se envían correos a destinatarios reales.
- Si necesitas habilitar una opción local que no esté mapeada explícitamente por Compose, puedes añadirla a `backend/.env`; no incluyas secretos en Git. En producción, usa secretos gestionados y no reutilices los valores locales.

### Nombre de la base y volumen existente

Una instalación nueva usa `acadex` cuando PostgreSQL prepara un volumen vacío. El recurso `pgdata` conserva su función y no se renombra ni se elimina. PostgreSQL solo usa `POSTGRES_DB` durante la inicialización inicial; cambiar `DB_NAME` no renombra una base dentro de un volumen ya inicializado.

La instalación existente de este equipo conserva `acadex_dev` en el volumen Docker conocido como `acadex_pgdata`. Para seguir usando esa base después de actualizar el repositorio, configura `DB_NAME=acadex_dev` en un `.env` local en la raíz antes de iniciar Compose. `.gitignore` excluye ese archivo. No hace falta crearlo para una instalación nueva, ni debe crearse ahora. Si el nombre configurado no existe en el volumen, `migrate` no podrá conectarse y FastAPI permanecerá detenido; no se renombra ni se borra la base existente.

La base local de Compose es independiente de Supabase. No copies credenciales de Supabase a los archivos locales; la configuración de producción pertenece a los paneles de los proveedores.

### Puertos

Los puertos publicados se ligan a `127.0.0.1`:

| Servicio | Puerto local predeterminado | Variable para cambiarlo |
| --- | ---: | --- |
| Frontend | 5173 | `ACADEX_FRONTEND_PORT` |
| API | 8000 | `ACADEX_API_PORT` |
| PostgreSQL | 5433 | `ACADEX_DB_PORT` |
| Mailpit web | 8025 | `ACADEX_MAILPIT_UI_PORT` |
| Mailpit SMTP | 1025 | `ACADEX_MAILPIT_SMTP_PORT` |

Por ejemplo, en PowerShell para cambiar el frontend:

```powershell
$env:ACADEX_FRONTEND_PORT = "5174"
docker compose up --build -d
```

En macOS/Linux:

```sh
ACADEX_FRONTEND_PORT=5174 docker compose up --build -d
```

La URL de API del navegador sigue siendo `localhost:8000`. Compose ajusta el origen CORS y `FRONTEND_URL` al puerto del frontend. Si eliges otra URL pública, establece también `CORS_ORIGINS` y, cuando se use, `FRONTEND_URL`. Si un puerto está ocupado, cambia su variable correspondiente o detén el proceso que lo ocupa; no cambies el puerto interno de PostgreSQL (`5432`) ni la URL de API sin actualizar el cliente.

### Logs, salud, reinicio y datos

```sh
docker compose ps
docker compose logs -f backend
docker compose logs -f db
docker compose logs -f frontend
```

`healthy` en PostgreSQL solo confirma que acepta conexiones. `healthy` en backend confirma además conexión a PostgreSQL, presencia de las migraciones obligatorias y, si se habilitó almacenamiento Supabase, disponibilidad de ese almacenamiento. Un servicio con puerto ocupado puede fallar antes de quedar saludable; revisa `docker compose ps` y sus logs.

Si PostgreSQL se reinicia después del backend, SQLAlchemy comprueba las conexiones reutilizadas y descarta una conexión obsoleta al siguiente uso. Las solicitudes que coincidan con la interrupción pueden fallar; cuando PostgreSQL vuelva, las siguientes conexiones pueden recuperarse sin reiniciar manualmente toda la aplicación. El healthcheck reportará el estado no saludable mientras la base o el esquema requerido no estén disponibles. Compose no fuerza reinicios del backend ante cualquier fallo; si el proceso termina, revisa primero sus logs y reinícialo cuando la dependencia esté saludable con `docker compose restart backend`.

Para detener y volver a iniciar sin borrar datos:

```sh
docker compose stop
docker compose start
```

`docker compose down` elimina contenedores y red, pero conserva el volumen nombrado de PostgreSQL y los archivos de adjuntos del anfitrión. Después pueden reconstruirse con `docker compose up --build -d`. **No uses `docker compose down -v` como forma de detener o reiniciar:** elimina el volumen de PostgreSQL.

Los datos de PostgreSQL viven en el volumen `pgdata`; los adjuntos locales, si se habilitan, se guardan bajo `backend/uploads/`, montado en el backend y excluido de Git. No se incluyen datos privados en la imagen ni en el repositorio. Un computador nuevo crea su propia base local; clonar Git no copia los datos de otra máquina.

### Versiones y reproducibilidad

Los Dockerfiles usan Node `24-alpine` y Python `3.14.8-slim`; Compose usa PostgreSQL `17.11` y Mailpit `v1.31.4`. `frontend/pnpm-lock.yaml` y `backend/requirements.txt` fijan las versiones de dependencias. Los tags versionados reducen cambios inesperados, pero no fijan el digest inmutable de cada imagen; además, las instalaciones iniciales descargan imágenes y paquetes de sus registros. El stack y el build de producción del frontend se validaron en Windows con Docker Desktop y contenedores Linux. No se han probado todas las arquitecturas de CPU ni todos los sistemas anfitriones.

### Primera instalación y actualización del esquema

- **Fuente vigente del esquema:** las revisiones ordenadas de Alembic en `backend/alembic/versions/`. `database/init.sql` y `backend/migrations/*.sql` se conservan como historia y referencia; Compose ya no los ejecuta.
- **Base local nueva:** ejecuta `docker compose up --build`. En un volumen vacío, PostgreSQL crea `acadex`; el servicio `migrate` aplica Alembic automáticamente antes de FastAPI. No se requiere el perfil `schema` ni SQL manual.
- **Base existente sin historial Alembic:** el servicio `migrate` se detiene antes de DDL si encuentra tablas Acadex sin `public.alembic_version`. La base local persistente de Docker `acadex_dev` ya fue respaldada y comparada antes de registrar la revisión `20261016_03`, y luego se actualizó hasta `20261016_06`. No ejecutes `stamp`, `upgrade` ni SQL sobre otra base existente sin identificarla, revisar su esquema e historial y preparar un respaldo.
- **Estado local verificado:** `acadex_dev`, únicamente en el entorno Docker local, está en la revisión `20261016_06`. Se comprobaron 18 tablas funcionales, las nueve categorías originales y que `alembic check` no encontrara operaciones pendientes. Esto no confirma el estado de PostgreSQL instalado en Windows ni el de las bases auxiliares.
- **Reinicio o recreación de contenedores:** `pgdata` conserva sus datos. En el arranque normal, Compose ejecuta `migrate` antes de FastAPI; Alembic omite revisiones ya registradas. FastAPI no ejecuta Alembic por su cuenta.
- **Actualización del esquema:** Compose ejecuta `migrate` durante `docker compose up --build`. Antes de iniciar una base existente, confirma su identidad, nombre, revisión e historial y prepara un respaldo. La base Docker `acadex_dev` de este equipo requiere la anulación local indicada arriba. Supabase es producción y no se ha reconciliado ni migrado con Alembic; revisa por separado su esquema, historial y RLS antes de cualquier cambio.

Al actualizar el código sin borrar datos:

```sh
git status
git pull
docker compose up --build -d
docker compose ps
```

Revisa primero las nuevas revisiones de `backend/alembic/versions/` y sigue el procedimiento de la guía de base de datos. Conserva tus cambios locales y crea un respaldo antes de modificar una base con información que necesites.

### Pruebas

Las pruebas unitarias de la guarda PostgreSQL no requieren una base de datos y pueden ejecutarse en el contenedor backend:

```sh
docker compose exec -T backend python -m pytest tests/test_postgres_safety.py -q
```

Las suites PostgreSQL y API usan un Compose separado con una red interna, una base `acadex_test` efímera en `tmpfs` y sin puerto publicado. El servicio `migrate` ejecuta Alembic antes de cada suite; no se conecta al volumen de la aplicación. Ejecuta una suite por proceso:

```sh
docker compose -f docker-compose.test.yml run --build --rm integration
docker compose -f docker-compose.test.yml run --build --rm api-tests
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

Esta ruta es para desarrollo de frontend/backend directamente en el anfitrión. Requiere Node.js/npm, Python y una instancia PostgreSQL ya instalada y configurada; no es necesaria para el flujo recomendado con Compose.

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
   pnpm install --frozen-lockfile
   pnpm dev
   ```

Para preparar el esquema manualmente, usa una base desechable o sigue los pasos de migración de [database/README.md](database/README.md). No ejecutes SQL de inicialización sobre una base existente.

## Arquitectura y módulos

- Frontend: React, TypeScript, Vite, Redux Toolkit y React Router.
- Backend: FastAPI, SQLAlchemy, Pydantic y autenticación JWT.
- Datos: PostgreSQL.
- Servicios locales: Mailpit para correo de prueba; análisis documental con Gemini opcional.
- Módulos: usuarios y perfiles; tareas, grupos e integrantes; cronómetro, notificaciones y estadísticas; adjuntos y análisis documental.

Consulta [STRUCTURE.md](STRUCTURE.md) para el mapa del repositorio y [database/README.md](database/README.md) para el ciclo de vida del esquema.

## Seguridad del repositorio

No subas archivos `.env` reales, claves, tokens, contraseñas, datos PostgreSQL, `backend/uploads/`, dependencias instaladas ni artefactos compilados. Las plantillas `.env.example` pueden versionarse; verifica que solo contengan valores ilustrativos y nunca credenciales personales.
