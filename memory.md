<!-- Ruta: memory.md (raíz del repositorio Acadex, junto a AGENTS.md y database.md) -->

# memory.md — Estado actual de Acadex

> **Instrucciones para el agente:** lee este archivo al empezar cada sesión. Al terminar cada tarea, actualízalo: mueve lo terminado a "Hecho", ajusta "Pendiente" y anota decisiones nuevas. Una o dos líneas por cambio. Si una sección pasa de ~15 líneas, resume lo viejo. Última actualización: 2026-10-22
>
> **Traspaso:** C4b está hecho; la próxima fase es C4c (`PUT /tareas/{id}/asignados`), según el "Prompt definitivo para C4b y C4c" (más abajo).

## Tanda de tareas grupales (C1–C4)

- **C1 — Hecho y pusheado.** `GET /tareas/{id}/asignados` ahora lo ve cualquier miembro del grupo (RF-045); las individuales solo su dueño. Sin cambios en el endpoint.
- **C2 — Hecho y pusheado.** `tareas.max_archivos` (INTEGER, def. 10, CHECK ≥ 1) con tope fijo del sistema 10 y default 3 al crear grupal; validación al subir (409) y al actualizar (400/403); `total_archivos` en las respuestas (sin N+1). Migración por revisión Alembic `20261018_01` + snippet `database/migrations/20261018_add_tarea_max_archivos.sql`.
- **C3 — Hecho (pruebas sin ejecutar).** `POST /tareas/{id}/completar` para asignados (dificultad_real 1-5, tiempo real de sesiones cerradas, upsert con dedupe, estado automático) + restricciones del `PUT` en grupales + campo `completado` en `GET /asignados`. Pruebas: `backend/tests/test_completar_tarea_grupal.py`.
- **C4a — Hecha y pusheada.** Archivos: `backend/app/services/estadistica_service.py`, `backend/app/repositories/estadisticas_repository.py`, `backend/app/schemas/tarea.py`, `backend/app/services/tarea_service.py` y `backend/tests/test_c4a_correcciones_previas.py` (pruebas nuevas, sin verificar). Arreglos: estadísticas personales y resumen semanal cuentan solo historial individual (`HistorialTarea.id_grupo IS NULL`); `TareaCreate`/`TareaGrupalCreate`/`TareaUpdate` validan dificultad 1..5 y `tiempo_estimado > 0` (422); `crear_tarea_grupal` rechaza `ids_usuarios` vacío o repetido. El SQL de recálculo de `estadistica_categoria` **no** está en el repo: Sam lo corrió en local; en producción se corre después de desplegar y con respaldo.
- **C4b — Hecho (pruebas sin verificar).** `POST /tareas/{id}/reabrir` para el líder: borra todo el historial, estado "en progreso", notifica a los asignados menos al líder (`tarea_reabierta`), sin recalcular estadísticas; conserva archivos, sesiones, asignaciones y detalles. Archivos: `historial_tarea_repository.py`, `notificacion_repository.py` (param `commit`), `tarea_service.py`, `tareas.py` y `backend/tests/test_reabrir_tarea_grupal.py` (nuevo).
- **C4c — Pendiente.** `PUT /tareas/{id}/asignados` + notificaciones + aviso al crear tarea grupal.

### Prompt definitivo para C3 — Completar la parte de una tarea grupal (hecho)
**Hecho (pruebas sin ejecutar).**
- `POST /tareas/{id_tarea}/completar`: solo grupales (individual → 400 "Esta tarea no es grupal; usa el flujo actual (PUT).") y solo asignados (403 si no; el líder sin asignación tampoco); 409 si ya está completada, si ya completó o si tiene cronómetro abierto.
- Body `{ "dificultad_real": 1..5 }`; `tiempo_real` = suma en SEGUNDOS de las sesiones cerradas de ese usuario en esa tarea (0 si no tiene); no se escribe a mano.
- `upsert` del historial en una sola transacción: una fila por (usuario, tarea), con `id_grupo`; si hay duplicados, deja una y borra el resto.
- Estado: `"Completada"` si todos los asignados tienen fila; si no y estaba `"pendiente"` → `"en progreso"`. No llama a `recalcular_estadistica_categoria`.
- `PUT` de grupales: solo líder (403); completada → 400 "Reábrila primero."; `estado="Completada"` → 400 "Usa Completar mi parte."; otro estado → 400 "No puedes cambiar el estado..."; el líder sí puede editar otros campos si no está completada.
- `GET /tareas/{id}/asignados` agrega `completado` (bool; campo nuevo, no rompe lo existente). Las individuales siguen con `PUT`.
- Hallazgos vigentes: `duracion` en segundos; `historial_tareas` sin unique (usuario, tarea) → dedupe; `"Completada"` con mayúscula y comparaciones con `.lower()`; el frontend no usa `PUT` con estado en grupales.

### Prompt definitivo para C4b y C4c — Reabrir, reasignar y notificar

**Contexto:** C1, C2, C3 y C4a están hechos. C4 se parte en C4b (reabrir + notificación) y C4c (reasignar + notificaciones + aviso al crear tarea grupal). Solo backend.

**Objetivo C4b (Fase 2):** `POST /tareas/{id_tarea}/reabrir` para que el líder devuelva a `"en progreso"` una tarea grupal `"Completada"`. Borra **todas** las filas de `historial_tareas` de esa tarea; conserva archivos, sesiones, asignaciones y datos de la tarea; **no** recalcula estadísticas; notifica a todos los asignados (excepto al líder) y devuelve la tarea actualizada.

**Objetivo C4c (Fase 3):** `PUT /tareas/{id_tarea}/asignados` con el conjunto **completo** de `ids_usuarios`. Solo el líder de una tarea grupal **no completada**. Quita a quien ya no está (solo su avance) y agrega a los nuevos; recalcula el estado con la regla de C3; **no** recalcula estadísticas; notifica a los afectados. Además, al crear una tarea grupal (`POST /tareas/grupos/{id_grupo}`), notificar a los asignados.

**Decisiones ya tomadas (no volver a discutir):**
- Reabrir solo si la tarea es grupal (individual → 400), el actor es el líder (si no → 403) y el estado es `"Completada"`; si no está completada → 409 "La tarea no está completada.".
- Reabrir borra **todo** el historial de la tarea y deja el estado en `"en progreso"`; no toca archivos, sesiones, asignaciones ni detalles; no llama a `recalcular_estadistica_categoria`.
- Reabrir notifica a todos los asignados excepto al líder: título "Una tarea volvió a estar en progreso"; detalle "El líder reabrió «{tarea}». Debes completar tu parte otra vez.".
- Reasignar recibe la lista **completa** nueva (no deltas). Si el conjunto es igual → 200, sin cambios y sin notificaciones.
- Reasignar solo si es grupal (individual → 400), el actor es el líder (si no → 403) y la tarea **no** está completada; si está completada → 409 "Reábrela primero.".
- Lista vacía o con repetidos → 400 (reutilizar los mensajes de C4a: "La tarea debe tener al menos un asignado." y "No se permiten asignados repetidos."); alguien que no es del grupo → 400 "Todos los asignados deben pertenecer a este grupo.".
- Al quitar a alguien se borran **solo de esa tarea y de esa persona**: sus archivos (solo los que `id_usuario_subida` sea suyo; los de autor NULL no se tocan), todas sus sesiones de cronómetro (cerradas y abiertas), su fila de historial y su asignación.
- Si el borrado en almacenamiento falla, la reasignación **no** falla: se registra en el log.
- No se recalcula `estadistica_categoria` al reasignar (aunque se borre historial); es una decisión explícita.
- Notificaciones de reasignación: al nuevo → "Tienes una tarea nueva" / "El líder te asignó «{tarea}». Entrega: {fecha corta en español}."; al quitado con trabajo (archivos, tiempo o historial) → "Ya no estás asignado a una tarea" / "El líder te quitó de «{tarea}». Se borraron tus archivos y tu tiempo."; al quitado sin trabajo → mismo título / "El líder te quitó de «{tarea}».".
- El nombre de la tarea se recorta a **35 caracteres con "…"** antes de armar título/detalle. `titulo` máx. 50 y `detalles` máx. 100.
- Al crear una tarea grupal se notifica a los asignados (excepto al líder) con el mismo texto de "Tienes una tarea nueva".
- Tipo de notificación: seguir el patrón snake_case del único tipo existente en el código (`archivo_tarea`). Propuestos: `tarea_reabierta`, `tarea_asignada`, `tarea_retirada`.
- No se crea migración para unique `(id_usuario, id_tarea)` en `historial_tareas`; queda como pendiente futuro.

**Hallazgos del código ya investigados (no volver a investigar):**
- `historial_tarea_repository.py` (C3) tiene `obtener_fila`, `obtener_filas`, `obtener_usuarios_completados`, `usuario_ya_completo`, `upsert`. **No** tiene borrado masivo: C4b necesita `eliminar_por_tarea` y C4c `eliminar_por_usuario_y_tarea`.
- `asignacion_tarea_repository.py` tiene `crear_asignacion(commit=False)`, `obtener_asignaciones_de_tarea`, `obtener_usuarios_asignados`, `usuario_tiene_asignacion`, `obtener_tareas_asignadas_a_usuario`; **no** tiene borrado → C4c necesita eliminar por tarea+integrante.
- `sesion_cronometro_repository.py` tiene `get_sesion_activa_de_usuario`, `sumar_duracion_cerrada`, `get_sesiones_by_usuario`, etc.; **no** tiene borrado → C4c necesita borrar todas las sesiones de la tarea y el usuario (incluidas las abiertas).
- `archivo_repository.py` tiene `obtener_archivos_de_tarea` (filtrar por `id_usuario_subida` en Python), `eliminar_archivo` (borra y commitea), `existe_referencia_fuera_de_tarea`, `existe_otra_referencia_a_ruta`; **no** tiene borrado por usuario.
- Patrón de borrado de archivos: `tarea_service.eliminar_tarea` usa `archivo_service.preparar_eliminacion_archivos_tarea(db, id_tarea)` (cuarentena local → borra BD/commit → borra Supabase y registra fallos). Para C4c hay que replicarlo para un subconjunto (solo archivos del quitado).
- `archivo_service.eliminar_archivo_tarea` (un archivo) valida permisos (`tarea.id_usuario == id_usuario or archivo.id_usuario_subida == id_usuario`), así que **no** sirve tal cual para que el líder borre archivos de otro; usar el patrón de bajo nivel.
- `archivo.id_usuario_subida` es nullable (NULL = histórico sin autor): no tocar esos archivos.
- La regla de estado de C3 está **inline** en `tarea_service.completar_parte_tarea` (~líneas 268-276), no en un helper. Para C4c, replicarla o extraer un helper (recomendado).
- `crear_tarea_grupal` está en `tarea_service.py` (~línea 331); después de C4a valida lista vacía/repetida y miembros. Agregar la notificación después del commit.
- `grupo_repository` tiene `obtener_integrante(db, id_usuario, id_grupo)` y `obtener_lider_de_grupo(db, id_grupo)`.
- `_es_lider(db, id_usuario, id_grupo)` (`tarea_service.py:19`) devuelve True solo si el rol es "lider". `crear_tarea_grupal` y `crear_tarea` además dejan pasar a `es_admin`; para C4 el prompt pide **solo líder**.
- `notificacion_repository.crear_notificacion(db, titulo, detalles, tipo, id_usuario, id_tarea=None)` **siempre hace `db.commit()` y `db.refresh()`**: no permite crear dentro de la misma transacción. Para C4 hay que agregarle `commit: bool = True` (o una función nueva) y llamarla con `commit=False` dentro de la transacción, o después del commit principal.
- `archivo_service` ya usa `crear_notificacion` y, si falla, hace `db.rollback()` (~líneas 460-470); ojo con ese patrón: un fallo de notificación no debería deshacer reabrir/reasignar.
- `Notificacion`: `titulo` 50, `detalles` 100, `tipo` 50; `id_tarea` opcional. Respetar límites.
- `Tarea`: `id_usuario` XOR `id_grupo` (`chk_tarea_owner`); en grupales `id_usuario` es NULL. `estado` es texto libre; se compara con `.lower()`.
- `tareas.py` ya tiene `POST /{id_tarea}/completar`; agregar `POST /{id_tarea}/reabrir` y `PUT /{id_tarea}/asignados` (sin conflicto con `PUT /{id_tarea}` porque son segmentos distintos).
- No hay helper de fecha corta en español en el backend; `panel_service._formatear_fecha` usa `%d/%m/%Y`. Crear uno pequeño para "30 oct." (mapa de meses) y reutilizarlo.
- `database/init.sql`/`acadex.sql` no necesitan cambios: C4 no toca el esquema. Si aparece la tentación de una migración (p. ej. unique en historial), **detenerse y avisar**.

**Fuera de alcance:** frontend (botones/diálogos de Reabrir y Reasignar); leer notificaciones o campanita; notificar al eliminar tarea o cambiar fecha (C5); `POST /tareas/{id}/cerrar`; cronómetro por persona y `GET /tiempos` (C6); regenerar código (C7); seguridad de endpoints amplios; paginación; migración de unique en `historial_tareas`; `seed.sql`, `supabase_*` y `*.rollback.sql`.

**Reglas de la sesión (igual que C3/C4a):**
- Mostrar el plan antes de escribir código, en cada fase.
- Cambios pequeños y puntuales; solo backend; no BD real; no ejecutar comandos (dar el comando exacto para que Sam lo corra); no `git commit`/`push` salvo que Sam lo pida.
- C4 **no requiere cambios de esquema**: si parece necesaria una migración, detenerse y avisar.
- Pruebas en el estilo de `backend/tests` pero marcadas "sin verificar"; releer los cambios antes de entregar.
- Guía de prueba manual en Swagger con JSON de ejemplo; mensaje de commit sugerido (`feat:`/`fix:`); cada archivo con su ruta arriba; explicar con analogías.
- Actualizar `memory.md` al terminar cada fase; parar tras cada fase con resumen, guía y esperar "sigue".

**Pruebas por fase:**
- **C4b** (`backend/tests/test_reabrir_tarea_grupal.py`, sin verificar): líder reabre completada → 200, estado "en progreso", historial borrado, archivos/sesiones/asignaciones/detalles intactos, sin recálculo de estadística, notificación a todos los asignados menos el líder con el texto exacto; no líder → 403; individual → 400; no completada → 409 "La tarea no está completada.".
- **C4c** (`backend/tests/test_reasignar_tarea_grupal.py`, sin verificar): líder cambia el conjunto → 200; al quitado se le borran archivos/sesiones/historial/asignación; se crean las asignaciones nuevas; estado recalculado; notificaciones exactas (nuevo / quitado con y sin trabajo); sin recálculo de estadística; mismo conjunto → 200 sin notificaciones; completada → 409 "Reábrela primero."; vacía/repetida/no miembro → 400; no líder → 403; individual → 400; fallo de almacenamiento no rompe la reasignación; nombre recortado a 35; límites de 50/100; notificación al crear tarea grupal.
- Actualizar `backend/tests/test_api_autorizacion.py` con las dos rutas nuevas en la matriz de rutas.

## Estado por módulo

| Módulo | Backend | Frontend | Notas |
|---|---|---|---|
| Autenticación (JWT) | Hecho | Hecho (login/registro) | Lo construyó un compañero. Bloqueo de cuenta: columnas `intentos_fallidos` y `bloqueado` listas; **lógica de desbloqueo pendiente** (delegada a un compañero) |
| Tareas individuales | CRUD completo | Hecho (lista "Tus Tareas", formulario "Nueva tarea") | Autocompletar con IA (Gemini) desde un PDF, hecho por compañeros. Sin filtros por categoría/título en la UI (decisión del equipo, se evalúa después) |
| Categorías | Hecho | — | 9 categorías iniciales vienen del `INSERT` en `database/init.sql` (~línea 905), que `acadex.sql` incluye |
| Grupos | Hecho | Hecho | Crear, mis grupos con rol, unirse por código, ver integrantes, salir (el líder no puede), expulsar y eliminar (solo líder, cascada completa) |
| Tareas grupales | Hecho (RF-036/037/038 + C3/C4a) | **Parcial** | Lista del grupo, crear+asignar y revelar asignados hechos (RF-036/044/045 UI). Faltan subir evidencias y detalle (RF-037/038 UI). Ver detalle abajo |
| Notificaciones | Parcial (solo `archivo_tarea` en el código) | Por confirmar | Verificado: solo se crea `archivo_tarea` (aviso al líder al subir evidencia). "Tarea por vencer" e "invitación a grupo" no aparecen en el código actual: **por verificar**. |
| Cronómetro | Funciona, incompleto | Funciona, incompleto | Faltan detalles por completar |
| Panel / Dashboard | Hecho | Hecho | Falta ajustarlo para cuando haya muchos datos |
| Perfil | Modelo, schemas y endpoints creados | Por confirmar | Un compañero hace aparte la lógica del botón de iniciar sesión |
| Calendario | Solo lógica de backend | Sin diseño oficial | El equipo de frontend lo diseñará |
| Panel de líder (RF-051 a RF-055) | Por confirmar | Parcial | Hechos: botón "Panel de líder" junto a "Eliminar grupo" (RF-051) y datos del grupo, código vigente e integrantes con expulsión (RF-052). Pendientes: gestionar tareas grupales (RF-054) y estadísticas del grupo (RF-055). **RF-053 sin verificar:** el botón se oculta a los miembros, pero falta confirmar que la ruta también esté protegida y que el backend lo valide |
| Admin (RF-056 a RF-058) | Por confirmar | Parcial | Hechos: rol `es_admin` en el estado de sesión (slice auth/Redux, RF-056) y enlace "Admin" en el Sidebar solo para administradores (RF-057). **RF-058 sin verificar:** no se sabe si `/admin` está protegida o solo se oculta el enlace; debe validarse también en el backend |

> Filas no verificadas en esta sesión: Autenticación, Tareas individuales, Grupos, Cronómetro, Panel, Perfil, Calendario, Panel de líder y Admin. Quedan **por verificar**.

## Tareas grupales (detalle)
- Frontend: `/grupos/:idGrupo/tareas` (lista + estados), «Ver grupo» lleva ahí; integrantes en `/grupos/:idGrupo`; modal reutiliza `FormularioNuevaTarea` con `modo="grupal"` + `AsignarIntegrantes`. Chip de prioridad oculto si es `null`.
- `POST /tareas/grupos/{id_grupo}` → solo el líder; crea la tarea grupal y la asigna a integrantes en una sola llamada (RF-036).
- `GET /tareas/asignadas/mias` → cada usuario ve sus tareas grupales asignadas (RF-038).
- `POST/GET /tareas/{id_tarea}/archivos` → solo un integrante con la tarea asignada sube evidencia. PDF/DOCX/JPG/PNG, máx. 5 MB, guardados en `backend/uploads/tareas/{id_tarea}/` (excluida con `.gitignore`). Al subir, se crea una notificación para el líder (RF-037).
- `GET /tareas/grupos/{id_grupo}` → todas las tareas de un grupo.
- `GET /tareas/{id_tarea}/asignados` → quién tiene asignada una tarea (botón "revelar"). **Hecho (C1):** cualquier integrante del grupo la ve (RF-045); las individuales solo su dueño.
- Repositories: `asignacion_tarea_repository.py`, `notificacion_repository.py`.

## Base de datos
- `database/scripts/acadex.sql` es **HISTÓRICO** (su cabecera lo dice): incluye `init.sql` + las migraciones SQL viejas de `backend/migrations/` y **no** escribe revisión Alembic. No usarlo para instalaciones nuevas.
- `database/init.sql` es el esquema base (9 categorías al final, ~línea 905). `database/seed.sql` **no existe**. Las columnas `intentos_fallidos`, `bloqueado` y `bloqueado_hasta` de `usuarios` no están en `init.sql`: las agrega `backend/migrations/20261012_add_security_guards.sql`.
- **Ruta vigente de migraciones: Alembic** (`backend/alembic/versions/`, `alembic upgrade head` en Compose). `backend/migrations/*.sql` es histórico y no se ejecuta. Revisión `20261018_01_add_tarea_max_archivos.py` agrega `tareas.max_archivos` (INTEGER, def. 10, CHECK ≥ 1); snippet manual en `database/migrations/20261018_add_tarea_max_archivos.sql`.
- Sin verificar en esta sesión: si `database/verify_schema.sql` sigue al día con Alembic y si `supabase_new_project.sql`/`supabase_resume_migrations.sql` se usan en el despliegue.

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
2. Backend siguiente (C4c): `PUT /tareas/{id}/asignados` (reasignar, limpiar archivos/sesiones/historial del quitado, notificar) + notificación al crear tarea grupal. C4b ya está hecho (pruebas sin verificar). **Ver el prompt definitivo arriba.**
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
