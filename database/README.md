# PostgreSQL: inicialización, actualizaciones y pruebas

El flujo recomendado de instalación está en el [README raíz](../README.md). Esta guía explica qué administra Compose en PostgreSQL y cómo probar cambios sin tocar la base normal del desarrollador. El stack requiere Docker Compose v2.24.0 o superior, necesario para que `env_file.required: false` admita la ausencia de `backend/.env`.

Para ejecutar el frontend manualmente se requiere Node.js 20.19 o superior, o 22.12 o superior, y pnpm 12.11.2; el archivo `frontend/package.json` declara el gestor de paquetes.

## Comandos del frontend con pnpm

Ejecuta estos comandos desde `frontend/`. Corepack selecciona la versión de pnpm declarada en `package.json`:

```sh
corepack enable
pnpm install --frozen-lockfile
pnpm dev
pnpm build
pnpm test --run
pnpm lint
```

`dev` inicia el servidor local; `build` genera el sitio compilado; `test --run` ejecuta todas las pruebas una vez; `lint` analiza el código sin modificarlo.

## Fuente vigente y archivos históricos

- `backend/alembic.ini`, `backend/alembic/env.py` y `backend/alembic/versions/`: configuración, conexión y secuencia vigente de migraciones. La revisión inicial contiene un snapshot autocontenido del esquema base para que el despliegue del backend no dependa de montar `database/`.
- **Histórico:** `database/init.sql` y `backend/migrations/*.sql` son la ruta SQL anterior, conservada para comparación y transición. `database/scripts/acadex.sql` todavía incluye `init.sql` como envoltorio antiguo; el arranque actual con Compose y Alembic no ejecuta esos archivos. No los uses como procedimiento nuevo.
- `database/supabase_new_project.sql` y `database/supabase_resume_migrations.sql`: antiguos snapshots manuales de Supabase; además del esquema activan políticas de seguridad a nivel de fila (RLS). Se conservan como referencia, pero no son la ruta vigente ni deben ejecutarse durante esta transición.
- `database/verify_schema.sql`: consulta de solo lectura para comprobar objetos del esquema.
- `database/scripts/acadex.sql`: antiguo punto de entrada compatible con `psql`; reúne el esquema SQL histórico y no es la ruta vigente.
- `database/seed.sql` fue eliminado porque pertenecía a una estructura antigua y contenía una contraseña fija. No cargues administradores desde SQL.
- `backend/app/db/init.sql`: archivo vacío que no participa en el arranque.

La secuencia vigente se aplica con `alembic upgrade head`, en el orden de las seis revisiones versionadas bajo `backend/alembic/versions/`. La base PostgreSQL desechable de pruebas llega a `head` antes de ejecutar las pruebas de integración.

Las bases que ya tienen tablas pero todavía no tienen `public.alembic_version` no se adoptan automáticamente. `env.py` detecta ese caso y aborta antes de ejecutar DDL. La base local persistente de Docker `acadex_dev` sí fue respaldada y comparada antes de registrar `20261016_03`; después se aplicaron las revisiones hasta `20261016_06`. Se verificaron 18 tablas funcionales, las nueve categorías originales y que `alembic check` no encontrara operaciones pendientes. Este resultado corresponde solo a Docker local; no confirma el PostgreSQL instalado en Windows ni las bases auxiliares. Supabase no se ha reconciliado ni migrado con Alembic. Antes de cualquier cambio en una base existente, confirma su identidad, compara esquema e historial y prepara un respaldo; en Supabase también se requiere una revisión separada de las políticas RLS. No ejecutes `stamp`, `upgrade` ni SQL a ciegas.

Los SQL anteriores no se borraron. Permanecen como evidencia de la conversión y no deben recibir cambios nuevos; futuras modificaciones del esquema deben ser una revisión Alembic nueva.

## Primera instalación, reinicio y actualización

- **Base local nueva:** ejecuta `docker compose up --build`. En un volumen vacío, PostgreSQL crea `acadex`; después de que PostgreSQL esté saludable, `migrate` aplica Alembic antes de que FastAPI inicie. No necesitas ejecutar SQL ni activar un perfil `schema`.
- **Base local persistente ya existente:** `acadex_dev` fue comparada y respaldada antes de registrarla en `20261016_03`; actualmente está en `20261016_06`, con 18 tablas funcionales y nueve categorías verificadas. `alembic check` no encontró operaciones pendientes. Este estado aplica solo a esa base de Docker. Para cualquier otra base existente, identifica el servidor y la base, revisa esquema e historial y prepara un respaldo antes de considerar una actualización.
- **Nombre de la base existente:** cambiar `DB_NAME` no renombra una base guardada en un volumen inicializado. Para seguir usando `acadex_dev` en este equipo, establece `DB_NAME=acadex_dev` en un `.env` local de la raíz antes de iniciar Compose. `.gitignore` excluye ese archivo. `backend/.env` no sustituye `DB_NAME` declarado en `environment` de Compose. No hace falta crear el archivo para una instalación nueva.
- **Reinicio:** `docker compose stop` seguido de `docker compose start`, o `docker compose down` y luego `docker compose up -d`, conserva el volumen. Compose inicia `migrate` antes de FastAPI; Alembic no repite revisiones ya registradas. FastAPI no ejecuta DDL por su cuenta.
- **Actualización del esquema:** `docker compose up --build` ejecuta `migrate` automáticamente. En una base existente, confirma primero el destino, su nombre, revisión e historial; compara el esquema y prepara un respaldo verificado. Nunca ejecutes el snapshot base en una base existente. Supabase no se ha reconciliado con Alembic; revisa su esquema, historial y políticas RLS por separado antes de decidir cualquier acción. No uses `stamp`, `upgrade` ni SQL a ciegas.

Para pgAdmin instalado en el computador, una instalación nueva usa host `localhost`, puerto `5433` y base `acadex`. Usa el usuario y la contraseña locales configurados para Compose. Este acceso es local; no uses credenciales de Supabase.

## Crear o promover un administrador

No hay una cuenta admin ni una contraseña predeterminadas. Después de iniciar el stack local, ejecuta el comando y escribe el correo. Si la cuenta no existe, escribe y confirma la contraseña en los avisos ocultos. Si ya existe, el comando solo la promueve a administradora y conserva su contraseña:

```sh
docker compose up --build -d
docker compose exec -it backend python -m scripts.crear_admin
```

El comando crea el usuario si el correo no existe o promueve el usuario existente. La contraseña de una cuenta nueva se guarda con bcrypt; también se crea el perfil si hace falta. Para automatización, el proceso debe recibir `ACADEX_ADMIN_EMAIL`, `ACADEX_ADMIN_PASSWORD` y `ACADEX_ADMIN_PASSWORD_CONFIRM`. Las dos variables de contraseña deben coincidir. No imprimas la contraseña en logs ni la guardes en el repositorio.

Para cambiar la contraseña de una cuenta existente, solicita el cambio de forma explícita; el comando pedirá confirmar la contraseña oculta:

```sh
docker compose exec -it backend python -m scripts.crear_admin --reset-password
```

En ejecución automatizada, `--reset-password` también es obligatorio y el proceso debe recibir las tres variables indicadas arriba. Sin `--reset-password`, el script ignora cualquier contraseña definida para una cuenta que ya existe y no la imprime ni la registra.

No uses `docker compose down -v` como rutina de detención o actualización: elimina `pgdata`. Tampoco cambies `DB_USER`, `DB_PASSWORD` o `DB_NAME` esperando que PostgreSQL modifique un volumen existente; las variables `POSTGRES_*` de la imagen solo inicializan una base nueva.

Después de arrancar, puedes realizar una verificación de solo lectura:

```sh
docker compose exec -T db sh -c 'psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB" -f /database/verify_schema.sql'
```

Las columnas de resultado deben confirmar los objetos que comprueba el script. Si faltan en una base existente, compara su `alembic_version` con las revisiones del repositorio; no borres el volumen para repetir la instalación.

Las revisiones actuales agregan autoría de archivos, evidencias de consentimiento, contadores y bloqueos de Gemini, límites de solicitudes y unicidad para cronómetros activos. La última revisión se detiene si encuentra más de un cronómetro activo para una tarea. Resuelve esa inconsistencia con el equipo y un respaldo antes de reintentarla. Las filas históricas de archivos quedan sin autor (`NULL`); no se inventa autoría ni consentimiento para registros previos.

## Pruebas PostgreSQL y API

Las suites de integración se ejecutan mediante `docker-compose.test.yml`, en procesos separados. El servicio `migrate` inicializa `acadex_test` mediante Alembic. El runner crea una red interna exclusiva, no publica PostgreSQL, utiliza un directorio `tmpfs` para los datos y monta el marcador operativo solo en los contenedores de prueba. No se comparte `pgdata` con la aplicación.

Desde la raíz del repositorio:

```sh
# Suite backend/tests, sin activar integración PostgreSQL.
docker compose -f docker-compose.test.yml run --build --rm -e ACADEX_RUN_POSTGRES_TESTS=0 api-tests python -m pytest tests -q

# Suite backend/test de API.
docker compose -f docker-compose.test.yml run --build --rm api-tests

# Integración PostgreSQL, en un proceso separado.
docker compose -f docker-compose.test.yml run --build --rm integration

# Limpia contenedores y red de pruebas al terminar.
docker compose -f docker-compose.test.yml down
```

Ejecuta cada comando `run` por separado. La integración PostgreSQL no debe descubrirse en el mismo proceso que `backend/test/`: algunas pruebas API importan `app.main` y la sesión global durante la colección, antes de que la guarda de integración pueda configurarse. Para verificar que un segundo `upgrade head` es una operación sin cambios, repite `docker compose -f docker-compose.test.yml run --rm migrate` mientras siga activo el proyecto de prueba. Su `down` elimina solo los recursos desechables; este Compose no declara volúmenes persistentes.

El Compose de pruebas suministra el opt-in y las variables `ACADEX_TEST_*`, exige el destino fijo `acadex_test` en `db:5432`, y compara el nombre de proyecto en el contenedor. Se puede personalizar el proyecto con `ACADEX_TEST_COMPOSE_PROJECT`; debe empezar por `acadex-test-` y terminar con 8 a 32 caracteres hexadecimales. `ACADEX_TEST_DB_USER` y `ACADEX_TEST_DB_PASSWORD` cambian las credenciales locales de la instancia efímera. Sus valores predeterminados solo son para pruebas locales, no para despliegues.

La guarda rechaza configuración incompleta, destinos alternativos de libpq, variables `DB_*` contradictorias, ejecución fuera de un contenedor y ausencia del marcador `/run/secrets/acadex-test-runner` antes de crear o eliminar esquemas. Después de conectar, vuelve a comprobar que PostgreSQL informa `acadex_test`. La integración crea y elimina únicamente esquemas aleatorios con prefijo `acadex_test_`; las pruebas API usan el mismo tipo de esquema con rollback por prueba. No habilites `ACADEX_RUN_POSTGRES_TESTS` en el Compose normal, contra el volumen ACADEX ni contra Supabase.

La suite unitaria de `backend/tests/test_postgres_safety.py` no requiere PostgreSQL. Puede ejecutarse en el contenedor backend normal con `docker compose exec -T backend python -m pytest tests/test_postgres_safety.py -q`.
