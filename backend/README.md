# Backend de Acadex

API FastAPI con SQLAlchemy, Pydantic y PostgreSQL. La entrada es `app.main:app`; la documentación interactiva está en `/docs` y las rutas de aplicación usan `/api/v1`.

## Ejecutar y probar

Para preparar Python, variables, base y migraciones, sigue [Inicio manual](../docs/inicio-manual.md). Para el sistema completo en contenedores, usa [Inicio con Docker](../docs/inicio-docker.md). Los comandos de pruebas y sus límites están en [Calidad y pruebas](../docs/calidad-y-pruebas.md).

Ejecuta los comandos Python desde `backend/`: [settings.py](app/config/settings.py) busca `.env` en el directorio de trabajo. API y Alembic comparten la conexión de [app/db/session.py](app/db/session.py). FastAPI no aplica migraciones al iniciar.

## Configuración e integraciones

Parte de [.env.example](.env.example); los campos de base de datos y autenticación son obligatorios. Las guías de inicio explican los valores locales.

- **Correo:** `PASSWORD_RESET_ENABLED` habilita recuperación de contraseña. La plantilla apunta a SMTP local; el método manual básico lo desactiva y Docker usa Mailpit.
- **Adjuntos:** `ATTACHMENTS_ENABLED` activa el backend. Para desarrollo usa `ATTACHMENTS_STORAGE_BACKEND=local`; la interfaz tiene su propia bandera `VITE_ATTACHMENTS_ENABLED`. Activarlas requiere revisar ambos componentes.
- **IA:** `GEMINI_API_KEY` y `GROQ_API_KEY` se configuran solo cuando se prueban esas integraciones. No se necesitan para iniciar las funciones básicas.
- **Producción:** Supabase y sus claves pertenecen al entorno de producción. No copies esa conexión a una guía local. La validación de `APP_ENV=production` está en `settings.py`; una comprobación local no valida la configuración desplegada.

`CORS_ORIGINS` acepta orígenes explícitos separados por comas, sin rutas ni `*`. Debe coincidir con el origen que abre el navegador.

## Organización

| Carpeta | Contenido |
| --- | --- |
| `app/api/` | Routers y endpoints |
| `app/config/` | Configuración y validaciones de entorno |
| `app/models/`, `app/schemas/` | Modelos y contratos de datos |
| `app/repositories/`, `app/services/` | Persistencia y lógica de aplicación |
| `app/db/` | Conexión, metadatos y guardas de Alembic |
| `alembic/versions/` | Migraciones vigentes |
| `test/`, `tests/` | Suites de pruebas |

Consulta [Arquitectura](../docs/arquitectura.md) para el flujo entre estas capas y [Base de datos](../database/README.md) antes de cambiar el esquema.
