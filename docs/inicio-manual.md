# Inicio manual y base local

Esta ruta ejecuta PostgreSQL, backend y frontend directamente en tu equipo. No usa Docker. Los ejemplos de preparación de PostgreSQL usan PowerShell en Windows; los comandos de la aplicación también incluyen activación de Python en Bash.

## 1. Comprueba los requisitos

Instala Git, Python 3.14, Node.js 24, Corepack y PostgreSQL 17. El repositorio fija pnpm 12.11.2 en `frontend/package.json`. Estas versiones de Python, Node y PostgreSQL siguen las imágenes del proyecto.

Desde la raíz de `Acadex/`:

```sh
python --version
node --version
corepack --version
psql --version
pg_ctl --version
initdb --version
```

Si falta una herramienta, instala el componente correspondiente y añade su carpeta de binarios al `PATH`. El repositorio no incluye un instalador ni define el nombre de un servicio PostgreSQL de Windows, Linux o macOS. No asumas una ruta de instalación concreta.

## 2. Prepara PostgreSQL de desarrollo

**Supabase es producción.** Aquí se usa únicamente `127.0.0.1:5433`, el puerto local de las plantillas. No reutilices credenciales ni una sesión de terminal configurada para producción.

### Si aún no tienes una instancia local

Con PostgreSQL 17 instalado, abre una terminal PowerShell normal. Desde la raíz del repositorio, introduce una ruta absoluta nueva, fuera del repositorio, donde guardarás los datos de desarrollo. La ruta la eliges tú; no es una carpeta que el proyecto ya incluya.

```powershell
$acadexPgData = Read-Host 'Ruta absoluta nueva, fuera del repositorio, para PostgreSQL de desarrollo'
if (-not [IO.Path]::IsPathRooted($acadexPgData)) { throw 'Usa una ruta absoluta.' }
if (Test-Path $acadexPgData) { throw 'La ruta ya existe. Revisa la instancia antes de continuar.' }
initdb -D $acadexPgData -U acadex_dev -W -A scram-sha-256 --encoding=UTF8
if ($LASTEXITCODE -ne 0) { throw 'No se pudo inicializar PostgreSQL.' }
pg_ctl -D $acadexPgData -l "$acadexPgData/server.log" -o "-h 127.0.0.1 -p 5433" start
if ($LASTEXITCODE -ne 0) { throw 'No se pudo iniciar PostgreSQL. Revisa server.log.' }
```

`initdb` pide una contraseña: elige una exclusiva de desarrollo y guárdala solo en tu configuración local. El usuario `acadex_dev` administra esta instancia local. No es una cuenta de producción. Conserva la ruta: la necesitas para detener y reanudar PostgreSQL.

Los comandos y opciones corresponden a [initdb](https://www.postgresql.org/docs/17/app-initdb.html) y [pg_ctl](https://www.postgresql.org/docs/17/app-pg-ctl.html). No forman parte de un script del repositorio. Para macOS/Linux, queda pendiente documentar el arranque específico de la instalación que use el equipo; no copies la sintaxis PowerShell.

### Si ya tienes PostgreSQL local

No ejecutes `initdb` sobre sus datos. Inicia esa instancia con el gestor de servicios de tu instalación y confirma host, puerto y usuario. Si usa otro puerto, cambia `DB_PORT` y los argumentos `-p` de esta guía de forma consistente. El nombre del servicio y la ruta de datos dependen de tu instalación y deben confirmarse allí.

### Crea y comprueba la base

Para la instancia nueva del paso anterior, ejecuta desde la raíz:

```sh
pg_isready -h 127.0.0.1 -p 5433 -U acadex_dev -d postgres
createdb -h 127.0.0.1 -p 5433 -U acadex_dev -W --maintenance-db=postgres -O acadex_dev acadex_dev
psql -h 127.0.0.1 -p 5433 -U acadex_dev -d acadex_dev -W -c "SELECT current_database(), current_user, inet_server_addr(), inet_server_port();"
```

La consulta debe mostrar base y usuario `acadex_dev`, servidor `127.0.0.1` y puerto `5433`. `createdb` se ejecuta solo una vez. Si la base ya existe, comprueba su identidad y esquema; no la borres ni la recrees. En una instalación previa, usa el usuario local que hayas preparado y refleja ese usuario en `backend/.env`.

## 3. Copia y revisa las variables

Desde la raíz, en PowerShell:

```powershell
if (-not (Test-Path backend/.env)) { Copy-Item backend/.env.example backend/.env }
if (-not (Test-Path frontend/.env.local)) { Copy-Item frontend/.env.example frontend/.env.local }
```

O en Bash:

```sh
test -f backend/.env || cp backend/.env.example backend/.env
test -f frontend/.env.local || cp frontend/.env.example frontend/.env.local
```

No necesitas el `.env` de la raíz para este método. Revisa `backend/.env`:

| Variable | Valor para la instancia nueva de esta guía |
| --- | --- |
| `APP_ENV` | `development` |
| `DB_HOST`, `DB_PORT` | `127.0.0.1`, `5433` |
| `DB_NAME`, `DB_USER` | `acadex_dev`, `acadex_dev` |
| `DB_PASSWORD` | La contraseña local elegida al inicializar PostgreSQL |
| `DB_SSLMODE` | `disable`, solo para esta conexión local |
| `SECRET_KEY` | Una clave de desarrollo propia; conserva `ALGORITHM` y `ACCESS_TOKEN_EXPIRE_MINUTES` de la plantilla |
| `CORS_ORIGINS`, `FRONTEND_URL` | `http://localhost:5173` |
| `PASSWORD_RESET_ENABLED` | `false`: esta ruta no inicia un servidor SMTP |
| `ATTACHMENTS_ENABLED`, `ATTACHMENTS_STORAGE_BACKEND` | `false`, `local` para el primer arranque |

Deja vacías las claves de Gemini y Groq si no vas a probar IA. En `frontend/.env.local`, conserva `VITE_API_URL=http://localhost:8000` y `VITE_ATTACHMENTS_ENABLED=false`. No añadas `/api/v1` a la URL; lo añade el cliente.

La aplicación lee `.env` desde su directorio de trabajo; por eso backend y Alembic se ejecutan desde `backend/`. Las variables de la terminal tienen prioridad sobre ese archivo. Usa una terminal sin variables de producción; no basta con corregir el archivo si la sesión sigue apuntando a otro destino.

## 4. Prepara el backend

Abre una terminal para el backend. Desde la raíz:

```sh
cd backend
python -m venv .venv
```

Activa el entorno en PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

O en Bash:

```sh
source .venv/bin/activate
```

Desde `backend/`, con el entorno activado:

```sh
python -m pip install -r requirements.txt
```

Si PowerShell bloquea la activación, no necesitas cambiar su política de ejecución: usa `.\.venv\Scripts\python.exe` en lugar de `python` en los comandos de instalación, Alembic, Uvicorn y pytest.

## 5. Aplica las migraciones locales

Antes de ejecutar Alembic, confirma otra vez que `backend/.env` y la terminal apuntan a la base local comprobada. Alembic y la API comparten conexión. `APP_ENV=development` por sí solo no impide conectar a un servidor remoto.

Para una base nueva y vacía, desde `backend/` y con `.venv` activo:

```sh
python -m alembic heads
python -m alembic upgrade head
python -m alembic current
psql -h 127.0.0.1 -p 5433 -U acadex_dev -d acadex_dev -W -v ON_ERROR_STOP=1 -f ../database/verify_schema.sql
```

`current` debe coincidir con `heads`; las columnas del script deben devolver `t`. La cadena versionada termina actualmente en `20261018_01`; comprueba la rama si se añaden revisiones.

Para una base local con datos, revisa las migraciones y prepara un respaldo recuperable antes de `upgrade`. Si tiene tablas sin historial Alembic, detente y sigue la [guía de adopción](DESPLIEGUE_ALEMBIC.md). No cargues los SQL históricos ni uses `stamp` como reparación rápida.

## 6. Arranca el backend

En la misma terminal, desde `backend/`:

```sh
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Mantén esta terminal abierta. Abre <http://localhost:8000/docs> y comprueba <http://localhost:8000/health/ready>; debe devolver `{"status":"ok"}`.

## 7. Arranca el frontend en otra terminal

Desde la raíz, en una segunda terminal:

```sh
cd frontend
corepack pnpm --version
corepack pnpm install --frozen-lockfile
corepack pnpm dev --host 127.0.0.1 --port 5173 --strictPort
```

La versión de pnpm debe ser `12.11.2`. Abre <http://localhost:5173/>. `--strictPort` evita que Vite cambie de puerto silenciosamente y deje de coincidir con CORS. Mantén ambas terminales abiertas mientras trabajas.

Para probar, usa los comandos de [Calidad y pruebas](calidad-y-pruebas.md). La configuración inicial deshabilita adjuntos y recuperación por correo; no esperes probar esas funciones hasta configurar sus dependencias.

## 8. Detén y reanuda el entorno

Detén Uvicorn y Vite con `Ctrl+C` en cada terminal. Si creaste la instancia con `pg_ctl`, desde cualquier directorio de la terminal PowerShell que conserva `$acadexPgData`:

```powershell
pg_ctl -D $acadexPgData stop -m fast
```

Para reanudarla:

```powershell
pg_ctl -D $acadexPgData -l "$acadexPgData/server.log" -o "-h 127.0.0.1 -p 5433" start
```

En una terminal nueva, vuelve a asignar a `$acadexPgData` la misma ruta existente. No repitas `initdb` ni `createdb`. Si usas un servicio instalado, contrólalo desde su gestor de servicios.

## Si algo falla

| Síntoma | Acción |
| --- | --- |
| PostgreSQL no inicia en 5433 | Revisa `server.log` y comprueba que otra instancia no use ese puerto. |
| `connection refused` o base no disponible | Comprueba `pg_isready`, host y puerto. Revisa variables de terminal que prevalezcan sobre `.env`. |
| Contraseña rechazada o base inexistente | Repite la consulta de identidad con las credenciales locales. Copiar la plantilla no crea usuarios ni bases. |
| Error de validación de configuración | Ejecuta desde `backend/` y completa los campos obligatorios de su plantilla. |
| API responde `Faltan migraciones obligatorias de seguridad` | Comprueba `alembic current` y las revisiones disponibles sobre la base local; revisa el error de migración antes de reintentar. |
| CORS o peticiones a una dirección incorrecta | Revisa `CORS_ORIGINS` y `VITE_API_URL`. Reinicia backend y Vite tras cambiar sus archivos de entorno. |
| No funciona la recuperación de contraseña | Está desactivada en esta ruta. Para probar correo local con Mailpit, usa el método Docker completo. |
