# Requisitos no funcionales de Acadex

Total: **32** requisitos no funcionales, organizados por categoría. Cada uno tiene su propio archivo. Estos documentos definen objetivos y restricciones; no son por sí mismos evidencia de que un objetivo ya se haya medido o cumplido. Para planificar o validar un cambio, registra la evidencia en su Issue o Pull Request. El mapa de fuentes canónicas está en [docs/README.md](../README.md).

## Seguridad y privacidad (9)

| ID | Requisito |
|---|---|
| [RNF-002](RNF-002.md) | La app debe garantizar el cifrado de contraseñas |
| [RNF-003](RNF-003.md) | Los archivos subidos (PDF, DOCX, JPG, PNG) deben almacenarse de forma segura |
| [RNF-004](RNF-004.md) | La autenticación con Google debe cumplir protocolos seguros (OAuth 2.0). |
| [RNF-005](RNF-005.md) | El acceso a grupos mediante código debe ser único, temporal y no predecible |
| [RNF-022](RNF-022.md) | El sistema debe garantizar que solo los integrantes de un grupo puedan ver la información, tareas y métricas d… |
| [RNF-023](RNF-023.md) | El sistema debe restringir la creación/asignación de tareas grupales, la expulsión de integrantes y la elimina… |
| [RNF-024](RNF-024.md) | Los archivos subidos deben validarse en tipo y formato antes de almacenarse, y analizarse para descartar conte… |
| [RNF-028](RNF-028.md) | Los datos personales de la cuenta deben protegerse, y eliminarse al eliminar la cuenta |
| [RNF-029](RNF-029.md) | El enlace o código de recuperación de contraseña enviado por correo debe ser único, de un solo uso y expirar e… |

## Desempeño y escalabilidad (7)

| ID | Requisito |
|---|---|
| [RNF-001](RNF-001.md) | La app debe responder en menos de 2 segundos en operaciones comunes (crear tarea, unirse a grupo, subir archiv… |
| [RNF-006](RNF-006.md) | El sistema debe recalcular y actualizar la prioridad de las tareas en menos de 2 segundos después de completar… |
| [RNF-007](RNF-007.md) | La carga de archivos no debe afectar significativamente el rendimiento general |
| [RNF-008](RNF-008.md) | El sistema debe soportar múltiples usuarios simultáneos sin degradar el rendimiento |
| [RNF-026](RNF-026.md) | Las notificaciones deben entregarse en menos de 5 segundos desde el evento, incluso con la app en segundo plan… |
| [RNF-027](RNF-027.md) | El tiempo de cálculo de prioridad debe mantenerse estable a medida que crece el historial de tareas por catego… |
| [RNF-032](RNF-032.md) | La búsqueda de tareas debe devolver resultados en menos de 1 segundo |

## Confiabilidad y disponibilidad (7)

| ID | Requisito |
|---|---|
| [RNF-009](RNF-009.md) | La aplicación debe estar disponible al menos el 99% del tiempo |
| [RNF-010](RNF-010.md) | Debe contar con mecanismos de respaldo (backup) de la información. |
| [RNF-020](RNF-020.md) | El sistema debe evitar pérdida de datos al crear/editar tareas |
| [RNF-021](RNF-021.md) | El sistema debe manejar errores (ej. fallo de red) sin afectar los datos del usuario mencionándoles en un mens… |
| [RNF-025](RNF-025.md) | El cronómetro debe mantener la precisión del tiempo y conservar el progreso acumulado aunque la app se cierre,… |
| [RNF-030](RNF-030.md) | Al eliminar un grupo, el sistema debe borrar de forma completa y consistente toda la información asociada (tar… |
| [RNF-031](RNF-031.md) | El cronómetro debe registrar el tiempo con precisión y conservar el progreso aunque la app se cierre o pierda… |

## Usabilidad (3)

| ID | Requisito |
|---|---|
| [RNF-011](RNF-011.md) | La interfaz debe ser intuitiva y fácil de usar (especialmente para gestión de tareas) |
| [RNF-012](RNF-012.md) | Debe permitir navegación clara entre modo individual y grupal |
| [RNF-013](RNF-013.md) | El proceso de registro e inicio de sesión debe ser simple y rápido |

## Mantenibilidad (2)

| ID | Requisito |
|---|---|
| [RNF-014](RNF-014.md) | El código debe estar estructurado para facilitar actualizaciones (ej. agregar nuevas funciones) |
| [RNF-015](RNF-015.md) | Debe permitir corrección de errores sin afectar otras funcionalidades |

## Compatibilidad (2)

| ID | Requisito |
|---|---|
| [RNF-016](RNF-016.md) | La app debe funcionar en diferentes dispositivos (PC, tablet, móvil) |
| [RNF-017](RNF-017.md) | Debe ser compatible con los principales navegadores (Chrome, Edge, etc.) |

## Almacenamiento (2)

| ID | Requisito |
|---|---|
| [RNF-018](RNF-018.md) | Debe definir un límite de tamaño para archivos subidos |
| [RNF-019](RNF-019.md) | Debe gestionar eficientemente el almacenamiento de documentos y datos |
