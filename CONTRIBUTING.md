# Contribuir a Acadex

Esta guía define el flujo oficial para llevar un cambio desde una necesidad hasta su integración. El código y la configuración son la fuente de verdad de ejecución; los [requisitos funcionales](docs/RF/README.md) y [no funcionales](docs/RNF/README.md) son la fuente de verdad del alcance de producto.

Las reglas de ramas, revisión, integración y planificación descritas aquí son política establecida por el equipo. El repositorio local no permite verificar si todos los ajustes administrativos equivalentes ya están activos en GitHub; esa verificación y configuración corresponde a quienes administran el repositorio.

## Flujo de trabajo

| Etapa | Qué debe quedar registrado | Condición para avanzar |
| --- | --- | --- |
| 1. Entender la necesidad | Issue existente o nueva, requisitos y contexto técnico relacionados | El objetivo y el resultado esperado son comprensibles |
| 2. Planificar | Responsable, prioridad, área y estado en el GitHub Project existente de Acadex | El alcance, dependencias y criterios de aceptación están claros |
| 3. Crear rama | Rama específica desde develop | La rama contiene un único propósito |
| 4. Implementar | Cambios acotados, decisiones relevantes y migraciones incluidas cuando proceda | El cambio respeta requisitos y no añade secretos |
| 5. Verificar | Comandos ejecutados, resultado y límites de la comprobación | El autor revisó su propio diff |
| 6. Abrir Pull Request | Contexto, Issue, pruebas, impacto y riesgos | El PR se dirige a develop, salvo una liberación |
| 7. Revisar e integrar | Aprobación independiente, CI correcto y conversaciones resueltas | Se cumplen los controles definidos en esta guía |
| 8. Cerrar | Issue cerrada y tarjeta del Project actualizada | El resultado y su evidencia están vinculados |

## Issues y GitHub Projects

Toda necesidad de funcionalidad, corrección, trabajo técnico, investigación o documentación se registra en una Issue. Antes de crearla, consulta las Issues y los requisitos pertinentes. Una Issue debe describir el problema, resultado esperado, alcance y fuera de alcance, criterios de aceptación comprobables, áreas afectadas, dependencias y pruebas previstas.

El GitHub Project existente de Acadex centraliza planificación y seguimiento. La Issue debe tener una persona responsable y mantenerse actualizada con estos campos:

| Campo | Valores | Objetivo |
| --- | --- | --- |
| Status | product baclog, sprint backlog, In progress, in rewiev, done | Distinguir trabajo por priorizar, planificado, en curso, en revisión e integrado |
| Priority | Alta, Media o sin valor asignado | Visibilizar la urgencia relativa sin inventar una prioridad |
| Area | Frontend, Backend, Database, Infrastructure, Docs | Identificar el componente o especialidad principal afectada |

Cuando una Issue entra al flujo, debe aparecer en el Project y pasar por sus estados hasta **done** al integrarse. El uso de automatizaciones para añadir Issues o actualizar el estado al cerrarlas no puede verificarse desde el repositorio local. Mientras no se confirme su configuración administrativa, quien abre, desarrolla o integra el trabajo debe comprobar manualmente que la tarjeta exista y tenga el estado correcto.

Usa la plantilla adecuada:

- **Tarea** para funcionalidad o mejora de comportamiento.
- **Bug** para una diferencia reproducible entre el resultado esperado y el actual.
- **Técnica** para refactorización, infraestructura, investigación o documentación.

Los bugs urgentes siguen el mismo registro mínimo: Issue, rama, pruebas y PR. Una investigación puede cerrar con hallazgos y próximos pasos en lugar de código, dejando claro qué no se verificó.

## Ramas y commits

Las ramas de trabajo se crean desde **develop** actualizado. Usa nombres descriptivos: **feature/nombre-funcionalidad** para funcionalidades y **fix/nombre-correccion** para correcciones. Una rama debe corresponder a una Issue o a un cambio claramente delimitado.

~~~sh
git fetch origin
git switch develop
git pull --ff-only
git switch -c feature/nombre-funcionalidad
~~~

Los Pull Requests de funcionalidades y correcciones se dirigen a **develop**. Las liberaciones se realizan mediante un Pull Request de **develop** hacia **main**, sujeto a los mismos controles de protección.

Los mensajes de commit deben ser descriptivos, comprensibles y coherentes con el cambio. No existe una convención formal de formato de mensajes; no se exige Conventional Commits. Mantén los commits acotados al propósito de la rama y no mezcles refactorizaciones no relacionadas, cambios masivos de formato ni secretos con una corrección funcional.

## Implementar y probar

Cuando un cambio toca frontend, backend y datos, una misma Issue debe explicitar el contrato entre ellos: comportamiento de API, datos o migración involucrada, tratamiento de errores y orden de entrega. Divide el trabajo en subtareas solo si sus resultados pueden verificarse y revisarse de forma independiente.

Antes de modificar archivos compartidos —por ejemplo, modelos, rutas, migraciones, contratos de API o estilos globales— avisa en la Issue o en el canal de coordinación del equipo. Esto reduce implementaciones incompatibles sin bloquear cambios pequeños e independientes.

Ejecuta las validaciones proporcionales al área cambiada antes de abrir el PR. La referencia de comandos y alcance es [docs/calidad-y-pruebas.md](docs/calidad-y-pruebas.md).

- **Frontend:** al menos pnpm lint, pnpm build y las pruebas afectadas o pnpm test --run.
- **Backend sin PostgreSQL:** python -m pytest test tests -q desde backend, cuando el entorno local esté preparado.
- **Migraciones, SQL o integración con PostgreSQL:** las suites aisladas de docker-compose.test.yml, nunca una base personal, compartida o de producción.
- **Configuración o Docker:** docker compose config y el arranque o verificación que corresponda, sin exponer valores privados.

Registra los comandos realmente ejecutados y su resultado. Si una validación no pudo ejecutarse, explica por qué y qué queda por comprobar; no la marques como completada.

### Migraciones, datos y secretos

Alembic es la ruta vigente del esquema. Una migración nueva debe estar revisada, acompañar el cambio de código que la necesita y poder aplicarse sobre una base de prueba aislada. No uses stamp, SQL histórico, upgrade ni comandos destructivos sobre una base existente sin seguir la [guía de datos](database/README.md) y, para una adopción excepcional, la [guía de Alembic](docs/DESPLIEGUE_ALEMBIC.md).

Nunca incluyas .env, contraseñas, tokens, claves de proveedores, datos de usuarios, volcados de PostgreSQL o adjuntos en la rama o el PR. Las plantillas .env.example solo pueden contener valores ilustrativos y no secretos.

## Pull Requests, revisión e integración

Completa la plantilla de Pull Request. Resume qué cambia y por qué; enlaza la Issue y usa **Closes #N** cuando el PR la resuelva por completo. Declara las pruebas, el impacto en frontend, backend, datos, infraestructura y documentación, y los riesgos que merecen atención.

Antes de integrar un PR deben cumplirse estas condiciones:

1. Los controles de CI configurados terminan correctamente.
2. Al menos una persona distinta del autor aprueba el cambio.
3. Todas las conversaciones de revisión están resueltas.
4. El autor incorporó las observaciones necesarias y revisó el diff final.

Los Pull Requests habituales se integran mediante **Squash and merge** para conservar un historial compacto. Las ramas temporales de feature o fix pueden eliminarse después de integrarse cuando ya no se necesiten. **develop** y **main** se conservan: no se eliminan como ramas de origen de un Pull Request de liberación. Esta guía no presupone que la eliminación automática de ramas esté activada o desactivada en GitHub.

Quien revisa debe comprobar, en proporción al cambio:

- que el alcance corresponde a la Issue y a los requisitos citados;
- que los criterios de aceptación y casos de error están cubiertos;
- que migraciones, API y cliente son compatibles cuando intervienen;
- que las pruebas informadas son pertinentes y que no hay secretos ni archivos ajenos;
- que el cambio mantiene o actualiza la documentación afectada.

Los comentarios deben señalar un problema concreto, su impacto y, cuando sea útil, una alternativa. El autor responde o aplica el ajuste antes de solicitar nuevamente la integración.

## Política de protección de ramas

La política del equipo para **develop** y **main** es:

- los cambios se integran solo mediante Pull Request; no se permiten integraciones directas;
- se exige al menos una aprobación de una persona distinta del autor;
- los controles de CI requeridos deben completarse antes de integrar;
- todas las conversaciones de revisión deben estar resueltas;
- cuando esté habilitada la opción de GitHub, las aprobaciones se descartan al incorporar nuevos commits;
- no se permiten force pushes ni la eliminación de estas ramas protegidas.

Esta es la política establecida. El archivo de CI valida código, pero no puede activar ni demostrar las restricciones administrativas de GitHub. Quienes administran el repositorio deben comprobar que las reglas de protección reales reflejen esta política, incluido el descarte de aprobaciones obsoletas si esa opción está disponible.

## Cerrar y actualizar documentación

Tras integrar, cierra la Issue si el PR no la cerró automáticamente y mueve su tarjeta a **done** en el GitHub Project existente. Actualiza documentación cuando cambie cualquiera de estos aspectos:

| Cambio | Fuente que se revisa |
| --- | --- |
| Uso, arranque, puertos o variables | [README](README.md), guía de frontend o backend |
| Componentes, rutas o integración | [Arquitectura](docs/arquitectura.md) |
| Lint, compilación, pruebas o CI | [Calidad y pruebas](docs/calidad-y-pruebas.md) |
| Tokens, estilos globales o componentes compartidos | [Diseño frontend](docs/diseno-frontend.md) |
| Esquema, migraciones o pruebas PostgreSQL | [Base de datos](database/README.md) y, si procede, Alembic |
| Comportamiento o criterios del producto | RF/RNF correspondientes |

No declares que un requisito está implementado solo porque exista una pantalla, una Issue o un PR. La evidencia debe incluir la implementación revisada y las validaciones pertinentes.
