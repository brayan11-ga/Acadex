# ACADEX

Aplicación web académica para organizar tareas individuales y grupales, coordinar integrantes, registrar tiempo, compartir archivos y consultar estadísticas.

## Tecnologías

- Frontend: React, TypeScript y Vite.
- Backend: Python, FastAPI y SQLAlchemy.
- Persistencia: PostgreSQL.
- Desarrollo local: Docker Compose para PostgreSQL, Mailpit y FastAPI; Vite se ejecuta con Node.js en el host.

## Desarrollo

La guía oficial para clonar la rama `docker`, configurar las variables locales, iniciar servicios, verificar el esquema, actualizar una base existente y ejecutar pruebas está en [database/README.md](database/README.md).

El backend aplica el esquema inicial y las migraciones pendientes automáticamente solo cuando PostgreSQL inicializa un volumen vacío. Para bases existentes, aplica las migraciones explícitamente según la guía. Los datos persisten en el volumen `pgdata` y los adjuntos en `backend/uploads/`.

No uses `docker compose down -v` para reiniciar un entorno que contenga datos: ese comando elimina los volúmenes.

## Módulos principales

- Registro, autenticación y perfiles.
- Tareas individuales, grupos, integrantes, roles y asignaciones.
- Cronómetro, historial, notificaciones y estadísticas.
- Adjuntos de tareas y análisis documental.

## Pruebas

La guía de desarrollo describe los comandos backend y frontend, además de una suite optativa de PostgreSQL que exige una base aislada cuyo nombre incluya `test`.
