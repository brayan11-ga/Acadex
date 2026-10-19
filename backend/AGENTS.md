<!-- Ruta: backend/AGENTS.md (dentro de la carpeta backend/, aparte del AGENTS.md de la raíz) -->

# backend/AGENTS.md — Reglas del backend de Acadex

> Este archivo **complementa** al `AGENTS.md` de la raíz. Si algo choca, manda el de la raíz. Léelo antes de cualquier tarea de backend.

## 1. Stack y carpetas
Python + FastAPI + SQLAlchemy + Pydantic, con **PostgreSQL** (no MySQL) y autenticación con **JWT**. Se ejecuta desde `backend/` con `uvicorn app.main:app --reload`; la documentación interactiva está en `/docs` (Swagger) y `/redoc`.

```
backend/app/
├── api/v1/endpoints/   # rutas HTTP: reciben la petición y llaman al service (sin lógica de negocio)
├── services/           # lógica de negocio y validación de permisos
├── repositories/       # consultas a la base de datos (único lugar que habla con SQLAlchemy)
├── models/             # tablas (SQLAlchemy)
├── schemas/            # validación de entrada y salida (Pydantic)
├── config/  core/  db/  dependencies/  middlewares/
└── main.py             # arranque de la app y registro de routers
```

## 2. Reglas de arquitectura
- Flujo obligatorio: `endpoint → service → repository → model`. El endpoint no consulta la BD y el repository no decide permisos.
- Un módulo nuevo lleva su propio model, schema, repository, service y endpoint, y su router se registra en `main.py` o donde se agrupan los routers.
- Nombres del dominio en **español** (`id_usuario`, `fecha_entrega`, `asignacion_tarea_repository.py`).
- Los errores se devuelven con `HTTPException` y el código correcto (400, 401, 403, 404, 409).
- Las tablas, constraints y borrados en cascada ya los resuelve la BD (`database.md`). No los repliques a mano en Python.

## 3. Seguridad y permisos
- Toda ruta que lo necesite exige JWT mediante la dependencia de autenticación (carpeta `dependencies/`). Las rutas públicas son solo registro, login y recuperación de contraseña.
- **Los permisos se validan aquí, siempre**, aunque el frontend oculte el botón:
  - Solo el **líder** del grupo: expulsar, eliminar el grupo, crear tareas grupales, abrir el panel de líder. El líder no puede abandonar su grupo.
  - Solo un **integrante con la tarea asignada** puede subir archivos a una tarea grupal.
  - Solo **`es_admin`** accede a las rutas de administración.
  - Un usuario que no pertenece a un grupo no puede ver sus integrantes, tareas ni estadísticas.
- Nunca devuelvas la contraseña ni su hash en una respuesta. Las claves (por ejemplo la de Gemini) se leen del `.env` a través de `config/`, nunca van escritas en el código.
- Bloqueo de cuenta: usa `intentos_fallidos` y `bloqueado` de `usuarios` (la lógica de desbloqueo está pendiente; ver `memory.md`).

## 4. Reglas que siempre aplican
- Una tarea tiene **exactamente uno** entre `id_usuario` o `id_grupo` (`chk_tarea_owner`). Valídalo también en el schema.
- Dificultad entre 1 y 5, tiempo estimado mayor a 0, y toda tarea necesita una categoría.
- Los `id_*` son automáticos: nunca se insertan a mano.
- Notificaciones: `titulo` máximo 50 caracteres y `detalles` máximo 100. Recórtalos antes de insertar.
- Archivos de tareas: solo PDF, DOCX, JPG y PNG, máximo 5 MB, guardados en `backend/uploads/tareas/{id_tarea}/`. En la BD se guarda la **ruta**, no el archivo. Valida formato y tamaño antes de guardar.
- Si cambias el esquema, avisa que hay que actualizar `database/scripts/acadex.sql` y `database.md`.

## 5. Receta: agregar un endpoint nuevo
1. Lee el RF de la función en `docs/RF/`: sus escenarios son los casos que el endpoint debe cubrir, incluidos los de error y permisos.
2. Muestra el plan: qué archivos de cada capa vas a crear o modificar.
3. Crea o ajusta, en este orden: model (si hace falta), schema, repository, service y endpoint.
4. Registra el router si es un módulo nuevo.
5. Prueba cada escenario del RF desde Swagger (`/docs`): el caso feliz, el de datos inválidos y el de falta de permisos.
6. Actualiza `memory.md`.

## 6. Para ahorrar tokens
- Un endpoint o módulo por sesión.
- Trabaja solo con los archivos que Sam te nombre; no leas todo el repo.
- Cambios pequeños con ediciones puntuales; no reescribas archivos completos.
- Cada archivo nuevo o modificado lleva arriba su ruta: `# Ruta: backend/app/services/...`.
