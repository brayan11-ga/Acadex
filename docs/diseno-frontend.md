# Diseño frontend

Esta guía describe las decisiones que se observan hoy en los estilos globales. La fuente canónica de los tokens es [frontend/src/styles/global.css](../frontend/src/styles/global.css); no se debe mantener una segunda paleta manual en este documento.

## Tokens y tipografía actuales

El archivo global define una interfaz oscura por defecto y variables para el modo .light. Entre los grupos de tokens actuales están:

| Uso | Variables verificadas |
| --- | --- |
| Fondos y paneles | --paper, --paper-deep, --paper-soft, --panel, --panel-alt, --background |
| Texto | --ink, --ink-soft |
| Acciones y estados | --azure, --azure-soft, --mint, --amber, --coral |
| Forma y movimiento | --radius-panel, --radius-control, --radius-chip, --transition |
| Tipografía | --font-display y --font-body |

La fuente de cuerpo actual es **Inter** y la fuente de presentación es **Press Start 2P**. Usa las variables existentes en vez de codificar variantes de color, radio, tipografía o transición en cada componente cuando el token ya cubra el caso.

No hay una escala global de espaciado declarada como tokens en el stylesheet actual. Mantén el espaciado coherente con el componente o layout cercano y no inventes una escala documental hasta que se implemente y acuerde en el código.

## Componentes y estilos compartidos

- Revisa frontend/src/components, layouts y styles antes de crear un componente o una regla equivalente.
- Mantén el alcance de los estilos cerca del componente cuando no sean una decisión global. Los cambios de tokens o estilos globales deben justificarse y actualizar esta guía si cambian las convenciones descritas.
- No existe en el repositorio una especificación versionada de una biblioteca de componentes, una escala completa de breakpoints ni una paleta distinta que deba imponerse desde documentación.

## Responsive y accesibilidad

La interfaz debe conservar los comportamientos responsive ya implementados en los componentes que se modifiquen. Para controles nuevos o editados, incluye etiquetas o nombres accesibles, navegación por teclado, estado de foco visible y contraste revisable; son criterios de calidad recomendados, no una certificación de accesibilidad del producto actual.

Comprueba en navegador los tamaños y estados afectados por el cambio. Si se adopta un sistema visual nuevo o reglas de accesibilidad medibles, debe aprobarse, implementarse en estilos y documentarse aquí; no se infiere de esta guía.
