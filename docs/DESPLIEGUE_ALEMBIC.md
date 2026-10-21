# Alinear una base existente con Alembic

## Alcance

Esta guía explica cómo adoptar con seguridad Alembic en una base que ya tiene
tablas y datos. `stamp` registra una revisión en `alembic_version`; no crea,
altera ni verifica las tablas. Por eso, primero se compara el esquema completo.

No guardes respaldos, archivos `.env`, credenciales ni datos personales dentro
del repositorio. Usa una copia aislada para ensayar el procedimiento.

## Evidencia histórica y estado a verificar

- Al revisar el repositorio, la revisión `head` era `20261018_01`. Confirma siempre el `head` de la rama que vayas a desplegar; este dato cambia al añadir migraciones.
- La copia restaurada tenía las mismas 18 tablas, 110 columnas, 72
  restricciones y 43 índices que una base nueva creada con las migraciones.
- La única diferencia textual en una restricción `CHECK` era el formato de un
  cast entre `VARCHAR` y `TEXT`; la condición resultó equivalente.
- El índice parcial único `uq_sesiones_tarea_activa` coincidía.
- Las 18 tablas de la copia tenían RLS activado y no tenían políticas. El equipo
  decidió conservar RLS como configuración de Supabase, sin una migración para
  las tablas de negocio.
- La copia local se comparó con la referencia y se adoptó en `20261016_06`.
  `current` mostró esa revisión; dos ejecuciones de `upgrade head` no aplicaron
  revisiones nuevas.
- La API local respondió en `/health/ready`; registro, login y creación de una
  tarea sintética pasaron. El usuario local de PostgreSQL era superusuario y
  omite RLS; la prueba no valida políticas ni permisos RLS de Supabase.
- La guardia de `backend/alembic/env.py` solo permite adoptar con
  `ALEMBIC_ALLOW_ADOPT_EXISTING=1`, únicamente para `stamp`, y después de
  verificar las 18 tablas esperadas. `upgrade` sigue bloqueado en una base sin
  historial.

## Procedimiento recomendado

### 1. Crear un respaldo recuperable

Haz un respaldo PostgreSQL antes de cualquier cambio. Guárdalo en una ubicación
segura fuera del repositorio y limita el acceso a quienes administran la base.
Prueba la restauración en una base aislada antes de usar el respaldo para una
recuperación real.

### 2. Preparar una copia aislada

Restaura el respaldo en una base local o de ensayo que no comparta datos ni
volúmenes con producción. Nunca ejecutes la prueba contra Supabase u otro
servicio remoto. Mantén el respaldo montado en solo lectura y no consultes filas
personales; para esta revisión basta con el esquema.

Ejemplo de inspección estructural:

```powershell
pg_dump --schema-only --no-owner --no-privileges --schema=public --dbname=base_aislada --file="$env:TEMP\estructura.sql"
```

Compara también `information_schema`, claves, restricciones `CHECK`, índices,
índices parciales, RLS y políticas, funciones, triggers, vistas y extensiones.
`pg_dump --schema-only` describe objetos; no exporta las filas de las tablas.

### 3. Resolver diferencias antes de marcar la revisión

No uses `stamp` si hay diferencias estructurales sin resolver. Añade una
migración revisada para diferencias que deban pertenecer al esquema. En este
proyecto, RLS de las tablas de negocio se conserva como configuración propia de
Supabase y no se agrega a Alembic.

### 4. Permitir `stamp` de forma controlada

La guardia de `backend/alembic/env.py` bloquea `stamp` si falta la opción
explícita. Solo después de comparar y aprobar el esquema, define
`ALEMBIC_ALLOW_ADOPT_EXISTING=1` en la sesión actual de PowerShell. La variable
no permite `upgrade`, `downgrade` ni otros comandos sobre una base sin historial.

### 5. Registrar y verificar la revisión

Después de aprobar el esquema y habilitar el paso anterior, ejecuta los
comandos desde `backend/` y con la conexión dirigida únicamente a la base
aislada:

```powershell
alembic stamp head
alembic current
alembic upgrade head
```

`current` debe mostrar la revisión `head` aprobada para la rama y el entorno.
Si `upgrade head` encuentra una revisión posterior, revisa primero su SQL y el
plan de datos; no supongas que `stamp` aplicó esas operaciones. Luego valida
`/health/ready` y ejecuta registro, inicio de sesión y creación de tarea con
datos de prueba sintéticos.

### 6. Activar RLS en la tabla de control de Alembic

Después del `stamp` en Supabase, activa RLS en la tabla de historial de Alembic:

```sql
ALTER TABLE public.alembic_version ENABLE ROW LEVEL SECURITY;
```

El comando se ejecutó correctamente en `acadex_copia`; el catálogo confirmó
RLS activo en `public.alembic_version`. Esa prueba local usó un superusuario,
que omite RLS. Ejecuta el comando con el rol propietario de la tabla y valida
por separado los permisos del rol de migración de Supabase.

## Procedimiento final para Windows (PowerShell)

Este procedimiento es para una persona autorizada a operar la base. No lo
ejecutes desde una sesión de prueba ni con una conexión que apunte a otra base.
El respaldo debe quedar fuera del repositorio y con acceso restringido.

### A. Preparar el entorno y revisar el destino

Desde la raíz del repositorio, conserva `backend/.env` si ya existe. Si falta,
copia la plantilla y configúrala localmente; no la agregues a Git:

```powershell
if (-not (Test-Path backend/.env)) {
    Copy-Item backend/.env.example backend/.env
}
```

Configura `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_NAME` y `DB_PASSWORD` para la
base autorizada. Puedes introducirlos en la sesión actual sin poner la
contraseña en un comando guardado:

```powershell
$env:DB_HOST = Read-Host 'DB_HOST del destino aprobado'
$env:DB_PORT = Read-Host 'DB_PORT del destino aprobado'
$env:DB_USER = Read-Host 'DB_USER del destino aprobado'
$env:DB_NAME = Read-Host 'DB_NAME del destino aprobado'
$claveSegura = Read-Host 'DB_PASSWORD del destino aprobado' -AsSecureString
$punteroClave = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($claveSegura)
try {
    $env:DB_PASSWORD = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($punteroClave)
} finally {
    [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($punteroClave)
    Remove-Variable claveSegura, punteroClave
}
```

La contraseña se mantiene en memoria de la sesión para que la lea Alembic; no
la escribas en el historial, en la URL de conexión ni en un archivo versionado.
Las demás opciones requeridas por la aplicación deben estar configuradas en
`backend/.env` o en variables protegidas de esa sesión. Antes de seguir,
confirma por un canal seguro que el host y nombre de base corresponden al
destino aprobado. No imprimas la contraseña ni una URL con credenciales.

### B. Crear y comprobar el respaldo

Elige una carpeta segura fuera del repositorio. `pg_dump` pedirá la contraseña
sin incluirla en el comando:

```powershell
$respaldo = Join-Path $env:USERPROFILE "acadex-antes-alembic-$(Get-Date -Format yyyyMMdd-HHmmss).dump"
pg_dump --host $env:DB_HOST --port $env:DB_PORT --username $env:DB_USER --dbname $env:DB_NAME --password --format=custom --no-owner --no-privileges --schema=public --file $respaldo
if ($LASTEXITCODE -ne 0) { throw 'pg_dump falló; no continúes con stamp.' }
if (-not (Test-Path $respaldo) -or (Get-Item $respaldo).Length -le 0) { throw 'El respaldo no existe o está vacío.' }
```

Guarda el respaldo fuera del repositorio, restringe su acceso y verifica que el
archivo exista y tenga tamaño mayor que cero. Para restaurarlo, usa una base
aislada y sigue la sección de comparación; nunca pruebes la restauración encima
de la base que estás protegiendo.

### C. Comparar, adoptar y verificar

Instala las dependencias del backend según `backend/requirements.txt` y trabaja
desde `backend/`. Si aún no hay un entorno virtual local, créalo. Estos comandos
no cambian archivos versionados:

```powershell
Set-Location backend
if (-not (Test-Path .venv\Scripts\python.exe)) { py -m venv .venv }
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Compara primero la estructura completa de la base objetivo con `alembic upgrade
head` aplicado a una base vacía. No leas filas personales. Si falta o difiere
un objeto, detente y resuelve la diferencia antes de adoptar.

En la misma sesión de PowerShell, permite solo el comando `stamp`:

```powershell
$env:ALEMBIC_ALLOW_ADOPT_EXISTING = '1'
.\.venv\Scripts\python.exe -m alembic stamp head
if ($LASTEXITCODE -ne 0) { throw 'stamp falló; detén el procedimiento.' }
$env:ALEMBIC_ALLOW_ADOPT_EXISTING = $null
.\.venv\Scripts\python.exe -m alembic current
if ($LASTEXITCODE -ne 0) { throw 'No se pudo verificar alembic current.' }
.\.venv\Scripts\python.exe -m alembic upgrade head
if ($LASTEXITCODE -ne 0) { throw 'upgrade head falló; no despliegues el backend.' }
.\.venv\Scripts\python.exe -m alembic upgrade head
if ($LASTEXITCODE -ne 0) { throw 'La segunda verificación de upgrade falló.' }
```

`current` debe mostrar la revisión `head` aprobada. Ambas ejecuciones de
`upgrade head` deben terminar sin aplicar revisiones nuevas. La variable de
adopción no habilita `upgrade`; quítala al terminar `stamp`.

Después del `stamp`, aplica también el comando RLS de la sección anterior a
`public.alembic_version`, con el rol propietario adecuado. `psql` pedirá la
contraseña; no la añadas a la línea de comandos:

```powershell
psql --host $env:DB_HOST --port $env:DB_PORT --username $env:DB_USER --dbname $env:DB_NAME --password --command "ALTER TABLE public.alembic_version ENABLE ROW LEVEL SECURITY;"
if ($LASTEXITCODE -ne 0) { throw 'No se pudo activar RLS en alembic_version.' }
psql --host $env:DB_HOST --port $env:DB_PORT --username $env:DB_USER --dbname $env:DB_NAME --password --command "SELECT relrowsecurity FROM pg_catalog.pg_class WHERE oid = 'public.alembic_version'::regclass;"
```

La consulta de verificación lee solo el catálogo de PostgreSQL, no filas de la
aplicación; debe devolver `t`. Comprueba también `/health/ready` y operaciones
de la aplicación en un entorno controlado. La prueba con el usuario superusuario
local no valida los permisos RLS de los roles de Supabase.

### D. Arranque de Render y reversión

El comando del contenedor backend en `backend/Dockerfile` inicia Uvicorn; no
ejecuta Alembic. El repositorio no contiene una configuración de Render que
añada una migración al arranque. Por eso, no asumas que el backend de Render
migra la base al iniciar: la adopción y cualquier migración deben ejecutarse
como operación explícita y controlada.

Si necesitas retirar solo el registro de Alembic, conéctate a la base correcta
como propietario y ejecuta:

```sql
DROP TABLE public.alembic_version;
```

Esto elimina únicamente la tabla de seguimiento de Alembic. No deshace cambios
de esquema ni borra datos de las tablas Acadex. No uses `CASCADE`. Luego detén
cualquier despliegue y vuelve a comparar el esquema antes de decidir el
siguiente paso. Para revertir cambios de una migración, evalúa esa migración por
separado o restaura el respaldo; borrar `alembic_version` no la revierte.
Al terminar o abortar, cierra esta sesión de PowerShell para retirar las
credenciales temporales de su entorno.

## Recuperación

Detén el despliegue si falla una comparación o una verificación. `stamp` cambia
el historial de Alembic, no revierte ni repara el esquema. Para volver a un
estado conocido, restaura el respaldo previo en una base nueva, verifica su
esquema y disponibilidad, y sigue el procedimiento aprobado para dirigir la
aplicación a esa base. No uses `alembic downgrade` como reversión automática de
un `stamp`: no deshace los cambios de esquema que pudieran existir antes.

Si ya se ejecutó una migración con cambios de esquema, evalúa por separado si
es seguro revertirla; puede haber datos nuevos que se perderían. Prefiere
restaurar el respaldo o preparar una migración correctiva revisada.

## Glosario

- **Migración:** instrucciones versionadas que cambian el esquema de una base.
- **Revisión (`revision`):** identificador de una migración.
- **Head:** última revisión disponible en la cadena de migraciones.
- **`stamp`:** registra una revisión como aplicada sin ejecutar sus cambios SQL.
- **`upgrade`:** ejecuta los cambios pendientes hasta una revisión.
- **RLS:** seguridad por filas de PostgreSQL; limita qué filas puede leer o
  cambiar cada rol.
- **Idempotente:** operación que se puede repetir sin causar un segundo cambio
  ni fallar porque el objeto ya existe.
- **DDL:** sentencias SQL que describen o cambian la estructura de la base.
- **Trigger:** acción automática que PostgreSQL ejecuta ante ciertos cambios.
