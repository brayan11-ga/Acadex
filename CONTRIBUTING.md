# Cómo colaborar en Acadex

Crea una issue antes de comenzar y trabaja en una rama propia. El recorrido habitual es: issue, tablero, rama desde `develop`, cambios y pruebas, PR a `develop`, revisión e integración.

Para preparar el entorno, sigue el [README](README.md). Esta guía se ocupa del trabajo en equipo.

## 1. Registra la tarea

Busca primero en las [issues](https://github.com/brayan11-ga/Acadex/issues) para no duplicar trabajo. Si no existe, crea una con la plantilla que corresponda:

- **Reporte de bug:** algo falla y puedes explicar cómo reproducirlo.
- **Tarea o funcionalidad:** necesitas añadir o mejorar un comportamiento.
- **Tarea técnica, investigación o documentación:** mantenimiento, infraestructura, investigación o documentación.

Escribe un título concreto: «El cronómetro permite iniciar dos sesiones para la misma tarea» ayuda más que «Arreglar backend».

Incluye el problema, el resultado esperado y criterios de aceptación que otra persona pueda comprobar. Para un error, añade pasos mínimos, resultado actual, resultado esperado y entorno. Enlaza RF/RNF si ayudan a entender el cambio. No pegues secretos ni datos de usuarios.

Puedes omitir una issue nueva para una corrección editorial mínima o un ajuste que ya pertenece a una issue abierta. Justifica la excepción en el PR. Si una urgencia obliga a empezar antes del registro, documenta el motivo y crea la issue antes de pedir revisión.

**Ejemplo ilustrativo: la issue #123 no identifica una tarea real en esta guía.**

```markdown
Título: Documentar el inicio manual con PostgreSQL local

Problema:
Después de clonar, no queda claro cómo crear la base ni aplicar el esquema.

Resultado esperado:
Un compañero puede iniciar API e interfaz sin usar credenciales de producción.

Criterios de aceptación:
- [ ] Se indica cómo preparar y comprobar PostgreSQL local.
- [ ] Los comandos de backend y frontend indican su directorio.
- [ ] Se explica cómo aplicar Alembic y comprobar /health/ready.
- [ ] El README enlaza la guía sin repetirla completa.

Fuera de alcance: cambiar código o desplegar a producción.
```

## 2. Asigna etiquetas y responsable

En la issue, selecciona las [etiquetas existentes](https://github.com/brayan11-ga/Acadex/labels). Este catálogo se comprobó el 21 de octubre de 2026:

| Qué clasificar | Etiquetas disponibles |
| --- | --- |
| Tipo | `bug`, `enhancement`, `documentation`, `question`, según el trabajo |
| Área técnica | `frontend`, `backend`, `database`; para documentación, `documentation` |
| Prioridad | `P0 - Crítica`, `P1 - Alta`, `P2 - Media` |

No hay una etiqueta de infraestructura ni de prioridad baja en el catálogo consultado. Usa el campo `Area` del Project para `Infrastructure`; no inventes una etiqueta. Otras etiquetas, como `duplicate`, `invalid`, `wontfix`, `help wanted` y `good first issue`, sirven para clasificar casos concretos.

Asigna a la persona que llevará la tarea. Acuerda la prioridad con el equipo si todavía no está clara. Para la issue ilustrativa, podrías usar `documentation` y `P2 - Media`.

## 3. Añade la issue al tablero

En la sección **Projects** de la issue, selecciona [Tablero Acadex - Desarrollo](https://github.com/users/brayan11-ga/projects/2). También está enlazado en [Projects del repositorio](https://github.com/brayan11-ga/Acadex/projects).

Completa los campos reales del tablero:

| Campo | Opciones verificadas |
| --- | --- |
| `Status` | `Product Backlog`, `Sprint Backlog / todo`, `In progress`, `In review / QA`, `Done` |
| `Priority` | `P0 - Critica`, `P1 - Alta`, `P2 - Media`, `baja` |
| `Area` | `Frontend`, `Backend`, `Database`, `Infrastructure`, `Docs` |

Las etiquetas de GitHub y los campos del Project son datos distintos. Por ejemplo, la etiqueta lleva tilde en `P0 - Crítica`, pero el campo usa `P0 - Critica`. Selecciona las opciones existentes y comprueba ambos lugares; no se verificó una automatización que los sincronice. Para `baja` no existe una etiqueta equivalente.

Una tarea por priorizar queda en `Product Backlog`. Cuando el equipo la selecciona para el sprint, pasa a `Sprint Backlog / todo`. **Al comenzar, cambia `Status` a `In progress`.** Si aparece un bloqueo, deja el motivo y la dependencia en la issue; no hay un estado «Blocked» en el catálogo consultado.

Las plantillas de issues ya existen como formularios YAML en [.github/ISSUE_TEMPLATE](.github/ISSUE_TEMPLATE). Sus preguntas de áreas e impacto son texto del reporte, no campos del Project ni etiquetas automáticas. Completa la clasificación en GitHub después de crear la issue. En bugs o tareas técnicas, escribe también los criterios de aceptación en el resultado esperado o en «Cómo se verificará».

## 4. Crea una rama desde develop

| Rama | Para qué se usa | Qué PR recibe |
| --- | --- | --- |
| `develop` | Integración del trabajo del equipo | Funcionalidades, correcciones, pruebas y documentación |
| `main` | Entregas; es la rama predeterminada | PR de liberación desde `develop` |

Este flujo coincide con los PR consultados: por ejemplo, el #54 se integró en `develop` y el #52 llevó `develop` a `main`. No hagas commits directamente en `main` ni en `develop`.

El historial usa `feature/` y también `feat/` para funcionalidades, `fix/` para errores y `chore/` para mantenimiento. La rama de esta revisión usa `docs/`. No se encontró una regla única que valide nombres. Usa un prefijo existente, una descripción breve y el número de issue cuando ayude a identificarla: `fix/123-sesion-duplicada` o `docs/123-inicio-local` son ejemplos, no ramas que debas reutilizar.

Con tu árbol de trabajo limpio, desde la raíz:

```sh
git status --short
git fetch origin
git switch develop
git pull --ff-only origin develop
git switch -c docs/123-inicio-local
```

Sustituye el número y nombre por los de tu tarea. Si tienes cambios pendientes o `pull --ff-only` no puede avanzar, resuélvelos antes de continuar; no uses un reset para descartarlos.

## 5. Haz cambios pequeños y compruébalos

Mantén cada commit centrado en un cambio que se pueda revisar. No mezcles una corrección con reformateos o refactorizaciones ajenas. Si compartes archivos o contratos con otra tarea, coordina el cambio en la issue.

Ejecuta las [validaciones del área afectada](docs/calidad-y-pruebas.md). Para documentación, comprueba enlaces, rutas, comandos y diff. Para esquema o consultas, usa las pruebas PostgreSQL aisladas; nunca Supabase ni la base personal de otro compañero.

Antes de guardar un commit, desde la raíz:

```sh
git diff
git add README.md docs/inicio-manual.md
git diff --cached
git commit -m "docs: explica el inicio manual con PostgreSQL local (#123)"
```

Los archivos y el mensaje son ilustrativos. Añade solo los archivos de tu cambio. El historial usa prefijos como `fix:`, `feat:`, `docs:` y `test:`; no se encontró un validador de formato de commits. Escribe mensajes concretos y relaciona el trabajo con su issue.

No incluyas `.env`, claves, respaldos, adjuntos ni archivos generados ajenos al cambio. Si cambias una instrucción de uso, actualiza su guía; consulta el [índice](docs/README.md) para saber dónde mantenerla.

## 6. Sube la rama y abre el PR

Desde la raíz, para la rama ilustrativa:

```sh
git push -u origin docs/123-inicio-local
```

En GitHub, crea el Pull Request con **base: `develop`** y tu rama como origen. Revisa la base: GitHub puede sugerir `main` porque es la predeterminada. Usa un borrador si todavía no está listo para revisar.

Completa la [plantilla del PR](.github/PULL_REQUEST_TEMPLATE.md): explica qué cambia y por qué, enlaza la issue, indica las pruebas ejecutadas y sus resultados, y señala lo pendiente. Solicita revisión a un compañero. Cuando esté listo, cambia la issue a `In review / QA`.

Ejemplo de contenido para el PR de documentación, también ilustrativo:

```markdown
Título: docs: explica el inicio manual con PostgreSQL local
Base: develop
Issue relacionada: Refs #123

Qué cambia y por qué:
Añade una guía de base local, migraciones y terminales de API e interfaz.
El README enlaza el procedimiento para evitar instrucciones duplicadas.

Pruebas y comprobaciones:
- git diff --check: sin errores (resultado ilustrativo).
- Enlaces relativos y rutas: revisados (resultado ilustrativo).
- Arranque completo: no ejecutado; pendiente de probar en un clon nuevo.

Revisión solicitada:
Comprobar que un clon nuevo tiene todos los pasos necesarios.
```

### Qué significa #123 y cuándo cierra GitHub la issue

- `#123` en un commit crea una referencia; por sí sola **no cierra** la issue.
- `Closes #123` en la descripción cierra la issue cuando el PR se fusiona en la rama predeterminada: aquí, `main`.
- Hacia `develop`, GitHub ignora esa palabra: no crea el vínculo de cierre ni cierra la issue al fusionar.
- Para `develop`, escribe `Refs #123` y comprueba el cierre manual. Si la tarea debe esperar a `main`, mantenla abierta y añade `Closes #123` al PR de liberación que la complete.
- Una palabra de cierre en un commit también puede cerrar la issue cuando ese commit llega a `main`. Prefiere referencias simples en los commits.

El comportamiento está descrito en la [documentación de GitHub](https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/linking-a-pull-request-to-an-issue). No supongas que el texto de cierre de un PR anterior a `develop` se trasladará automáticamente al PR de liberación.

## 7. Resuelve la revisión

Responde cada comentario o aplica el ajuste. Haz commits nuevos en la misma rama, repite las pruebas afectadas y ejecuta `git push`; el PR se actualiza automáticamente. Explica qué cambió y vuelve a solicitar revisión cuando corresponda.

Antes de integrar, comprueba los criterios de aceptación, CI, la aprobación de otra persona y las conversaciones resueltas. Son las condiciones de colaboración que ya recogía la guía del equipo; no equivalen a afirmar que GitHub las imponga todas.

## 8. Integra y comprueba el cierre

Para los PR habituales, la guía del equipo indica **Squash and merge**. Úsalo cuando esté disponible y conserva la referencia a la issue en el mensaje final. La liberación `develop` a `main` debe coordinarse con el responsable; confirma su método de fusión y no elimines ninguna de esas dos ramas.

La consulta pública del 21 de octubre de 2026 marca `main` y `develop` como protegidas. No permitió leer el detalle de las protecciones. **Pendiente de confirmar con quien administra GitHub:** aprobaciones exigidas, checks obligatorios, descarte de aprobaciones tras nuevos commits, restricciones de force push/borrado, métodos de fusión habilitados y automatizaciones del Project. No intentes saltar una protección si GitHub bloquea la integración.

Después de fusionar:

1. Comprueba que el PR quedó integrado en la rama prevista.
2. Si la tarea termina en `develop`, verifica los criterios, comenta el enlace al PR y cierra la issue manualmente si sigue abierta.
3. Si sus criterios incluyen la entrega en `main`, déjala abierta hasta cumplirlos. Comprueba entonces el cierre del PR de liberación.
4. Mueve la tarjeta a `Done` solo cuando se cumplan todos los criterios. Revisa el estado aunque esperes una automatización.

## 9. Limpia la rama terminada

Elimina en GitHub la rama temporal cuando el PR esté integrado y nadie la necesite. No borres `develop` ni `main`. Después, desde la raíz:

```sh
git switch develop
git pull --ff-only origin develop
git fetch --prune origin
git branch -d docs/123-inicio-local
```

Tras un squash, `git branch -d` puede rechazar el borrado porque no encuentra los commits originales en `develop`. Comprueba que el PR esté fusionado, que su contenido esté integrado y que la rama no tenga trabajo pendiente antes de usar `git branch -D` con el nombre exacto. No lo uses como limpieza automática.
