# Base de datos de Acadex

PostgreSQL guarda los datos de la aplicación y Alembic mantiene el esquema. **Supabase es la base de producción.** Las guías de [Docker](../docs/inicio-docker.md) e [inicio manual](../docs/inicio-manual.md) preparan una base local; empieza por una de ellas para instalar el proyecto.

Este documento cubre cambios de esquema, administración local y las barreras del entorno de pruebas.

## Fuente vigente y archivos históricos

| Archivo o carpeta | Uso |
| --- | --- |
| [backend/alembic.ini](../backend/alembic.ini), [env.py](../backend/alembic/env.py) y [versions/](../backend/alembic/versions) | Configuración y cadena vigente de migraciones |
| [verify_schema.sql](verify_schema.sql) | Consulta de solo lectura para comprobar objetos concretos del esquema |
| [init.sql](init.sql), [scripts/acadex.sql](scripts/acadex.sql) y [backend/migrations/](../backend/migrations/README.md) | Ruta SQL histórica; no se ejecuta en el arranque actual |
| [supabase_new_project.sql](supabase_new_project.sql) y [supabase_resume_migrations.sql](supabase_resume_migrations.sql) | Snapshots manuales antiguos, con políticas RLS; no son la ruta actual de instalación |
| [backend/app/db/init.sql](../backend/app/db/init.sql) | Archivo vacío, sin participación en el arranque |

La revisión inicial de Alembic contiene un snapshot autocontenido. No necesita montar `database/` para crear el esquema. Las revisiones posteriores añaden autoría de archivos, consentimientos, límites y bloqueos de IA, guardas de seguridad y `tareas.max_archivos`. La cadena actual termina en `20261018_01`; comprueba siempre las revisiones de tu rama.

No añadas cambios nuevos a los SQL históricos. Tampoco hay un `seed.sql` vigente para crear administradores: usa el comando dedicado más abajo.

## Actualizar una base local existente

Antes de aplicar cambios:

1. Identifica servidor, puerto, base y usuario. Comprueba tanto el archivo de entorno como las variables de la terminal. API y Alembic comparten la conexión de `backend/app/db/session.py`.
2. Revisa las migraciones nuevas y consulta la revisión aplicada. Desde `backend/`, con el entorno Python local preparado, usa `python -m alembic current` y `python -m alembic heads`. `current` conecta a la base; comprueba primero el destino.
3. Si necesitas conservar los datos, prepara un respaldo recuperable fuera del repositorio y comprueba su restauración en una base aislada.
4. Aplica las revisiones con el método que ya usas: el arranque Docker ejecuta `migrate`; la guía manual usa `python -m alembic upgrade head` antes de Uvicorn.
5. Comprueba la revisión y `verify_schema.sql` como indica tu guía de inicio. No interpretes `/health/ready` como una auditoría de todo el esquema.

Si hay tablas Acadex sin `public.alembic_version`, Alembic aborta antes de ejecutar DDL. También rechaza un historial vacío cuando ya existen tablas. Sigue la [guía de adopción](../docs/DESPLIEGUE_ALEMBIC.md); `stamp` registra una revisión, pero no crea ni verifica sus objetos.

La revisión de guardas de seguridad aborta si encuentra más de un cronómetro activo por tarea. No elimina filas para resolverlo. Revisa esa inconsistencia con el equipo y un respaldo antes de reintentar. Los archivos históricos conservan autoría `NULL`; no se inventan autores ni consentimientos previos.

No uses `downgrade` como reparación automática. Algunas revisiones bloquean la reversión o comprueban que no se pierdan datos. Consulta las [notas históricas de reversión](../backend/migrations/README.md#downgrade-de-alembic).

## Volumen de desarrollo con Compose

- La plantilla raíz establece `DB_NAME=acadex_dev`; sin esa plantilla, Compose usa `acadex`.
- PostgreSQL solo usa `POSTGRES_USER`, `POSTGRES_PASSWORD` y `POSTGRES_DB` para inicializar un directorio de datos vacío. Cambiar las variables después no renombra bases, usuarios ni contraseñas existentes.
- `backend/.env` no sustituye los `DB_*` declarados en `environment` por Compose. La interpolación de esos valores procede del entorno y del `.env` raíz.
- `docker compose down` conserva `pgdata`; `down -v` lo elimina. No lo uses para resolver errores de conexión o migraciones.

Para una herramienta del equipo como pgAdmin, usa `127.0.0.1:5433`, el nombre efectivo de la base y tus credenciales locales. Los contenedores acceden por `db:5432`.

## Crear o promover un administrador

No hay una cuenta administradora ni contraseña predeterminadas. Con el stack Docker local ya iniciado y comprobado, desde la raíz:

```sh
docker compose exec -it backend python -m scripts.crear_admin
```

Introduce el correo cuando se solicite. Si la cuenta no existe, el script pide y confirma una contraseña mediante avisos ocultos, la guarda con bcrypt y crea el perfil si falta. Si existe, la promueve y conserva su contraseña.

Para cambiar deliberadamente la contraseña de una cuenta local existente:

```sh
docker compose exec -it backend python -m scripts.crear_admin --reset-password
```

Para automatización, el script recibe `ACADEX_ADMIN_EMAIL`, `ACADEX_ADMIN_PASSWORD` y `ACADEX_ADMIN_PASSWORD_CONFIRM`; las contraseñas deben coincidir. En una cuenta existente, solo las usa si también se indica `--reset-password`. No las imprimas ni las guardes en archivos versionados.

## Guardas del entorno de pruebas

La secuencia de ejecución y limpieza está en [Calidad y pruebas](../docs/calidad-y-pruebas.md#3-backend-y-postgresql-en-el-entorno-aislado).

[docker-compose.test.yml](../docker-compose.test.yml) usa una base `acadex_test` en `db:5432`, almacenamiento `tmpfs`, red interna y un marcador montado solo en los runners. No comparte el volumen persistente de desarrollo.

Puedes personalizar:

| Variable | Alcance |
| --- | --- |
| `ACADEX_TEST_COMPOSE_PROJECT` | Nombre del proyecto de pruebas: `acadex-test-` seguido de 8 a 32 caracteres hexadecimales |
| `ACADEX_TEST_DB_USER`, `ACADEX_TEST_DB_PASSWORD` | Credenciales exclusivas de la instancia efímera |

El Compose ya suministra `ACADEX_RUN_POSTGRES_TESTS` y las demás variables `ACADEX_TEST_*`. No copies ese opt-in al entorno normal. La guarda rechaza configuración incompleta, destinos alternativos de libpq, `DB_*` contradictorias, ejecución fuera de un contenedor y ausencia de `/run/secrets/acadex-test-runner`.

Antes de crear o eliminar esquemas, verifica esas condiciones; después de conectar, comprueba que PostgreSQL informa `acadex_test`. Las suites usan esquemas aleatorios con prefijo `acadex_test_`; la API aplica rollback por prueba. Estas barreras no autorizan ejecutar pruebas contra Supabase o una base compartida.

## Producción y evidencia histórica

Este recorrido no verifica ni modifica Supabase. Las notas antiguas de adopción describen copias o ensayos de otro momento; no prueban su estado actual. Antes de una operación de producción, el responsable debe confirmar esquema, historial Alembic, respaldo y políticas RLS. Ese procedimiento está separado en [Adopción de Alembic](../docs/DESPLIEGUE_ALEMBIC.md).
