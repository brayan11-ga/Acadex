# Acadex

[![CI](https://github.com/brayan11-ga/Acadex/actions/workflows/ci.yml/badge.svg)](https://github.com/brayan11-ga/Acadex/actions/workflows/ci.yml)

Acadex ayuda a organizar tareas académicas individuales y grupales. Incluye cuentas, categorías, calendario, cronómetro, estadísticas, grupos y adjuntos. El análisis con IA, el correo y el almacenamiento remoto necesitan configuración adicional.

La interfaz usa React, TypeScript, Vite y Redux Toolkit. La API usa Python, FastAPI, SQLAlchemy y Pydantic; el esquema de PostgreSQL se mantiene con Alembic. Las pruebas usan Vitest y pytest.

## 1. Clona el repositorio

Necesitas Git. Desde la carpeta donde guardas tus proyectos:

```sh
git clone https://github.com/brayan11-ga/Acadex.git
cd Acadex
git switch develop
```

`develop` reúne el trabajo del equipo; `main` es la rama predeterminada y recibe las entregas. Antes de cambiar archivos, sigue [CONTRIBUTING.md](CONTRIBUTING.md) para registrar la tarea y crear tu rama.

## 2. Elige cómo iniciarlo

Sigue una sola guía de principio a fin. Ambas usan una base local de desarrollo. **Supabase es producción: no copies sus credenciales ni ejecutes allí los comandos locales.**

| Método | Requisitos | Qué vas a iniciar |
| --- | --- | --- |
| [Docker Compose](docs/inicio-docker.md) | Docker con soporte para contenedores Linux y Compose 2.24.0 o posterior | PostgreSQL, migraciones, backend, frontend y Mailpit |
| [Inicio manual](docs/inicio-manual.md) | Python 3.14, Node.js 24, Corepack, pnpm 12.11.2 y PostgreSQL 17 | Base local y backend/frontend desde terminales separadas |

Las versiones manuales siguen los Dockerfiles; CI usa Node.js 22 y Python 3.14. `frontend/package.json` fija pnpm 12.11.2.

### Con Docker Compose

Desde la raíz, prepara los archivos de ejemplo siguiendo el [paso 1 de la guía Docker](docs/inicio-docker.md#1-prepara-el-entorno-local). Después:

```sh
docker compose up --build -d
docker compose ps -a
```

Compose espera a PostgreSQL, ejecuta `python -m alembic upgrade head` mediante `migrate` y después arranca la API y la interfaz. La guía explica cómo comprobar cada servicio y detenerlo conservando los datos.

### Con terminales separadas

Sigue la [guía manual](docs/inicio-manual.md): primero inicia PostgreSQL local y crea la base; luego copia las plantillas, instala dependencias y aplica Alembic. Con esa preparación terminada:

```sh
# Terminal del backend, desde backend/ y con .venv activado.
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

```sh
# Terminal del frontend, desde frontend/.
corepack pnpm dev --host 127.0.0.1 --port 5173 --strictPort
```

## Archivos de entorno

Copia las plantillas; no reutilices archivos de producción. Cada guía indica cuáles necesitas y cómo copiarlos sin sobrescribir tu configuración.

| Plantilla | Archivo local | Quién lo lee |
| --- | --- | --- |
| [.env.example](.env.example) | `.env` en la raíz | Docker Compose: base, puertos y variables interpoladas |
| [backend/.env.example](backend/.env.example) | `backend/.env` | API y Alembic; Compose sobrescribe las variables declaradas en `environment` |
| [frontend/.env.example](frontend/.env.example) | `frontend/.env.local` | Vite en el inicio manual |

La plantilla raíz usa `DB_NAME=acadex_dev`; Compose sin `.env` usa `acadex`. Elige antes de crear el volumen: cambiar esa variable después no renombra una base existente. Las variables de la terminal pueden prevalecer sobre los archivos `.env`.

Los archivos locales de entorno están ignorados por Git. No incluyas secretos en capturas, logs o PR. Las variables `VITE_*` llegan al navegador y nunca deben contener claves privadas.

## Direcciones locales

Con los puertos de las plantillas y de estas guías:

| Servicio | Dirección |
| --- | --- |
| Aplicación | <http://localhost:5173/> |
| API y documentación interactiva | <http://localhost:8000/docs> |
| Comprobación de API y base | <http://localhost:8000/health/ready> |
| PostgreSQL | `127.0.0.1:5433` |
| Mailpit, solo en la ruta Docker | <http://localhost:8025/>; SMTP en `127.0.0.1:1025` |

`/health/ready` debe responder `{"status":"ok"}`. Comprueba conexión y algunas estructuras obligatorias; no sustituye la revisión completa del esquema. `VITE_API_URL` contiene solo el origen de la API: el frontend añade `/api/v1`.

## Pruebas

Con las dependencias instaladas y el entorno local preparado:

```sh
# Desde backend/, con .venv activado y sin habilitar ACADEX_RUN_POSTGRES_TESTS.
python -m pytest test tests -q
```

```sh
# Desde frontend/.
corepack pnpm lint
corepack pnpm build
corepack pnpm test --run
```

La suite backend anterior omite las pruebas que requieren PostgreSQL aislado. Para ejecutarlas, o para probar dentro de contenedores, sigue [Calidad y pruebas](docs/calidad-y-pruebas.md). Esa guía contiene la secuencia completa y la limpieza del entorno de pruebas.

## Si algo falla

| Síntoma | Qué revisar |
| --- | --- |
| API devuelve `503` | Revisa la conexión y el resultado de Alembic: [Docker](docs/inicio-docker.md#si-algo-falla) o [manual](docs/inicio-manual.md#si-algo-falla). |
| Base inexistente o contraseña rechazada | Compara `DB_NAME`, usuario y puerto con la instancia creada; las plantillas no cambian volúmenes existentes. |
| Navegador bloquea peticiones por CORS | `CORS_ORIGINS` debe contener el origen exacto del frontend, incluido el puerto. Reinicia la API tras modificarlo. |
| Falta `VITE_API_URL` o las peticiones tienen `/api/v1/api/v1` | Copia la plantilla del frontend y configura solo `http://localhost:8000`. Reinicia Vite. |
| Alembic detecta tablas sin historial | Detente y consulta [adopción de Alembic](docs/DESPLIEGUE_ALEMBIC.md). No uses `stamp` para saltar el error. |

## Dónde seguir

- [Colaborar](CONTRIBUTING.md): issue, tablero, rama, commits, PR y revisión.
- [Índice de documentación](docs/README.md): responsabilidad de cada documento.
- [Arquitectura](docs/arquitectura.md): componentes y flujos.
- [Base de datos](database/README.md): migraciones, administración local y archivos históricos.
- [RF](docs/RF/README.md) y [RNF](docs/RNF/README.md): comportamiento esperado y restricciones del producto.
