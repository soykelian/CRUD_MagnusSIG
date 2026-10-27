# Prompt: rediseño integral de Magnus SIG

Adjunta la nueva imagen de referencia al mensaje en que uses este prompt. Esta imagen es la única referencia visual autorizada para el rediseño. Si no está disponible, detente y solicítala; no sustituyas la referencia por capturas o mockups anteriores.

## Prompt listo para usar

Actúa como diseñador/a senior de producto y desarrollador/a frontend con experiencia en sistemas empresariales de inventario. Rediseña integralmente la interfaz de Magnus SIG desde cero, usando la imagen adjunta a este mensaje como referencia visual principal.

### Objetivo visual

Recrea con alta fidelidad la composición y el lenguaje visual de la referencia: marco y navegación carbón, superficie de trabajo clara con esquinas amplias, barra lateral estrecha con iconos, encabezado con marca y búsqueda, jerarquía tipográfica marcada, tarjetas espaciosas, azul pastel en visualizaciones y una tarjeta azul de énfasis. Respeta las proporciones, agrupación, ritmo y relación entre áreas que se ven en la imagen. No reutilices el diseño de la interfaz actual ni las guías visuales previas como objetivo. Las capturas de Nexo, mockups antiguos y estilos anteriores son referencias descartadas.

Conserva el logo oficial de Magnus SIG. Adapta los acentos visuales de la referencia a la identidad del logo donde sea necesario para que la marca siga siendo reconocible; la dirección general, el fondo, la navegación, las superficies y la composición deben seguir la imagen adjunta.

La referencia muestra una aplicación financiera. Traduce sus patrones a un sistema real de inventario para una empresa de seguridad laboral que administra EPP, equipos de protección, dotación y suministros. No copies su marca, texto, usuarios, avatares, artículos, importes, moneda ni operaciones financieras. No inventes inspecciones de EPP, certificaciones, incidentes u otros procesos que el sistema no implemente.

### Antes de editar

1. Inspecciona el proyecto, sus rutas, modelos, permisos, vistas, plantillas, CSS, JavaScript y documentación para identificar la implementación y los comportamientos actuales.
2. Revisa la imagen adjunta y úsala como única referencia del nuevo lenguaje visual. No asumas que los diseños discutidos antes siguen vigentes.
3. Define una dirección visual coherente y aplícala al conjunto de pantallas. Actualiza la documentación de diseño que contradiga esa dirección; no borres documentación académica, planeaciones de entregas ni registros históricos del proyecto.
4. Implementa el rediseño en el proyecto; no te limites a devolver una propuesta, un mockup o una lista de recomendaciones.

### Pantallas y módulos que debes conservar

Rediseña todas las pantallas existentes de la aplicación y mantén sus nombres y destinos actuales:

- Inicio de sesión y dashboard.
- Inventario y catálogo de productos.
- Categorías.
- Movimientos.
- Entradas y recepciones.
- Salidas y despachos.
- Proveedores y clientes.
- Reportes.
- Configuración.
- Detalle de producto y formularios de creación, edición y confirmación que ya existan.
- Enlace y acceso existente a la administración de Django, sujeto a sus permisos actuales.

Aplica el mismo sistema visual a todas las pantallas, pero organiza cada una según su tarea. No fuerces la distribución del dashboard en formularios, tablas o detalles cuando no corresponda. La navegación debe incluir los módulos que el usuario actual está autorizado a ver; no ocultes ni elimines módulos para imitar la barra corta de la referencia.

### Límites funcionales y técnicos

- Conserva Django, las plantillas existentes, CSS/Tailwind y el JavaScript del proyecto. No migres el frontend a React, Vue ni otra tecnología.
- Conserva rutas, modelos, permisos, roles de administrador y vendedor, validaciones, reglas de negocio y contratos existentes. No cambies el backend, el esquema de datos ni las migraciones como parte del rediseño visual.
- Mantén operativos todos los botones, enlaces, formularios, filtros, búsquedas, ordenamientos, paginación, exportaciones y acciones existentes. No dejes controles decorativos o sin comportamiento.
- Toda cifra, gráfico, listado, estado o alerta debe derivarse de datos guardados y de las consultas actuales, respetando los permisos por rol. No agregues datos semilla, demostraciones ni actividad ficticia.
- Adapta los widgets de la imagen solo cuando Magnus tenga datos equivalentes. Por ejemplo, usa los movimientos reales para actividad reciente y entradas/salidas; usa stock real para disponibilidad y alertas. Omite cualquier panel promocional o función que no exista.
- Conserva los estados vacíos reales y muestra claramente cómo iniciar la operación cuando no hay registros.
- No debilites controles de acceso para que un elemento aparezca visualmente. La autorización del servidor debe seguir aplicándose.

### Calidad de interfaz

- Mantén una jerarquía clara entre navegación, encabezado, título, indicadores, gráficos, tablas y acciones.
- Asegura contraste legible, foco de teclado, etiquetas accesibles y objetivos táctiles cómodos.
- En pantallas estrechas, reorganiza el menú y las columnas sin ocultar acciones importantes. Las tablas pueden desplazarse dentro de su propio contenedor; la página completa no debe desbordarse horizontalmente.
- Conserva textos en español y el contexto de seguridad laboral. No copies el inglés ni el contexto financiero de la imagen.

### Verificación y entrega

Al terminar:

1. Ejecuta las comprobaciones y pruebas existentes del proyecto, sin aplicar migraciones ni alterar la base de datos local del usuario.
2. Revisa visualmente el dashboard, inventario, productos, categorías, movimientos, entradas, salidas, proveedores, clientes, reportes, configuración, login y formularios en tamaños de escritorio y móvil.
3. Comprueba que las acciones y permisos de administrador y vendedor sigan funcionando, que no haya controles inactivos y que no se haya introducido información ficticia.
4. Corrige los problemas visuales o funcionales encontrados antes de terminar.
5. Resume qué cambió, cómo se verificó y cualquier limitación que siga pendiente. No afirmes que una comprobación pasó si no se ejecutó.

El resultado debe parecer una adaptación cuidada de la imagen adjunta a Magnus SIG: la referencia define el lenguaje visual; los datos, módulos y comportamientos siguen perteneciendo al sistema real.
