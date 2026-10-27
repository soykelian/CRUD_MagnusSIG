from pathlib import Path
from datetime import date
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak, Table, TableStyle,
    KeepTogether, HRFlowable
)
from reportlab.lib.utils import ImageReader

ROOT = Path(r"C:\Users\Julian\Documents\CRUD_MagnusSIG")
SCREEN = ROOT / "tmp" / "manual_support" / "screens"
OUT = ROOT / "output" / "pdf" / "Manual_Usuario_Magnus_SIS.pdf"
LOGO = ROOT / "magnus_sig" / "productos" / "static" / "branding" / "magnus-sig-horizontal.png"

PAGE = landscape(A4)
PAGE_W, PAGE_H = PAGE
INK = colors.HexColor("#172B3A")
MUTED = colors.HexColor("#526579")
BLUE = colors.HexColor("#1590B9")
PALE = colors.HexColor("#E9F5F8")
PURPLE = colors.HexColor("#EDEBFA")
ORANGE = colors.HexColor("#F5A23A")
LINE = colors.HexColor("#D7E0E5")
WHITE = colors.white

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="CoverTitle", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=27, leading=33, textColor=INK, alignment=TA_LEFT, spaceAfter=8))
styles.add(ParagraphStyle(name="CoverSub", parent=styles["Normal"], fontName="Helvetica", fontSize=12, leading=18, textColor=MUTED, spaceAfter=8))
styles.add(ParagraphStyle(name="H1x", parent=styles["Heading1"], fontName="Helvetica-Bold", fontSize=19, leading=24, textColor=INK, spaceBefore=0, spaceAfter=6))
styles.add(ParagraphStyle(name="H2x", parent=styles["Heading2"], fontName="Helvetica-Bold", fontSize=12, leading=15, textColor=INK, spaceBefore=5, spaceAfter=4))
styles.add(ParagraphStyle(name="Bodyx", parent=styles["BodyText"], fontName="Helvetica", fontSize=9.2, leading=13, textColor=INK, spaceAfter=5))
styles.add(ParagraphStyle(name="Smallx", parent=styles["BodyText"], fontName="Helvetica", fontSize=8, leading=10.5, textColor=MUTED, spaceAfter=3))
styles.add(ParagraphStyle(name="Captionx", parent=styles["BodyText"], fontName="Helvetica-Oblique", fontSize=7.8, leading=10, alignment=TA_CENTER, textColor=MUTED, spaceBefore=3))
styles.add(ParagraphStyle(name="Calloutx", parent=styles["BodyText"], fontName="Helvetica", fontSize=8.5, leading=12, textColor=INK))
styles.add(ParagraphStyle(name="Tocx", parent=styles["BodyText"], fontName="Helvetica", fontSize=9, leading=13, textColor=INK))

def P(text, style="Bodyx"):
    return Paragraph(text, styles[style])

def bullets(lines):
    return [P("- " + line) for line in lines]

def numbered(lines):
    return [P(f"<b>{i}.</b> {line}") for i, line in enumerate(lines, 1)]

def callout(title, text, bg=PALE):
    box = Table([[P(f"<b>{title}</b><br/>{text}", "Calloutx")]], colWidths=[PAGE_W - 44*mm])
    box.setStyle(TableStyle([
        ("BACKGROUND", (0,0),(-1,-1), bg), ("BOX", (0,0),(-1,-1), 0.5, LINE),
        ("LEFTPADDING",(0,0),(-1,-1),10), ("RIGHTPADDING",(0,0),(-1,-1),10),
        ("TOPPADDING",(0,0),(-1,-1),7), ("BOTTOMPADDING",(0,0),(-1,-1),7),
    ]))
    return box

def screenshot(name, caption, max_h=345):
    path = SCREEN / name
    if not path.exists():
        return P(f"Captura no disponible: {escape(name)}", "Smallx")
    iw, ih = ImageReader(str(path)).getSize()
    max_w = PAGE_W - 45*mm
    scale = min(max_w / iw, max_h / ih)
    img = Image(str(path), width=iw*scale, height=ih*scale)
    img.hAlign = "CENTER"
    return KeepTogether([img, P(caption, "Captionx")])

def page_header(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(INK)
    canvas.setFont("Helvetica-Bold", 7.4)
    canvas.drawString(18*mm, PAGE_H - 10*mm, "MAGNUS SIG  |  MANUAL DE USUARIO")
    canvas.setStrokeColor(LINE)
    canvas.setLineWidth(0.5)
    canvas.line(18*mm, PAGE_H - 12*mm, PAGE_W - 18*mm, PAGE_H - 12*mm)
    canvas.setFillColor(MUTED)
    canvas.setFont("Helvetica", 7.5)
    canvas.drawString(18*mm, 9*mm, "Guía operativa del inventario de seguridad laboral")
    canvas.drawRightString(PAGE_W - 18*mm, 9*mm, f"Página {doc.page}")
    canvas.restoreState()

doc = SimpleDocTemplate(
    str(OUT), pagesize=PAGE, rightMargin=18*mm, leftMargin=18*mm,
    topMargin=18*mm, bottomMargin=16*mm,
    title="Manual de usuario - Magnus SIG", author="Magnus SIG",
    subject="Guía de uso de los módulos de inventario y seguridad laboral"
)
story = []

# Portada
logo = Image(str(LOGO), width=170*mm, height=39*mm)
logo.hAlign = "LEFT"
story += [Spacer(1, 9*mm), logo, Spacer(1, 7*mm)]
story += [P("Manual de usuario", "CoverTitle"), P("Magnus SIG - Inventario de seguridad laboral", "CoverSub")]
story += [HRFlowable(width="100%", thickness=2, color=BLUE, spaceBefore=2, spaceAfter=9)]
story += [P("Guía práctica para consultar existencias, mantener el catálogo, registrar entradas y salidas, y revisar la trazabilidad de los equipos de protección personal (EPP).", "CoverSub")]
story += [Spacer(1, 3*mm), callout("Alcance", "Este manual describe las pantallas y reglas operativas actuales de Magnus SIG. Los ejemplos y capturas se prepararon en una base temporal de demostración; sus nombres y cantidades ilustran el flujo y no corresponden a los registros reales de la empresa.", PURPLE)]
story += [Spacer(1, 6*mm), P(f"Versión de la guía: 1.0  |  Actualizado: {date.today().strftime('%d/%m/%Y')}", "Smallx")]
story += [PageBreak()]

# Indice + primer uso
story += [P("Cómo usar esta guía", "H1x"), P("El manual sigue el recorrido habitual: acceso, consulta del inventario, actualización del catálogo y registro de operaciones. Cada sección indica qué rol puede ejecutarla, qué debe prepararse y qué cambia al guardar.")]
toc = [
    ["Sección", "Qué encontrarás"],
    ["1. Acceso y roles", "Inicio de sesión, navegación y permisos de administrador/vendedor."],
    ["2. Dashboard", "Resumen y lectura de indicadores por rol."],
    ["3. Categorías y productos", "Crear y mantener la clasificación y el catálogo."],
    ["4. Existencias y movimientos", "Consultar stock, rastrear cambios y registrar ajustes."],
    ["5. Entradas", "Registrar una compra/recepción y confirmar unidades recibidas."],
    ["6. Salidas", "Registrar una venta, reservar unidades y despachar."],
    ["7. Clientes y proveedores", "Crear y consultar contactos comerciales."],
    ["8. Reportes y administración", "Exportar datos y gestionar las cuentas del sistema."],
    ["9. Inicio local y solución de problemas", "Poner en marcha el proyecto y resolver situaciones comunes."],
]
t = Table([[P(escape(c), "Smallx") for c in row] for row in toc], colWidths=[57*mm, 205*mm], repeatRows=1)
t.setStyle(TableStyle([
    ("BACKGROUND",(0,0),(-1,0),INK), ("TEXTCOLOR",(0,0),(-1,0),WHITE),
    ("GRID",(0,0),(-1,-1),0.4,LINE), ("ROWBACKGROUNDS",(0,1),(-1,-1),[WHITE,PALE]),
    ("VALIGN",(0,0),(-1,-1),"TOP"), ("LEFTPADDING",(0,0),(-1,-1),7),
    ("RIGHTPADDING",(0,0),(-1,-1),7), ("TOPPADDING",(0,0),(-1,-1),5),
    ("BOTTOMPADDING",(0,0),(-1,-1),5),
]))
story += [t, Spacer(1, 7*mm), P("Roles y alcance de acceso", "H2x")]
roles = [
    ["Acción / módulo", "Administrador", "Vendedor"],
    ["Dashboard", "Resumen general y analítica del inventario.", "Consulta de stock y actividad de sus propias salidas; no ve análisis completo del sistema."],
    ["Inventario, productos y categorías", "Consulta, creación y edición.", "Consulta del catálogo y existencias; sin administración del catálogo."],
    ["Entradas y proveedores", "Puede registrar compras y confirmar recepciones.", "No tiene acceso."],
    ["Salidas y clientes", "Puede registrar y consultar todas las salidas.", "Registra salidas, consulta sus registros y gestiona clientes según permisos asignados."],
    ["Movimientos y reportes", "Consulta la trazabilidad y genera reportes.", "No accede a reportes globales ni al historial administrativo."],
    ["Administración Django", "Acceso para cuentas autorizadas con privilegios administrativos.", "Sin acceso."],
]
rt = Table([[P(escape(str(c)), "Smallx") for c in row] for row in roles], colWidths=[49*mm, 101*mm, 112*mm], repeatRows=1)
rt.setStyle(TableStyle([
    ("BACKGROUND",(0,0),(-1,0),INK), ("TEXTCOLOR",(0,0),(-1,0),WHITE),
    ("GRID",(0,0),(-1,-1),0.4,LINE), ("ROWBACKGROUNDS",(0,1),(-1,-1),[WHITE,PALE]),
    ("VALIGN",(0,0),(-1,-1),"TOP"), ("LEFTPADDING",(0,0),(-1,-1),6),
    ("RIGHTPADDING",(0,0),(-1,-1),6), ("TOPPADDING",(0,0),(-1,-1),5),
    ("BOTTOMPADDING",(0,0),(-1,-1),5),
]))
story += [rt]
story += [PageBreak()]

# Login
story += [P("1. Acceso al sistema", "H1x"), P("Cada persona debe usar la cuenta que le asignó el administrador. Las cuentas son individuales: las acciones quedan asociadas al usuario que las realiza.", "Bodyx")]
story += numbered(["Abre la dirección local o institucional que te compartió el equipo del proyecto.", "Escribe tu nombre de usuario y contraseña.", "Pulsa <b>Iniciar sesión</b>. Si las credenciales son válidas, Magnus SIG abre el dashboard correspondiente a tu rol.", "Al terminar, usa <b>Cerrar sesión</b> en la parte inferior del menú lateral, especialmente si compartes el equipo."])
story += [screenshot("01-login.png", "Pantalla de acceso. El campo de contraseña permite ocultar o mostrar el texto mientras se escribe.", 350)]
story += [Spacer(1, 4*mm), callout("Si no puedes entrar", "Verifica mayúsculas, teclado y nombre de usuario. La aplicación no ofrece autorregistro ni recuperación pública de contraseña; solicita ayuda al administrador.", PURPLE)]

# Dashboard & navigation
story += [P("2. Dashboard y navegación", "H1x"), P("El dashboard resume el estado de las existencias y enlaza con las tareas frecuentes. La información se calcula a partir de los productos y movimientos guardados; no son cifras editables desde el propio gráfico.")]
story += [P("Administrador", "H2x"), P("Revisa existencias suficientes, stock bajo y agotados; valor estimado del inventario; productos por revisar; movimientos recientes y entradas/salidas. Los filtros de periodo cambian el rango del gráfico, no los registros almacenados.")]
story += [screenshot("02-dashboard-admin.png", "Dashboard administrativo de ejemplo. Las cifras de esta captura provienen exclusivamente de la base temporal de demostración.", 345)]
story += [P("Vendedor", "H2x"), P("Puede consultar el stock general para orientar una atención. Su panel limita el análisis y muestra sus propias salidas; no incluye el conjunto de reportes ni toda la analítica administrativa.")]
story += [screenshot("22-dashboard-vendedor.png", "Dashboard de vendedor: resumen de existencias y actividad del vendedor, sin analítica global.", 285)]
story += [P("Navegación común", "H2x"), P("El menú lateral contiene Dashboard, Inventario, Productos, Categorías, Movimientos, Entradas, Salidas, Proveedores, Clientes y Reportes, aunque algunas opciones solo están disponibles para el administrador. La barra superior permite buscar productos y equipos de seguridad.")]

# Inventory + product list
story += [P("3. Consultar inventario y catálogo", "H1x"), P("El inventario muestra el estado actual de los productos. Para ubicar un artículo, usa el campo de búsqueda y, cuando estén disponibles, limita por categoría o condición de stock. La lista de Productos permite abrir el detalle y, con permisos de administrador, editar o eliminar.")]
story += bullets(["Disponible: hay unidades para asignar.", "Stock bajo: las existencias llegaron al umbral que usa el sistema para revisión.", "Agotado: la cantidad disponible es cero.", "La búsqueda trabaja sobre información guardada; limpia el texto y ejecuta Buscar para volver a la lista completa."])
story += [screenshot("03-inventario.png", "Pantalla de inventario/catálogo con filtros y estado de existencias. La etiqueta lateral muestra el área activa.", 350)]
story += [P("Abrir el detalle de un producto", "H2x"), P("En la lista de productos, pulsa <b>Ver</b> junto al artículo. El detalle muestra categoría, precio, existencias, umbral de stock bajo y el historial de movimientos asociado. Si el producto ya tiene historial, el sistema protege su trazabilidad y puede impedir eliminarlo.")]
story += [screenshot("12-detalle-producto.png", "Detalle de producto y trazabilidad. El registro de demostración incluye una entrada inicial.", 310)]

# Categories
story += [P("4. Crear categorías", "H1x"), P("Las categorías ayudan a ordenar los equipos por tipo. Crea la categoría antes de registrar productos que deban pertenecer a ella.")]
story += [P("Pasos", "H2x")] + numbered(["Abre <b>Categorías</b> desde el menú.", "Pulsa <b>Nueva categoría</b>.", "Escribe un nombre claro y único. La descripción es opcional y puede indicar el tipo de elementos agrupados.", "Pulsa <b>Crear categoría</b>. Comprueba que aparece en la lista."])
story += [screenshot("05-categorias.png", "Listado de categorías: búsqueda, orden alfabético y acceso a productos de la categoría.", 310)]
story += [screenshot("06-form-categoria.png", "Formulario de categoría. El nombre es obligatorio; la descripción es opcional.", 280)]
story += [callout("Antes de crear", "Evita categorías duplicadas o demasiado generales. Si la categoría ya tiene productos asociados, la aplicación puede impedir eliminarla para conservar la clasificación.")]

# Products
story += [P("5. Registrar y editar productos", "H1x"), P("El administrador mantiene el catálogo. Cada producto debe poder reconocerse sin ambigüedad, especialmente cuando se trata de EPP de tallas, clases o especificaciones diferentes.")]
story += [P("Alta de un producto", "H2x")] + numbered(["Desde <b>Productos</b>, pulsa <b>Nuevo producto</b>.", "Escribe el nombre. Añade una descripción útil cuando haga falta diferenciar protección, clase, material o uso.", "Selecciona una categoría previamente creada.", "Indica el precio en COP y la cantidad inicial disponible. Usa cero cuando el artículo aún no tenga unidades.", "Revisa los campos y pulsa <b>Guardar producto</b>.", "Verifica que el nuevo artículo figure en el listado y que su detalle muestre el stock esperado."])
story += [screenshot("09-form-producto.png", "Formulario de producto: datos básicos, clasificación, precio y cantidad inicial.", 360)]
story += [P("Reglas importantes", "H2x")]
story += bullets(["El nombre, la categoría, el precio y la cantidad son necesarios. El precio debe ser mayor que cero y la cantidad no puede ser negativa.", "La cantidad inicial queda como existencia inicial y se refleja en la trazabilidad.", "Para cambios de cantidad posteriores, registra el movimiento correspondiente en lugar de alterar el stock sin explicación.", "Editar conserva el producto; eliminar puede bloquearse cuando hay historial de entradas, salidas o ajustes."])
story += [P("Para EPP, indica en nombre o descripción la clase, talla, material o norma que diferencie cada referencia. No sustituyas un equipo por otro solo porque sus nombres sean parecidos.", "Smallx")]

# Entries
story += [P("6. Registrar entradas y confirmar recepción", "H1x"), P("Las entradas registran compras o recepciones de proveedores. Guardar una entrada la deja pendiente; las unidades se suman al stock cuando un usuario administrador confirma que la mercancía fue recibida.")]
story += [P("Registrar entrada", "H2x")] + numbered(["Abre <b>Entradas</b> y pulsa <b>Registrar entrada</b>.", "Selecciona un proveedor activo y el producto recibido.", "Indica cantidad y costo unitario. Completa la fecha prevista si se conoce.", "Pulsa <b>Guardar</b>. La entrada queda como <b>Pendiente</b> y todavía no modifica las existencias.", "Al recibir físicamente los artículos, localiza el registro y pulsa <b>Confirmar recepción</b>. Confirma solo las unidades efectivamente recibidas.", "Verifica el estado recibido y el nuevo stock en el inventario."])
story += [screenshot("14-entradas.png", "Lista de entradas: el botón de confirmación aparece en los registros pendientes.", 280)]
story += [screenshot("15-entrada-completada.png", "Formulario de entrada con proveedor, producto, unidades, costo y fecha prevista.", 300)]
story += [callout("Control de recepción", "Compara cantidad y artículo con la recepción física antes de confirmar. Una entrada pendiente no es stock disponible; la confirmación genera el movimiento de entrada.")]

# Outgoing/sales
story += [P("7. Registrar salidas y despachar", "H1x"), P("Las salidas representan entregas o ventas a clientes. El registro inicial reserva unidades y queda en preparación. El descuento definitivo ocurre al despachar.")]
story += [P("Pasos del vendedor", "H2x")] + numbered(["Abre <b>Clientes</b> y crea el cliente si todavía no existe.", "Abre <b>Salidas</b> y pulsa <b>Registrar salida</b>.", "Selecciona cliente y producto; escribe una cantidad positiva que no supere las unidades disponibles.", "Guarda. La salida queda en <b>Preparando</b> y esas unidades quedan reservadas para evitar asignarlas de nuevo.", "Cuando se entregue el producto, pulsa <b>Despachar</b> en tu salida. La salida cambia a <b>Entregada</b> y se registra el movimiento que descuenta el stock.", "Comprueba el estado y las unidades restantes en la lista o en el detalle del producto."])
story += [screenshot("24-salidas-vendedor.png", "El vendedor ve sus propias salidas y puede despachar las que estén preparando.", 305)]
story += [callout("No despachar antes de la entrega", "El despacho confirma una salida real y crea el movimiento de inventario. No uses ese botón solo para liberar una reserva; contacta al administrador si el registro debe corregirse.", PURPLE)]

# Movements
story += [P("8. Movimientos y trazabilidad", "H1x"), P("Cada cambio de existencias debe tener un motivo rastreable. La pantalla de Movimientos permite al administrador consultar producto, tipo, variación, referencia, responsable y fecha.")]
story += bullets(["Entrada: suma unidades al producto.", "Salida: descuenta unidades al despachar una entrega.", "Ajuste: corrige el saldo por una diferencia justificada de inventario.", "Devolución: registra unidades que regresan según el proceso habilitado.", "Usa búsqueda y filtro por tipo para acotar el historial. La exportación CSV facilita revisar los registros en una hoja de cálculo."])
story += [screenshot("13-movimientos.png", "Historial de movimientos en la cuenta administradora, con filtros y opción de exportar CSV.", 360)]
story += [callout("Trazabilidad", "No borres ni recrees un movimiento para ocultar un error. Si una operación quedó incorrecta, solicita al administrador que registre el ajuste o la corrección que corresponda y deja un motivo claro.")]

# Providers and clients
story += [P("9. Proveedores y clientes", "H1x"), P("Los contactos se usan para asociar movimientos comerciales. Un proveedor identifica el origen de una compra; un cliente identifica el destino de una salida.")]
story += [P("Proveedores - administrador", "H2x"), P("Abre <b>Proveedores</b>, busca por nombre o datos de contacto y pulsa <b>Nuevo proveedor</b>. Registra los datos solicitados y guarda. El proveedor debe estar activo para seleccionarlo en una nueva entrada.")]
story += [screenshot("18-proveedores.png", "Listado de proveedores disponible para el administrador.", 280)]
story += [P("Clientes - administrador y vendedor", "H2x"), P("Abre <b>Clientes</b>. Para una nueva salida, registra primero el cliente si no existe. Usa datos precisos para evitar duplicados y revisa el cliente seleccionado antes de guardar la salida.")]
story += [screenshot("20-clientes.png", "Listado de clientes. El vendedor tiene acceso a este módulo para asociar sus salidas.", 280)]
story += [screenshot("21-form-cliente.png", "Formulario de cliente: completa los datos requeridos y guarda antes de iniciar la salida.", 250)]

# Reports & admin
story += [P("10. Reportes y administración de usuarios", "H1x"), P("Los reportes consolidados y la administración de cuentas están restringidos al administrador.")]
story += [P("Exportar un reporte", "H2x")] + numbered(["Abre <b>Reportes</b>.", "Selecciona el reporte que necesitas, por ejemplo inventario general, productos agotados, stock bajo o historial de movimientos.", "Pulsa la opción de descarga correspondiente. El archivo se genera con los registros actuales del sistema.", "Revisa el periodo y el contenido del archivo antes de compartirlo."])
story += [screenshot("28-reportes.png", "Vista de reportes. El acceso se limita a las cuentas administradoras.", 300)]
story += [P("Crear o revisar cuentas", "H2x"), P("La administración de usuarios se realiza desde <b>Administración Django</b>. Un superusuario inicia sesión con su cuenta, abre el módulo y gestiona usuarios y grupos. Asigna a cada integrante solo el rol que necesita; el vendedor no requiere privilegios de personal ni permisos de administración.")]
story += [screenshot("30-admin-django.png", "Panel de administración Django; el contenido visible depende de los permisos de la cuenta.", 285)]
story += [callout("Buenas prácticas de acceso", "Cada integrante utiliza su propia cuenta. No compartas contraseñas de superusuario. Si una cuenta cambia de responsable, desactívala o reasígnala según las reglas del equipo.", PURPLE)]

# FAQ, server start
story += [P("11. Solución de problemas frecuentes", "H1x")]
faq = [
    ["Situación", "Qué revisar"],
    ["El inicio de sesión es rechazado", "Confirma usuario y contraseña. Pide al administrador restablecer o habilitar la cuenta."],
    ["No aparece un módulo", "Es probable que tu rol no tenga acceso. El vendedor no ve Entradas, Proveedores, Reportes ni Administración Django."],
    ["Una entrada no aumentó el stock", "Comprueba si sigue pendiente. Solo confirmar la recepción suma unidades."],
    ["Una salida no se refleja como descuento", "Comprueba su estado. La salida descuenta al despachar, no al guardarla como preparando."],
    ["No se puede eliminar una categoría o producto", "Puede haber productos asociados o movimientos históricos. La protección conserva la trazabilidad."],
    ["El producto aparece agotado o con stock bajo", "Revisa entradas confirmadas, salidas despachadas y ajustes en el historial. No corrijas el saldo editando datos sin dejar un movimiento."],
]
ft = Table([[P(escape(str(c)), "Smallx") for c in row] for row in faq], colWidths=[69*mm, 193*mm], repeatRows=1)
ft.setStyle(TableStyle([
    ("BACKGROUND",(0,0),(-1,0),INK), ("TEXTCOLOR",(0,0),(-1,0),WHITE),
    ("GRID",(0,0),(-1,-1),0.4,LINE), ("ROWBACKGROUNDS",(0,1),(-1,-1),[WHITE,PALE]),
    ("VALIGN",(0,0),(-1,-1),"TOP"), ("LEFTPADDING",(0,0),(-1,-1),7),
    ("RIGHTPADDING",(0,0),(-1,-1),7), ("TOPPADDING",(0,0),(-1,-1),6),
    ("BOTTOMPADDING",(0,0),(-1,-1),6),
]))
story += [ft, Spacer(1, 7*mm), P("Puesta en marcha local (equipo técnico)", "H2x"), P("Desde la carpeta raíz del proyecto, en PowerShell, ejecuta estos comandos la primera vez:")]
commands = [
    "py -m venv .\\venv",
    ".\\venv\\Scripts\\python.exe -m pip install -r requirements.txt",
    ".\\venv\\Scripts\\python.exe .\\magnus_sig\\manage.py migrate",
    ".\\venv\\Scripts\\python.exe .\\magnus_sig\\manage.py preparar_roles",
    ".\\venv\\Scripts\\python.exe .\\magnus_sig\\manage.py createsuperuser",
]
code = Table([[P("<font name='Courier'>" + escape(c) + "</font>", "Smallx")] for c in commands], colWidths=[PAGE_W-44*mm])
code.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),colors.HexColor("#F2F5F7")),("BOX",(0,0),(-1,-1),0.5,LINE),("LEFTPADDING",(0,0),(-1,-1),8),("TOPPADDING",(0,0),(-1,-1),4),("BOTTOMPADDING",(0,0),(-1,-1),4)]))
story += [code, Spacer(1, 3*mm), P("Para iniciar el servidor en adelante: <font name='Courier'>.\\venv\\Scripts\\python.exe .\\magnus_sig\\manage.py runserver</font>. Abre <b>http://127.0.0.1:8000/</b> en el navegador. Detén el servidor con <b>Ctrl+C</b> en la terminal. Si el equipo ya cuenta con el entorno virtual y la base de datos configurados, no repitas los pasos iniciales.")]

# Closing/short glossary
story += [P("12. Recomendaciones de uso", "H1x")]
story += bullets(["Registra las operaciones cuando suceden y confirma las recepciones solo después de cotejar el material.", "Usa nombres consistentes para categorías, productos y clientes.", "Antes de guardar una salida, comprueba el cliente, referencia y cantidad.", "Consulta el historial cuando el saldo no coincida con el conteo físico.", "Limita los permisos de cada usuario a las tareas que realiza.", "Descarga y comparte reportes con cuidado: pueden contener datos operativos de la organización."])
story += [Spacer(1, 6*mm), callout("Nota sobre los datos", "Las capturas de este documento se obtuvieron en una instancia temporal con datos ficticios creados exclusivamente para mostrar las pantallas. La base de datos real no se modificó al preparar el manual. Las cifras, nombres y fechas pueden variar según el estado real del sistema.", PALE)]
story += [Spacer(1, 14*mm), P("Magnus SIG", "H1x"), P("Sistema de inventario para equipos de protección personal, dotación y elementos de seguridad laboral.", "CoverSub")]

doc.build(story, onFirstPage=page_header, onLaterPages=page_header)
print(OUT)
