# Plan de implantación de Acadex

| Campo | Valor |
| --- | --- |
| Proyecto | Acadex · gestión de tareas académicas individuales y grupales |
| Equipo por roles | Responsable de entrega, operador de plataforma, administrador PostgreSQL y Storage, soporte y equipo de aceptación |
| Versión del plan | 1.0 |
| Versión del software | Última entrega registrada en `origin/main`: `1bd904edc9be0d18be816deda98b6112b1f1e449`. Referencia técnica de este plan: `b7ec11919955ef3bdf30d8920594a68434e9c493`. |
| Fecha | 21 de noviembre de 2026 |

| Versión del plan | Fecha | Cambio |
| --- | --- | --- |
| Borrador `b7ec119` | 21 de noviembre de 2026 | Inventario de la arquitectura, proveedores y procedimientos de operación |
| 1.0 | 21 de noviembre de 2026 | Instalación, migración y restauración paso a paso. Criterios y registro del simulacro cruzado. |

**Índice**

1. [Ficha técnica y requisitos mínimos](#1-ficha-técnica-y-requisitos-mínimos)
2. [Plan de migración de datos](#2-plan-de-migración-de-datos)
3. [Plan de respaldo y restauración](#3-plan-de-respaldo-y-restauración)
4. [Hosting y dominio](#4-hosting-y-dominio)
5. [Plan de instalación y despliegue](#5-plan-de-instalación-y-despliegue)
6. [Configuración y verificación](#6-configuración-y-verificación)
7. [Seguridad, usuarios y permisos](#7-seguridad-usuarios-y-permisos)
8. [Pipeline de despliegue y monitoreo](#8-pipeline-de-despliegue-y-monitoreo)
9. [Mantenimiento, soporte y capacitación](#9-mantenimiento-soporte-y-capacitación)
10. [Aceptación y entrega](#10-aceptación-y-entrega)

## 1. Ficha técnica y requisitos mínimos

### 1.1 Arquitectura

El navegador carga la interfaz React compilada con Vite. El cliente añade `/api/v1` al origen de FastAPI. SQLAlchemy conecta la API a PostgreSQL. En modo de producción, FastAPI también requiere un bucket privado de Supabase Storage. PostgreSQL guarda las referencias a los binarios. En Compose, `migrate` aplica Alembic antes del arranque de la API. [Arquitectura](arquitectura.md) · [Cliente HTTP](../frontend/src/services/api.ts) · [Compose](../docker-compose.yml) · [Configuración](../backend/app/config/settings.py).

~~~mermaid
flowchart LR
    Browser["Navegador"] --> Site["Interfaz React"]
    Browser -->|"/api/v1"| Api["API FastAPI"]
    Api --> Db["PostgreSQL"]
    Api -->|Adjuntos en modo producción| Storage["Supabase Storage"]
    Migrate["Proceso Alembic"] --> Db
    Api -->|SMTP en Compose| Mail["Mailpit"]
~~~

### 1.2 Plataforma e inventario

| Componente | Función | Versión o referencia | Costo de operación |
| --- | --- | --- | --- |
| Linux en contenedores | Entorno de ejecución local y de la imagen de la API | Python `3.14.8-slim` para backend. Node.js `24-alpine` para el servidor Vite de desarrollo. | Recursos de la máquina local o plan del proveedor |
| React, TypeScript, Vite y pnpm | Interfaz y compilación | React `^19.2.8`, TypeScript `~6.0.2`, Vite `^8.2.0` y pnpm `12.11.2`. CI usa Node.js 22. | Hosting de la interfaz y consumo de CI |
| FastAPI, Uvicorn, SQLAlchemy y Alembic | API, acceso a datos y esquema | `0.136.3`, `0.48.0`, `2.0.52` y `1.16.5`, respectivamente | Cómputo de la API |
| PostgreSQL | Persistencia | `17.11` en Compose. La versión efectiva de Supabase se obtiene en el destino autorizado con `SHOW server_version;`. | Almacenamiento, cómputo y copias |
| Mailpit | Correo local | `v1.31.4` en Compose | Recursos locales |

Usa un host Linux o una máquina con Docker compatible con contenedores Linux. En la nube se contratan servicios gestionados. La distribución del host, su ciclo de soporte y la topología física quedan a cargo del proveedor. Las imágenes del repositorio fijan los runtimes. Acadex se distribuye con licencia MIT. [Dockerfile backend](../backend/Dockerfile) · [Dockerfile frontend](../frontend/Dockerfile) · [Dependencias Python](../backend/requirements.txt) · [Frontend](../frontend/package.json) · [CI](../.github/workflows/ci.yml) · [Licencia del proyecto](../LICENSE).

### 1.3 Matriz y verificación de requisitos

| Recurso | Mínimo comprobable antes de instalar | Recomendado para el simulacro |
| --- | --- | --- |
| Sistema y herramientas | Git, Docker con contenedores Linux y Compose ≥ 2.24.0 para `env_file.required` | Host limpio e independiente. Registra SO, arquitectura y versiones. |
| CPU y RAM | Dimensionamiento sin umbral validado | Mide reposo y pico por servicio durante build, uso concurrente y restauración. Añade margen según el pico observado. |
| Disco e I/O | Espacio para imágenes, volumen `pgdata`, volcado y restauración de prueba | Medio separado para copias. Mide espacio máximo y tiempo de restauración antes de fijar el mínimo. |
| Red | Acceso saliente al repositorio, registros e índices de dependencias. Puertos locales libres según [§6.2](#62-servicios-dependencias-y-salud). | HTTPS para los orígenes públicos y TLS para PostgreSQL remoto. Valida DNS, conectividad y capacidad de transferencia en la ventana. |
| Herramientas de copia | Cliente PostgreSQL compatible con la versión principal de origen. `restic` para la política propuesta. | Comprueba ambas versiones y los accesos a los repositorios de respaldo antes del ensayo. |

En el host Linux, reúne evidencia previa sin arrancar servicios.

~~~bash
uname -srm
git --version
docker version
docker compose version
nproc
free -h
df -h .
~~~

**Verificación:** registra fecha, host por función, CPU, RAM, disco y salida de cada comando. Tras el arranque, toma muestras con `docker compose stats --no-stream` y registra picos durante el ensayo. **Limitación conocida:** el repositorio carece de un verificador de requisitos. Su resultado, los mínimos numéricos y la medición de capacidad quedan abiertos para el gate. [Inicio con Docker](inicio-docker.md) · [Inicio manual](inicio-manual.md).

## 2. Plan de migración de datos

### 2.1 Objetivo, origen, destino y mapeo

Para un traslado de instancia, conserva los datos de `public`, sus referencias y el historial de Alembic. En una base existente, aplica las revisiones de esquema por separado. El objetivo de aceptación del traslado es igualdad de conteos y huellas por tabla antes de cambiar el esquema, con referencias de adjuntos resolubles.

| Origen y formato | Destino | Mapeo y regla de rechazo |
| --- | --- | --- |
| PostgreSQL autorizado, esquema `public`, volcado lógico en formato custom | PostgreSQL vacío y aislado para ensayo. En un traslado aprobado, instancia de destino distinta de la de origen. | Identidad de tablas, columnas, claves y datos antes de migrar. Detén el traslado si hay errores de restauración o diferencias de conteo o huella. |
| `public.alembic_version`, si existe | Misma tabla de control | Conserva la revisión original para verificar el traslado. Evalúa la actualización después. Una base con tablas y sin historial requiere adopción explícita. |
| Binarios en bucket privado o almacenamiento local anterior | Bucket privado aprobado y registro de referencias | Conciliar clave de objeto, tamaño y SHA-256. Una referencia sin binario o un objeto con huella distinta bloquea el cambio. |

El administrador de datos inventaría tablas, roles, extensiones, volumen y adjuntos antes de fijar el tiempo de corte. Conserva la base de origen y evita escrituras simultáneas sobre los dos destinos. [Fuente vigente del esquema](../database/README.md#fuente-vigente-y-archivos-históricos).

### 2.2 Procedimiento de traslado propuesto

1. Identifica origen y destino conforme a [§3.2](#32-conexión-y-huella-reproducible). Acuerda la ventana y detén las escrituras desde la API, las integraciones y cualquier proceso que modifique tablas u objetos. Captura el volcado, la huella y el inventario de objetos según [§3.3](#33-generar-y-cifrar-la-copia). **Verificación:** origen identificado, copia cifrada disponible y manifiestos del mismo corte.
2. Restaura la copia en el destino aislado según [§3.4](#34-restaurar-y-verificar). Hazlo antes de aplicar cambios de esquema. Si hay adjuntos, restaura los objetos en el bucket privado de ensayo y comprueba el manifiesto desde una terminal autorizada. **Verificación:** huellas y conteos idénticos, revisión conservada y ninguna referencia huérfana.
3. Ensaya [§2.3](#23-migración-de-esquema-con-alembic) y las comprobaciones de [§6](#6-configuración-y-verificación) con datos sintéticos. En el corte aprobado, repite la captura si hubo nuevas escrituras y verifica el destino final antes de redirigir la API. **Verificación:** registra inicio y fin, revisión, comprobaciones de permisos y decisión de activar.
4. Si falla antes de habilitar escrituras en el destino, conserva el origen y vuelve a dirigir la API al origen. Si el destino ya aceptó escrituras, suspéndelas, inventaría el delta y acuerda la conciliación antes de volver. **Verificación:** identifica el destino efectivo y repite el humo antes de reabrir.

| Riesgo | Acción |
| --- | --- |
| DDL con bloqueos o tiempos fuera de ventana | Mide sobre la copia. En `20261018_01`, la validación del `CHECK` puede recorrer `tareas`. Si el tiempo supera la ventana, pospón el corte. |
| Diferencias de esquema, RLS, propietarios o extensiones | Revisa catálogos y permisos con el rol previsto. Resuelve la causa antes de repetir. |
| Exportación incompleta o escritura durante el corte | Mantén bloqueadas las escrituras durante exportación y huella. Repite ambos si se pierde esa condición. |

### 2.3 Migración de esquema con Alembic

La imagen de la API inicia Uvicorn. El operador ejecuta Alembic en un proceso separado. La cadena de siete revisiones en `b7ec119` termina en `20261018_01`. Consulta `heads` sobre el commit que se vaya a instalar. Los SQL históricos se conservan como referencia. [Revisiones](../backend/alembic/versions) · [Dockerfile](../backend/Dockerfile) · [Historial](../backend/migrations/README.md).

1. **Preparar la sesión.** Desde la raíz del checkout aprobado, instala el entorno de migración en Linux. Inyecta `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_NAME`, `DB_PASSWORD`, `DB_SSLMODE` y, si se requiere, `DB_SSLROOTCERT` desde la configuración protegida del destino. Completa los campos de autenticación obligatorios de [§6.1](#61-variables-por-ambiente). Usa una sesión por destino y confirma su identidad con la consulta de [§3.2](#32-conexión-y-huella-reproducible).

   ~~~bash
   cd backend
   python3.14 -m venv .venv
   . .venv/bin/activate
   python -m pip install -r requirements.txt
   python -m alembic heads
   python -m alembic current
   ~~~

   **Verificación:** salida de `heads`, revisión inicial e identidad registradas. Si la base ya tiene tablas pero carece de historial, detén `upgrade` y aplica la regla de adopción indicada abajo.

2. **Respaldar y ensayar.** Genera y restaura el respaldo según [§3](#3-plan-de-respaldo-y-restauración). En la sesión apuntada exclusivamente a la copia, ejecuta:

   ~~~bash
   python -m alembic upgrade head
   python -m alembic current
   python -m alembic upgrade head
   psql -X -v ON_ERROR_STOP=1 -f ../database/verify_schema.sql
   ~~~

   **Verificación:** `current` coincide con la revisión objetivo, el segundo `upgrade` no aplica revisiones y todas las columnas del SQL devuelven `t`. Contrasta tablas, columnas, restricciones, índices y conteos contra lo esperado para la revisión. Para una instalación base, construye también una base vacía con `upgrade head` para comparar su estructura.

3. **Aplicar una vez.** En la ventana aprobada, verifica otra vez identidad, historial y copia recuperable. Desde `backend/` y con la sesión de migración autorizada, ejecuta los comandos en orden. Detén los pasos ante el primer fallo.

   ~~~bash
   python -m alembic current
   python -m alembic upgrade head
   python -m alembic current
   psql -X -v ON_ERROR_STOP=1 -f ../database/verify_schema.sql
   ~~~

   **Verificación:** revisión final, comprobaciones de catálogo y cambios esperados cuadran con el ensayo. Publica el backend que depende del esquema solo después de este control. Si falla, bloquea el despliegue y evalúa una migración correctiva o la recuperación de [§3.4](#34-restaurar-y-verificar), incluyendo escrituras posteriores a la copia.

**Adopción excepcional:** compara el catálogo completo con una base vacía migrada a la revisión exacta que representa el esquema existente. Si todo coincide y el responsable acepta la revisión, en la copia aislada ejecuta `ALEMBIC_ALLOW_ADOPT_EXISTING=1 python -m alembic stamp '<REVISIÓN_COMPATIBLE>'` y luego `python -m alembic current`. `stamp` solo escribe el historial. Si la política aprobada requiere RLS en `public.alembic_version`, el propietario ejecuta `ALTER TABLE public.alembic_version ENABLE ROW LEVEL SECURITY;`. El administrador comprueba `relrowsecurity` en `pg_class` y que Alembic pueda leer y actualizar el historial con el rol efectivo. Cualquier intervención equivalente en producción requiere autorización y evidencia específica. [Guardas de Alembic](../backend/alembic/env.py) · [Adopción y reversión](DESPLIEGUE_ALEMBIC.md).

### 2.4 Evidencia histórica de ejecución

| Entorno | Operación registrada | Verificación histórica |
| --- | --- | --- |
| Base persistente de Docker local | Respaldo y comparación previos al registro de `20261016_03`. Actualización posterior a `20261016_06`. | 18 tablas funcionales, nueve categorías y `alembic check` sin operaciones pendientes. [Historial SQL](../backend/migrations/README.md#secuencia-sql-histórica-convertida-a-revisiones-alembic) |
| Copia PostgreSQL aislada restaurada | Comparación del catálogo, adopción de `20261016_06` y dos invocaciones de `upgrade head` sin revisiones nuevas en el checkout de ese ensayo. | 18 tablas, 110 columnas, 72 restricciones y 43 índices comparados. RLS de la tabla de historial comprobado en la copia. `/health/ready`, registro, inicio de sesión y tarea sintética comprobados localmente. [Evidencia de adopción](DESPLIEGUE_ALEMBIC.md#evidencia-histórica-y-estado-a-verificar) |

**Limitación conocida:** las notas históricas no incluyen tiempos ni huellas de filas. No acreditan el traslado local a nube, la revisión que corre hoy en Supabase ni las políticas o permisos efectivos de producción.

## 3. Plan de respaldo y restauración

### 3.1 Política operativa propuesta

| Campo | Propuesta para el gate | Estado operativo |
| --- | --- | --- |
| Alcance | Volcado completo de `public`, historial Alembic, huellas por tabla y manifiesto. Copia separada de objetos de Storage y de los permisos, roles y dependencias externas necesarios para recuperar el servicio. | `pg_dump` y `pg_restore` documentados. No hay evidencia de una política de copias activa. |
| Objetivos | Candidatos de ensayo: RPO ≤ 24 h y RTO ≤ 4 h. Mide pérdida respecto del último punto consistente y desde el inicio de recuperación hasta humo y permisos en verde. | Objetivos sin acuerdo ni medición. |
| Frecuencia y retención | Diario y antes de cambios de esquema. Conservar 7 diarios, 4 semanales y 12 mensuales si capacidad y política de datos lo permiten. Ensayo mensual y ante cambios del método. | Calendario, retención y ejecución sin demostrar. |
| Regla 3-2-1 | Datos activos, copia cifrada en un medio independiente y segunda copia cifrada fuera del sitio, en un repositorio administrado por separado. Restringir modificación y borrado en el repositorio externo. | Ubicaciones y controles por asignar. |
| Cifrado y acceso | `restic` cifra ambas copias. Usa credenciales administradas fuera de Git. Usa área temporal privada en disco cifrado y TLS para conexiones remotas. | Herramienta, repositorios y automatización propuestos. |
| Responsables | Operador de respaldo toma la copia y registra el ID. Otro equipo restaura con acceso de lectura. El administrador de datos valida la base y el operador de plataforma valida la aplicación. | Falta registro de un ensayo cruzado del respaldo cifrado. |

Comprueba qué ofrece el plan contratado antes de depender de copias administradas o recuperación a un punto en el tiempo. El volcado de `public` cubre las referencias de adjuntos. El bucket, sus políticas y los binarios se recuperan por separado. [Copias de Supabase](https://supabase.com/docs/guides/platform/backups) · [Repositorios cifrados de restic](https://restic.readthedocs.io/en/stable/030_preparing_a_new_repo.html).

### 3.2 Conexión y huella reproducible

Ejecuta los bloques en Bash con `pg_dump`, `pg_restore`, `psql` y `restic` disponibles. Usa clientes PostgreSQL de la misma versión principal que el origen para el ensayo. Trabaja en una sesión con solo el destino autorizado. En cada cambio de base, reemplaza los cuatro parámetros y vuelve a comprobar identidad. Elige TLS y CA según el destino. El ejemplo remoto usa `verify-full`. Una instancia desechable local sin TLS usa `PGSSLMODE=disable` solo si se comprobó que es local.

~~~bash
set -euo pipefail
umask 077
export PGHOST='<HOST_APROBADO>' PGPORT='<PUERTO_APROBADO>'
export PGDATABASE='<BASE_APROBADA>' PGUSER='<ROL_AUTORIZADO>'
export PGSSLMODE=verify-full PGSSLROOTCERT='<RUTA_CA_APROBADA>'
psql -X -W -v ON_ERROR_STOP=1 -c 'SELECT current_database(), current_user; SHOW server_version;'
~~~

Ejecuta el siguiente bloque en ambos destinos con la misma versión principal y alcance. Asigna `HUELLA` a un archivo distinto en cada ejecución. El archivo contiene tabla, conteo y SHA-256 de los hashes de filas ordenados. Excluye el historial de Alembic y verifícalo por separado. El rol debe poder leer el contenido completo de las tablas incluidas. Para tablas grandes, mide el consumo de esta agregación antes de usarla fuera del simulacro.

~~~bash
psql -X -W -qAt -F '|' -v ON_ERROR_STOP=1 -o "$HUELLA" <<'SQL'
SET TIME ZONE 'UTC';
SET extra_float_digits = 3;
SET bytea_output = 'hex';
SET row_security = off;
SELECT format($q$
  SELECT %L, count(*), encode(sha256(convert_to(
    coalesce(string_agg(h, '' ORDER BY h COLLATE "C"), ''), 'UTF8')), 'hex')
  FROM (SELECT encode(sha256(convert_to(to_jsonb(t)::text, 'UTF8')), 'hex') h
        FROM ONLY public.%I t) filas
$q$, tablename, tablename)
FROM pg_tables
WHERE schemaname = 'public' AND tablename <> 'alembic_version'
ORDER BY tablename COLLATE "C"
\gexec
SQL
test -s "$HUELLA"
~~~

### 3.3 Generar y cifrar la copia

1. En el origen comprobado, con escrituras detenidas para el corte, prepara un directorio de trabajo nuevo, privado y cifrado fuera de Git. Si hay objetos, el administrador exporta los binarios y su manifiesto de claves y SHA-256 al área de copia por el mecanismo autorizado del proyecto. Registra versión, revisión, fecha y alcance sin datos de conexión.

   ~~~bash
   AREA='<DIRECTORIO_CIFRADO_EXISTENTE>'
   COPIA=$(mktemp -d "$AREA/acadex-copia.XXXXXXXX")
   pg_dump -W --format=custom --schema=public --no-privileges \
     --file="$COPIA/acadex.dump"
   test -s "$COPIA/acadex.dump"
   pg_restore --list "$COPIA/acadex.dump" > "$COPIA/contenido.txt"
   test -s "$COPIA/contenido.txt"
   HUELLA="$COPIA/huella.tsv"
   ~~~

   **Verificación:** ejecuta el bloque de huella de [§3.2](#32-conexión-y-huella-reproducible) sobre el mismo origen antes de reabrir escrituras. Comprueba que estén el volcado, la huella y el inventario acordado. Si hay adjuntos, incluye su copia y manifiesto en el área protegida. Guarda también la referencia de la revisión obtenida con `alembic current` cuando exista historial.

2. Inicializa cada repositorio una sola vez si el administrador lo entrega vacío. Luego cifra y copia la instantánea. Sustituye el ID por el obtenido en el primer repositorio. `restic` pide las contraseñas de repositorio de forma interactiva si la sesión carece de un mecanismo autorizado.

   ~~~bash
   REPO_LOCAL='<REPOSITORIO_LOCAL_ABSOLUTO>'
   REPO_EXTERNO='<REPOSITORIO_EXTERNO_AUTORIZADO>'
   # Solo para repositorios nuevos aprobados.
   restic -r "$REPO_LOCAL" init
   restic -r "$REPO_EXTERNO" init --from-repo "$REPO_LOCAL" --copy-chunker-params
   # Para cada copia.
   (cd "$COPIA" && restic -r "$REPO_LOCAL" backup . --tag acadex)
   restic -r "$REPO_LOCAL" snapshots --tag acadex
   SNAPSHOT_LOCAL='<ID_LOCAL>'
   restic -r "$REPO_EXTERNO" copy --from-repo "$REPO_LOCAL" "$SNAPSHOT_LOCAL"
   restic -r "$REPO_EXTERNO" snapshots --tag acadex
   restic -r "$REPO_LOCAL" check
   restic -r "$REPO_EXTERNO" check
   ~~~

   **Verificación:** registra ambos IDs y estado de integridad. Aplica la retención aprobada con el operador de cada repositorio. Retira los archivos temporales mediante el procedimiento de custodia acordado. Una copia se considera recuperable después de completar [§3.4](#34-restaurar-y-verificar). [Copia y verificación en restic](https://restic.readthedocs.io/en/stable/045_working_with_repos.html).

### 3.4 Restaurar y verificar

1. En una máquina aislada y una sesión nueva, prepara una instancia compatible con los mismos prerrequisitos de catálogo. Para una copia sintética de PostgreSQL 17, puedes iniciar solo la base de Compose desde un clon preparado como en [§5.2](#52-servidor-local-con-compose). El nombre de proyecto nuevo aísla el volumen. Usa un puerto libre en loopback.

   ~~~bash
   PROYECTO_RESTAURACION='<PROYECTO_NUEVO_RESTAURACION>'
   export ACADEX_DB_PORT='<PUERTO_LOCAL_LIBRE>'
   docker compose -p "$PROYECTO_RESTAURACION" up -d --wait db
   docker compose -p "$PROYECTO_RESTAURACION" ps db
   ~~~

   En [§3.2](#32-conexión-y-huella-reproducible) conecta primero a la base de mantenimiento del servidor aislado. Usa `localhost` y `ACADEX_DB_PORT` para la instancia de Compose. Crea una base vacía con nombre nuevo. Si el volcado contiene políticas que dependen de roles o extensiones externas, prepara esas dependencias desde el inventario autorizado antes de restaurar.

   ~~~bash
   DESTINO_DB='<BASE_NUEVA_DEL_ENSAYO>'
   createdb -W --template=template0 "$DESTINO_DB"
   export PGDATABASE="$DESTINO_DB"
   psql -X -W -v ON_ERROR_STOP=1 -c "SELECT current_database(), current_user; SELECT count(*) FROM pg_tables WHERE schemaname = 'public';"
   ~~~

   **Verificación:** base nueva y vacía, versión compatible y sin tráfico de la API. No uses la base original como destino.

2. Recupera la instantánea del repositorio externo al área cifrada y restaura el volcado en una transacción. Confirma mediante `restic ls` las rutas de los dos archivos.

   ~~~bash
   REPO_EXTERNO='<REPOSITORIO_EXTERNO_AUTORIZADO>'
   SNAPSHOT_EXTERNO='<ID_EXTERNO>'
   AREA='<DIRECTORIO_CIFRADO_EXISTENTE>'
   RESTAURACION=$(mktemp -d "$AREA/acadex-restauracion.XXXXXXXX")
   restic -r "$REPO_EXTERNO" ls "$SNAPSHOT_EXTERNO"
   restic -r "$REPO_EXTERNO" restore "$SNAPSHOT_EXTERNO" --target "$RESTAURACION" --verify
   test -s "$RESTAURACION/acadex.dump"
   test -s "$RESTAURACION/huella.tsv"
   pg_restore -W --exit-on-error --single-transaction --no-owner --no-privileges \
     --dbname="$PGDATABASE" "$RESTAURACION/acadex.dump"
   HUELLA="$RESTAURACION/huella-restaurada.tsv"
   ~~~

   **Verificación:** ejecuta el bloque de huella de [§3.2](#32-conexión-y-huella-reproducible) contra el destino nuevo y comprueba igualdad exacta antes de cualquier migración o cambio de datos.

   ~~~bash
   cmp "$RESTAURACION/huella.tsv" "$HUELLA"
   ~~~

3. Valida la revisión original, el catálogo y los permisos. Restituye propietarios, permisos y roles aprobados porque `--no-owner` y `--no-privileges` delegan esa tarea al administrador. Si el respaldo está en la revisión objetivo, ejecuta el SQL de [§6.3](#63-prueba-de-humo-y-verificación-de-esquema). Si requiere migración, verifica primero la huella y después aplica [§2.3](#23-migración-de-esquema-con-alembic). Cuando corresponda, restaura el bucket privado de ensayo y concilia el manifiesto con `archivos.ruta`.

4. Apunta la aplicación de ensayo a la base restaurada. Para la copia desechable local de los pasos anteriores, arranca el backend manualmente con el entorno Python de [§2.3](#23-migración-de-esquema-con-alembic) y un rol de aplicación de ensayo. El operador introduce la contraseña del rol y una clave de firma nueva mediante entradas ocultas. Usa TLS y la configuración de [§6.1](#61-variables-por-ambiente) si el ensayo emplea un destino remoto autorizado.

   ~~~bash
   # Desde backend/, con .venv activo, en una sesión con PGHOST y PGPORT del ensayo.
   export APP_ENV=development DB_SSLMODE=disable
   export DB_HOST="$PGHOST" DB_PORT="$PGPORT" DB_NAME="$DESTINO_DB"
   export DB_USER='<ROL_APP_ENSAYO>' ALGORITHM=HS256 ACCESS_TOKEN_EXPIRE_MINUTES=30
   read -rsp 'Contraseña de la cuenta de ensayo: ' DB_PASSWORD; printf '\n'
   read -rsp 'Clave de firma de ensayo: ' SECRET_KEY; printf '\n'
   export DB_PASSWORD SECRET_KEY
   export ATTACHMENTS_ENABLED=false PASSWORD_RESET_ENABLED=false
   export CORS_ORIGINS=http://localhost:5173 FRONTEND_URL=http://localhost:5173
   python -m uvicorn app.main:app --host localhost --port 8000
   ~~~

   En otra terminal, desde `frontend/` y con los puertos libres, ejecuta `corepack enable`, `pnpm install --frozen-lockfile` y `VITE_API_URL=http://localhost:8000 pnpm dev --host localhost --port 5173 --strictPort`. Si el Compose de instalación usa esos puertos en el mismo host, detenlo primero conservando su volumen. Repite el humo de [§6.3](#63-prueba-de-humo-y-verificación-de-esquema) y comprueba un dato sintético restaurado desde la interfaz.

   **Verificación:** conserva las dos huellas, conteos, resultado del humo y tiempo exacto. Bloquea aceptación si difieren las huellas o si falla cualquier prueba. Para recuperación real, redirige la API solo después de la autorización y las verificaciones. [Referencia de restauración de PostgreSQL](https://www.postgresql.org/docs/17/app-pgrestore.html) · [Restauración de restic](https://restic.readthedocs.io/en/stable/050_restore.html).

**Limitación conocida:** la copia local histórica acredita comparación estructural. Falta un resultado de restauración cifrada por un segundo equipo, con huellas y comparación contra el RTO.


## 4. Hosting y dominio

### 4.1 Ambientes y transferencia

| Ambiente o servicio | Tipo de hosting | Dirección del ambiente | Artefacto y transferencia |
| --- | --- | --- | --- |
| Desarrollo y simulacro local | Compose en host compatible con contenedores Linux | Interfaz `http://localhost:5173` y API `http://localhost:8000` con los puertos de ejemplo | Checkout de Git por HTTPS y build de imágenes a partir de los Dockerfiles |
| Frontend de producción | Cloudflare Pages, hosting estático | [Interfaz pública](https://acadex-2r2.pages.dev/) | El build Vite genera `dist/`. El procedimiento de nube usa Git y compilación del proveedor. |
| API de producción | Render, servicio gestionado con Docker | [Origen de API publicado en el frontend](https://acadex-b3ff.onrender.com) | La imagen reproducible se construye con `backend/Dockerfile`. Verifica si Render la construye desde Git o la descarga de un registro. |
| Datos y adjuntos de producción | PostgreSQL y Storage gestionados en Supabase | `<HOST_POSTGRESQL>` y `<ORIGEN_HTTPS_STORAGE>` | Alembic desde un operador autorizado. Copias lógicas cifradas y objetos por un canal autorizado. |

### 4.2 DNS, HTTPS y frontera de red

Pages sirve la interfaz por HTTPS. Render publica el origen HTTPS y enruta al puerto HTTP del proceso. Usa PostgreSQL remoto con TLS. Si se incorpora un dominio propio, registra zona, titular, nombre, tipo y destino del registro que exige cada proveedor. Verifica resolución, certificado, redirecciones y CORS antes de usarlo. Las reglas de publicación y acceso están en [§7.2](#72-frontera-de-acceso-y-secretos). [Dominios en Pages](https://developers.cloudflare.com/pages/configuration/custom-domains/) · [Servicios web de Render](https://render.com/docs/web-services#port-binding).

**Limitación conocida:** están identificados los subdominios públicos de la aplicación. Quedan por acreditar dominios propios, registros DNS, regiones, origen efectivo de la imagen, rama, versión y modo de publicación en cada servicio.

## 5. Plan de instalación y despliegue

### 5.1 Prerrequisitos y versión

El responsable de entrega registra el commit aprobado para ambos servicios, el commit anterior recuperable, la revisión Alembic objetivo y la ventana de cambio. Usa las herramientas de [§1.3](#13-matriz-y-verificación-de-requisitos), espacio para respaldos y accesos por rol a Git y al entorno de destino. Para una entrega nueva, sustituye los marcadores. Para un simulacro, usa una máquina y datos sintéticos independientes.

La última entrega registrada en Git se identifica en la cabecera. Los IDs de despliegue activos requieren confirmación del operador.

### 5.2 Servidor local con Compose

Ejecuta en Bash desde el host del simulacro. Los ejemplos de puertos suponen que estos están libres. Si cambias puertos, ajusta también los tres orígenes descritos en [§5.3](#53-nube-orden-de-instalación).

1. **Obtener la revisión.** Clona en una carpeta nueva y selecciona el commit de entrega.

   ~~~bash
   git clone https://github.com/brayan11-ga/Acadex.git acadex-ensayo
   cd acadex-ensayo
   git switch --detach '<COMMIT_APROBADO>'
   git rev-parse HEAD
   docker compose version
   ~~~

   **Verificación:** el hash coincide con el registro de entrega y Compose cumple el mínimo de [§1.3](#13-matriz-y-verificación-de-requisitos).

2. **Preparar configuración local.** Copia las plantillas en el clon nuevo y aplica los valores locales de [§6.1](#61-variables-por-ambiente). Sustituye las credenciales de ejemplo por valores exclusivos del entorno. Deja adjuntos locales desactivados para el arranque básico. Compose conecta el backend con Mailpit. Usa una terminal sin variables de producción.

   ~~~bash
   umask 077
   test -e .env || cp .env.example .env
   test -e backend/.env || cp backend/.env.example backend/.env
   docker compose config --quiet
   ~~~

   **Verificación:** no hay errores de configuración, el destino efectivo de PostgreSQL es el servicio `db` y los servicios se publican solo en la interfaz de loopback.

3. **Instalar con base vacía.** Usa un nombre de proyecto nuevo durante todo el ensayo. Si ya tienes una copia que debas restaurar, usa la instancia aislada y el procedimiento de [§3.4](#34-restaurar-y-verificar) antes de apuntar cualquier API a ella.

   ~~~bash
   PROYECTO='<NOMBRE_NUEVO_DEL_ENSAYO>'
   docker compose -p "$PROYECTO" up --build -d
   docker compose -p "$PROYECTO" ps -a
   docker compose -p "$PROYECTO" logs migrate
   ~~~

   **Verificación:** `db` queda saludable, `migrate` termina con código 0 y luego arrancan `backend` y `frontend`. Mailpit queda en ejecución. Conserva el nombre de proyecto para logs y limpieza.

4. **Comprobar API, esquema y persistencia.** Desde la raíz del clon:

   ~~~bash
   docker compose -p "$PROYECTO" exec -T db sh -c \
     'pg_isready -U "$POSTGRES_USER" -d "$POSTGRES_DB"'
   docker compose -p "$PROYECTO" exec -T db sh -c \
     'psql -X -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB" -f /database/verify_schema.sql'
   curl -fsS http://localhost:8000/health/live
   curl -fsS http://localhost:8000/health/ready
   curl -fsS -o /dev/null http://localhost:5173/
   ~~~

   **Verificación:** salud con `{"status":"ok"}` y todas las columnas de catálogo con `t`. Crea una tarea sintética. Ejecuta `docker compose -p "$PROYECTO" stop` y `docker compose -p "$PROYECTO" start`. Comprueba que la tarea persiste. Para retirar contenedores conservando el volumen usa `docker compose -p "$PROYECTO" down`. [Guía Docker](inicio-docker.md) · [Guía manual](inicio-manual.md).

### 5.3 Nube: orden de instalación

Este procedimiento propone una configuración compatible con el repositorio. El operador responsable registra los ajustes efectivos de los tres servicios antes de autorizar cada fase.

1. **Fijar los orígenes y proteger la ventana.** Identifica los dos orígenes HTTPS que se usarán. La interfaz necesita conocer la API durante el build mediante `VITE_API_URL`. A la vez, la API necesita el origen de la interfaz en `CORS_ORIGINS` y lo usa en `FRONTEND_URL` para los enlaces de recuperación. Resuelve la dependencia mutua reservando ambos orígenes antes de publicar. Mantén controlados los automatismos de publicación durante cambios de esquema. **Verificación:** cada valor contiene su origen previsto y `VITE_API_URL` carece del sufijo `/api/v1`.
2. **Preparar Supabase.** El administrador habilita el acceso PostgreSQL autorizado y TLS. Si se opera en modo producción, verifica bucket privado y credencial de servidor en [§6.1](#61-variables-por-ambiente). Para una base vacía, ejecuta `python -m alembic heads`, `python -m alembic upgrade head` y `python -m alembic current` desde el entorno de [§2.3](#23-migración-de-esquema-con-alembic), con la identidad de la nueva base comprobada. Para una base existente, aplica todo [§2.3](#23-migración-de-esquema-con-alembic), incluido el respaldo y el ensayo. **Verificación:** revisión objetivo, comprobaciones SQL y permisos aprobados antes de publicar la API.
3. **Construir y publicar Render.** Si el servicio construye desde Git, selecciona el commit aprobado y el runtime Docker. Con raíz del servicio en el repositorio, usa Dockerfile `./backend/Dockerfile` y contexto `./backend`. Si la raíz es `backend`, usa `./Dockerfile` y contexto `.`. En el host de ensayo se puede verificar la construcción con `docker build -f backend/Dockerfile -t acadex-backend:ensayo backend`. Configura las variables de [§6.1](#61-variables-por-ambiente) y el enrutamiento al puerto efectivo. El `CMD` versionado es `uvicorn app.main:app --host 0.0.0.0 --port 8000`. **Verificación:** el ID de despliegue corresponde al commit o imagen aprobados y pasan `/health/live` y `/health/ready`. [Docker en Render](https://render.com/docs/docker) · [Rutas relativas en Render](https://render.com/docs/monorepo-support#root-relative-settings).
4. **Construir y publicar Pages.** Conecta el proyecto al commit o rama aprobados. Usa `frontend/` como raíz, activa el gestor pnpm fijado y configura las variables públicas antes de compilar. En el build de Pages, asegúrate de que la fase de instalación respeta el lockfile o usa una instalación explícita sin duplicar la fase automática. Para reproducir el build en una terminal con Node.js 24, Corepack y los orígenes aprobados:

   ~~~bash
   cd frontend
   export VITE_API_URL='<ORIGEN_HTTPS_API>'
   export VITE_ATTACHMENTS_ENABLED=true
   corepack enable
   pnpm install --frozen-lockfile
   pnpm build
   test -s dist/index.html
   ~~~

   Configura `dist` como salida relativa a `frontend/`. **Verificación:** el build y la publicación corresponden al commit aprobado. Desde el navegador, recarga `/iniciarSesion` y verifica que el cliente llama al origen de API esperado. [Monorepos en Pages](https://developers.cloudflare.com/pages/configuration/monorepos/) · [Configuración de build](https://developers.cloudflare.com/pages/configuration/build-configuration/).

5. **Validar y cerrar la ventana.** Desde un cliente de verificación, ejecuta el humo de [§6.3](#63-prueba-de-humo-y-verificación-de-esquema) y registra versión, orígenes y resultado. Prueba los casos funcionales de [§10](#10-aceptación-y-entrega) en el ambiente de ensayo. **Verificación:** aplica los criterios de salida. Si falla una dependencia, suspende el corte y usa la ruta de recuperación de [§8](#8-pipeline-de-despliegue-y-monitoreo).

### 5.4 Costos de referencia y ventana

Estimación en USD para un servicio por componente, con tarifas consultadas el 21 de noviembre de 2026. El administrador aporta los planes activos y el consumo previsto.

| Componente | Escenario de referencia | Fuente |
| --- | --- | --- |
| Cloudflare Pages | USD 0 por peticiones a activos estáticos sin Functions. Aplica límites del plan. | [Precios de Pages](https://developers.cloudflare.com/pages/functions/pricing/) · [Límites](https://developers.cloudflare.com/pages/platform/limits/) |
| Render | Desde USD 7/mes por una instancia web Docker de pago de entrada. | [Hosting Docker de Render](https://render.com/hosting/docker) |
| Supabase | Desde USD 25/mes para Pro. | [Precios de Supabase](https://supabase.com/pricing) |
| Subtotal ilustrativo | Desde USD 32/mes. Añade uso extra, impuestos, correo, IA y copias externas si aplican. | Tarifas anteriores |

| Fase | Responsable | Tiempo que se registra en el ensayo |
| --- | --- | --- |
| Preparación y respaldo | Operador de plataforma y administrador de datos | Inicio, fin y tiempo de generar y recuperar la instantánea |
| Migración y publicación | Administrador de datos y operador de plataforma | Congelación de escrituras, revisión, despliegues y espera de salud |
| Verificación y cierre | Equipo de aceptación | Humo, revisión de permisos y decisión de activar o revertir |

## 6. Configuración y verificación

### 6.1 Variables por ambiente

Compose toma la interpolación de `.env` y configura los servicios. La API y Alembic leen variables del proceso y, si existe, `backend/.env` desde su directorio de trabajo. En modo manual, Vite toma `frontend/.env.local`. Los valores `VITE_*` son públicos y se incorporan al bundle durante el build. [Plantilla Compose](../.env.example) · [Plantilla backend](../backend/.env.example) · [Plantilla frontend](../frontend/.env.example) · [Validación](../backend/app/config/settings.py).

| Variable | ¿Secreto? | Desarrollo | Nube | Si falta o no coincide |
| --- | --- | --- | --- | --- |
| `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER` | No, datos de conexión restringidos | Compose fija host interno `db:5432`. En manual usa los de la instancia local. | Configuración protegida de Render y perfil de Alembic | Sin una variable obligatoria, la configuración del backend falla. Con un destino inválido, readiness y migración fallan. |
| `DB_PASSWORD` | Sí | `.env` local o `backend/.env` en manual | Secreto en Render y canal de migración | La autenticación contra la base falla o se usa el valor local de ejemplo si Compose conserva su sustitución. |
| `APP_ENV`, `DB_SSLMODE`, `DB_SSLROOTCERT` | No | `development`. En el migrador Compose se fija `disable` para la base local. | `production`. `require`, `verify-ca` o `verify-full` según la configuración. CA si el modo la requiere. | El entorno por defecto es desarrollo. Producción rechaza un modo que no exija TLS. Una CA ausente o incorrecta puede impedir la conexión. |
| `SECRET_KEY` | Sí | Genera un valor exclusivo de desarrollo. Compose ofrece un valor de ejemplo. | Secreto de Render, al menos 32 caracteres | La configuración de la API exige este campo. Un valor inválido en producción impide el arranque. |
| `ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES` | No | Plantillas: `HS256` y 30 minutos | Configuración de Render y perfil autorizado de migración | Campos obligatorios del backend. Cambios de firma o clave pueden invalidar sesiones. |
| `CORS_ORIGINS`, `FRONTEND_URL` | No | Origen local de la interfaz, por defecto `http://localhost:5173` | Orígenes HTTPS explícitos en Render. Usa el frontend aprobado para enlaces de recuperación. | Sin ajuste se conservan los defaults locales. Origen incorrecto bloquea el navegador. Con recuperación activa, producción exige `FRONTEND_URL` HTTPS. |
| `VITE_API_URL` | No | `.env` para Compose o `frontend/.env.local` en manual | Variable de build de Pages | El cliente falla al inicializar si falta. Una ruta añadida puede duplicar `/api/v1`. |
| `VITE_ATTACHMENTS_ENABLED` | No | `frontend/.env.local` para Vite manual. El Compose versionado pasa `VITE_API_URL` al frontend. | `true` en el build cuando la API ofrece adjuntos | La interfaz de adjuntos se oculta salvo que el valor sea `true`. |
| `ATTACHMENTS_ENABLED`, `ATTACHMENTS_STORAGE_BACKEND` | No | `false` y `local` para el arranque básico | `true` y `supabase` con `APP_ENV=production` | Producción rechaza el arranque si la combinación es incorrecta. |
| `SUPABASE_URL`, `SUPABASE_STORAGE_BUCKET` | No | Solo al probar Storage en un ambiente autorizado | Origen HTTPS del proyecto y bucket privado en Render | Producción valida la forma del origen. Un bucket erróneo o público falla en readiness. |
| `SUPABASE_SECRET_KEY` o `SUPABASE_SERVICE_ROLE_KEY` | Sí | Solo para un ensayo con Storage aislado | Solo en backend de Render | Producción requiere una de estas claves para adjuntos. |
| `PASSWORD_RESET_ENABLED`, `SMTP_HOST`, `SMTP_PORT`, `SMTP_STARTTLS`, `MAIL_FROM` | No | Mailpit en Compose. Desactiva la recuperación si el ensayo manual carece de SMTP. | Configuración de Render si se habilita recuperación | La función queda desactivada por defecto en el código. Con ella activa, producción exige host, remitente y STARTTLS. |
| `SMTP_USERNAME`, `SMTP_PASSWORD` | Contraseña sí | Vacíos para Mailpit | Credenciales del proveedor SMTP, si se usan | Cuando se usa autenticación SMTP con recuperación activa, deben configurarse juntos. |
| `GEMINI_API_KEY`, `GROQ_API_KEY` | Sí | Vacías en el entorno básico | Secretos de Render si se usan esas integraciones | Las funciones que dependen de la clave quedan indisponibles. |
| `GROQ_MODEL`, `GEMINI_USER_DAILY_LIMIT`, `GEMINI_GLOBAL_DAILY_LIMIT` | No | Defaults de la aplicación o valores de ensayo | Configuración de Render si se requiere ajustar la integración | Se aplican los defaults y validaciones del backend. |
| `ACADEX_DB_PORT`, `ACADEX_API_PORT`, `ACADEX_FRONTEND_PORT`, `ACADEX_MAILPIT_UI_PORT`, `ACADEX_MAILPIT_SMTP_PORT` | No | `.env` raíz | No aplican a servicios gestionados | Compose aplica sus puertos publicados por defecto. |

### 6.2 Servicios, dependencias y salud

| Servicio | Dependencia y verificación | Reinicio y logs |
| --- | --- | --- |
| Compose `db` | `pg_isready`. PostgreSQL interno `5432`, publicado en loopback `5433` por defecto. | Consulta `docker compose logs db`. |
| Compose `migrate` | Espera a `db` saludable, aplica `python -m alembic upgrade head` y termina con código 0. | Tarea de una sola ejecución por arranque de la secuencia. Conserva sus logs del ensayo. |
| Compose `backend` | Espera migración exitosa y Mailpit iniciado. `/health/ready` en `8000`. | Revisa logs de Uvicorn. |
| Compose `frontend` y `mailpit` | Vite verifica respuesta en `5173`. Mailpit publica interfaz `8025` y SMTP `1025`. | Consulta logs por servicio. |
| Cloudflare Pages y Render | Comprobar interfaz, ruta cliente y API desde un observador autorizado. | Consulta logs de build y del servicio. El plan de logs y el chequeo de Render se registran al validarlos en el panel. |

Compose carece de política explícita de reinicio y rotación de logs por servicio. Render puede usar un check HTTP si el operador lo configura. [Compose](../docker-compose.yml) · [Chequeos de Render](https://render.com/docs/health-checks).

### 6.3 Prueba de humo y verificación de esquema

Desde una terminal de verificación, sustituye los orígenes por los valores del ambiente de ensayo o del despliegue aprobado. Para Compose, usa los orígenes locales de [§4.1](#41-ambientes-y-transferencia).

~~~bash
FRONTEND='<ORIGEN_FRONTEND>'
API='<ORIGEN_API>'
curl -fsS -o /dev/null "$FRONTEND/"
curl -fsS -o /dev/null "$FRONTEND/iniciarSesion"
curl -fsS "$API/health/live"
curl -fsS "$API/health/ready"
curl -fsSi -X OPTIONS "$API/api/v1" \
  -H "Origin: $FRONTEND" -H 'Access-Control-Request-Method: GET' \
  -H 'Access-Control-Request-Headers: Authorization, Content-Type'
~~~

**Verificación:** ambas páginas y ambas rutas de salud devuelven HTTP 200. Los endpoints de salud responden `{"status":"ok"}`. El preflight incluye `Access-Control-Allow-Origin` para el origen indicado. El navegador completa la carga y hace peticiones a la API. `/health/live` comprueba el proceso. `/health/ready` consulta PostgreSQL, objetos concretos y el bucket cuando corresponde. Si falla esa dependencia, devuelve `503`. Verifica aparte `python -m alembic current` y ejecuta desde la raíz `psql -X -v ON_ERROR_STOP=1 -f database/verify_schema.sql` contra la base aprobada. El SQL cubre objetos específicos, y la comparación de catálogo de [§2.3](#23-migración-de-esquema-con-alembic) cubre el esquema de la entrega. [Salud de la API](../backend/app/main.py) · [SQL de verificación](../database/verify_schema.sql).

En ensayo aislado, ejecuta en `frontend/` `pnpm lint`, `pnpm build` y `pnpm test --run`. Para backend aplica las suites de [Calidad y pruebas](calidad-y-pruebas.md), con la base efímera del Compose de pruebas para la integración. Registra el resultado de los casos de [§10.2](#102-casos-de-aceptación) antes de decidir el corte.

## 7. Seguridad, usuarios y permisos

### 7.1 Matriz de roles

| Capa y rol | Acceso y permisos | Estado |
| --- | --- | --- |
| Usuario Acadex | Sesión con JWT Bearer y acceso a operaciones de su cuenta y sus tareas conforme a las reglas de API | Implementado en el código |
| Integrante y líder de grupo | El integrante ve asignaciones autorizadas. Las operaciones restringidas verifican el liderazgo de ese grupo. La dependencia de autorización contempla al administrador. | Implementado en el código |
| Administrador Acadex | Operaciones administrativas detrás de `es_admin`. En desarrollo se puede crear o promover con `docker compose exec -it backend python -m scripts.crear_admin`. | Script interactivo y control de API versionados |
| Operador del host o plataforma | Acceso individual a Docker local o a los paneles por función. Para los servicios gestionados, administra despliegues y acceso por panel. | Accesos efectivos por registrar |
| Rol PostgreSQL de aplicación | Propuesta: acceso a tablas y secuencias necesarias y sujetos a reglas efectivas. Restringir DDL y administración. | Privilegios de nube sin demostrar |
| Rol PostgreSQL de migración | Propuesta: control de los objetos del esquema necesarios para Alembic y sus migraciones, con acceso temporal. | Propiedad y permisos por verificar |
| Rol PostgreSQL de respaldo | Propuesta: lectura completa del alcance de copia, incluyendo el efecto de RLS, sin permisos de escritura. | Permisos por verificar |

El frontend conserva el token de acceso en `localStorage` y lo adjunta como `Authorization: Bearer`. La API verifica el algoritmo, la firma, la identidad y los permisos. Comprueba privilegios con roles sintéticos en ensayo. El usuario común debe recibir rechazo en operaciones administrativas y de liderazgo ajenas. El rol de aplicación de PostgreSQL debe poder hacer las operaciones necesarias, pero carecer de privilegios de propietario y de creación del esquema. Verifica la condición con consultas al catálogo como `has_schema_privilege(current_user,'public','CREATE')` y la propiedad efectiva de las tablas. Comprueba RLS con los roles reales de cada operación, no a través de un superusuario. [Autenticación y autorización](../backend/app/dependencies/auth.py) · [JWT](../backend/app/core/security.py) · [Cliente HTTP](../frontend/src/services/api.ts) · [Alta de administrador](../database/README.md#crear-o-promover-un-administrador).

### 7.2 Frontera de acceso y secretos

Compose publica puertos de desarrollo en loopback y el equipo administra el firewall de su host. En nube, usa los orígenes HTTPS del proveedor y las reglas de acceso de PostgreSQL y Storage. Configura orígenes CORS específicos. Conserva el bucket privado y expón los adjuntos solo mediante la API autorizada. **Limitación conocida:** reglas de red o firewall del proveedor, RLS efectiva y pruebas de privilegios de producción carecen de evidencia operativa. [Compose](../docker-compose.yml) · [Acceso a Storage](https://supabase.com/docs/guides/storage/security/access-control).

| Secreto | Custodia y lectores por rol | Rotación propuesta |
| --- | --- | --- |
| `DB_PASSWORD` para cada rol | Gestor de secretos. Render recibe la credencial de aplicación. Operadores autorizados reciben la credencial de migración o respaldo durante su tarea. | Actualiza consumidor, verifica conexión y revoca la credencial anterior. |
| `SECRET_KEY` | Exclusiva del backend. Acceso del responsable de autenticación y del operador durante cambios. | Acordar ventana por invalidación de tokens y comprobar nuevo inicio de sesión. |
| Clave privada de Supabase Storage | Solo backend de Render. Administrador de datos y operador de plataforma. | Cambiar clave, verificar bucket y API, retirar la anterior. |
| `SMTP_PASSWORD` y claves de IA | Solo en el backend donde esté activa la integración. | Rotar por servicio y probar la integración en ensayo. |
| Credenciales de restic y accesos de operadores | Gestor protegido. Acceso de escritura al operador de copias y de lectura al equipo de restauración. | Rotar o revocar al cambiar responsables y verificar acceso de recuperación. |

Genera valores distintos por ambiente. Mantén archivos privados, secretos y tokens fuera de Git, del navegador y de registros compartidos. Los Dockerfiles se construyen con las exclusiones de sus contextos. [Exclusiones backend](../backend/.dockerignore) · [Exclusiones frontend](../frontend/.dockerignore).

## 8. Pipeline de despliegue y monitoreo

### 8.1 CI versionada

| Workflow | Disparo | Etapas comprobables |
| --- | --- | --- |
| [`ci.yml`](../.github/workflows/ci.yml) | PR hacia `develop` o `main` | Frontend: instalación con lockfile, lint, build y Vitest. Backend: pytest sin PostgreSQL. Integración: PostgreSQL efímero, migraciones y suites de API e integración. |

~~~mermaid
flowchart LR
    Pr["PR a develop o main"] --> Front["Lint, build y Vitest"]
    Pr --> Unit["Pytest sin PostgreSQL"]
    Pr --> Integracion["Alembic y pruebas con PostgreSQL efímero"]
~~~

El workflow tiene permisos de lectura de contenido. Sus credenciales de prueba son sintéticas. El repositorio carece de workflow de publicación, rollback y monitoreo continuo. **Limitación conocida:** la configuración de despliegues automáticos, ramas protegidas y revisores de producción se acredita con el estado de GitHub y de los paneles. Registra enlace de CI, commit, resultado, duración e IDs de cada despliegue antes de aceptar una entrega.

### 8.2 Rollback por componente

| Componente | Acción en una intervención autorizada | Verificación |
| --- | --- | --- |
| Pages | Selecciona en Deployments el despliegue de producción anterior aprobado y ejecuta el rollback. Verifica que incluya el origen correcto de API. | Bundle, ruta interna y conexión desde el navegador. [Rollback de Pages](https://developers.cloudflare.com/pages/configuration/rollbacks/) |
| Render | En la lista de despliegues, selecciona el artefacto anterior aprobado. Antes de confirmar, comprueba compatibilidad con el esquema y las variables de entorno actuales. | ID de despliegue, salud y operación sintética. [Rollback de Render](https://render.com/docs/rollbacks) |
| PostgreSQL y Storage | Ante un cambio incompatible, suspende escrituras. Restaura una base y bucket alternos conforme a [§3](#3-plan-de-respaldo-y-restauración), o aplica una corrección de esquema aprobada. Decide cómo conciliar datos nuevos antes de redirigir. | Huellas, revisión, permisos y humo desde el destino recuperado. |
| Compose | Detén el proyecto, selecciona la revisión aprobada en un checkout separado y verifica compatibilidad del volumen. Si hace falta, recupera en un volumen de ensayo distinto antes del cambio. | Verifica el proyecto, la revisión y la persistencia antes de abrir tráfico. |

### 8.3 Monitoreo

Compose implementa verificaciones locales de PostgreSQL, backend y frontend. FastAPI expone `/health/live` y `/health/ready`. Falta evidencia de un monitor externo, alertas, destinatarios o chequeo HTTP activo de Render.

| Propuesta | Señal | Acción |
| --- | --- | --- |
| Salud externa | HTTPS de Pages, `/health/live` y `/health/ready` de API | Registra línea base, umbral, canal y evidencia de una alerta de prueba. |
| Operación | Errores de aplicación, latencia y fallo de build | Correlaciona versión y hora con logs de proveedor sin volcar secretos. |
| Recuperación | Antigüedad de la última copia verificable y resultado del ensayo | Abre incidente si se supera el RPO aprobado o se pierde la capacidad de restaurar. |

## 9. Mantenimiento, soporte y capacitación

### 9.1 Calendario propuesto

| Cuándo | Tarea | Responsable y evidencia |
| --- | --- | --- |
| Diario y antes de migrar | Revisar última copia y salud de servicios | Operador de respaldo y soporte. ID de copia y resultado de salud. |
| Tras cada entrega | Revisar logs, esquema y tasa de errores | Operador de plataforma. Commit, enlaces, humo y decisión de cierre. |
| Mensual | Ensayar recuperación aislada y revisar dependencias | Administrador de datos y desarrollo. Huellas, tiempo vs RTO e inventario de cambios. |
| Trimestral y al cambiar responsables | Revisar accesos, secretos y contactos | Operador y responsable de seguridad. Accesos revisados, revocaciones y prueba de continuidad. |

### 9.2 Soporte y respuesta

| Nivel | Atiende | Ruta de escalamiento |
| --- | --- | --- |
| N0 | Persona usuaria | Consulta [Inicio y diagnóstico](../README.md#si-algo-falla) y la guía del ambiente. |
| N1 | Soporte | Registra versión, impacto, reproducción, hora y evidencia depurada. Usa las [plantillas de incidencias](../.github/ISSUE_TEMPLATE). |
| N2 | Plataforma o datos | Comprueba salud, dependencias, logs, conectividad y opciones de recuperación. |
| N3 | Desarrollo | Reproduce en un entorno aislado, corrige y prepara una entrega revisable. [Flujo de contribución](../CONTRIBUTING.md#5-haz-cambios-pequeños-y-compruébalos). |

| Incidente | Guía operativa |
| --- | --- |
| `/health/live` falla | Identifica la entrega del backend, revisa estado, puerto y arranque. Si el artefacto falla, aplica [§8.2](#82-rollback-por-componente). |
| `/health/ready` devuelve 503 | Distingue conexión, objetos faltantes y Storage en respuesta y logs. Comprueba identidad, revisión y permisos. Detén el corte si el esquema no coincide. |
| El navegador no llega a la API | Comprueba origen del bundle, permisos CORS y ruta interna. Corrige el origen autorizado y recompila la interfaz si cambió su variable de build. |
| Copia ausente o huellas distintas | Conserva origen y evidencia. Suspende corte, verifica el ID y repite [§3.4](#34-restaurar-y-verificar) en una base vacía. |

**Limitación conocida:** faltan horario de atención, responsables asignados, canal de incidentes y tiempos acordados de primera respuesta y resolución por severidad.

### 9.3 Capacitación y ayudas

| Público | Práctica propuesta | Evidencia |
| --- | --- | --- |
| Personas usuarias | Registrar cuenta sintética, iniciar sesión, crear tarea y revisar asignaciones en el ambiente de ensayo. | Lista de tareas completadas y preguntas. [Requisitos funcionales](RF/README.md). |
| Líderes y administración Acadex | Crear grupo y asignar tarea. Validar acceso del líder y rechazo del integrante sin privilegios. | Casos A03 y A04 de [§10.2](#102-casos-de-aceptación). |
| Soporte y operación | Resolver un fallo simulado de origen CORS o readiness, verificar esquema y hacer una restauración aislada. | Registro de diagnóstico y restauración. [Inicio Docker](inicio-docker.md) · [Calidad y pruebas](calidad-y-pruebas.md). |

## 10. Aceptación y entrega

### 10.1 Criterios de entrada y salida

Antes de ejecutar, el responsable de entrega y el equipo receptor acuerdan alcance, requisitos, versión, datos sintéticos, límite de tiempo del gate, RPO/RTO y responsables de firma. La prueba de humo comprueba que el servicio está operativo. La aceptación comprueba los flujos acordados y su evidencia.

Clasifica defectos como bloqueante, mayor, menor o cosmético. Para cerrar, exige gate superado, casos críticos aprobados, cero bloqueantes o mayores abiertos y tratamiento acordado de las observaciones restantes. **Estado de aceptación: sin ejecución del gate ni decisión firmada.**

### 10.2 Casos de aceptación

| ID y requisitos | Dado | Cuando | Entonces | Resultado |
| --- | --- | --- | --- | --- |
| A01 · [RF-001](RF/RF-001.md), [RF-023](RF/RF-023.md) | Cuenta sintética sin registrar | Completa el registro e inicia sesión | Se crea la cuenta y la sesión da acceso al panel | Sin ejecutar |
| A02 · [RF-003](RF/RF-003.md), [RNF-017](RNF/RNF-017.md) | Sesión válida y datos sintéticos | Crea una tarea y recarga la vista en Chrome y Edge | La tarea aparece y persiste con los campos guardados | Sin ejecutar |
| A03 · [RF-036](RF/RF-036.md), [RF-038](RF/RF-038.md) | Grupo con líder e integrante | El líder asigna una tarea y el integrante lista sus asignaciones | Se guarda la asignación y aparece para el integrante seleccionado | Sin ejecutar |
| A04 · [RF-053](RF/RF-053.md), [RF-058](RF/RF-058.md), [RNF-023](RNF/RNF-023.md) | Integrante sin liderazgo y usuario común sin rol administrador | Intenta abrir el panel de líder, crear o asignar una tarea grupal, expulsar un integrante, eliminar el grupo y ejecutar una operación administrativa | La interfaz restringe el acceso y la API rechaza las acciones sin modificar el grupo ni los datos | Sin ejecutar |
| A05 · [RF-002](RF/RF-002.md) | Entorno de ensayo con adjuntos y un archivo sintético válido | Adjunta y descarga como usuario autorizado. Repite acceso con otra cuenta sin permiso. | El archivo conserva su huella y se rechaza el acceso no autorizado | Sin ejecutar |
| A06 · [RNF-009](RNF/RNF-009.md) | Observación externa y periodo previamente acordados | Registra disponibilidad durante ese periodo | Se calcula el porcentaje y se compara con el 99 % indicado por el requisito | Medición sin ejecutar |

### 10.3 Simulacro cruzado y registro

1. Entrega a otro equipo este plan, el commit, el material sintético y acceso de lectura a una copia cifrada. El observador inicia el cronómetro. El equipo instalador opera en un entorno vacío sin asistencia técnica del equipo autor.
2. Instala desde cero mediante [§5.2](#52-servidor-local-con-compose), restaura según [§3.4](#34-restaurar-y-verificar) y verifica humo, huellas, esquema y permisos. Registra tiempos y desviaciones mientras ocurren. Si necesita una instrucción no documentada para completar el recorrido, registra intento fallido.
3. Compara tiempos con el límite acordado y el RTO. Si servicios, huellas, humo o tiempos fallan, corrige el plan y repite con otro equipo. Registra y comparte las lecciones de la instalación y restauración.

| Campo de verificación | Evidencia que se incorpora |
| --- | --- |
| Roles y fecha | Equipo instalador, observador, responsable de entrega y fecha |
| Identidad | Versión del plan, commit, SO, herramienta de verificación y versión principal de PostgreSQL |
| Tiempo | Inicio, fin, duración de instalación y restauración, límite y RTO acordados |
| Resultado técnico | Servicios sanos, salida de humo, huellas y revisión Alembic |
| Resultado funcional | ID de caso, resultado, defecto, severidad, decisión y responsable |
| Desviaciones | Paso, corrección, versión del plan afectada y resultado de la repetición |
| Firmas | Validación por rol del observador y de los equipos |

### 10.4 Acta y entrega

| Entregable | Referencia o estado |
| --- | --- |
| Plan y procedimientos | Este documento versionado |
| Registro firmado del simulacro | Sin emisión. Incorporar `<ENLACE_AL_REGISTRO_FIRMADO>` después del ensayo. |
| Acta de entrega | Sin emisión. Incorporar `<ENLACE_AL_ACTA_FIRMADA>` después del gate. |
| Ayudas y soporte | Guías de inicio, respuesta a incidentes de [§9.2](#92-soporte-y-respuesta) y canales acordados con recepción |
| Transferencia de accesos | Proveedores, dominio, repositorio y custodia de copias por rol. Transferir por canal seguro y registrar recepción. |

El acta debe incluir el alcance y ambientes, resultados y defectos, desviaciones corregidas, compromisos verificables de disponibilidad y soporte, RPO/RTO, mantenimiento, garantía si se acuerda y firmas por rol. La socialización presenta los resultados, tiempos, huellas, incidencias y próxima acción. Los registros compartidos excluyen credenciales y datos personales.
