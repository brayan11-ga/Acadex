# Migraciones SQL históricas de ACADEX

Esta carpeta reúne los SQL de la ruta manual anterior. Crea las nuevas migraciones en
[`backend/alembic/versions/`](../../backend/alembic/versions) y sigue
[Inicio con Docker](../../docs/inicio-docker.md) o
[Inicio manual](../../docs/inicio-manual.md) para preparar una base local.
Consulta la [guía de base de datos](../README.md) para actualizar una instalación.

## Archivos conservados

- [`init.sql`](init.sql) es el volcado base. [`acadex.sql`](acadex.sql) reproduce el
  arranque manual antiguo con ese volcado y las cinco primeras migraciones SQL.
- Los SQL fechados contienen los cambios y las dos reversiones manuales que
  antes se guardaban en los directorios de migraciones.
- [`supabase_new_project.sql`](supabase_new_project.sql) y
  [`supabase_resume_migrations.sql`](supabase_resume_migrations.sql) son
  snapshots manuales antiguos con configuración RLS.

Los scripts se conservan para consulta y reproducción histórica en bases aisladas.
Algunos comentarios conservan las rutas originales.

Las referencias a bases migradas o pendientes describen el estado registrado en
aquella transición. No confirman el estado actual de Supabase. Para instalar en
local, usa [Inicio con Docker](../../docs/inicio-docker.md) o
[Inicio manual](../../docs/inicio-manual.md); para una base existente, consulta
[Base de datos](../../database/README.md).

## Secuencia SQL histórica convertida a revisiones Alembic

1. [`20261011_add_archivo_uploader.sql`](20261011_add_archivo_uploader.sql) agrega la columna opcional `archivos.id_usuario_subida` y una FK a `usuarios.id_usuario` con `ON DELETE SET NULL`. Las filas históricas quedan sin autor conocido.
2. [`20261011_add_registration_consents.sql`](20261011_add_registration_consents.sql) crea `consentimientos_usuario`, su FK con `ON DELETE CASCADE`, el `CHECK` de los dos tipos vigentes y la restricción `UNIQUE` por usuario, tipo y versión.
3. [`20261012_add_gemini_usage_limits.sql`](20261012_add_gemini_usage_limits.sql) crea contadores diarios para limitar análisis de Gemini por usuario y para toda la demostración. No guarda documentos ni respuestas.
4. [`20261012_add_gemini_quota_lockout.sql`](20261012_add_gemini_quota_lockout.sql) crea el bloqueo compartido que evita nuevas llamadas hasta el reinicio diario de Google cuando la API confirma que agotó su cuota diaria.
5. [`20261012_add_security_guards.sql`](20261012_add_security_guards.sql) añade el vencimiento de bloqueos de cuenta, una tabla de límites temporales compartidos y un índice único parcial para permitir solo un cronómetro activo por tarea. La migración se detiene sin borrar filas si encuentra sesiones activas duplicadas.
6. [`20261018_add_tarea_max_archivos.sql`](20261018_add_tarea_max_archivos.sql) es el SQL manual equivalente a `20261018_01`, que agrega `tareas.max_archivos`.

La ruta de análisis de Gemini requiere las revisiones Alembic que crean los contadores y bloqueos. En Compose, el servicio `migrate` ejecuta Alembic antes de iniciar FastAPI. Para la demostración gratuita, el límite inicial es 1 análisis exitoso por usuario y 18 intentos para todo el proyecto por día de reinicio de Google. `GEMINI_GLOBAL_DAILY_LIMIT` puede configurarse entre 1 y 20. Solo súbelo a 20 si AI Studio confirma 20 solicitudes diarias para ese proyecto y no se harán llamadas manuales con la misma cuota. El backend impone el máximo de 20 aunque queden variables antiguas con valores mayores en un `.env`. La cuota personal usa día UTC. La global usa el día de Google (medianoche del Pacífico). Los intentos que Google rechaza liberan el cupo personal y siguen contando contra el límite global. Un error confirmado de cuota diaria crea un bloqueo persistente hasta medianoche del Pacífico. Si faltan las tablas, el endpoint rechaza la solicitud sin llamar al proveedor.

Registro, inicio de sesión, recuperación de contraseña y unión a grupos responden `503` si falta la tabla de límites de la revisión de guardas de seguridad. Si la revisión aborta por sesiones activas duplicadas, acuerda con el propietario qué sesión debe finalizar antes de reintentar.

El código bloquea una cuenta durante 15 minutos al quinto intento fallido y también libera los bloqueos heredados permanentes. La tabla de límites almacena solo HMAC de los identificadores y contadores con retención de 24 horas; los límites se comparten entre instancias mediante PostgreSQL.

Durante la transición se respaldó y comparó la base persistente de Docker
`acadex_dev` antes de registrar `20261016_03`. Luego se actualizó a
`20261016_06`. En esa base local se comprobaron 18 tablas, las nueve
categorías originales y el resultado de `alembic check` sin operaciones
pendientes. El estado informado de Supabase se registra en la
[guía de Alembic](../../docs/DESPLIEGUE_ALEMBIC.md#estado-informado-de-supabase).

Los SQL originales tenían comprobaciones para repetir la ejecución manual.
Alembic usa `public.alembic_version` para aplicar solo las revisiones pendientes.
Si encuentra tablas de Acadex sin historial, la guardia exige
[adoptar la base existente](../../docs/DESPLIEGUE_ALEMBIC.md#adopción-de-una-base-sin-historial).

## Archivos adjuntos

Los binarios nuevos se guardan con una clave interna aleatoria bajo `ACADEX_UPLOADS_DIR`; en desarrollo local se monta `backend/uploads` dentro del contenedor. La API conserva lectura de rutas históricas `uploads/tareas/<tarea>/<archivo>`. Los servicios mantienen las reglas de autorización actuales: para tareas grupales, la persona asignada puede consultar los adjuntos; solo quien subió el archivo puede borrarlo individualmente. Los registros históricos sin autor siguen disponibles, pero no se borran de forma individual porque no puede verificarse quién los subió.

En producción, los adjuntos nuevos se guardan en un bucket privado de Supabase Storage mediante llamadas servidor a servidor desde FastAPI. La ruta del objeto se registra en `archivos.ruta`; la clave `service_role` nunca se envía al frontend. FastAPI comprueba primero el acceso a la tarea y solo entonces descarga o borra el objeto. Las subidas siguen limitadas a 5 MiB y a PDF, DOCX, JPG y PNG, validando nombre, MIME y firma/contenido.

Para habilitarlos, crea manualmente en Supabase un bucket privado `acadex-adjuntos` con límite de 5 MiB y MIME permitidos `application/pdf`, `application/vnd.openxmlformats-officedocument.wordprocessingml.document`, `image/jpeg` y `image/png`. En el backend configura `ATTACHMENTS_ENABLED=true`, `ATTACHMENTS_STORAGE_BACKEND=supabase`, `SUPABASE_URL`, `SUPABASE_SECRET_KEY` y `SUPABASE_STORAGE_BUCKET`. Si tu proyecto solo muestra la clave antigua, `SUPABASE_SERVICE_ROLE_KEY` también funciona. En Cloudflare Pages configura `VITE_ATTACHMENTS_ENABLED=true` y el `VITE_API_URL` público del backend. No configures ninguna clave privada Supabase en Cloudflare Pages. Producción rechaza iniciar si falta la configuración necesaria para el almacenamiento persistente.

El PDF elegido para autocompletar con Gemini forma parte de la lista pendiente de adjuntos. El frontend lo envía al endpoint `POST /api/v1/tareas/con-pdf`, que sube el binario y guarda la tarea y sus metadatos en una sola transacción de PostgreSQL. Si falla Storage o la transacción, la tarea no se confirma y la interfaz conserva el formulario para reintentar; no se presenta una tarea sin su PDF como terminada. Los adjuntos adicionales se suben después y la pantalla de reintento permanece abierta hasta que terminen. Si Storage no responde, ningún sistema puede completar la escritura en ese momento; el usuario verá el error y deberá reintentar. En desarrollo local se puede mantener `ATTACHMENTS_STORAGE_BACKEND=local`.

Los archivos históricos que solo existan en `backend/uploads/` no se copian automáticamente a Supabase. Antes de cambiar una instalación con adjuntos previos, migra los binarios preservando referencias y verifica checksums; la API no borra ni migra ese origen. Si Supabase no responde durante el borrado de una tarea, PostgreSQL ya habrá eliminado sus referencias y el objeto puede quedar huérfano dentro del bucket privado; no será descargable por la aplicación y requerirá limpieza posterior. Configura también en el proxy un límite de cuerpo multipart ligeramente superior a 5 MiB.

## Reversiones históricas

Los archivos `*.rollback.sql` no son parte de la actualización normal. La reversión del autor aborta si ya hay autorías no nulas; la de consentimientos aborta si ya existe evidencia. Antes de plantear cualquiera, exporta y revisa los datos afectados y define una reversión que los preserve.

## Downgrade de Alembic

La revisión base y la revisión de guardas de seguridad detienen cualquier `alembic downgrade`: borrar el esquema inicial puede perder datos y retirar el índice de sesión activa o los límites debilita protecciones. Las revisiones intermedias solo permiten retroceder si primero comprueban que no hay autorías, evidencias, contadores o bloqueos que se perderían. Una reversión también requiere desplegar una versión de la aplicación compatible; no es un mecanismo para reparar producción.
