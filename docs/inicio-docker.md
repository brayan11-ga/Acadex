# Inicio con Docker Compose

Usa esta guía para ejecutar todo el proyecto en contenedores. No necesitas instalar Python, Node.js ni PostgreSQL en el equipo. Necesitas Git, Docker en ejecución y Compose 2.24.0 o posterior; esa versión permite el `env_file` opcional que usa el repositorio.

Si todavía no tienes el código, sigue el [paso de clonación](../README.md#1-clona-el-repositorio). Todos los comandos de esta guía se ejecutan desde la raíz de `Acadex/`.

## 1. Prepara el entorno local

Comprueba Compose:

```sh
docker compose version
```

Copia las plantillas únicamente si los destinos no existen.

En PowerShell:

```powershell
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
if (-not (Test-Path backend/.env)) { Copy-Item backend/.env.example backend/.env }
```

En Bash:

```sh
test -f .env || cp .env.example .env
test -f backend/.env || cp backend/.env.example backend/.env
```

Revisa ambos archivos antes de arrancar:

1. En `.env`, conserva una base y credenciales exclusivas de desarrollo. La plantilla usa `DB_NAME=acadex_dev`. Sus credenciales son ejemplos locales, no credenciales de Supabase.
2. En `backend/.env`, conserva `APP_ENV=development`, `ATTACHMENTS_ENABLED=false` y `ATTACHMENTS_STORAGE_BACKEND=local`. Deja vacías las claves de proveedores si no vas a probar integraciones.
3. Para correo local, la plantilla habilita recuperación de contraseña y desactiva STARTTLS. Compose dirige SMTP a Mailpit. No necesita un servidor de correo externo.
4. Comprueba que la terminal no tenga variables de otro entorno que sustituyan las del `.env` raíz. No imprimas ni compartas sus valores privados.

No hace falta crear `frontend/.env.local` para esta ruta: Compose entrega `VITE_API_URL` al contenedor. El [Compose versionado](../docker-compose.yml) fija la conexión interna de API y migraciones en `db:5432`; desde el equipo se accede por `127.0.0.1:5433`.

**Si ya existe un volumen de datos**, confirma su nombre de base y credenciales antes de arrancar. Compose sin `.env` usa `acadex`, mientras que la plantilla usa `acadex_dev`. Cambiar `DB_NAME`, `DB_USER` o `DB_PASSWORD` no modifica un volumen inicializado. Para actualizarlo, revisa antes la [guía de datos](../database/README.md).

## 2. Construye y arranca

```sh
docker compose config --quiet
docker compose up --build -d
```

`config --quiet` valida la configuración sin imprimir los valores resueltos. No inicia servicios. `up` sí crea o actualiza el entorno y aplica las migraciones pendientes.

El orden configurado es:

1. `db` inicia PostgreSQL 17.11 y espera a estar saludable.
2. `migrate` ejecuta `python -m alembic upgrade head`.
3. `backend` arranca cuando la migración termina correctamente; también depende de Mailpit.
4. `frontend` arranca cuando la API está saludable.

En una base nueva no cargues `database/init.sql` ni los SQL de `backend/migrations/`: son históricos. Alembic crea el esquema vigente.

## 3. Comprueba el resultado

```sh
docker compose ps -a
docker compose logs migrate
docker compose exec -T db sh -c 'pg_isready -U "$POSTGRES_USER" -d "$POSTGRES_DB"'
```

Es normal que `migrate` aparezca como `Exited (0)`: es una tarea que termina. `db`, `backend` y `frontend` deben aparecer saludables; Mailpit debe seguir en ejecución. `pg_isready` debe indicar que PostgreSQL acepta conexiones.

Abre <http://localhost:5173/> y <http://localhost:8000/docs>. Comprueba <http://localhost:8000/health/ready>; debe devolver `{"status":"ok"}`. En PowerShell también puedes consultar:

```powershell
Invoke-RestMethod http://localhost:8000/health/ready
```

Para comprobar los objetos cubiertos por el script del repositorio:

```sh
docker compose exec -T db sh -c 'psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB" -f /database/verify_schema.sql'
```

Todas sus columnas deben devolver `t`. El script solo lee el catálogo; no valida todos los objetos posibles. La bandeja de correo de desarrollo está en <http://localhost:8025/>.

## 4. Trabaja, detén y vuelve a iniciar

Consulta los logs mientras trabajas:

```sh
docker compose logs -f backend frontend
```

`Ctrl+C` sale de los logs; los servicios siguen activos. Los cambios en `backend/app/` y `frontend/src/` se montan en los contenedores. Tras cambiar dependencias, migraciones u otros archivos que se copian a las imágenes, vuelve a construir con `docker compose up --build -d`.

Para detener el entorno y reanudarlo sin actualizar imágenes:

```sh
docker compose stop
docker compose start
```

Para retirar contenedores y red conservando la base:

```sh
docker compose down
```

No añadas `-v` ni `--volumes` a esa limpieza habitual: eliminaría el volumen de PostgreSQL. Los adjuntos locales, cuando se habilitan, se guardan en `backend/uploads/` mediante un montaje del equipo.

Las pruebas y su entorno desechable están en [Calidad y pruebas](calidad-y-pruebas.md). La creación de una cuenta administradora está en [Base de datos](../database/README.md#crear-o-promover-un-administrador).

## Si algo falla

| Síntoma | Acción |
| --- | --- |
| Docker no responde | Inicia Docker Desktop o el servicio Docker de tu instalación y vuelve a consultar `docker compose version`. |
| Compose rechaza `required: false` | Actualiza Compose a 2.24.0 o posterior. |
| Puerto ocupado | Detén tu otro entorno local o ajusta `ACADEX_DB_PORT`, `ACADEX_API_PORT`, `ACADEX_FRONTEND_PORT`, `ACADEX_MAILPIT_UI_PORT` o `ACADEX_MAILPIT_SMTP_PORT` en `.env`. Si cambias frontend, ajusta también `CORS_ORIGINS` y `FRONTEND_URL`, que la plantilla fija en 5173. |
| `migrate` termina con error | Lee `docker compose logs migrate`. Revisa destino, credenciales e historial con la [guía de datos](../database/README.md); no borres el volumen para ocultar el error. |
| `backend` no está saludable o devuelve `503` | Lee `docker compose logs backend` y comprueba el resultado de `migrate`. El endpoint distingue base no disponible, migraciones obligatorias faltantes y almacenamiento Supabase no disponible. |
| La base no existe tras copiar `.env` | Comprueba si el volumen se creó antes con `acadex`. Usa su configuración original o prepara otra base deliberadamente; cambiar la plantilla no renombra datos. |
| No aparece un cambio de migración | Reconstruye las imágenes después de revisar la migración y respaldar los datos locales necesarios. `backend/alembic/` no es un montaje vivo. |

Los servicios se publican solo en `127.0.0.1`. Los puertos internos siguen siendo 5432, 8000, 5173, 8025 y 1025 aunque cambies los puertos del equipo.
