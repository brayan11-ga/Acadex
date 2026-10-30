# Índice de documentación

Empieza por el [README](../README.md). Para ejecutar el proyecto, elige Docker o inicio manual; para cambiarlo, sigue [CONTRIBUTING](../CONTRIBUTING.md).

## Qué mantiene cada archivo

| Documento | Responsabilidad |
| --- | --- |
| [README](../README.md) | Qué es Acadex, cómo clonar, elegir un método de inicio y encontrar las guías |
| [Inicio con Docker](inicio-docker.md) | Preparar variables, levantar el stack, comprobar servicios y conservar datos al detenerlo |
| [Inicio manual](inicio-manual.md) | PostgreSQL local, entorno Python, migraciones y terminales de backend/frontend |
| [CONTRIBUTING](../CONTRIBUTING.md) | Issue, etiquetas, Project, ramas, commits, PR, revisión y cierre |
| [Plantilla de PR](../.github/PULL_REQUEST_TEMPLATE.md) | Información mínima para revisar un cambio |
| [Formularios de issues](../.github/ISSUE_TEMPLATE) | Reportar errores, proponer funcionalidades y registrar trabajo técnico; son YAML, no Markdown |
| [Backend](../backend/README.md) | Entrada de la API, estructura y configuración de sus integraciones |
| [Frontend](../frontend/README.md) | Variables públicas, scripts disponibles y referencias de interfaz |
| [Base de datos](../database/README.md) | Fuente del esquema, actualización de bases existentes, administración local y guardas de pruebas |
| [Migraciones SQL históricas](../backend/migrations/README.md) | Historia anterior a Alembic y notas técnicas de esa transición; no es una guía de inicio |
| [Adopción de Alembic](DESPLIEGUE_ALEMBIC.md) | Procedimiento excepcional para una base con tablas e historial por reconciliar; separado del desarrollo local |
| [Arquitectura](arquitectura.md) | Componentes, comunicación y organización del código |
| [Calidad y pruebas](calidad-y-pruebas.md) | Comandos de validación, entorno de pruebas PostgreSQL y alcance de CI |
| [Diseño frontend](diseno-frontend.md) | Tokens, estilos y convenciones de interfaz existentes |
| [RF](RF/README.md) y sus 58 fichas | Requisitos funcionales, historias y escenarios |
| [RNF](RNF/README.md) y sus 32 fichas | Requisitos no funcionales y restricciones |
| [Decisiones sobre tareas grupales](decisiones/tareas-grupales.md) | Documento de trabajo fechado: decisiones, hallazgos y pendientes de ese momento |

Las fichas RF/RNF describen objetivos, no certifican su implementación. «Tipo de cambio» en RF clasifica una edición del requisito. Para saber si está resuelto, consulta implementación, issue, PR y pruebas.

El documento de tareas grupales contiene planes fechados y referencias históricas a archivos retirados. Contrasta sus pendientes con el código y las issues antes de iniciar trabajo.

## Cómo mantener estas guías

1. Actualiza el documento que contiene el procedimiento; en los demás, añade o corrige el enlace.
2. Comprueba comandos, rutas y variables contra los archivos del repositorio. Marca como pendiente lo que no puedas verificar.
3. Conserva los nombres exactos de etiquetas y campos de GitHub. El catálogo comprobado y los ajustes administrativos pendientes están en [CONTRIBUTING](../CONTRIBUTING.md).
4. Usa ejemplos sin secretos ni datos personales. No documentes una prueba como pasada si no se ejecutó.

Las guías de inicio describen desarrollo local. Los resultados históricos de una migración o una copia restaurada no prueban el estado actual de Supabase.
