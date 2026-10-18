# Alinear una base existente con Alembic

## Alcance

Esta guía explica cómo adoptar con seguridad Alembic en una base que ya tiene
tablas y datos. `stamp` registra una revisión en `alembic_version`; no crea,
altera ni verifica las tablas. Por eso, primero se compara el esquema completo.

No guardes respaldos, archivos `.env`, credenciales ni datos personales dentro
del repositorio. Usa una copia aislada para ensayar el procedimiento.

## Estado comprobado del proyecto

- La revisión `head` actual es `20261016_06`.
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

`current` debe mostrar `20261016_06` o la revisión `head` aprobada más reciente.
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
