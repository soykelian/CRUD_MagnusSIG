---
title: "Diseño de interfaz del inventario Magnus SIG"
status: implemented
created: 2026-10-27
target_stack: Django templates, CSS, JavaScript, Tailwind CSS v4
wcag_target: 2.2 AA
---

# Diseño de interfaz del inventario Magnus SIG

## Dirección visual

La interfaz sigue una composición de alto contraste: marco carbón, panel de contenido blanco con esquinas amplias y navegación lateral flotante con iconos. La cabecera oscura muestra el logo Magnus SIG, búsqueda y cuenta activa. Los tonos de marca aparecen en gráficos, estados y acciones puntuales.

| Uso | Color |
| --- | --- |
| Marco exterior y cabecera | `#303030` |
| Panel de contenido | `#FFFFFF` |
| Navegación y botones principales | `#292D83` |
| Azul del símbolo | `#2AA5D2` |
| Violeta del símbolo | `#7775B9` |
| Naranja SIG | `#ED922E` |
| Texto principal | `#242424` |

## Estructura

- La marca completa está en la cabecera; la barra lateral contiene accesos a dashboard, productos, categorías y administración según permisos.
- En el panel principal, títulos y accesos rápidos preceden a los indicadores; tablas y alertas quedan agrupadas por tarea.
- En móvil, la navegación se convierte en una barra horizontal y el contenido ocupa una sola columna.

## Pantallas

### Dashboard — `/dashboard/`

Indicadores de productos, unidades, categorías y valor estimado. Un resumen de salud muestra existencias adecuadas, stock bajo y agotados. El resto de la página presenta distribución por categoría, productos recientes y alertas enlazadas al detalle. Los datos corresponden al inventario real; no se simulan operaciones financieras.

### Productos — `/` y `/productos/`

Búsqueda y filtros por categoría y estado, tabla con detalle y acciones según rol, junto a un resumen de productos que requieren atención. El estado vacío explica cómo iniciar el catálogo.

### Categorías — `/categorias/`

Búsqueda, orden y tarjetas con cantidad de productos. Formularios y controles de mantenimiento mantienen la misma jerarquía y estilo del resto del sistema.

### Acceso y permisos

El vendedor consulta productos y categorías. El administrador también puede crear, editar y eliminar. Las rutas del servidor aplican los permisos independientemente de los controles visuales.

## Accesibilidad

Se conservan etiquetas accesibles, foco de teclado visible, textos alternativos, títulos jerárquicos y soporte para `prefers-reduced-motion`. WCAG 2.2 AA es el objetivo; hace falta revisión manual con teclado y lector de pantalla antes de afirmar conformidad formal.
