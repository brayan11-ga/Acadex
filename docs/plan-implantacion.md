# Plan de implantación de Acadex

| Campo | Valor |
| --- | --- |
| Aplicación | Gestión de tareas académicas individuales y grupales |
| Repositorio | [brayan11-ga/Acadex](https://github.com/brayan11-ga/Acadex) |
| Alcance | Instalación local, despliegue, operación y aceptación |
| Revisión del plan | 21 de noviembre de 2026, [issue #63](https://github.com/brayan11-ga/Acadex/issues/63) |

**Comprobado** indica evidencia en archivos versionados, en el contexto confirmado de la issue o en los recursos públicos indicados. **Procedimiento documentado** indica pasos para una intervención futura. **Recomendación** identifica una propuesta operativa. **Pendiente** identifica evidencia o decisiones que debe aportar el equipo.

Estructura adaptada del [plan de implantación de referencia](https://github.com/ergrato-dev/bc-implantacion/blob/main/referencia/docs/plan-implantacion.md). Esta revisión se limitó a inspección del repositorio y consultas públicas de lectura.

## 1. Ficha técnica y requisitos mínimos

| Entorno | Requisitos comprobados |
| --- | --- |
| Local con Docker | Git, Docker compatible con contenedores Linux y Compose 2.24.0 o posterior. Compose usa PostgreSQL 17.11 y Mailpit. [Inicio con Docker](inicio-docker.md) |
| Local manual | Git, Python 3.14, Node.js 24, Corepack, pnpm 12.11.2 y PostgreSQL 17, según la guía del proyecto. [Inicio manual](inicio-manual.md) |
| Producción gestionada | Para operar el despliegue se requiere acceso autorizado a Cloudflare Pages, Render y Supabase, además de la revisión de Git que se vaya a publicar. |

**Comprobado.** El frontend usa React, TypeScript y Vite. El backend usa FastAPI y SQLAlchemy. Su imagen parte de `python:3.14.8-slim`. El Dockerfile del frontend usa `node:24-alpine` para servir Vite en desarrollo. Estas versiones proceden del repositorio. [Dockerfile backend](../backend/Dockerfile), [Dockerfile frontend](../frontend/Dockerfile), [package.json](../frontend/package.json).

**Pendiente.** Confirmar recursos contratados, límites de los planes y dimensionamiento según la carga. Las guías locales no fijan mínimos de CPU, RAM ni disco.

## 2. Arquitectura y componentes desplegados

**Comprobado.** El navegador carga la interfaz de Cloudflare Pages y envía peticiones HTTPS a FastAPI en Render bajo `/api/v1`. FastAPI conecta con PostgreSQL en Supabase. Alembic mantiene el esquema mediante un proceso separado del arranque de la API. [Arquitectura](arquitectura.md), [Adopción de Alembic](DESPLIEGUE_ALEMBIC.md).

Con `APP_ENV=production`, el código exige adjuntos habilitados y Supabase Storage. PostgreSQL guarda las referencias a los objetos y FastAPI gestiona el acceso al bucket privado. El correo y los proveedores de IA dependen de la configuración del backend. [Configuración del backend](../backend/README.md), [Diseño de adjuntos](../backend/migrations/README.md#archivos-adjuntos).

Para desarrollo, [Docker Compose](../docker-compose.yml) crea su propia base, ejecuta el servicio `migrate` y publica los servicios en la interfaz local. Mailpit captura correo de desarrollo.

## 3. Hosting, servicios y dominio

| Servicio | Estado comprobado y evidencia |
| --- | --- |
| Cloudflare Pages | El perfil del repositorio enlaza la [interfaz publicada](https://acadex-2r2.pages.dev/). Una consulta HTTPS devolvió HTTP 200 y el título «Acadex». |
| Render | La issue confirma el uso de Docker. Los recursos públicos de la interfaz incluyen el [origen de la API](https://acadex-b3ff.onrender.com). |
| Supabase | PostgreSQL aloja los datos de producción, según la [guía de datos](../database/README.md#producción-y-evidencia-histórica) y la issue. |

**Pendiente.** Confirmar en los paneles los dominios canónicos y personalizados, DNS, certificados, regiones, planes y estado de las integraciones. Las direcciones anteriores son subdominios de proveedor observados públicamente.

## 4. Plan de instalación y despliegue

**Procedimiento documentado para desarrollo.** Sigue [Inicio con Docker](inicio-docker.md) o [Inicio manual](inicio-manual.md). Ambos usan PostgreSQL local. Los archivos de ejemplo de la [raíz](../.env.example), [backend](../backend/.env.example) y [frontend](../frontend/.env.example) documentan la configuración local.

**Procedimiento documentado para una entrega autorizada.**

1. Registra el commit de la entrega y valida sus cambios según [Calidad y pruebas](calidad-y-pruebas.md). Confirma los ajustes de los proveedores y ensaya en un entorno aislado antes de intervenir en producción.
2. Verifica que el esquema de Supabase sea compatible con la entrega. Si hay migraciones pendientes, sigue la [sección de Alembic](#6-migración-de-datos-mediante-alembic) antes de publicar código que dependa de ellas.
3. En Render, comprueba el origen de la imagen y el puerto. Para construir desde el repositorio, el contexto debe ser `backend/`. El [Dockerfile](../backend/Dockerfile) toma `requirements.txt` del contexto y copia su contenido a `/app`. Con **Root Directory** en `backend`, usa **Dockerfile Path** `./Dockerfile` y **Docker Build Context** `.`. Con la raíz en el repositorio, las rutas equivalentes son `./backend/Dockerfile` y `./backend`. El `CMD` arranca Uvicorn en `0.0.0.0:8000` sin ejecutar Alembic. Verifica que Render enrute al puerto efectivo. [Docker en Render](https://render.com/docs/docker), [rutas del monorepo](https://render.com/docs/monorepo-support#root-relative-settings), [puerto del servicio](https://render.com/docs/web-services#port-binding).
4. En Cloudflare Pages, la configuración compatible con el repositorio usa `frontend/` como raíz, `pnpm install --frozen-lockfile` para instalar dependencias, `pnpm build` para compilar y `dist/` como salida relativa. Prepara las variables públicas antes de compilar. Publica la interfaz tras verificar la API. [Scripts del frontend](../frontend/README.md#scripts-disponibles), [monorepos en Pages](https://developers.cloudflare.com/pages/configuration/monorepos/), [configuración de build](https://developers.cloudflare.com/pages/configuration/build-configuration/).

**Pendiente.** Confirmar la rama y el commit activos en cada proveedor. En Render, comprobar origen de la imagen, raíz, Dockerfile, contexto, puerto y posibles comandos de arranque o predespliegue. En Pages, comprobar raíz, versiones de herramientas, instalación, comando y directorio de salida. Las configuraciones anteriores se deducen del repositorio y de la documentación de los proveedores.

## 5. Configuración y verificación

| Dónde | Configuración que se debe verificar |
| --- | --- |
| Cloudflare Pages | `VITE_API_URL` contiene solo el origen HTTPS de la API. El cliente añade `/api/v1`. Alinea `VITE_ATTACHMENTS_ENABLED` con el backend. Los cambios de variables requieren compilar de nuevo. [Configuración pública](../frontend/README.md#configuración-pública) |
| Render, API | `APP_ENV=production`, `CORS_ORIGINS` con los orígenes HTTPS explícitos, `FRONTEND_URL` y parámetros de autenticación `SECRET_KEY`, `ALGORITHM` y `ACCESS_TOKEN_EXPIRE_MINUTES`. |
| Render, PostgreSQL | `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER` y `DB_PASSWORD`. El código arma la conexión a partir de estos campos. En producción `DB_SSLMODE` debe exigir TLS. Comprueba `DB_SSLROOTCERT` si el modo elegido lo necesita. |
| Render, integraciones | Comprueba `ATTACHMENTS_ENABLED`, `ATTACHMENTS_STORAGE_BACKEND`, `SUPABASE_URL`, `SUPABASE_STORAGE_BUCKET` y `SUPABASE_SECRET_KEY` o la clave heredada `SUPABASE_SERVICE_ROLE_KEY`. Si se habilita recuperación de contraseña, verifica SMTP con STARTTLS. Confirma aparte el proveedor de IA habilitado. |

Las validaciones efectivas están en [settings.py](../backend/app/config/settings.py). Los valores activos de los paneles quedan pendientes de confirmar sin exponer secretos.

**Procedimiento de verificación.** Registra entorno, commit y resultado de cada comprobación.

1. Abre la interfaz por HTTPS y recarga una ruta interna. Comprueba que las peticiones del navegador llegan al origen de la API y que CORS admite el origen de la interfaz.
2. Comprueba HTTP 200 en `/health/live` y `/health/ready`. El primero comprueba que FastAPI responde. El segundo consulta PostgreSQL, algunos objetos del esquema y el bucket privado cuando corresponde. Comprueba por separado la revisión Alembic. [Implementación de salud](../backend/app/main.py).
3. Usa cuentas y datos sintéticos en el entorno de ensayo para las operaciones de aceptación. Guarda resultados sin credenciales, tokens, correos ni datos personales.

## 6. Migración de datos mediante Alembic

**Comprobado.** La cadena de [revisiones versionadas](../backend/alembic/versions) termina en `20261018_01` en la revisión auditada. [Alembic](../backend/alembic/env.py) comparte conexión con la API y registra el historial en `public.alembic_version`. El estado actual de Supabase queda pendiente.

**Procedimiento documentado.** Desde `backend/`, compara `python -m alembic heads` con `python -m alembic current` en el destino autorizado. Ensaya `python -m alembic upgrade head` sobre una copia aislada y compara esquema, restricciones y conteos acordados. Con respaldo restaurable y resultado aprobado, ejecuta la migración una vez desde un proceso controlado. Verifica la revisión y el esquema antes de desplegar la API que requiera el cambio. [Orden y verificaciones de producción](DESPLIEGUE_ALEMBIC.md#aplicar-migraciones-nuevas-en-producción), [comprobaciones de esquema](../database/verify_schema.sql).

Si encuentras tablas sin historial, detén el despliegue y sigue la guía de adopción. `stamp` registra una revisión sin aplicar SQL y requiere comparar primero el esquema completo. Si falla una migración o cambia la compatibilidad, evalúa una corrección revisada o la recuperación desde una copia verificada. Revisa el posible efecto sobre escrituras posteriores al respaldo. [Recuperación](DESPLIEGUE_ALEMBIC.md#recuperación).

## 7. Respaldo y restauración de PostgreSQL

**Procedimiento documentado.** Antes de una intervención, confirma qué respaldos administrados ofrece el plan de Supabase y qué alcance tienen. Para un volcado lógico del esquema `public` de Acadex, la guía de adopción documenta `pg_dump` y `pg_restore`. Guarda la copia fuera de Git, con acceso restringido, y registra origen, fecha, alcance y revisión de Alembic. Revisa por separado roles, permisos, extensiones y cualquier objeto fuera de `public`. [Guía de adopción](DESPLIEGUE_ALEMBIC.md#procedimiento-recomendado), [copias administradas de Supabase](https://supabase.com/docs/guides/platform/backups).

Restaura primero en una instancia aislada y compatible con la versión principal de PostgreSQL de origen. Verifica esquema, revisión de Alembic, conteos permitidos y disponibilidad de la aplicación. Ensaya también los permisos con el rol de aplicación. Para recuperar producción, acuerda el punto de recuperación y la ventana de intervención antes de redirigir la API a una base restaurada y verificada. [Restauración en entorno local](https://supabase.com/docs/guides/local-development/restoring-downloaded-backup).

**Recomendación.** Define una copia y un ensayo separados para los objetos de Storage. La copia de PostgreSQL conserva referencias a esos objetos, mientras que los binarios pertenecen al bucket. Comprueba que las referencias y los objetos restaurados coincidan.

**Pendiente.** Confirmar responsable, calendario, retención, última copia recuperable, pérdida de datos admisible (RPO), tiempo objetivo de recuperación (RTO) y disponibilidad de recuperación a un punto en el tiempo. Adjunta evidencia de un nuevo ensayo en la [issue #34](https://github.com/brayan11-ga/Acadex/issues/34). La [evidencia histórica](DESPLIEGUE_ALEMBIC.md#evidencia-histórica-y-estado-a-verificar) corresponde a una copia anterior.

## 8. Seguridad, usuarios, permisos y secretos

**Comprobado.** La API autentica con token de acceso y comprueba permisos administrativos y de liderazgo de grupo. La [guía de datos](../database/README.md#crear-o-promover-un-administrador) documenta la creación o promoción de un administrador en local. En producción, el código exige una `SECRET_KEY` de al menos 32 caracteres, CORS con HTTPS y conexión PostgreSQL con TLS. [Autorización en la API](../backend/app/dependencies/auth.py), [validación de producción](../backend/app/config/settings.py).

**Recomendación.** Usa cuentas individuales y mínimo privilegio en los proveedores. Separa permisos de operación, migración y respaldo. Restringe las claves privadas al backend o al proceso autorizado y mantenlas fuera de Git, del navegador, de logs y de capturas. Limita `VITE_*` a datos públicos. Mantén los archivos de entorno privados fuera del contexto de construcción. Revisa permisos y seguridad por fila (RLS) con los roles efectivos de Supabase. [Exclusiones de la imagen backend](../backend/.dockerignore).

**Pendiente.** Confirmar responsables de cuentas, roles y permisos efectivos en los proveedores, políticas activas de RLS, custodia, rotación y revocación de secretos.

## 9. CI/CD, monitoreo y mantenimiento

**Comprobado.** El workflow de GitHub Actions se activa en PR hacia `develop` o `main`. Ejecuta lint, build y Vitest para frontend, pytest sin PostgreSQL y migraciones y pruebas contra PostgreSQL aislado para backend. El archivo versionado define tareas de CI. [Workflow de CI](../.github/workflows/ci.yml), [alcance de CI](calidad-y-pruebas.md#qué-ejecuta-ci).

**Recomendación.** Usa la evidencia de CI como control previo a la publicación. Registra el commit de cada servicio y verifica compatibilidad del esquema antes de volver a una versión previa. Supervisa el frontend, `/health/live`, `/health/ready`, errores y logs de la API, y resultados de copias y restauraciones. Si se habilita el chequeo HTTP de Render, evalúa `/health/ready` como ruta. Acuerda responsables y frecuencia para revisar incidencias, dependencias, accesos y respaldos. [Chequeos de Render](https://render.com/docs/health-checks).

**Pendiente.** Verificar despliegues automáticos y reglas de ramas o rutas en cada proveedor, chequeo de salud configurado, alertas, destinatarios y calendario de mantenimiento.

## 10. Soporte, capacitación y aceptación

**Procedimiento documentado de soporte.** Usa las [plantillas de GitHub](../.github/ISSUE_TEMPLATE) y el flujo de [CONTRIBUTING](../CONTRIBUTING.md). Registra entorno, versión, impacto, pasos de reproducción y evidencia depurada. Deriva incidencias de infraestructura al responsable del servicio y las de aplicación al equipo de desarrollo.

**Recomendación de capacitación.** Practica con usuarios de ensayo el acceso, las tareas propias, los grupos y los adjuntos. Para el equipo técnico, recorre las guías locales, la verificación de la API, el ensayo de migración y la restauración aislada.

**Criterios propuestos de aceptación.** Registra resultado, evidencia y responsable para cada punto.

- Interfaz accesible por HTTPS y comunicación con la API desde el navegador. Ambos endpoints de salud responden como se espera.
- Registro e inicio de sesión, creación de tarea y flujo grupal completados en ensayo. Un usuario sin permiso recibe el rechazo previsto. Las integraciones aprobadas tienen evidencia de su prueba. [Requisitos funcionales](RF/README.md), [requisitos no funcionales](RNF/README.md).
- Revisión del esquema compatible con la entrega, restauración ensayada y capacidad de recuperación revisada.
- Entrega documentada con commits de frontend y backend, dominios, responsables, pendientes y decisión de aceptación. Incluye la referencia a un simulacro de instalación desde cero cuando se complete. [Issue #33](https://github.com/brayan11-ga/Acadex/issues/33).

**Pendiente.** Acordar canal y tiempos de soporte, responsables de capacitación y aceptación, y adjuntar resultados, incidencias y acta de entrega.
