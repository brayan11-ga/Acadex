# Desarrollo local de ACADEX

Esta es la guía oficial para levantar la rama `docker` en desarrollo. El flujo usa PostgreSQL en Docker Compose y ejecuta Vite desde el computador del integrante. No se requiere instalar PostgreSQL ni Python para el uso normal.

## Fuente del esquema

- `database/init.sql` es el esquema base versionado para una base nueva e incluye las categorías iniciales.
- Las actualizaciones incrementales oficiales están en `backend/migrations/`. Compose las aplica después del esquema base únicamente al inicializar un volumen PostgreSQL vacío.
- `database/scripts/acadex.sql` es un punto de entrada de compatibilidad para `psql`; incluye el esquema base y las migraciones vigentes. No es una segunda copia del DDL.
- `database/seed.sql` conserva datos de una estructura antigua y no forma parte de la inicialización actual. No lo ejecutes.
- `backend/app/db/init.sql` está vacío y no participa en el arranque.

La secuencia limpia es `database/init.sql`, `20261011_add_archivo_uploader.sql`, `20261011_add_registration_consents.sql`, `20261012_add_gemini_usage_limits.sql`, `20261012_add_gemini_quota_lockout.sql` y `20261012_add_security_guards.sql`, en ese orden. Las migraciones se mantienen aunque el bootstrap las use, porque también son necesarias para bases existentes.

## Requisitos

- Windows: Docker Desktop con Compose v2 y Node.js 20.19 o superior, o 22.12 o superior.
- macOS: Docker Desktop con Compose v2 y Node.js 20.19 o superior, o 22.12 o superior.
- Linux: Docker Engine con el plugin Docker Compose v2 y Node.js 20.19 o superior, o 22.12 o superior.
- Git. El uso de Vite requiere `pnpm`, incluido con Node.js.

La versión mínima de Node corresponde al requisito de Vite 8 (`^20.19.0 || >=22.12.0`). Compose fija PostgreSQL en `17.11` y el backend usa `python:3.14-slim`; no es necesario instalar esas versiones localmente.

## Instalación en una máquina nueva

Clona la rama de desarrollo y entra en el repositorio:

```powershell
git clone --branch docker --single-branch https://github.com/brayan11-ga/Acadex.git
Set-Location Acadex
```

En PowerShell, crea los archivos locales de configuración solo si aún no existen:

```powershell
if (-not (Test-Path .\backend\.env)) { Copy-Item .\backend\.env.example .\backend\.env }
if (-not (Test-Path .\frontend\.env.local)) { Copy-Item .\frontend\.env.example .\frontend\.env.local }
```

En macOS/Linux:

```sh
test -f backend/.env || cp backend/.env.example backend/.env
test -f frontend/.env.local || cp frontend/.env.example frontend/.env.local
```

Los valores de ejemplo son solo para desarrollo local. `backend/.env` es ignorado por Git y contiene los valores que Compose entrega al backend y usa para crear una base nueva. No compartas el archivo real. `GEMINI_API_KEY` es opcional para el registro y las funciones que no analizan documentos.

Construye e inicia PostgreSQL, Mailpit y FastAPI:

```powershell
docker compose --env-file backend/.env up --build -d
docker compose --env-file backend/.env ps
docker compose --env-file backend/.env logs -f db backend
```

En macOS/Linux usa los mismos comandos. Compose espera que PostgreSQL acepte conexiones antes de iniciar FastAPI. El estado `healthy` del backend indica que la API responde; no reemplaza la verificación de esquema que sigue.

Comprueba que la base fue inicializada con las cinco actualizaciones:

```powershell
docker compose --env-file backend/.env exec -T db sh -c 'psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB" -f /database/verify_schema.sql'
```

Las doce columnas de verificación deben ser `t`. API: <http://localhost:8000/>. UI de correo de prueba: <http://localhost:8025/>.

Levanta el frontend en otra terminal:

```powershell
Set-Location frontend
pnpm install --frozen-lockfile
pnpm dev --host 0.0.0.0
```

Abre <http://localhost:5173/>. `frontend/.env.local` debe mantener `VITE_API_URL=http://localhost:8000`.

## Verificación funcional manual

1. Registra una cuenta sintética desde la UI marcando las dos confirmaciones obligatorias.
2. Inicia sesión y crea una tarea de prueba.
3. Con la configuración predeterminada, verifica que los adjuntos no se ofrecen ni se guardan. Si se configuró la clave de Gemini, selecciona un PDF sintético para proponer una tarea y confirma que el archivo no queda guardado como adjunto.
4. Los correos de recuperación de prueba se consultan en Mailpit; no se envían a destinatarios externos.

Las pruebas automatizadas se describen abajo; el flujo manual no sustituye la revisión automatizada.

## Actualizar una base existente sin perder datos

`docker-entrypoint-initdb.d` solo se ejecuta cuando PostgreSQL crea un directorio de datos vacío. Un `git pull` o `docker compose up` no aplica migraciones a una base que ya existe. Antes de actualizar una base local con datos, crea y verifica un respaldo según el procedimiento del equipo. Después:

```powershell
docker compose --env-file backend/.env up -d db
docker compose --env-file backend/.env exec -T db sh -c 'psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB" -f /migrations/20261011_add_archivo_uploader.sql'
docker compose --env-file backend/.env exec -T db sh -c 'psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB" -f /migrations/20261011_add_registration_consents.sql'
docker compose --env-file backend/.env exec -T db sh -c 'psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB" -f /migrations/20261012_add_gemini_usage_limits.sql'
docker compose --env-file backend/.env exec -T db sh -c 'psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB" -f /migrations/20261012_add_gemini_quota_lockout.sql'
docker compose --env-file backend/.env exec -T db sh -c 'psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB" -f /migrations/20261012_add_security_guards.sql'
docker compose --env-file backend/.env up --build -d backend
```

La misma secuencia sirve en macOS/Linux. Las migraciones son aditivas e idempotentes para un esquema compatible: añaden la columna de autor, crean la tabla de consentimientos y sus restricciones, los contadores y bloqueo de cuota de Gemini, y los límites compartidos, vencimientos de bloqueo e índice único del cronómetro. La migración de seguridad se detiene sin borrar datos si encuentra más de un cronómetro activo para la misma tarea; revisa esas sesiones antes de volver a aplicarla. Si una instancia tiene objetos parciales con definiciones diferentes, detente y revisa el esquema antes de ejecutar; la idempotencia no repara definiciones incompatibles. No ejecutes `database/init.sql` sobre una base existente.

Verifica los objetos después de aplicar las migraciones con la consulta de la sección anterior. Las filas históricas de `archivos` quedan con `id_usuario_subida = NULL`; no se inventa autoría ni consentimiento para cuentas preexistentes.

No cambies `DB_USER`, `DB_PASSWORD` o `DB_NAME` en una instalación ya creada esperando que PostgreSQL modifique el rol o la base. Las variables de inicialización del contenedor solo se aplican a una base nueva; un cambio en una base existente requiere una operación explícita, respaldada y coordinada.

## Persistencia y ciclo de vida

- `pgdata` conserva la base de datos.
- `./backend/uploads` conserva adjuntos y está ignorado por Git; Compose lo monta en `/app/uploads`.
- El código `backend/app` se monta para recarga automática.
- `docker compose ... stop`, `start`, `restart` y `down` conservan los volúmenes y archivos.
- **No ejecutes `docker compose down -v`** para reiniciar: elimina el volumen `pgdata` y los datos persistidos.
- Cambiar la versión mayor de PostgreSQL o mover datos entre computadores requiere un respaldo y un procedimiento de actualización de PostgreSQL; no basta con cambiar el tag de la imagen.

Puertos locales: PostgreSQL `5433` (ajustable con `ACADEX_DB_PORT`), API `8000`, Mailpit web `8025`, Mailpit SMTP `1025` y Vite `5173`. Los puertos publicados por Compose quedan ligados a `127.0.0.1`.

## Pruebas

Desde la raíz del repositorio, con el servicio backend iniciado:

```powershell
docker compose --env-file backend/.env exec -T backend python -m unittest discover -s tests -p "test_*.py" -v
```

Desde `frontend/`:

```powershell
pnpm install --frozen-lockfile
pnpm test --run
pnpm build
```

Las pruebas PostgreSQL optativas crean un esquema aleatorio y lo eliminan al terminar; se bloquean si el nombre de la base no incluye `test`. Para no usar el volumen de desarrollo, crea una instancia Compose separada. En PowerShell, desde la raíz:

```powershell
$env:DB_NAME = "acadex_test"
$env:ACADEX_DB_PORT = "55433"
docker compose --env-file backend/.env -p acadex-test up -d db
docker compose --env-file backend/.env -p acadex-test build backend
docker compose --env-file backend/.env -p acadex-test run --no-deps --rm -e DB_NAME=acadex_test -e ACADEX_RUN_POSTGRES_TESTS=1 backend python -m unittest discover -s tests -p "test_postgres_integration.py" -v
docker compose --env-file backend/.env -p acadex-test stop db
```

Ese proyecto usa un volumen PostgreSQL distinto llamado `acadex-test_pgdata`; `stop` lo conserva. Si las variables `$env:DB_NAME` o `$env:ACADEX_DB_PORT` ya tenían valores importantes, restáuralos al terminar. Para borrar el entorno de pruebas se requiere una acción deliberada y confirmar el nombre del proyecto/volumen; no reutilices para ello el proyecto normal `acadex`.

## Después de `git pull`

1. Revisa `git status` y conserva tus cambios locales.
2. Reconstruye servicios con `docker compose --env-file backend/.env up --build -d`.
3. Si es una base existente, aplica explícitamente las migraciones nuevas en orden siguiendo la sección de actualización; verifica cada resultado.
4. Ejecuta los tests backend y frontend anteriores.
5. Inicia Vite y comprueba una operación de registro y adjuntos.

### Lista de comprobación del equipo

- [ ] Rama `docker` actualizada y cambios locales preservados.
- [ ] Archivos `.env` locales creados sin sobrescribir los que ya existían.
- [ ] PostgreSQL y backend reportan estado saludable.
- [ ] `consentimientos_usuario` existe y tiene sus restricciones.
- [ ] `archivos.id_usuario_subida` existe y permite `NULL`.
- [ ] Frontend carga y usa la API local.
- [ ] Registro guarda nombre y dos evidencias; las casillas siguen siendo obligatorias.
- [ ] Un usuario puede subir, listar, descargar y borrar los adjuntos permitidos.
- [ ] Backend y frontend pasan las pruebas disponibles.

## Diagnóstico rápido

- `DB_USER`, `DB_PASSWORD` o `DB_NAME` faltan: verifica que `backend/.env` exista y pásalo a Compose con `--env-file backend/.env`.
- El backend no conecta: espera a `db` en estado `healthy`; dentro de Compose el host es `db` y el puerto es `5432`, aunque el puerto publicado en el host sea `5433`.
- Falta tabla/columna en una base existente: aplica las dos migraciones del bloque de actualización; Compose no las reaplica a volúmenes inicializados.
- No se ejecutó el SQL inicial: revisa el estado de `pgdata`. Los scripts de inicialización solo corren sobre un volumen vacío. No borres el volumen como método de reparación.
- Vite falla por `VITE_API_URL`: crea `frontend/.env.local` desde `.env.example` y reinicia Vite.
- Adjuntos no aparecen después de recrear contenedores: confirma que Compose monta `./backend/uploads` y no muevas/borres esa carpeta.
