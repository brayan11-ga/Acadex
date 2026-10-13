# Migraciones SQL de ACADEX

Las migraciones son SQL versionado, explícito y aditivo. No se agregó un ejecutor de migraciones ni se aplican cambios de esquema al iniciar FastAPI.

## Secuencia vigente

1. `20261011_add_archivo_uploader.sql`: agrega `archivos.id_usuario_subida` como nullable y una FK a `usuarios.id_usuario` con `ON DELETE SET NULL`. Las filas históricas quedan sin autor conocido.
2. `20261011_add_registration_consents.sql`: crea `consentimientos_usuario`, su FK con `ON DELETE CASCADE`, el `CHECK` de los dos tipos vigentes y la restricción `UNIQUE` por usuario, tipo y versión.
3. `20261012_add_gemini_usage_limits.sql`: crea contadores diarios para limitar análisis de Gemini por usuario y para toda la demostración. No guarda documentos ni respuestas.
4. `20261012_add_gemini_quota_lockout.sql`: crea el bloqueo compartido que evita nuevas llamadas hasta el reinicio diario de Google cuando la API confirma que agotó su cuota diaria.
5. `20261012_add_security_guards.sql`: agrega el vencimiento de bloqueos de cuenta, una tabla de límites temporales compartidos y un índice único parcial para permitir solo un cronómetro activo por tarea. La migración se detiene sin borrar filas si encuentra sesiones activas duplicadas.

La ruta de análisis de Gemini requiere que las migraciones tercera y cuarta estén aplicadas. El backend no las ejecuta al arrancar. Para la demostración gratuita, el límite inicial es 1 análisis exitoso por usuario y 18 intentos para todo el proyecto por día de reinicio de Google. `GEMINI_GLOBAL_DAILY_LIMIT` puede configurarse entre 1 y 20; solo súbelo a 20 si AI Studio confirma 20 solicitudes diarias para ese proyecto y no se harán llamadas manuales con la misma cuota. El backend impone el máximo de 20 aunque queden variables antiguas con valores mayores en un `.env`. La cuota personal usa día UTC; la global usa el día de Google (medianoche del Pacífico). Los intentos que Google rechaza liberan el cupo personal, pero siguen contando contra el límite global. Un error confirmado de cuota diaria crea un bloqueo persistente hasta medianoche del Pacífico. Si las tablas no están disponibles, el endpoint falla de forma segura y no llama al proveedor.

La migración quinta es necesaria antes de habilitar registro, inicio de sesión, recuperación de contraseña o unión a grupos: si falta su tabla de límites, esas rutas responden `503` de forma segura. En producción, aplicar la migración después de una copia de seguridad y antes de desplegar el código. Si aborta por sesiones activas duplicadas, no elimine filas automáticamente: revise con el propietario qué sesión debe finalizar y vuelva a aplicar la migración solo después de resolver la inconsistencia.

El código bloquea una cuenta durante 15 minutos al quinto intento fallido y también libera los bloqueos heredados permanentes. La tabla de límites almacena solo HMAC de los identificadores y contadores con retención de 24 horas; los límites se comparten entre instancias mediante PostgreSQL.

Para una base limpia, Compose monta el esquema base y estas migraciones en `/docker-entrypoint-initdb.d`. Para una base existente, la inicialización de Docker no vuelve a ejecutarse: aplica cada archivo de forma explícita después de crear y verificar un respaldo, usando el bloque **Actualizar una base existente** de [database/README.md](../../database/README.md). El mismo procedimiento se aplica a entornos desplegados con coordinación manual; el arranque de la aplicación no ejecuta DDL.

Las migraciones usan `IF NOT EXISTS` y la migración de la FK busca el nombre de constraint antes de crearla. Esto permite repetirlas sobre el esquema compatible. No valida ni repara objetos preexistentes que tengan el mismo nombre con una definición distinta; revisa el esquema y detente si el estado es parcial o incompatible. No apliques `database/init.sql` sobre datos existentes.

## Archivos adjuntos

Los binarios nuevos se guardan con una clave interna aleatoria bajo `ACADEX_UPLOADS_DIR`; en desarrollo local se monta `backend/uploads` dentro del contenedor. La API conserva lectura de rutas históricas `uploads/tareas/<tarea>/<archivo>`. Los servicios mantienen las reglas de autorización actuales: para tareas grupales, la persona asignada puede consultar los adjuntos; solo quien subió el archivo puede borrarlo individualmente. Los registros históricos sin autor siguen disponibles, pero no se borran de forma individual porque no puede verificarse quién los subió.

En producción, los adjuntos nuevos se guardan en un bucket privado de Supabase Storage mediante llamadas servidor a servidor desde FastAPI. La ruta del objeto se registra en `archivos.ruta`; la clave `service_role` nunca se envía al frontend. FastAPI comprueba primero el acceso a la tarea y solo entonces descarga o borra el objeto. Las subidas siguen limitadas a 5 MiB y a PDF, DOCX, JPG y PNG, validando nombre, MIME y firma/contenido.

Para habilitarlos, crea manualmente en Supabase un bucket privado `acadex-adjuntos` con límite de 5 MiB y MIME permitidos `application/pdf`, `application/vnd.openxmlformats-officedocument.wordprocessingml.document`, `image/jpeg` y `image/png`. En el backend configura `ATTACHMENTS_ENABLED=true`, `ATTACHMENTS_STORAGE_BACKEND=supabase`, `SUPABASE_URL`, `SUPABASE_SECRET_KEY` y `SUPABASE_STORAGE_BUCKET`. Si tu proyecto solo muestra la clave antigua, `SUPABASE_SERVICE_ROLE_KEY` también funciona. En Cloudflare Pages configura `VITE_ATTACHMENTS_ENABLED=true` y el `VITE_API_URL` público del backend. No configures ninguna clave privada Supabase en Cloudflare Pages. Producción rechaza iniciar si falta la configuración necesaria para el almacenamiento persistente.

El PDF elegido para autocompletar con Gemini forma parte de la lista pendiente de adjuntos. El frontend lo envía al endpoint `POST /api/v1/tareas/con-pdf`, que sube el binario y guarda la tarea y sus metadatos en una sola transacción de PostgreSQL. Si falla Storage o la transacción, la tarea no se confirma y la interfaz conserva el formulario para reintentar; no se presenta una tarea sin su PDF como terminada. Los adjuntos adicionales se suben después y la pantalla de reintento permanece abierta hasta que terminen. Si Storage no responde, ningún sistema puede completar la escritura en ese momento; el usuario verá el error y deberá reintentar. En desarrollo local se puede mantener `ATTACHMENTS_STORAGE_BACKEND=local`.

Los archivos históricos que solo existan en `backend/uploads/` no se copian automáticamente a Supabase. Antes de cambiar una instalación con adjuntos previos, migra los binarios preservando referencias y verifica checksums; la API no borra ni migra ese origen. Si Supabase no responde durante el borrado de una tarea, PostgreSQL ya habrá eliminado sus referencias y el objeto puede quedar huérfano dentro del bucket privado; no será descargable por la aplicación y requerirá limpieza posterior. Configura también en el proxy un límite de cuerpo multipart ligeramente superior a 5 MiB.

## Reversiones

Los archivos `*.rollback.sql` no son parte de la actualización normal. La reversión del autor aborta si ya hay autorías no nulas; la de consentimientos aborta si ya existe evidencia. Antes de plantear cualquiera, exporta y revisa los datos afectados y define una reversión que los preserve.
