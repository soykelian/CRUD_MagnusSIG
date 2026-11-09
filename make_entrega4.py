from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Image, Table, TableStyle, KeepTogether
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from PIL import Image as PILImage, ImageDraw, ImageFont
import re

ROOT=Path(__file__).parent
OUT=ROOT/'docs'/'Entrega4_MagnusSIG_ProyectoFinal.pdf'
AS=ROOT/'docs'/'screens'
TMP=ROOT/'tmp'/'entrega4'; TMP.mkdir(parents=True,exist_ok=True)

# Fonts
font_dir=Path('C:/Windows/Fonts')
for nm,fn in [('Liberation','arial.ttf'),('Liberation-Bold','arialbd.ttf')]:
 try: pdfmetrics.registerFont(TTFont(nm,str(font_dir/fn)))
 except: pass

def diagram(path, title, boxes, links):
 W,H=1500,760; im=PILImage.new('RGB',(W,H),(248,250,252)); dr=ImageDraw.Draw(im)
 f=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',22); fb=ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',26)
 dr.text((60,35),title,font=fb,fill=(24,40,64))
 loc={}
 for name,x,y,w,h,subtitle in boxes:
  loc[name]=(x,y,w,h)
  dr.rounded_rectangle((x,y,x+w,y+h),radius=18,fill=(255,255,255),outline=(43,87,139),width=3)
  dr.rounded_rectangle((x,y,x+w,y+50),radius=16,fill=(31,58,95))
  dr.rectangle((x,y+32,x+w,y+50),fill=(31,58,95))
  dr.text((x+14,y+11),name,font=fb,fill='white')
  words=subtitle.split('\n')
  for i,t in enumerate(words): dr.text((x+14,y+64+i*30),t,font=f,fill=(52,65,81))
 for a,b,label in links:
  x,y,w,h=loc[a]; X,Y,ww,hh=loc[b]
  start=(x+w//2,y+h//2); end=(X+ww//2,Y+hh//2)
  dr.line((start,end),fill=(70,117,167),width=3)
  mx=(start[0]+end[0])//2; my=(start[1]+end[1])//2
  dr.text((mx+4,my-22),label,font=f,fill=(41,75,115))
 im.save(path)

architecture=TMP/'arquitectura.png'
diagram(architecture,'Arquitectura de Magnus SIG | Django MVT',[
 ('Navegador',60,290,260,150,'Interfaz HTML/CSS/JS\nHTMX y recursos estáticos'),
 ('URLs',410,290,220,150,'Enrutamiento HTTP\nproductos/urls.py'),
 ('Vistas',730,290,240,150,'Reglas de aplicación\nproductos/views.py'),
 ('Modelos y servicios',1060,260,360,200,'ORM y entidades\nServicio transaccional de stock'),
 ('Base de datos',1080,560,320,130,'MySQL 8 por defecto\nSQLite opcional'),
 ('Plantillas',700,560,280,130,'Templates Django\nHTML renderizado'),
], [('Navegador','URLs','solicitud'),('URLs','Vistas','resuelve'),('Vistas','Modelos y servicios','consulta/actualiza'),('Modelos y servicios','Base de datos','ORM'),('Vistas','Plantillas','contexto')])
model=TMP/'modelo.png'
diagram(model,'Modelo de datos | relaciones principales',[
 ('Categoría',40,100,250,135,'nombre, estado'),('Producto',380,100,300,175,'código, precios\nstock mínimo'),
 ('Inventario',810,100,280,150,'cantidad y ubicación'),('Movimiento',1160,100,290,170,'tipo, cantidad\nfecha, responsable'),
 ('Proveedor',110,470,270,145,'datos comerciales'),('Compra',490,470,280,165,'estado y detalles'),
 ('Cliente',850,470,260,145,'datos de contacto'),('Venta',1190,470,250,165,'estado y detalles'),
], [('Categoría','Producto','1:N'),('Producto','Inventario','1:1'),('Producto','Movimiento','1:N'),('Proveedor','Compra','1:N'),('Compra','Producto','detalles'),('Cliente','Venta','1:N'),('Venta','Producto','detalles')])

styles=getSampleStyleSheet()
styles.add(ParagraphStyle(name='TitleX',parent=styles['Title'],fontName='Liberation-Bold',fontSize=23,leading=29,textColor=colors.HexColor('#17365D'),alignment=TA_CENTER,spaceAfter=18))
styles.add(ParagraphStyle(name='SubX',parent=styles['Normal'],fontName='Liberation',fontSize=12,leading=17,alignment=TA_CENTER,textColor=colors.HexColor('#526174')))
styles.add(ParagraphStyle(name='H1X',parent=styles['Heading1'],fontName='Liberation-Bold',fontSize=16,leading=20,textColor=colors.HexColor('#17365D'),spaceBefore=6,spaceAfter=10,keepWithNext=True))
styles.add(ParagraphStyle(name='H2X',parent=styles['Heading2'],fontName='Liberation-Bold',fontSize=12,leading=15,textColor=colors.HexColor('#205493'),spaceBefore=8,spaceAfter=5,keepWithNext=True))
styles.add(ParagraphStyle(name='BodyX',parent=styles['BodyText'],fontName='Liberation',fontSize=9.4,leading=14,spaceAfter=7,alignment=TA_LEFT))
styles.add(ParagraphStyle(name='SmallX',parent=styles['BodyText'],fontName='Liberation',fontSize=8,leading=11,textColor=colors.HexColor('#506176'),spaceAfter=5))
styles.add(ParagraphStyle(name='BulletX',parent=styles['BodyText'],fontName='Liberation',fontSize=9.2,leading=13,leftIndent=14,firstLineIndent=-8,spaceAfter=4))
styles.add(ParagraphStyle(name='RefX',parent=styles['BodyText'],fontName='Liberation',fontSize=8.4,leading=11,spaceAfter=4))

def P(s,style='BodyX'): return Paragraph(s,styles[style])
def bullets(items): return [P('• '+x,'BulletX') for x in items]
def pic(path,caption,w=6.7):
 im=Image(str(path)); im._restrictSize(w*inch,4.4*inch)
 return [im,P('<b>Figura.</b> '+caption,'SmallX'),Spacer(1,6)]

story=[]
story += [Spacer(1,1.0*inch),P('MAGNUS SIG','TitleX'),P('Proyecto final, documentación y sustentación','SubX'),Spacer(1,.35*inch),P('Versión académica 1.0','SubX'),Spacer(1,.7*inch)]
for t in ['Asignatura: Lenguaje de Programación 1','Periodo: 2026-2','Integrantes: Juan José Osorio Quitian · Kevin Julián Sánchez Pérez · Brayan Steven Sánchez Carvajal · Luis Esteban Medina Echeverry · Hilver Eduardo Galindo','Docente: dato pendiente de confirmar','Neiva, Huila · 2026']:
 story.append(P(t,'SubX')); story.append(Spacer(1,8))
story += [PageBreak(),P('Tabla de contenido','H1X')]
toc=['1. Presentación del proyecto','2. Problema, objetivos y alcance','3. Requisitos y funciones principales','4. Arquitectura y modelo de datos','5. Metodología de desarrollo','6. Calidad y resultados de pruebas','7. Guía breve de usuario','8. Retos y conclusiones','9. Sustentación y enlaces','Referencias']
story += [P(f'{x}','BodyX') for x in toc]
story += [PageBreak(),P('1. Presentación del proyecto','H1X'),P('Magnus SIG es una aplicación web para administrar inventario de equipos de protección personal, dotación y suministros relacionados con seguridad y salud en el trabajo. El sistema permite gestionar catálogo y categorías, existencias, movimientos, compras y despachos, proveedores, clientes, servicios, reportes y configuración. La versión revisada corresponde a una aplicación Django organizada con el patrón Modelo-Vista-Plantilla (MVT).','BodyX'),P('Tecnologías y organización','H2X')]
story += bullets(['Backend: Python 3.14 en el entorno verificado y Django 6.1.1.','Persistencia: MySQL configurado por defecto; SQLite se puede activar con DJANGO_USE_SQLITE.','Interfaz: plantillas Django, Tailwind CSS 4, JavaScript y HTMX; las dependencias de movimiento y visualización se empaquetan con npm/esbuild.','Control de acceso: inicio de sesión con perfiles Administrador y Vendedor y restricciones por módulo.'])
story += pic(AS/'02-dashboard-admin.png','Panel de administración con indicadores y navegación de módulos.',6.5)
story += [P('2. Problema, objetivos y alcance','H1X'),P('El proyecto aborda la dispersión de datos y la dificultad para mantener existencias actualizadas en operaciones que registran productos, entradas y despachos. Su objetivo es centralizar esas operaciones y mantener registros consultables de los cambios de inventario.','BodyX'),P('Funciones incluidas','H2X')]
story += bullets(['Crear, consultar, editar y administrar productos y categorías.','Consultar existencias y alertas según el stock mínimo configurado.','Registrar compras/entradas y ventas/despachos mediante estados pendientes y confirmación.','Conservar movimientos con producto, cantidad, tipo, fecha y responsable.','Administrar proveedores, clientes y servicios SG-SST.','Consultar reportes, exportar datos y modificar parámetros globales.'])
story += [P('La documentación cubre las funciones del código en la rama main. No atribuye al sistema certificaciones de cumplimiento, inspecciones de EPP ni gestión de incidentes, que no están implementadas.','BodyX')]
story += [PageBreak(),P('3. Requisitos y funciones principales','H1X'),P('El software se ejecuta localmente con Python/Django y una base de datos MySQL accesible, o con SQLite para un entorno aislado. Para compilar los recursos de frontend se requieren Node.js y npm. El README describe instalación, variables de entorno, migraciones, preparación de roles y creación de superusuario.','BodyX'),P('Criterios funcionales demostrables','H2X')]
story += bullets(['El usuario inicia sesión antes de acceder a las vistas protegidas.','El Administrador mantiene el catálogo, proveedores, compras y configuración; el Vendedor consulta inventario y registra despachos dentro de sus permisos.','Una entrada afecta existencias cuando se confirma su recepción.','Una salida descuenta existencias al despacharse y se rechaza si no hay unidades suficientes.','Los formularios validan datos antes de guardar.'])
story += pic(AS/'03-inventario.png','Consulta de inventario con estado de existencias.',6.5)
story += [PageBreak(),P('4. Arquitectura y modelo de datos','H1X'),P('La capa de presentación usa plantillas HTML y archivos estáticos. Las URL dirigen solicitudes a las vistas; estas aplican permisos y coordinan formularios, modelos y servicios. El servicio de inventario usa transacciones atómicas para registrar la operación y ajustar el saldo. Los modelos Django representan entidades relacionales persistidas mediante el ORM.','BodyX')]
story += pic(architecture,'Diagrama de arquitectura derivado de rutas, vistas, servicios, modelos y configuración del proyecto.',6.8)
story += pic(model,'Relaciones principales observadas en los modelos Django; el diagrama resume las entidades centrales, no todos los campos.',6.8)
story += [P('Persistencia y migraciones','H2X'),P('La configuración leída para esta revisión conecta por defecto a MySQL, y ambas migraciones de la aplicación productos aparecen aplicadas en esa conexión. El aviso de una migración pendiente visto en otra terminal puede corresponder a otra base o configuración local. Para comprobarlo, ejecutar showmigrations con las mismas variables de entorno y el mismo archivo .env que usa runserver.','BodyX')]
story += [PageBreak(),P('5. Metodología de desarrollo','H1X'),P('El equipo organizó el trabajo en seis Sprints y utilizó Kanban para visualizar el estado de las tareas. La secuencia documentada comienza con el entorno y el MVP de consola, continúa con el modelo de datos, operaciones CRUD e interfaz, y termina con pruebas y documentación.','BodyX')]
tb=Table([['Sprint','Propósito'],['1','Preparación del entorno y prototipo inicial'],['2','Modelo y persistencia'],['3','CRUD y validaciones'],['4','Interfaz y experiencia de usuario'],['5','Pruebas funcionales'],['6','Cierre y documentación']],colWidths=[.85*inch,5.6*inch])
tb.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#17365D')),('TEXTCOLOR',(0,0),(-1,0),colors.white),('FONTNAME',(0,0),(-1,-1),'Liberation'),('FONTNAME',(0,0),(-1,0),'Liberation-Bold'),('FONTSIZE',(0,0),(-1,-1),9),('GRID',(0,0),(-1,-1),.4,colors.HexColor('#CBD5E1')),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#F1F5F9')]),('VALIGN',(0,0),(-1,-1),'MIDDLE'),('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7)]))
story += [tb,Spacer(1,10),P('La asignación nominal del Product Owner no se incluye porque el dato anterior fue confirmado como incorrecto y el equipo aún debe definir el nombre correcto.','BodyX')]
story += [PageBreak(),P('6. Calidad y resultados de pruebas','H1X'),P('La revisión ejecutó el chequeo de configuración y la suite de Django sobre la conexión MySQL activa. El chequeo no reportó problemas y las 20 pruebas finalizaron correctamente. Durante la primera ejecución, un caso falló al intentar duplicar un tipo de servicio que la migración ya había creado; el test se ajustó para reutilizar el registro y luego la suite pasó completa.','BodyX')]
story += [P('Evidencia de verificación','H2X'),P('<b>Comandos ejecutados:</b> manage.py check; manage.py showmigrations productos; manage.py test productos.','BodyX'),P('<b>Resultado:</b> 20 pruebas ejecutadas, resultado OK. El tiempo informado por la ejecución final fue aproximadamente 12,9 segundos.','BodyX'),P('La ejecución de tests crea una base temporal para pruebas y la destruye al terminar. No modifica la base de datos del usuario. La migración 0002 está aplicada en la conexión consultada.','BodyX')]
story += [PageBreak(),P('7. Guía breve de usuario','H1X'),P('Acceso. Abrir la dirección local de la aplicación e iniciar sesión con las credenciales configuradas por el administrador. Los usuarios y contraseñas no se incluyen en este documento.','BodyX')]
for imgpath,caption in [('01-login.png','Acceso al sistema.'),('04-catalogo-productos.png','Catálogo y consulta de productos.'),('09-form-producto.png','Formulario para crear o editar productos.'),('14-entradas.png','Listado de entradas de mercancía.'),('24-salidas-vendedor.png','Módulo de salidas para vendedor.')]:
 story += pic(AS/imgpath,caption,6.3)
story += [P('Flujo de operación de inventario','H2X'),P('Para recibir mercancía, el usuario autorizado registra la entrada y confirma la recepción una vez verificada. Para despachar, registra la salida, revisa el cliente, los productos y las cantidades, y confirma el despacho. Si las existencias no alcanzan, el sistema rechaza la operación y presenta un mensaje. El manual completo está disponible en docs/Manual_Usuario_Magnus_SIG.pdf y contiene procedimientos detallados de todos los módulos.','BodyX')]
story += [PageBreak(),P('8. Retos y conclusiones','H1X'),P('Un reto técnico fue mantener sincronizados los cambios de existencias con el historial de movimientos y evitar saldos negativos. La lógica se concentra en un servicio transaccional que valida cantidades y registra el cambio junto con el movimiento. También se resolvió la convivencia de tipos de servicio base con las pruebas automatizadas, haciendo que los datos iniciales provengan de migraciones y que las pruebas reutilicen esos registros.','BodyX'),P('El proyecto integra conceptos de programación orientada a objetos, funciones modulares, validaciones, colecciones, persistencia relacional y control de acceso. La suite actual cubre rutas, formularios, entradas, salidas, servicios y permisos. Como cierre, se recomienda mantener la configuración local fuera de Git, revisar las migraciones de cada entorno y documentar futuras mejoras en nuevos incrementos.','BodyX')]
story += [PageBreak(),P('9. Sustentación y enlaces','H1X'),P('<b>Repositorio público:</b> <link href="https://github.com/soykelian/CRUD_MagnusSIG" color="#1558A6">https://github.com/soykelian/CRUD_MagnusSIG</link>','BodyX'),P('<b>Video de demostración:</b> pendiente de grabación y publicación. Agregar aquí el enlace compartible antes de cargar el PDF.','BodyX'),P('Recorrido recomendado para el video','H2X')]
story += bullets(['Iniciar sesión con un usuario de demostración seguro, sin mostrar contraseñas.','Mostrar dashboard, inventario y búsqueda de productos.','Registrar o consultar un producto y enseñar una validación de formulario.','Registrar una entrada y confirmar recepción para evidenciar el aumento de existencias.','Intentar una salida superior al stock para mostrar el rechazo; luego despachar una salida válida.','Mostrar el historial de movimientos, permisos de Administrador/Vendedor y un reporte exportado.','Cerrar con arquitectura, manejo transaccional de stock, pruebas, reto técnico y conclusiones del equipo.'])
story += [P('<b>Historial de commits:</b> consultar el registro público de GitHub para evidenciar participación individual. Cada integrante debe poder explicar el módulo en el que colaboró.','BodyX'),P('Datos de portada por completar antes de entregar: nombre del docente y enlace del video.','BodyX')]
story += [P('Referencias','H2X'),P('Django Software Foundation. (s. f.). <i>Django documentation</i>. https://docs.djangoproject.com/','RefX'),P('Schwaber, K., & Sutherland, J. (2020). <i>La guía de Scrum</i>. https://scrumguides.org/','RefX'),P('Tailwind Labs. (s. f.). <i>Tailwind CSS documentation</i>. https://tailwindcss.com/docs','RefX'),P('Magnus SIG. (2026). <i>Manual de usuario Magnus SIG</i> (versión 1.0) [Manual de usuario]. docs/Manual_Usuario_Magnus_SIG.pdf','RefX')]

# Keep the cover and contents on their own pages; let body sections flow naturally.
break_count=0
flow=[]
for item in story:
    if isinstance(item,PageBreak):
        break_count+=1
        if break_count>2: continue
    flow.append(item)
story=flow

def footer(canvas,doc):
 canvas.saveState(); w,h=letter
 canvas.setStrokeColor(colors.HexColor('#CBD5E1')); canvas.line(.75*inch,.62*inch,w-.75*inch,.62*inch)
 canvas.setFont('Liberation',8); canvas.setFillColor(colors.HexColor('#64748B'))
 canvas.drawString(.75*inch,.42*inch,'MAGNUS SIG · Proyecto final · 2026-2')
 canvas.drawRightString(w-.75*inch,.42*inch,str(doc.page)); canvas.restoreState()

SimpleDocTemplate(str(OUT),pagesize=letter,rightMargin=.78*inch,leftMargin=.78*inch,topMargin=.72*inch,bottomMargin=.8*inch,title='Entrega 4 Magnus SIG Proyecto Final',author='Equipo Magnus SIG').build(story,onFirstPage=footer,onLaterPages=footer)
print(OUT)
