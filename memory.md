<!-- Ruta: memory.md (raíz del repositorio Acadex, junto a AGENTS.md y database.md) -->

# memory.md — Estado actual de Acadex

> **Instrucciones para el agente:** lee este archivo al empezar cada sesión. Al terminar cada tarea, actualízalo: mueve lo terminado a "Hecho", ajusta "Pendiente" y anota decisiones nuevas. Una o dos líneas por cambio. Si una sección pasa de ~15 líneas, resume lo viejo. Última actualización: 2026-10-18

## Estado por módulo

| Módulo | Backend | Frontend | Notas |
|---|---|---|---|
| Autenticación (JWT) | Hecho | Hecho (login/registro) | Lo construyó un compañero. Bloqueo de cuenta: columnas `intentos_fallidos` y `bloqueado` listas; **lógica de desbloqueo pendiente** (delegada a un compañero) |
| Tareas individuales | CRUD completo | Hecho (lista "Tus Tareas", formulario "Nueva tarea") | Autocompletar con IA (Gemini) desde un PDF, hecho por compañeros. Sin filtros por categoría/título en la UI (decisión del equipo, se evalúa después) |
| Categorías | Hecho | — | 9 categorías iniciales vienen del `INSERT` al final de `acadex.sql` |
| Grupos | Hecho | Hecho | Crear, mis grupos con rol, unirse por código, ver integrantes, salir (el líder no puede), expulsar y eliminar (solo líder, cascada completa) |
| Tareas grupales | Hecho (RF-036, 037, 038) | **Parcial** | Lista del grupo, crear+asignar y revelar asignados hechos (RF-036/044/045 UI). Faltan subir evidencias y detalle (RF-037/038 UI). Ver detalle abajo |
| Notificaciones | Hecho (varios tipos) | Por confirmar | Incluye: tarea por vencer, invitación a grupo, y archivo subido (aviso al líder) |
| Cronómetro | Funciona, incompleto | Funciona, incompleto | Faltan detalles por completar |
| Panel / Dashboard | Hecho | Hecho | Falta ajustarlo para cuando haya muchos datos |
| Perfil | Modelo, schemas y endpoints creados | Por confirmar | Un compañero hace aparte la lógica del botón de iniciar sesión |
| Calendario | Solo lógica de backend | Sin diseño oficial | El equipo de frontend lo diseñará |
| Panel de líder (RF-051 a RF-055) | Por confirmar | Parcial | Hechos: botón "Panel de líder" junto a "Eliminar grupo" (RF-051) y datos del grupo, código vigente e integrantes con expulsión (RF-052). Pendientes: gestionar tareas grupales (RF-054) y estadísticas del grupo (RF-055). **RF-053 sin verificar:** el botón se oculta a los miembros, pero falta confirmar que la ruta también esté protegida y que el backend lo valide |
| Admin (RF-056 a RF-058) | Por confirmar | Parcial | Hechos: rol `es_admin` en el estado de sesión (slice auth/Redux, RF-056) y enlace "Admin" en el Sidebar solo para administradores (RF-057). **RF-058 sin verificar:** no se sabe si `/admin` está protegida o solo se oculta el enlace; debe validarse también en el backend |

## Tareas grupales (detalle)
- Frontend: `/grupos/:idGrupo/tareas` (lista + estados), «Ver grupo» lleva ahí; integrantes en `/grupos/:idGrupo`; modal reutiliza `FormularioNuevaTarea` con `modo="grupal"` + `AsignarIntegrantes`. Chip de prioridad oculto si es `null`.
- `POST /tareas/grupos/{id_grupo}` → solo el líder; crea la tarea grupal y la asigna a integrantes en una sola llamada (RF-036).
- `GET /tareas/asignadas/mias` → cada usuario ve sus tareas grupales asignadas (RF-038).
- `POST/GET /tareas/{id_tarea}/archivos` → solo un integrante con la tarea asignada sube evidencia. PDF/DOCX/JPG/PNG, máx. 5 MB, guardados en `backend/uploads/tareas/{id_tarea}/` (excluida con `.gitignore`). Al subir, se crea una notificación para el líder (RF-037).
- `GET /tareas/grupos/{id_grupo}` → todas las tareas de un grupo.
- `GET /tareas/{id_tarea}/asignados` → quién tiene asignada una tarea (botón "revelar"). **Hecho (C1):** cualquier integrante del grupo la ve (RF-045); las individuales solo su dueño.
- Repositories: `asignacion_tarea_repository.py`, `notificacion_repository.py`.

## Base de datos
- `database/scripts/acadex.sql` actualizado y aprobado por el equipo (incluye `intentos_fallidos`, `bloqueado` y las 9 categorías iniciales). Una sola ejecución deja la app funcional.
- `init.sql` y `seed.sql` de `database/` no se ejecutan en ningún lado.
- **Ruta vigente de migraciones: Alembic** (`backend/alembic/versions/`, `alembic upgrade head` en Compose). `backend/migrations/*.sql` es histórico y no se ejecuta. Nuevo: revisión `20261018_01` agrega `tareas.max_archivos` (INTEGER, def. 10, CHECK ≥ 1); snippet manual en `database/migrations/20261018_add_tarea_max_archivos.sql`.

## Decisiones tomadas
- Desde el Perfil **no** se actualizan correo ni contraseña.
- Se eliminó el botón "Ajustes" del Sidebar; el Perfil se abre desde el ícono de la esquina superior derecha del Panel.
- Los archivos subidos se guardan en disco local, no en la BD.
- `src/utils/jwt.ts` decodifica el JWT solo para uso visual; la seguridad real va en el backend.
- Los componentes de grupos se partieron de v0 (Vercel) y se adaptaron: sin Next.js, Tailwind ni shadcn, con `.css` en `src/styles/`. Flujo con agentes: el código de v0 se guarda en `frontend/_v0/` (no se importa) y el agente lo adapta siguiendo `frontend/AGENTS.md`.
- Se descartó el acceso con Google (decisión de todo el equipo): solo correo y contraseña.
- Gemini: respuestas vacías, truncadas o JSON inválido devuelven 502; logs guardan metadatos sin contenido del PDF ni de la respuesta.
- Al expulsar a un integrante, la app le envía una notificación.
- La documentación de requisitos vive en `docs/RF/` (58 RF con historia y escenarios) y `docs/RNF/` (32 RNF por categoría). RF-013 quedó fusionado en RF-010.

## Pendiente (en orden de prioridad)
1. Frontend restante de tareas grupales: subir evidencias y ver detalle (RF-037); lista «mis asignadas» en UI si aplica (RF-038). RF-054 en panel de líder sigue pendiente.
2. Backend siguiente (C3): `POST /tareas/{id}/completar` solo grupales (dificultad real, upsert del historial, tiempo real desde sesiones) y bloquear el cambio de estado por `PUT` en grupales. Ver `docs/decisiones/tareas-grupales.md` §8-9.
3. RF-025: prioridad automática de tareas según el historial del grupo.
4. RF-018: estadísticas de dificultad por categoría y grupo.
5. Definir con el equipo la transferencia de liderazgo de un grupo (RF-050) y si la invitación a un grupo (RF-049) es una función completa.
6. Lógica de desbloqueo de cuentas (compañero).
7. Terminar el Cronómetro y ajustar el Panel para muchos datos.
8. Verificar si el `id_usuario` fijo temporal en la creación de tareas ya se reemplazó por el del JWT.
9. Prototipo de tema claro (hoy la app solo tiene tema oscuro).
10. Verificar la protección real de las rutas del panel de líder (RF-053) y de `/admin` (RF-058), tanto en el frontend como en el backend.
11. RF-054 y RF-055: gestión de tareas y estadísticas dentro del panel de líder.
12. Actualizar el `README.md` del repo (aún dice MySQL, HTML/CSS/JS y una estructura de carpetas que ya no existe).
13. Documentación: decidir si se agregan RF para eliminar cuenta y para estadísticas personales por categoría; revisar RNF-004 (Google, ya no aplica) y RNF-025/RNF-031 (parecen duplicados).

## Ideas para después
- Cambio de idioma en el perfil.
- Más funciones con IA (hoy solo existe el autocompletado de tareas con Gemini).
- Subagentes y skills para los agentes de IA.

## Contexto de entrega
- El proyecto debe estar 100% terminado para la feria del SENA.
