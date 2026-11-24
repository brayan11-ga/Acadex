# Calidad y pruebas

Esta guía reúne los comandos de [package.json](../frontend/package.json), [CI](../.github/workflows/ci.yml) y los archivos Compose. Indica qué se ejecuta, no certifica resultados de una máquina concreta.

## 1. Pruebas con instalación manual

Prepara las dependencias y variables con [Inicio manual](inicio-manual.md). Para frontend, desde `frontend/`:

```sh
corepack pnpm lint
corepack pnpm build
corepack pnpm test --run
```

Para backend, desde `backend/`, con `.venv` activo y configuración local:

```sh
python -m pytest test tests -q
```

No habilites `ACADEX_RUN_POSTGRES_TESTS` en esta terminal. Sin ese opt-in, las pruebas que requieren PostgreSQL quedan omitidas. Esto coincide con el trabajo de CI «Backend sin PostgreSQL»; no demuestra que las migraciones o consultas reales funcionen.

## 2. Frontend dentro de Docker

Con el stack de desarrollo iniciado, desde la raíz:

```sh
docker compose exec -T frontend pnpm lint
docker compose exec -T frontend pnpm build
docker compose exec -T frontend pnpm test --run
```

## 3. Backend y PostgreSQL en el entorno aislado

Desde la raíz, ejecuta esta secuencia **un comando a la vez**:

```sh
# Suite backend/tests sin habilitar sus pruebas PostgreSQL.
docker compose -f docker-compose.test.yml run --build --rm -e ACADEX_RUN_POSTGRES_TESTS=0 api-tests python -m pytest tests -q

# Suite backend/test de API con PostgreSQL.
docker compose -f docker-compose.test.yml run --build --rm api-tests

# Integración PostgreSQL en un proceso separado.
docker compose -f docker-compose.test.yml run --build --rm integration

# Retira contenedores y red de pruebas al terminar, incluso si una suite falló.
docker compose -f docker-compose.test.yml down
```

Este Compose crea `acadex_test`, aplica Alembic y usa almacenamiento `tmpfs`, una red interna y un marcador exclusivo de los runners. No publica PostgreSQL ni comparte `pgdata` con desarrollo. Incluso el primer comando puede iniciar la base y `migrate` por las dependencias del servicio: no es una comprobación sin operaciones de base de datos.

No mezcles `backend/test/` e integración PostgreSQL en un mismo proceso ni lances esas suites en paralelo sobre este proyecto de pruebas. La colección de pruebas API puede importar la aplicación y su sesión global antes de preparar el destino de integración.

Para comprobar que un segundo `upgrade head` no aplica cambios, antes de `down` puedes ejecutar:

```sh
docker compose -f docker-compose.test.yml run --rm migrate
```

No uses estas pruebas contra Supabase, el Compose habitual o una base compartida. La [guía de datos](../database/README.md#guardas-del-entorno-de-pruebas) explica las barreras y las variables de personalización.

La prueba unitaria de las guardas no necesita PostgreSQL. Con el backend de desarrollo iniciado, desde la raíz:

```sh
docker compose exec -T backend python -m pytest tests/test_postgres_safety.py -q
```

## 4. Comprobar el arranque desde un clon limpio

Esta comprobación crea una base de desarrollo nueva y sí aplica migraciones.
Úsala cuando necesites verificar las instrucciones de instalación:

1. Clona la rama que quieres comprobar en otra carpeta. No copies archivos de
   entorno ni datos del directorio donde trabajas.
2. Sigue [Inicio con Docker](inicio-docker.md) para preparar las plantillas.
   Si mantienes otro entorno activo, elige puertos libres con las variables
   `ACADEX_*_PORT` y ajusta también las URLs indicadas en esa guía.
3. Usa un nombre de proyecto Compose nuevo. En PowerShell, desde la raíz del
   clon, puedes generar uno así:

   ```powershell
   $acadexPrueba = "acadex-prueba-$([guid]::NewGuid().ToString('N').Substring(0,8))"
   docker compose -p $acadexPrueba up --build -d
   docker compose -p $acadexPrueba ps -a
   docker compose -p $acadexPrueba logs migrate
   ```

4. Comprueba `migrate` con código de salida 0, salud de la API y acceso al
   frontend. Registra una cuenta sintética, inicia sesión y crea una tarea.
   Detén y reanuda el mismo proyecto con `stop` y `start`; comprueba que la
   tarea persiste.
5. Al terminar, ejecuta `docker compose -p $acadexPrueba down`. Conserva el
   volumen. Si decides eliminar también los datos desechables, verifica el
   nombre del proyecto antes de añadir `--volumes --remove-orphans`.

Usa siempre el mismo `-p $acadexPrueba` en los comandos de ese ensayo, incluidos
logs, comprobaciones y limpieza. El nombre separa contenedores y volumen del
entorno habitual; los puertos deben separarse también.

## Qué ejecuta CI

El workflow se activa en PR dirigidos a `develop` o `main` y define tres trabajos:

1. **frontend:** Node.js 22, pnpm 12.11.2, instalación con lockfile, lint, build y Vitest.
2. **backend:** Python 3.14, instalación de `requirements.txt` y `python -m pytest test tests -q`, sin habilitar PostgreSQL.
3. **backend-postgres:** Python 3.14 y PostgreSQL 17; aplica Alembic y ejecuta API e integración en procesos separados.

Que un check exista no prueba que GitHub lo exija para fusionar. Las reglas comprobadas y pendientes están en [CONTRIBUTING](../CONTRIBUTING.md#8-integra-y-comprueba-el-cierre).

## Qué comprobar según el cambio

| Cambio | Comprobaciones |
| --- | --- |
| Frontend | Lint, build, pruebas afectadas y estados visuales modificados |
| Backend | Pruebas del comportamiento modificado y sus errores |
| Migración o consulta PostgreSQL | Revisión de la migración y suites aisladas |
| Docker o arranque | `docker compose config --quiet` y arranque local cuando esté autorizado |
| Documentación | Enlaces relativos, comandos contra configuración y diff; no requiere migrar una base |

En el PR, anota directorio, comando y resultado real. Si una comprobación falta, explica por qué y qué queda pendiente. No cuentes una prueba omitida como una prueba aprobada.
