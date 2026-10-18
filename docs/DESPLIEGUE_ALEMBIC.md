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
- Las 18 tablas de la copia tenían RLS activado; las migraciones no lo activan.
  La copia no tenía políticas RLS.
- La copia no tenía `alembic_version`; la base de referencia sí, con la revisión
  `20261016_06`.
- `backend/alembic/env.py` rechaza una base con tablas Acadex y sin
  `public.alembic_version` en las líneas 56–79. La comprobación se ejecuta en
  cada operación en línea, incluida `stamp`, en las líneas 99–105.

Por esas diferencias, no se ejecutó `stamp`. Antes hay que decidir y registrar
en una migración cómo conservar el estado RLS, y revisar una forma explícita y
protegida de permitir `stamp` después de comparar el esquema. No elimines la
protección para permitir `upgrade` a ciegas.

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
migración revisada para normalizar el esquema, o documenta y aprueba por qué
una diferencia pertenece solo al entorno. Haz que la migración sea repetible;
para objetos opcionales usa formas idempotentes como `ALTER TABLE IF EXISTS`.

En este proyecto, una migración que habilite RLS debe cubrir las 18 tablas
existentes y las bases nuevas. `ALTER TABLE IF EXISTS public.<tabla> ENABLE ROW
LEVEL SECURITY` es repetible. Debe probarse con el usuario de conexión real del
backend: RLS sin políticas puede denegar consultas a roles que no sean dueños
de las tablas ni tengan `BYPASSRLS`.

### 4. Permitir `stamp` de forma controlada

La protección actual de `backend/alembic/env.py` también bloquea `stamp` cuando
la base tiene tablas Acadex, pero no tiene `alembic_version`. No la evadas con
SQL manual ni retires el control para todas las operaciones. Primero se debe
aprobar un cambio que permita `stamp` solo mediante una opción explícita y solo
después de la comparación y aprobación del esquema. Ese cambio no forma parte
de esta guía ni de la auditoría realizada.

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
