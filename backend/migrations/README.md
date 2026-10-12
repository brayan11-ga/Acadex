# Migraciones SQL de ACADEX

Las migraciones son SQL versionado, explícito y aditivo. No se agregó un ejecutor de migraciones ni se aplican cambios de esquema al iniciar FastAPI.

## Secuencia vigente

1. `20261011_add_archivo_uploader.sql`: agrega `archivos.id_usuario_subida` como nullable y una FK a `usuarios.id_usuario` con `ON DELETE SET NULL`. Las filas históricas quedan sin autor conocido.
2. `20261011_add_registration_consents.sql`: crea `consentimientos_usuario`, su FK con `ON DELETE CASCADE`, el `CHECK` de los dos tipos vigentes y la restricción `UNIQUE` por usuario, tipo y versión.

Para una base limpia, Compose monta el esquema base y ejecuta las migraciones en este orden en `/docker-entrypoint-initdb.d`. Para una base existente, la inicialización de Docker no vuelve a ejecutarse: aplica cada archivo de forma explícita después de crear y verificar un respaldo, usando el bloque **Actualizar una base existente** de [database/README.md](../../database/README.md). El mismo procedimiento se aplica a entornos desplegados con coordinación manual; el arranque de la aplicación no ejecuta DDL.

Las migraciones usan `IF NOT EXISTS` y la migración de la FK busca el nombre de constraint antes de crearla. Esto permite repetirlas sobre el esquema compatible. No valida ni repara objetos preexistentes que tengan el mismo nombre con una definición distinta; revisa el esquema y detente si el estado es parcial o incompatible. No apliques `database/init.sql` sobre datos existentes.

## Archivos adjuntos

Los binarios nuevos se guardan con una clave interna aleatoria bajo `ACADEX_UPLOADS_DIR`; en desarrollo local se monta `backend/uploads` dentro del contenedor. La API conserva lectura de rutas históricas `uploads/tareas/<tarea>/<archivo>`. Los servicios mantienen las reglas de autorización actuales: para tareas grupales, la persona asignada puede consultar los adjuntos; solo quien subió el archivo puede borrarlo individualmente. Los registros históricos sin autor siguen disponibles, pero no se borran de forma individual porque no puede verificarse quién los subió.

En un entorno desplegado, configura una ruta privada y persistente, compartida por todas las instancias FastAPI; no expongas el directorio como contenido estático. Antes de cambiar la ubicación de archivos, copia los binarios preservando la estructura por tarea y verifica checksums y referencias. La API no migra ni borra el origen. Configura también en el proxy un límite de cuerpo multipart ligeramente superior a 5 MiB; el backend mantiene el límite de 5 MiB por archivo.

## Reversiones

Los archivos `*.rollback.sql` no son parte de la actualización normal. La reversión del autor aborta si ya hay autorías no nulas; la de consentimientos aborta si ya existe evidencia. Antes de plantear cualquiera, exporta y revisa los datos afectados y define una reversión que los preserve.
