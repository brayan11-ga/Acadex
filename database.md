<!-- Ruta: database.md (raíz del repositorio Acadex, junto a AGENTS.md y memory.md) -->

# database.md — Base de datos y reglas de negocio de Acadex

> **Fuente de verdad:** `database/scripts/acadex.sql`. Si este archivo y el script no coinciden, **gana el script**. Si cambias el esquema, actualiza primero `acadex.sql` y luego este archivo.
> **Motor:** PostgreSQL (NO MySQL). Los `id_*` son `INTEGER GENERATED ALWAYS AS IDENTITY`: nunca se insertan a mano.
> Los scripts `init.sql` y `seed.sql` de `database/` no se ejecutan en ningún lado; ignóralos.

## Mapa de relaciones
```
usuarios 1──1 perfiles
usuarios 1──N integrantes N──1 grupos
grupos   1──N tareas            (tarea grupal)
usuarios 1──N tareas            (tarea individual)
categorias 1──N tareas
tareas   1──N asignacion_tareas N──1 integrantes
tareas   1──N archivos | sesiones_cronometro | historial_tareas | notificaciones
perfiles 1──N estadistica_categoria N──1 categorias
grupos   1──N estadistica_categoria_grupo N──1 categorias
usuarios / grupos 1──N tokens_temporales
```

## Tablas (campos clave y reglas)

| Tabla | Campos clave | Reglas / constraints |
|---|---|---|
| **usuarios** | `id_usuario`, `correo_electronico` (único), `contrasena` (VARCHAR(60), hash), `fecha_registro`, `es_admin`, `intentos_fallidos` (def. 0), `bloqueado` (def. false) | Correo único. Guarda siempre el hash de la contraseña, nunca el texto plano |
| **categorias** | `id_categoria`, `nombre_categoria` (único, 50) | 9 iniciales: Programación, Base de Datos, Documentación, Proyecto Formativo, Inglés, Pruebas y QA, Investigación, Diseño UX/UI, Matemáticas |
| **grupos** | `id_grupo`, `nombre_grupo` (50), `descripcion`, `codigo_acceso` (único, 20), `fecha_creacion` | Se une a un grupo con `codigo_acceso` |
| **integrantes** | `id_integrante`, `rol`, `fecha_ingreso`, `id_usuario`, `id_grupo` | `rol` solo `'lider'` o `'miembro'`. Un usuario no puede estar dos veces en el mismo grupo (`uq_usuario_grupo`) |
| **tareas** | `id_tarea`, `nombre` (100), `descripcion`, `fecha_entrega` (TIMESTAMP), `estado` (def. `'pendiente'`), `dificultad_estimada`, `tiempo_estimado`, `prioridad`, `tiempo_acumulado` (REAL, def. 0), `cronometro_activo`, `ultima_pausa`, `max_archivos` (INTEGER, def. 10, ≥ 1), `id_usuario`, `id_grupo`, `id_categoria` | Ver reglas de tareas abajo |
| **asignacion_tareas** | `id_asignacion`, `fecha_asignacion`, `id_tarea`, `id_integrante` | Una tarea no se asigna dos veces al mismo integrante (`uq_tarea_integrante`) |
| **perfiles** | `id_perfil`, `nombre_usuario` (50), `telefono`, `foto_perfil`, `descripcion`, `notif_activas` (def. true), `limite_cronometro`, `id_usuario` (único) | Un perfil por usuario. `limite_cronometro` es NULL o > 0. No incluye correo ni contraseña |
| **tokens_temporales** | `id_token`, `tipo_token`, `valor_token` (único, 50), `fecha_creacion`, `fecha_expiracion`, `usado`, `id_usuario`, `id_grupo` | `fecha_expiracion` debe ser posterior a `fecha_creacion` |
| **sesiones_cronometro** | `id_sesion`, `fecha_inicio`, `fecha_fin`, `duracion` (REAL), `id_tarea`, `id_usuario` | `duracion` NULL o ≥ 0. `fecha_fin` NULL o ≥ `fecha_inicio` |
| **historial_tareas** | `id_historial`, `fechahora_fin`, `tiempo_real`, `dificultad_real`, `id_usuario`, `id_tarea`, `id_grupo` | `dificultad_real` NULL o 1-5. `tiempo_real` NULL o ≥ 0 |
| **archivos** | `id_archivo`, `nombre` (100), `tamano` (BIGINT), `tipo`, `fecha_adjuncion`, `ruta` (255), `id_tarea` | `tipo` solo `'PDF'`, `'DOCX'`, `'JPG'`, `'PNG'` (en mayúsculas). `ruta` apunta al archivo en disco, no se guarda el archivo en la BD |
| **notificaciones** | `id_notificacion`, `titulo` (máx. 50), `detalles` (máx. 100), `fecha_envio`, `estado` (false = no leída), `tipo` (50), `id_usuario`, `id_tarea` (opcional) | Los textos tienen límite corto: recórtalos antes de insertar |
| **estadistica_categoria** | `promedio_tiempo`, `promedio_dificultad`, `total_tareas`, `id_perfil`, `id_categoria` | `total_tareas` NULL o ≥ 0. `promedio_dificultad` NULL o 1-5 |
| **estadistica_categoria_grupo** | igual que la anterior, pero con `id_grupo` en vez de `id_perfil` | Mismos checks |

## Reglas de negocio críticas

**Tareas**
- **`chk_tarea_owner`:** una tarea tiene **exactamente uno** entre `id_usuario` o `id_grupo`. Nunca ambos, nunca ninguno. El schema `TareaCreate` del backend lo valida igual.
- `dificultad_estimada` entre 1 y 5. `tiempo_estimado` > 0 (en minutos). `prioridad` NULL o > 0.
- `id_categoria` es obligatoria: toda tarea necesita una categoría.
- `max_archivos` es el límite de archivos **por tarea** (al crear una tarea grupal, por defecto 3). Tope fijo del sistema: **10**, nadie puede superarlo. Solo el líder lo cambia, y solo en tareas grupales, nunca por debajo de los archivos que la tarea ya tiene.
- `estado` es texto libre sin `CHECK` en la BD (por defecto `'pendiente'`). Mantén los mismos valores en backend y frontend (Pendiente, En progreso, Completada) para evitar inconsistencias.

**Grupos**
- Solo el `'lider'` puede: expulsar integrantes, eliminar el grupo y crear tareas grupales.
- El líder no puede salir de su propio grupo.
- Solo un integrante con la tarea asignada (`asignacion_tareas`) puede subir archivos a ella.

**Eliminaciones (qué se borra en cascada)**
- Eliminar un **grupo** borra: integrantes, tareas del grupo, tokens, historial y estadísticas del grupo. Por las tareas, también caen asignaciones, archivos, sesiones y notificaciones de esas tareas.
- Eliminar una **tarea** borra: asignaciones, archivos, sesiones del cronómetro, historial y notificaciones.
- Eliminar un **usuario** borra su perfil, sesiones, historial, notificaciones y tokens. **No** borra sus `integrantes` ni sus `tareas` (esas FK no tienen `ON DELETE CASCADE`): primero hay que limpiarlas, o la BD rechaza el borrado.
- Las **categorías** no se pueden eliminar si hay tareas que las usan.

## Estado de uso (qué tablas ya tienen lógica en el backend)
- Con lógica: `usuarios`, `categorias`, `grupos`, `integrantes`, `tareas`, `asignacion_tareas`, `perfiles`, `archivos`, `notificaciones`, `sesiones_cronometro`.
- Pendientes: `estadistica_categoria` y `estadistica_categoria_grupo` (RF-018), `historial_tareas` (alimenta la prioridad automática, RF-025) y `tokens_temporales`.

## Índices existentes
Sobre `tareas` (nombre, fecha_entrega, usuario, grupo, categoría), `integrantes`, `asignacion_tareas`, `sesiones_cronometro`, `historial_tareas` (tarea, usuario), `archivos` y `notificaciones`. Si agregas filtros nuevos (ej. por estado), evalúa si necesitan índice.

## Cómo ejecutar el script
Ejecutar **una sola vez** sobre una base `acadex` vacía: crea las 14 tablas, los índices y las 9 categorías iniciales. Si cambias una tabla ya creada, usa un `ALTER TABLE` y refléjalo también en `acadex.sql`.
