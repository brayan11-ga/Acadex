# Migraciones manuales de Acadex

Acadex aún no tiene un ejecutor de migraciones versionadas. La migración SQL de esta carpeta es aditiva y debe aplicarse una vez, en el despliegue controlado, después de respaldar PostgreSQL:

```powershell
psql -v ON_ERROR_STOP=1 -f .\migrations\20261011_add_archivo_uploader.sql
```

La columna nueva es nullable para conservar los adjuntos históricos sin atribuirlos a un usuario ficticio. No se requiere índice nuevo: las operaciones consultan por `id_tarea`, que ya cuenta con índice en el esquema actual.

En tareas personales, el propietario puede eliminar sus adjuntos. En tareas grupales, la API solo permite borrar el adjunto a quien lo subió; los adjuntos históricos sin autor siguen disponibles para los asignados, pero no se pueden borrar individualmente porque no se puede verificar su autor. El líder del grupo puede eliminar la tarea completa; esa operación elimina también sus adjuntos y solo retira los binarios después de que PostgreSQL confirma el borrado.

## Almacenamiento

Los binarios nuevos se guardan con una clave interna aleatoria bajo el directorio indicado por `ACADEX_UPLOADS_DIR`. Si no se configura, el backend usa `backend/uploads/tareas`, adecuado para desarrollo local. En producción, la ruta debe ser privada, persistente y compartida por todas las instancias de FastAPI; no debe exponerse como contenido estático. El servicio conserva lectura de las rutas históricas `uploads/tareas/<tarea>/<archivo>`.

Antes de cambiar de almacenamiento, copie los binarios existentes preservando la estructura por tarea y verifique checksums y referencias. La API no ejecuta esa migración de contenido ni borra el origen. Configure también en el proxy de entrada un límite de cuerpo multipart ligeramente superior a 5 MiB para permitir los encabezados del formulario; el backend mantiene el límite de 5 MiB por archivo.

## Reversión

`20261011_add_archivo_uploader.rollback.sql` solo procede si no se ha registrado ninguna autoría nueva. Contiene una comprobación que aborta antes de quitar la columna si detecta valores no nulos. Si ya existen autores, respalde/exporte esa información y prepare una reversión explícita antes de retirar el esquema.

## Consentimientos de registro

Antes de desplegar la versión que exige aceptación en el registro, aplique la migración aditiva de evidencias:

```powershell
psql -v ON_ERROR_STOP=1 -f .\migrations\20261011_add_registration_consents.sql
```

La tabla `consentimientos_usuario` guarda el tipo de aceptación, la versión del aviso y la fecha de registro. Las cuentas que ya existían quedan sin registros históricos inventados. El alta de una cuenta, su perfil y ambas evidencias se confirma en una sola transacción.

La reversión `20261011_add_registration_consents.rollback.sql` aborta si existe evidencia; expórtela y revise esos datos antes de planear la retirada. El límite antiabuso se mantiene en memoria por proceso, por lo que en producción debe configurarse también en el proxy o en una capa compartida si se ejecutan varias instancias. Si el backend está detrás de un proxy, confíe las cabeceras de cliente solo desde proxies conocidos.
