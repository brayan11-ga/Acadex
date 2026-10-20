<!-- Ruta: docs/decisiones/tareas-grupales.md (dentro de docs/, en una carpeta nueva "decisiones") -->

# Tareas grupales: decisiones, hallazgos y pendientes

Documento de trabajo (17 de octubre de 2026). Reúne lo que se decidió, lo que se encontró al revisar el código de `tarea_service.py` y el inventario de endpoints, y lo que falta por confirmar. Está pensado para consultarlo antes de pedirle trabajo a V0 y a los agentes.

---

## 1. Reglas acordadas

### Permisos
- Solo el **líder** edita, elimina y reasigna tareas grupales (es quien las crea).
- Cualquier **integrante del grupo** puede ver el detalle de una tarea y sus asignados (corrige el bug de RF-045).
- Una tarea **completada** no se puede editar ni reasignar. Para cambiarla, el líder usa la acción explícita **Reabrir** (con confirmación), que la devuelve a "en progreso".
- El líder puede eliminar una tarea completada, con una advertencia fuerte (sale del historial).

### Reasignación (quitar a un asignado)
- Se borran, **solo de esa tarea y de esa persona**: sus archivos, sus sesiones de cronómetro y su registro en el historial. Después se recalcula su estadística de esa categoría.
- El líder recibe una confirmación antes de reasignar. El afectado recibe una notificación. Si la tarea se había reabierto, también se avisa a los asignados que siguen.
- Si el borrado de un archivo falla en Supabase, la reasignación **no falla**: se completa y el archivo queda anotado para limpieza posterior.

### Completar
- Cada asignado completa **su parte**. Al hacerlo se le pide la **dificultad real** (1 a 5). El **tiempo real** sale del cronómetro y se muestra solo como lectura; si es cero, aparece una advertencia pero puede continuar.
- Si la persona no subió archivos, se le pregunta si quiere entregar de todos modos. Se evalúa por persona, no por tarea.
- La tarea pasa a completada cuando **todos** los asignados completaron su parte. El líder puede cerrarla antes.
- Cuando nadie ha subido ningún archivo, la tarea muestra un **ícono de "sin archivos"** (lo diseña Sam).

### Cronómetro
- Solo los **asignados** ven y manejan su propio cronómetro de una tarea grupal, en una sección propia dentro del detalle ("Mi cronómetro": iniciar, pausar, reiniciar).
- El panel del modo individual **no** muestra tareas grupales, y se mantiene así.
- Una tarea grupal pasa a "en progreso" cuando algún asignado sube un archivo o inicia el cronómetro (por confirmar con el código).

### Estadísticas y priorización
- El historial de tareas grupales **no cuenta** para la priorización de las tareas individuales. Evita mezclar datos y mantiene los cálculos simples.

### Archivos
- El líder define un **límite de archivos** al crear la tarea, para evitar abusos y proteger el rendimiento (ver la recomendación en la sección 6).

### Fechas
- Al cambiar la fecha de entrega de una tarea grupal: diálogo de confirmación, aviso a los asignados y no se permiten fechas en el pasado. Cambiar nombre, descripción o categoría no genera notificación.

### Seguridad
- Hay que proteger los endpoints amplios (ver sección 6). Se consulta con el equipo antes de decidir.

---

## 2. Qué dice el código hoy

Basado en `tarea_service.py`, `sesion_cronometro_service.py` (solo los nombres de las funciones) y el inventario de `openapi.json`.

| # | Hallazgo | Qué implica |
|---|---|---|
| 1 | En `actualizar_tarea`, un asignado que no es líder **puede cambiar el `estado`** de una tarea grupal, por ejemplo a "completada". | Hoy cualquier asignado cierra la tarea para todos. Es la opción C que se descartó. |
| 2 | Al completar, el historial guarda `dificultad_real = dificultad_estimada` y `tiempo_real = tarea.tiempo_acumulado`. | **RF-016 no está implementado**: la dificultad real nunca se pide. Además `tiempo_acumulado` es un solo valor por tarea, no por persona. Afecta también a las tareas individuales. |
| 3 | Al completar se crea **una sola** fila de historial, para quien presionó el botón. | Para completar "por persona" hay que crear una fila por asignado, con su propio tiempo. |
| 4 | Una tarea completada **sí se puede actualizar** (no hay bloqueo). Reabrir ya existe en la práctica, cambiando el `estado` por `PUT`, y el historial anterior se conserva. | Si se reabre y se completa de nuevo, se agrega otra fila: la misma persona queda **dos veces** en los promedios. Conviene un `upsert` (una fila por usuario y tarea). |
| 5 | Al completar se llama a `recalcular_estadistica_categoria(usuario, categoría)`: la estadística está **guardada**, no calculada al vuelo. | Si se borra una fila de historial, hay que volver a recalcular esa categoría para esa persona. Falta ver si el recálculo excluye las tareas grupales (decisión de la sección 1). |
| 6 | `listar_asignados_de_tarea` solo deja pasar al líder o a un asignado. | Es el bug de RF-045. `obtener_tarea` ya garantiza que quien llega es miembro del grupo. |
| 7 | `verificar_permiso_tarea` con la acción `"cronometro"` ya limita las tareas grupales a los **asignados**. | La regla que propuso Sam ya existe a nivel de permisos. Falta que el cronómetro de la tabla `tareas` (`cronometro_activo`, `tiempo_acumulado`) sea por persona. |
| 8 | `eliminar_tarea` usa `preparar_eliminacion_archivos_tarea`, no bloquea tareas completadas y no avisa a nadie. | Ya existe el patrón para limpiar archivos. Falta la notificación. |
| 9 | `crear_tarea_grupal` deja crear a un **administrador** en cualquier grupo, no notifica a los asignados y no valida ids repetidos, lista vacía ni fecha pasada (a menos que lo haga el schema). | Confirmar si el permiso de admin es intencional. |
| 10 | Hay **dos formas** de crear una tarea de grupo: `POST /tareas/` con `id_grupo` (sin asignados) y `POST /tareas/grupos/{id}`. | Aclarar cuál es la oficial para no mantener dos caminos. |
| 11 | Los listados (`/tareas/`, tareas de un grupo) no tienen paginación. | Riesgo en pruebas de estrés si crecen los datos. |
| 12 | `estado` es texto libre, sin `CHECK`, y el código compara `"completada"` en minúscula. | Mantener los mismos valores en backend y frontend. |
| 13 | Existen `estadistica_service.py` y `estadisticas_service.py`. | Posible duplicado. Revisar si uno sobra. |
| 14 | No hay endpoints para **leer notificaciones**. | Sin ellos no hay campanita en la interfaz. |
| 15 | `sesiones-cronometro` solo tiene iniciar, listar y finalizar. | Falta reiniciar (RF-034) y obtener el tiempo por integrante de una tarea. |

---

## 3. Endpoints: reciclar, ajustar y crear

### Existen y se reciclan (con ajustes)
| Endpoint | Ajuste |
|---|---|
| `GET /tareas/{id}` (detalle) | Sin cambio de permisos (miembros del grupo). |
| `PUT /tareas/{id}` (actualizar) | Grupales: solo el líder. Bloquear si está completada. Validar fecha. Notificar si cambia la fecha. **Quitar** que un asignado pueda cambiar el `estado`. |
| `DELETE /tareas/{id}` | Notificar a los asignados. Advertencia en la interfaz. |
| `GET /tareas/{id}/asignados` | Abrir a cualquier miembro del grupo. |
| `POST/GET/DELETE /tareas/{id}/archivos` | Aplicar el límite de archivos. Solo quien subió un archivo puede borrarlo individualmente. |
| `POST /sesiones-cronometro/iniciar` y `PATCH .../finalizar` | Adaptar a tareas grupales (cronómetro por persona). |

### Nuevos
| Endpoint propuesto | Quién | Reglas |
|---|---|---|
| `PUT /tareas/{id}/asignados` (reasignar) | Líder | Bloqueado si está completada. Borra el avance de quien sale. Notifica a los afectados. |
| `POST /tareas/{id}/completar` | Asignado (solo tareas grupales) | Recibe la dificultad real. Crea o actualiza la fila de historial de esa persona. La tarea se completa cuando todos terminan. En tareas grupales reemplaza el uso de `PUT` con `estado`. Las tareas individuales siguen completándose por `PUT`. |
| `POST /tareas/{id}/reabrir` | Líder | Solo si está completada. Vuelve a "en progreso". Avisa a los asignados. |
| `POST /tareas/{id}/cerrar` (opcional) | Líder | Cierra antes de que todos terminen. |
| Reiniciar cronómetro de mi parte | Asignado | Borra mis sesiones de esa tarea. Nombre por definir. |
| `GET /tareas/{id}/tiempos` | Miembros del grupo | Tiempo real por integrante (RF-017). |
| `GET /notificaciones` y marcar como leída | Usuario autenticado | Hoy no existen. |

Las notificaciones de asignación, reasignación, reapertura, eliminación y cambio de fecha **no son endpoints**: se envían automáticamente dentro de esas operaciones.

---

## 4. Cambios en la base de datos

- **Límite de archivos:** columna nueva en `tareas` (propuesta: `max_archivos_por_integrante`, entero con `CHECK` entre 1 y 10 y un valor por defecto por definir). Va como migración nueva en `backend/migrations/` (con `IF NOT EXISTS`), más su comprobación en `verify_schema.sql` y la actualización de `database.md`.
- **"Completó su parte":** no hace falta una tabla nueva. Se usa `historial_tareas` (una fila por usuario y tarea, con `upsert`). Si se quiere garantizar la unicidad en la base, habría que revisar primero si ya hay filas duplicadas.

---

## 5. Mensajes

Las notificaciones tienen límites (título 50 caracteres, detalle 100). El nombre de la tarea se **recorta a 35 caracteres con "…"**.

### Notificaciones
| Para quién | Título | Detalle |
|---|---|---|
| Asignado nuevo | Tienes una tarea nueva | El líder te asignó «{tarea}». Entrega: 30 oct. |
| Quitado (con avance) | Ya no estás asignado a una tarea | El líder te quitó de «{tarea}». Se borraron tus archivos y tu tiempo. |
| Quitado (sin avance) | Ya no estás asignado a una tarea | El líder te quitó de «{tarea}». |
| Los que siguen, al reabrir | Una tarea volvió a estar en progreso | El líder reabrió «{tarea}». Aún hay partes por entregar. |
| Asignados, al eliminar | Se eliminó una tarea | El líder eliminó «{tarea}» del grupo. |
| Asignados, al cambiar la fecha | *(por redactar)* | *(por redactar, con la fecha nueva)* |

### Confirmaciones
- **Reasignar (quitando a alguien):** "¿Reasignar esta tarea? Vas a quitar a {correo}. Se eliminarán sus archivos y su tiempo registrado, y no se podrá deshacer. Se avisará a las personas afectadas." Botones: Sí, reasignar / Cancelar.
- **Eliminar:** "¿Eliminar «{tarea}»? Se borrarán sus archivos, tiempos y asignaciones para todos. No se puede deshacer."
- **Reabrir:** "¿Reabrir esta tarea? Volverá a estar en progreso y podrás editarla o reasignarla."
- **Mover la fecha:** "Vas a mover la entrega del {fecha anterior} al {fecha nueva}. Se avisará a los asignados. ¿Confirmas?"
- **Completar sin archivos:** "Aún no has subido ningún archivo a esta tarea. ¿Quieres entregarla de todos modos?" Botones: Entregar sin archivos / Volver.
- **Completar sin tiempo registrado:** "No registraste tiempo en el cronómetro. ¿Completar de todos modos?"

---

## 6. Pendiente por consultar o decidir

### Para decidir (Sam)
1. **Límite de archivos: ¿por integrante o por tarea?** Recomendación: **por integrante**. Con un límite total de 2 en una tarea que pide dos documentos (uno por persona), el primer integrante podría subir los dos y bloquear al segundo. Además, un tope absoluto del sistema (por ejemplo 10) protege el rendimiento. Falta definir el valor por defecto.
2. **Historial al reabrir y completar de nuevo:** ¿`upsert` (una fila por usuario y tarea) o seguir agregando filas? Recomendación: `upsert`.
3. **Tareas individuales completadas:** hoy se pueden editar y reabrir cambiando el estado. ¿Se mantiene así o se aplica también la regla de bloqueo?
4. **¿El cronómetro de tareas grupales cuenta para el límite continuo del perfil** (RF-032 y RF-033)?
5. **Interfaz de notificaciones:** ¿campanita con lista? Hoy no hay endpoints de lectura.
6. **RF-005 (regenerar el código de acceso):** no veo un endpoint para esto en el inventario. Confirmar si existe o si falta.

### Para consultar con el equipo
- **Seguridad de endpoints amplios** (se probará con intentos de ruptura):
  - `GET /grupos/` ("todos los grupos"): ¿expone códigos de acceso a cualquier usuario?
  - `GET /usuarios/`, `GET /perfiles/usuario/{id}` y `PUT /usuarios/{id}`: ¿quién puede llamarlos?
  - Rutas `/admin`: ¿validan `es_admin` en el backend (RF-058)?
  - Panel de líder: ¿el backend valida el rol (RF-053)?
- ¿El permiso del administrador para crear tareas en cualquier grupo es intencional?
- ¿Cuál de las dos rutas para crear tareas de grupo es la oficial?
- ¿`estadistica_service.py` y `estadisticas_service.py` son duplicados?
- El historial grupal **no** cuenta para la priorización individual: confirmarlo con quien hizo RF-007 y RF-009.

### Código que falta por revisar
- `backend/app/services/sesion_cronometro_service.py` (completo): ¿actualiza `tareas.cronometro_activo` y `tiempo_acumulado`? ¿Qué pasa si dos asignados inician a la vez?
- `backend/app/services/estadistica_service.py` (completo): cómo recalcula y si filtra por `id_grupo`.
- `backend/app/services/archivo_service.py`: dónde poner el límite y cómo se borra en Supabase.
- Schemas `TareaUpdate`, `TareaResponse` y `TareaGrupalCreate`.
- Frontend: de dónde sale hoy el botón "Completar" del panel y si ya pide la dificultad real.

---

## 7. Detalles que te pueden servir

### Orden de trabajo sugerido para los agentes
Una tarea por sesión, con su RF y sus escenarios como criterio de aceptación.
1. Redactar los RF nuevos (editar, eliminar, reasignar, completar, reabrir, notificar, límite de archivos, cronómetro grupal, consentimientos, descarga de adjuntos).
2. Corregir el bug de permisos de `GET /tareas/{id}/asignados` (cambio pequeño, sirve para probar el flujo).
3. Migración del límite de archivos y su validación al subir.
4. Endpoint `completar` (con dificultad real, para tareas individuales y grupales) y retiro del cambio de estado por `PUT`.
5. Cronómetro por persona en tareas grupales y `GET .../tiempos`.
6. Reasignar, reabrir y las notificaciones automáticas.
7. Ajustes a actualizar y eliminar (permisos, bloqueo de completadas, aviso de cambio de fecha).
8. Endpoints para leer notificaciones.

Las pantallas de V0 se piden en paralelo, una por sesión: detalle de la tarea (con "Mi cronómetro", contador de archivos, ícono de "sin archivos", Completar y Reabrir), editar con reasignación y límite de archivos, los diálogos de confirmación y la campanita de notificaciones.

### Buenas prácticas para esta tanda
- Cada endpoint nuevo se prueba en Swagger con el caso feliz, el de datos inválidos y el de falta de permisos.
- El borrado del historial al quitar a alguien debe filtrar **siempre** por usuario y tarea a la vez (nunca solo por usuario o por categoría), dentro de la misma transacción, con una prueba que lo verifique.
- Después de cada `git pull`, revisar si llegaron migraciones nuevas: `git diff --name-status HEAD@{1} HEAD -- backend/migrations`.
- Al terminar la migración del límite de archivos, actualizar `database.md` y `memory.md`.
- Para las pruebas de estrés: agregar paginación a los listados y mantener los topes de archivos.

### Pendientes de documentación
- El Excel tiene IDs repetidos: `RF-002` (debería haber un RF-019 y un RF-023) y `RF-031` (debería haber un RF-032).
- Observaciones desactualizadas: RF-036, RF-044 y RF-045 dicen que el frontend está pendiente, y RF-039 dice que falta el desbloqueo (el README de migraciones indica que el bloqueo de 15 minutos ya existe).
- Sumar los RF nuevos y sus escenarios a `docs/RF/`.
- `README.md` de la raíz y la sección de comandos de `AGENTS.md`.

---

## 8. Aclaraciones del 17 de octubre (noche)

Estas respuestas **reemplazan** los puntos de la sección 6 que quedaron abiertos.

1. **Límite de archivos: por tarea**, editable por el líder al crear y al actualizar la tarea. Además hay un **tope fijo del sistema** (constante en la configuración, propuesta: 10) que nadie puede superar, ni siquiera el líder. Queda abierta la puerta a subirlo en una versión de pago. Reglas: no se puede fijar un límite menor al número de archivos que ya tiene la tarea ni mayor al tope. Valor por defecto propuesto en el formulario: 3. En la base, la columna `max_archivos` tendría por defecto el tope (10), para no afectar las tareas existentes y las individuales.
2. **Historial al reabrir y completar de nuevo: `upsert`** (una sola fila por usuario y tarea; si ya existe se actualiza, si no se crea).
3. **Cronómetro de grupos:** no se usa el límite del perfil para pausar solo. Cuando se pase del límite personal se muestra un **aviso** ("El cronómetro ya superó el límite de tu perfil. ¿Quieres pararlo o continuar?"). Se deja para cuando se implemente el cronómetro por persona. No se crea un límite propio del grupo.
4. **Notificaciones (lectura e interfaz): aplazadas**, las hará otra persona del equipo. Las notificaciones sí se siguen **creando** dentro de crear, reasignar y reabrir, aunque todavía no se puedan ver.
5. **Regenerar el código de acceso: sí se necesita**, por seguridad del grupo (si el código se filtra, el líder lo "recarga" y el anterior deja de servir). La regla antigua de esperar 30 minutos entre códigos choca con este uso, y hay que revisarla: el líder debe poder regenerarlo al instante.
6. **Seguridad de los endpoints:** aplazada, no es parte de este trabajo.

## 9. Plan de trabajo

### Esta noche, con Cursor (backend)
| # | Tarea | Listo cuando |
|---|---|---|
| C1 | Corregir el permiso de `GET /tareas/{id}/asignados`: cualquier miembro del grupo | Un miembro no asignado ve la lista; alguien de fuera recibe 403 |
| C2 | Límite de archivos: migración `max_archivos`, tope fijo en la configuración, validación al subir, y que crear y actualizar tarea grupal lo reciban (sin bajar del conteo actual ni pasar el tope). Actualizar `verify_schema.sql` y `database.md` | Sube dentro del límite; falla al pasarse; el líder puede subir el límite; falla si supera el tope |
| C3 | `POST /tareas/{id}/completar` **solo para tareas grupales**: recibe la dificultad real, hace `upsert` del historial de esa persona, calcula el tiempo real desde sus sesiones, completa la tarea cuando todos terminaron y bloquea el cambio de estado por `PUT` en grupales | Los escenarios de completar pasan en Swagger |

### Mañana, con Cursor
- C4: reasignar, reabrir y notificaciones de crear, reasignar y reabrir.
- C5: ajustes a actualizar y eliminar (bloqueo de completadas, fecha, notificación).
- C6: cronómetro por persona y `GET /tareas/{id}/tiempos`.
- C7: regenerar el código de acceso (primero revisar `grupo_service.py`).
- C8: pedir la dificultad real al completar tareas **individuales**, **sin quitar ni cambiar** el botón actual (lo usan el panel y el calendario). Se agrega un campo opcional `dificultad_real` al `PUT` existente: si no llega, todo funciona como hoy. Al terminar, comprobar que el panel y el calendario siguen mostrando la tarea como completada.

### V0 (solo diseño)
- **Esta noche:** una sola pantalla, el **Detalle de tarea grupal**, con la sección "Mi cronómetro", el contador de archivos, el botón "Completar mi parte" con su ventana (tiempo registrado en solo lectura, dificultad real del 1 al 5 y las advertencias), el estado por integrante, y Reabrir, Editar y Eliminar solo para el líder.
- **Sin V0, con el agente a partir de lo que ya existe:** editar tarea (el mismo formulario de crear), el campo del límite de archivos, los diálogos de confirmación y el botón de regenerar código en el panel de líder.

### Fuera de alcance por ahora
Cerrar tarea, límite de cronómetro de grupo, lectura e interfaz de notificaciones, seguridad de endpoints, paginación, los RF nuevos en `docs/RF/` y el ícono de "sin archivos".

### Para no dejar nada a medias
- Una rama propia y un commit por tarea terminada. No hacer push a la rama que despliega el sitio.
- La migración de C2 se aplica primero en local y **antes de desplegar** en producción. Si no, pasará lo mismo que con el 503: el código espera una columna que no existe.
- Cada tarea termina actualizando `memory.md` con tres líneas: qué se hizo, qué falta y cuál es la siguiente tarea.
