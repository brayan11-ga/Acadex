<!-- Ruta: memory.md (raíz del repositorio Acadex, junto a AGENTS.md y database.md) -->

# memory.md — Estado actual de Acadex

> **Instrucciones para el agente:** lee este archivo al empezar cada sesión. Al terminar cada tarea, actualízalo: mueve lo terminado a "Hecho", ajusta "Pendiente" y anota decisiones nuevas. Una o dos líneas por cambio. Si una sección pasa de ~15 líneas, resume lo viejo. Última actualización: 2026-10-21

## Tanda de tareas grupales (C1–C4)

- **C1 — Hecho y pusheado.** `GET /tareas/{id}/asignados` ahora lo ve cualquier miembro del grupo (RF-045); las individuales solo su dueño. Sin cambios en el endpoint.
- **C2 — Hecho y pusheado.** `tareas.max_archivos` (INTEGER, def. 10, CHECK ≥ 1) con tope fijo del sistema 10 y default 3 al crear grupal; validación al subir (409) y al actualizar (400/403); `total_archivos` en las respuestas (sin N+1). Migración por revisión Alembic `20261018_01` + snippet `database/migrations/20261018_add_tarea_max_archivos.sql`.
- **C3 — Hecho (pruebas sin ejecutar).** `POST /tareas/{id}/completar` para asignados (dificultad_real 1-5, tiempo real de sesiones cerradas, upsert con dedupe, estado automático) + restricciones del `PUT` en grupales + campo `completado` en `GET /asignados`. Pruebas: `backend/tests/test_completar_tarea_grupal.py`.
- **C4a — Hecho (pruebas sin ejecutar).** Estadísticas personales y resumen semanal excluyen historial grupal (`id_grupo IS NULL`); `TareaCreate`/`TareaGrupalCreate`/`TareaUpdate` validan dificultad 1-5 y tiempo > 0 (422); crear grupal rechaza lista vacía o repetida. Pruebas: `backend/tests/test_c4a_correcciones_previas.py`. SQL de recálculo entregado aparte (no ejecutado).

### Prompt definitivo para C3 — Completar la parte de una tarea grupal

**Contexto:** C1 y C2 están terminados y pusheado. C1 abrió `GET /tareas/{id}/asignados` a cualquier miembro del grupo (RF-045). C2 agregó `tareas.max_archivos` (tope fijo 10, default 3 al crear grupal) con validación al subir (409) y al actualizar (400/403), y `total_archivos` en las respuestas.

**Objetivo:** endpoint `POST /tareas/{id_tarea}/completar` para que un asignado complete SU PARTE de una tarea grupal, más las restricciones de `PUT`.

**Decisiones ya tomadas (no volver a discutir):**
- Solo tareas grupales. Si es individual → 400 "Esta tarea no es grupal; usa el flujo actual (PUT)."
- Solo un usuario asignado (si no → 403; el líder sin asignación tampoco).
- Si la tarea ya está completada → 409.
- Si el usuario tiene una sesión de cronómetro abierta en esa tarea → 409 "Pausa tu cronómetro antes de completar tu parte."
- `dificultad_real` obligatoria, entera 1..5 (body: `{ "dificultad_real": int }`).
- `tiempo_real` = suma de `duracion` (en SEGUNDOS) de las sesiones CERRADAS de ESE usuario en ESA tarea; 0 si no tiene. No se escribe a mano.
- Upsert del historial: una fila por (id_usuario, id_tarea). Si ya existe, actualizarla (fechahora_fin, tiempo_real, dificultad_real); si hay varias, dejar una y borrar las demás. Todo en una transacción. Crear con `id_grupo`.
- Estado: si TODOS los asignados tienen fila → `"Completada"`; si no y era `"pendiente"` → `"en progreso"`. No inventar otros valores.
- NO llamar a `recalcular_estadistica_categoria` desde este endpoint. (Hallazgo: esa función SÍ incluye filas con `id_grupo`; no la cambiamos.)
- Tareas individuales NO cambian: se siguen completando con PUT como hoy.

**Restricciones de `PUT /tareas/{id}` en grupales (`tarea_service.actualizar_tarea`):**
- No líder → 403 (todo).
- Tarea ya completada y alguien intenta editarla → 400 "Reábrila primero." (nadie edita una completada).
- Alguien pone `estado = "Completada"` por PUT → 400 "Usa Completar mi parte."
- Cambiar `estado` a otro valor → 400 "No puedes cambiar el estado de una tarea grupal; se actualiza al completar cada parte."
- Líder cambia otros campos en tarea NO completada → 200 (permitido).

**`GET /tareas/{id}/asignados`:** agregar campo `completado` (bool) a cada elemento (si esa persona ya tiene fila en el historial). Campo nuevo, no romper lo existente.

**Fuera de alcance (dejar para C4):** el endpoint `POST /tareas/{id}/reabrir` (el líder reabre una completada: borra las filas de historial con dificultad/tiempo real, conserva archivos y detalles, y los integrantes vuelven a completar desde cero). También reasignar y notificaciones.

**Hallazgos del código (ya investigados, no volver a investigar):**
- `sesion_cronometro_service.py:47` guarda `duracion` con `total_seconds()` → segundos.
- `historial_tareas` NO tiene restricción única (id_usuario, id_tarea) → puede haber duplicados → dedupe.
- No existe `historial_tarea_repository.py` → crearlo.
- `recalcular_estadistica_categoria` (`estadistica_service.py:45-57`) une HistorialTarea→Tarea y filtra por id_usuario + Tarea.id_categoria SIN filtrar id_grupo → incluye grupales.
- Valor de estado que ya se guarda: `"Completada"` (mayúscula, lo envía Panel.tsx). Backend compara con `.lower()`.
- Frontend: ningún lugar usa PUT con estado para tareas grupales (Panel.tsx y useTareas.ts son individuales; TareasGrupoPage no PUT estado; FormularioNuevaTarea no envía estado). El cambio en `actualizar_tarea` no rompe el frontend.

**Reglas de la sesión (igual que C1/C2):** plan antes de tocar código; cambios pequeños y puntuales; solo backend (no frontend, no BD real, no `seed.sql`/`supabase_new_project.sql`/`supabase_resume_migrations.sql`/`*.rollback.sql`); no ejecutar comandos (dar el comando exacto para que Sam lo corra); pruebas en el estilo de `backend/tests` pero marcar "sin verificar"; releer los cambios antes de entregar; guía de prueba manual en Swagger con JSON de ejemplo; mensaje de commit sugerido (`feat:`/`fix:`); cada archivo con su ruta arriba; explicar con analogías; actualizar `memory.md` al terminar.

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
- Al expulsar a un integrante, la app le envía una notificación.
- La documentación de requisitos vive en `docs/RF/` (58 RF con historia y escenarios) y `docs/RNF/` (32 RNF por categoría). RF-013 quedó fusionado en RF-010.

## Pendiente (en orden de prioridad)
1. Frontend restante de tareas grupales: subir evidencias y ver detalle (RF-037); lista «mis asignadas» en UI si aplica (RF-038). RF-054 en panel de líder sigue pendiente.
2. Backend siguiente (C4b y C4c): `POST /tareas/{id}/reabrir` (borra historial, estado "en progreso", notifica) y `PUT /tareas/{id}/asignados` (reasignar, limpiar archivos/sesiones/historial del quitado, notificar) + notificación al crear tarea grupal.
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
