# Índice de documentación

Este índice indica dónde buscar y mantener cada tema. Evita copiar procedimientos completos entre documentos: cuando una regla tenga una fuente canónica, los demás documentos deben enlazarla.

| Documento | Público y momento de consulta | Fuente canónica de | Cuándo actualizarlo |
| --- | --- | --- | --- |
| [README raíz](../README.md) | Cualquier integrante al conocer o ejecutar el proyecto | Propósito, acceso inicial, servicios locales y enlaces principales | Cambios en arranque, puertos, stack o punto de entrada |
| [CONTRIBUTING](../CONTRIBUTING.md) | Quien propone, implementa o revisa un cambio | Issues, GitHub Project, ramas, Pull Requests, revisión, integración y actualización documental | Cambios acordados en el proceso de equipo |
| [Arquitectura](arquitectura.md) | Desarrollo de funcionalidades e integraciones | Componentes, límites y flujos técnicos | Cambios de componentes, contratos o configuración entre servicios |
| [Calidad y pruebas](calidad-y-pruebas.md) | Antes de abrir o revisar un Pull Request | Comandos, alcance de pruebas y CI | Cambios en scripts, suites o CI |
| [Diseño frontend](diseno-frontend.md) | Cambios visuales o de componentes | Tokens y convenciones que existen en los estilos | Cambios en estilos globales, tokens o componentes compartidos |
| [Guía del backend](../backend/README.md) | Desarrollo local manual de API | Preparación y ejecución local del backend | Cambios en dependencias, ejecución o variables del backend |
| [Guía del frontend](../frontend/README.md) | Desarrollo local manual de interfaz | Preparación y ejecución local del frontend | Cambios en scripts, Vite o variables VITE |
| [Base de datos](../database/README.md) | Cambios de esquema, administración local o pruebas PostgreSQL | Alembic, fuentes históricas y cautelas de datos | Nueva migración, cambios de seguridad o de pruebas de datos |
| [Adopción de Alembic](DESPLIEGUE_ALEMBIC.md) | Solo para una base existente sin historial Alembic | Procedimiento excepcional de adopción | Si se valida un nuevo procedimiento de adopción |
| [RF](RF/README.md) y [RNF](RNF/README.md) | Planificación y validación de producto | Requisitos y criterios de producto | Cambio aprobado de alcance o de criterio |

## Estado de requisitos

Los índices de RF y RNF describen requisitos, no un estado de implementación validado. El campo **Tipo de cambio** en RF clasifica cambios editoriales respecto de una versión anterior; no prueba que una capacidad esté completa.

No se creó una matriz de estado en esta fase porque no hay evidencia homogénea de implementación y prueba para todos los requisitos. Cuando el equipo defina quién verifica cada requisito y con qué evidencia, una matriz deberá enlazar a los RF/RNF originales en vez de duplicarlos.

## Mantenimiento editorial

- Redacta en español y conserva rutas, comandos, variables e identificadores técnicos tal como existen en el código.
- Usa enlaces relativos a la fuente canónica y corrígelos al mover o retirar documentos.
- No guardes secretos, datos personales, credenciales, volcados de bases de datos ni ejemplos con valores reales.
- Comprueba los comandos frente a la configuración antes de documentarlos. Una instrucción escrita no garantiza que una configuración administrativa de GitHub esté activa.
