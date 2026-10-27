from pathlib import Path
from io import BytesIO
from pypdf import PdfReader,PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph,Table,TableStyle
from reportlab.lib.utils import ImageReader
from reportlab.lib.enums import TA_CENTER
R=Path(__file__).resolve().parents[4]; T=R/'docs'/'planeacion'/'revision'/'pdf'; src=PdfReader(R/'docs'/'especificacion'/'documento_Sistema.pdf'); W,H=792,612
navy=HexColor('#0b3f91'); blue=HexColor('#1684f8'); ink=HexColor('#172b4d'); muted=HexColor('#73819a'); line=HexColor('#dce5f0'); pale=HexColor('#f3f7fc'); amber=HexColor('#fff5e5')
st={'body':ParagraphStyle('body',fontName='Helvetica',fontSize=9.5,leading=13,textColor=ink),'small':ParagraphStyle('small',fontName='Helvetica',fontSize=8,leading=10.5,textColor=muted),'cell':ParagraphStyle('cell',fontName='Helvetica',fontSize=8,leading=10,textColor=ink),'head':ParagraphStyle('head',fontName='Helvetica-Bold',fontSize=12,leading=15,textColor=navy),'center':ParagraphStyle('center',fontName='Helvetica',fontSize=9,leading=11,textColor=ink,alignment=TA_CENTER)}
def page(n,title=None,sub=None):
 b=BytesIO(); c=canvas.Canvas(b,pagesize=(W,H)); c.setFillColor(colors.white); c.rect(0,0,W,H,fill=1,stroke=0)
 if title:
  c.setFillColor(navy); c.setFont('Helvetica-Bold',16); c.drawString(42,574,title)
  if sub: c.setFillColor(muted); c.setFont('Helvetica',8.5); c.drawString(42,558,sub)
  c.setStrokeColor(line); c.line(42,547,750,547)
 c.setStrokeColor(line); c.line(42,33,750,33); c.setFillColor(muted); c.setFont('Helvetica',7); c.drawString(42,20,'Sistema Web de Gestión de Inventario · Magnus SIG'); c.drawRightString(750,20,'Página '+str(n))
 return b,c
def P(c,s,x,top,w,style='body'):
 q=Paragraph(s,st[style]); _,h=q.wrap(w,500); q.drawOn(c,x,top-h); return top-h
def box(c,x,y,w,h,fill=pale,stroke=line):
 c.setFillColor(fill); c.setStrokeColor(stroke); c.roundRect(x,y,w,h,7,fill=1,stroke=1)
def note(c,s,x,y,w,h,fill=pale):
 box(c,x,y,w,h,fill,fill); P(c,s,x+10,y+h-8,w-20,'small')
def done(b,c): c.save(); b.seek(0); return PdfReader(b).pages[0]
def tab(c,data,x,y,widths,heights=None):
 t=Table([[Paragraph(v,st['cell']) for v in row] for row in data],colWidths=widths,rowHeights=heights)
 t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),HexColor('#edf4fc')),('GRID',(0,0),(-1,-1),.45,line),('VALIGN',(0,0),(-1,-1),'MIDDLE'),('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7)])); _,h=t.wrapOn(c,sum(widths),500); t.drawOn(c,x,y-h); return h
pages={}
# cover
b,c=page(1); c.drawImage(ImageReader(R/'assets'/'branding'/'logo.png'),42,442,width=108,height=108,mask='auto',preserveAspectRatio=True); c.setFillColor(navy); c.setFont('Helvetica-Bold',11); c.drawString(164,532,'MAGNUS SIG'); c.setFillColor(ink); c.setFont('Helvetica-Bold',23); c.drawString(164,500,'Sistema Web de Gestión de Inventario'); c.setFillColor(muted); c.setFont('Helvetica',10); c.drawString(164,479,'Modelado lógico · prototipo visual · propuesta de esqueleto Django'); c.setStrokeColor(navy); c.setLineWidth(2); c.line(42,458,750,458); P(c,'INTEGRANTES',42,435,700,'head')
names=['Kevin Julian Sanchez Perez','Juan Jose Osorio Quitian','Luis Esteban Medina','Brayan Steven Sanchez','Sergio Neira','Hilver Galindo']
for i,n in enumerate(names):
 x=55+(i%2)*350; y=394-(i//2)*35; c.setFillColor(blue); c.circle(x,y+2,3,fill=1,stroke=0); c.setFillColor(ink); c.setFont('Helvetica',10); c.drawString(x+12,y-2,n)
note(c,'<b>Estado:</b> mockups estáticos terminados; el proyecto Django está en etapa inicial. El CRUD, la app de productos y la conexión MySQL aún son trabajo pendiente.',42,100,708,48); c.setFillColor(muted); c.setFont('Helvetica',8.5); c.drawString(42,81,'Stack objetivo: Python · Django MVT · HTML/CSS · SQLite local / MySQL objetivo'); c.drawString(42,64,'Fecha: Octubre de 2026'); pages[0]=done(b,c)
# contents
b,c=page(2,'Contenido y alcance','Funciones previstas y estado real del proyecto.')
P(c,'CONTENIDO',42,525,320,'head'); y=493
for s in ['1. Modelado: flujos, casos de uso, clases y arquitectura.','2. Prototipado: navegación y seis pantallas de referencia.','3. Esqueleto: estado del repositorio, estructura propuesta, stubs y datos.','4. Resumen del README y tecnologías.']:
 y=P(c,s,50,y,330)-9
P(c,'ALCANCE FUNCIONAL PROPUESTO',420,525,330,'head'); P(c,'Aplicación web académica para gestionar productos y categorías: registrar, consultar, buscar, actualizar y eliminar productos; validar datos y representar existencias. Las categorías clasifican productos.',420,495,330); P(c,'Fuera de alcance: facturación, pagos y reportes complejos.',420,397,330)
note(c,'<b>Mockups:</b> capturas de HTML/CSS estático. Los productos, cifras, precios, fechas y estados son ejemplos de diseño, no datos guardados ni funciones operativas.',42,175,708,58); note(c,'<b>Código:</b> la estructura y los stubs de inventario descritos son la propuesta a implementar. En el repositorio actual solo está creado el proyecto base Django, con SQLite.',42,105,708,52,amber); pages[1]=done(b,c)
# use cases diagram
b,c=page(5,'1.3 Casos de uso','El Administrador puede realizar las operaciones del Usuario y acceder al panel de Django.')
x0,y0,bw,bh=150,80,492,435; c.setStrokeColor(navy); c.roundRect(x0,y0,bw,bh,7,fill=0,stroke=1); c.setFillColor(navy); c.setFont('Helvetica-Bold',9); c.drawString(165,495,'Sistema Web de Gestión de Inventario')
labels=['Registrar producto','Consultar productos','Buscar producto','Actualizar producto','Eliminar producto','Gestionar categorías','Administrar información del sistema']; ys=[]
for i,s in enumerate(labels):
 cy=454-i*50; ys.append(cy); c.setFillColor(pale); c.setStrokeColor(HexColor('#b9cce5')); c.ellipse(284,cy-14,508,cy+14,fill=1,stroke=1); c.setFillColor(ink); c.setFont('Helvetica',8); c.drawCentredString(396,cy-3,s)
def actor(x,y,label):
 c.setStrokeColor(ink); c.circle(x,y+18,6,fill=0,stroke=1); c.line(x,y+12,x,y-9); c.line(x,y+5,x-9,y-2); c.line(x,y+5,x+9,y-2); c.line(x,y-9,x-7,y-22); c.line(x,y-9,x+7,y-22); c.setFillColor(ink); c.setFont('Helvetica-Bold',8); c.drawCentredString(x,y-36,label)
actor(82,285,'Usuario'); actor(710,285,'Administrador')
for cy in ys[:-1]: c.setStrokeColor(HexColor('#b7c3d1')); c.setLineWidth(.4); c.line(94,285,284,cy); c.line(508,cy,698,285)
c.line(508,ys[-1],698,285); P(c,'Asociaciones simples. Los perfiles y permisos son conceptuales; el mockup muestra un usuario administrador de ejemplo y no implementa autenticación.',42,66,708,'small'); pages[4]=done(b,c)
# actors + classes
b,c=page(6,'1.4 Actores y modelo de clases','Una categoría puede contener cero o muchos productos; cada producto pertenece a una categoría.')
P(c,'RESPONSABILIDADES PROPUESTAS',42,520,370,'head')
data=[['Actor','Acceso propuesto'],['Usuario','Registrar, consultar, buscar, actualizar y eliminar productos; consultar y gestionar categorías.'],['Administrador','Todas las operaciones del Usuario y acceso adicional al panel administrativo de Django.']]
tab(c,data,42,490,[105,280],[27,48,48]); note(c,'Los roles aún no están implementados. El perfil “Admin Magnus” en los mockups es ilustrativo.',42,275,385,53,amber)
P(c,'ENTIDADES DEL DOMINIO',455,520,300,'head')
for x,title,ls in [(455,'Categoria',['id: entero','nombre: texto','descripcion: texto','obtener_productos()']), (610,'Producto',['id: entero','nombre: texto','descripcion: texto','categoria: FK','precio: decimal','cantidad: entero','fechas'])]:
 box(c,x,275,140,190,colors.white,line); c.setFillColor(navy); c.roundRect(x,434,140,31,6,fill=1,stroke=0); c.setFillColor(colors.white); c.setFont('Helvetica-Bold',9); c.drawCentredString(x+70,445,title); yy=416
 for z in ls: c.setFillColor(ink); c.setFont('Helvetica',7.8); c.drawString(x+10,yy,z); yy-=18
P(c,'Relación: Categoria (1) a Producto (0..*).',455,260,295,'small'); P(c,'Los atributos y métodos son el modelo propuesto para la app Django.',455,242,295,'small'); pages[5]=done(b,c)
# architecture
b,c=page(7,'1.5 Arquitectura objetivo','El HTML/CSS es un prototipo visual separado del backend Django pendiente.')
steps=[('1','Interfaz de referencia','HTML y CSS estáticos. Los controles no guardan ni consultan información.'),('2','Aplicación Django','Templates, views, forms y models de inventario (por implementar).'),('3','Django ORM','Capa propuesta para persistir y consultar entidades.'),('4','Base de datos','SQLite está configurado; MySQL es el destino previsto.')]
for i,(n,t,d) in enumerate(steps):
 x=42+i*181; box(c,x,250,164,195,colors.white,line); c.setFillColor(blue if i==0 else navy); c.circle(x+22,420,11,fill=1,stroke=0); c.setFillColor(colors.white); c.setFont('Helvetica-Bold',8); c.drawCentredString(x+22,417,n); P(c,t,x+14,394,136,'head'); P(c,d,x+14,355,136,'small')
 if i<3: c.setStrokeColor(blue); c.line(x+164,345,x+178,345); c.line(x+173,349,x+178,345); c.line(x+173,341,x+178,345)
note(c,'El ORM, las entidades y la conexión MySQL no están implementados en el proyecto actual.',42,145,708,46); pages[6]=done(b,c)
# navigation
b,c=page(8,'2. Prototipado y navegación','Seis pantallas HTML/CSS estáticas representan rutas principales previstas.')
rows=[['Pantalla','Ruta prevista','Correspondencia'],['Productos','/','Listado, búsqueda, filtros y stock'],['Nuevo producto','/productos/nuevo/','Formulario y validación prevista'],['Detalle','/productos/&lt;id&gt;/','Datos del producto y existencias'],['Editar / eliminar','/productos/&lt;id&gt;/editar/ · /eliminar/','Formulario y confirmación'],['Categorías','/categorias/','Listado y acceso visual para crear'],['Administración','/admin/','Panel Django; fuera del mockup']]
tab(c,rows,42,520,[125,225,358],[27,38,38,38,43,38,38]); note(c,'El prototipo de categorías solo muestra el listado. El formulario para crear o editar categorías queda pendiente. Contadores y ejemplos de productos son ilustrativos.',42,122,708,57); pages[7]=done(b,c)
# screenshot pages

def imgpage(n,title,sub,items,notetext):
 b,c=page(n,title,sub)
 for fn,label,x,top,mw,mh in items:
  c.setFillColor(navy); c.setFont('Helvetica-Bold',9); c.drawString(x,612-top-12,label); im=ImageReader(str(T/fn)); iw,ih=im.getSize(); s=min(mw/iw,mh/ih); c.drawImage(im,x,612-top-20-ih*s,width=iw*s,height=ih*s,mask='auto')
 note(c,notetext,42,42,708,30); return done(b,c)
pages[8]=imgpage(9,'2.1 Mockup · Inventario de productos','Listado, búsqueda, filtros, existencias y accesos CRUD.',[('screen-1.png','Listado y búsqueda',42,88,708,430)],'Captura estática. Filas, cifras y estados de stock son datos de ejemplo.')
pages[9]=imgpage(10,'2.2 Mockups · Registro y edición','Formularios y mensajes que corresponden a las validaciones propuestas.',[('screen-2.png','Registrar producto',42,88,345,415),('screen-3.png','Editar · mensajes',405,88,345,415)],'La validación se propone en Django Forms; no está implementada en estas pantallas estáticas.')
b,c=page(11,'2.3 Mockups · Detalle, categorías y eliminación','Consulta, clasificación y confirmación antes de eliminar.')
for fn,label,x,top,mw,mh in [('screen-4.png','Detalle',42,88,350,420),('screen-5.png','Categorías',410,88,340,198),('screen-6.png','Confirmación de eliminación',410,308,340,198)]:
 c.setFillColor(navy); c.setFont('Helvetica-Bold',9); c.drawString(x,612-top-12,label); im=ImageReader(str(T/fn)); iw,ih=im.getSize(); s=min(mw/iw,mh/ih); c.drawImage(im,x,612-top-20-ih*s,width=iw*s,height=ih*s,mask='auto')
note(c,'Los datos son ilustrativos. La pantalla de categorías solo representa el listado; la administración funcional queda pendiente.',42,42,708,30); pages[10]=done(b,c)
# repo actuality and target
b,c=page(12,'3. Estado del código y estructura','Se distingue el contenido presente en el repositorio de la app que se propone implementar.')
P(c,'REPOSITORIO ACTUAL',42,520,330,'head'); P(c,'CRUD_MagnusSIG/<br/>├─ README.md<br/>├─ Logotipo corporativo Magnus SIG.png<br/>├─ mockups-inventario.html<br/>├─ mockups-inventario.css<br/>└─ magnus_sig/<br/>&nbsp;&nbsp; ├─ manage.py<br/>&nbsp;&nbsp; └─ magnus_sig/{settings,urls,asgi,wsgi}.py',52,488,320,'small')
note(c,'El proyecto tiene /admin/ y SQLite configurado. No existen todavía la app productos, modelos, migraciones, vistas, forms, templates ni rutas CRUD.',42,298,340,63,amber)
P(c,'ESTRUCTURA OBJETIVO · PENDIENTE',420,520,330,'head'); P(c,'magnus_sig/productos/<br/>├─ models.py · Categoria y Producto<br/>├─ forms.py · validaciones<br/>├─ views.py · operaciones CRUD<br/>├─ urls.py · rutas del mockup<br/>├─ admin.py · configuración<br/>├─ migrations/<br/>└─ templates/productos/<br/>&nbsp;&nbsp; ├─ lista.html<br/>&nbsp;&nbsp; ├─ detalle.html<br/>&nbsp;&nbsp; ├─ form.html<br/>&nbsp;&nbsp; └─ confirmar_eliminar.html<br/>requirements.txt · pendiente',430,488,320,'small')
note(c,'No se afirman `manage.py check` ni pruebas de humo aprobadas: la app y sus pruebas todavía no existen en el repositorio.',420,298,330,63,amber); P(c,'Repositorio remoto de GitHub: no se indicó una URL verificable.',42,205,708,'small'); pages[11]=done(b,c)
# schema/config current vs future
b,c=page(16,'3.4 Datos y configuración','Esquema relacional propuesto; SQLite es la única base configurada actualmente.')
P(c,'MODELO DE DATOS OBJETIVO',42,520,330,'head'); P(c,'<b>Categoria</b>: id PK, nombre VARCHAR(100) obligatorio, descripcion TEXT opcional.<br/><br/><b>Producto</b>: id PK, nombre VARCHAR(150) obligatorio, descripcion TEXT opcional, categoria_id FK obligatoria, precio DECIMAL(10,2) mayor que cero, cantidad entero ≥ 0, fechas de creación y actualización.<br/><br/>Una categoría puede contener cero o muchos productos; cada producto pertenece a una categoría.',42,488,330)
P(c,'CONFIGURACIÓN',420,520,330,'head'); P(c,'<b>Actual:</b> `magnus_sig/settings.py` usa SQLite local. No configura variables de entorno para cambiar a MySQL.<br/><br/><b>Objetivo:</b> MySQL mediante Django ORM, pendiente de instalar y configurar.<br/><br/><b>Pendiente:</b> `requirements.txt` y dependencia del conector MySQL.',420,488,330)
note(c,'Los ejemplos de `.gitignore` ampliado y `requirements.txt` del borrador original son propuestas, no archivos presentes en la raíz.',42,123,708,52,amber); pages[15]=done(b,c)
# README summary
b,c=page(17,'README.md · resumen alineado','Descripción de referencia que refleja el estado real del proyecto.')
P(c,'Sistema Web de Gestión de Inventario',42,520,708,'head'); P(c,'<b>Integrantes</b><br/>Kevin Julian Sanchez Perez · Juan Jose Osorio Quitian · Luis Esteban Medina<br/>Brayan Steven Sanchez · Sergio Neira · Hilver Galindo',42,488,708)
P(c,'<b>Descripción</b><br/>Propuesta académica para gestionar productos y categorías. El prototipo HTML/CSS presenta listado, búsqueda, formularios, detalle, categorías y confirmación de eliminación. El CRUD Django con persistencia queda pendiente.',42,425,708)
P(c,'<b>Tecnologías</b><br/>Prototipo: HTML5 y CSS3. Backend objetivo: Python y Django MVT. Base actual: SQLite; destino previsto: MySQL.',42,337,708)
P(c,'<b>Estado</b><br/>Existe el proyecto base Django y el mockup estático. La app de inventario, validaciones, migraciones, integración MySQL y pruebas no están implementadas.',42,270,708)
note(c,'El README de la raíz sigue siendo una descripción breve; este resumen en el PDF no afirma que el README ya se haya modificado.',42,112,708,49); P(c,'Repositorio: soykelian/CRUD_MagnusSIG · nombre interno Django: magnus_sig.',42,90,708,'small'); pages[16]=done(b,c)
# Build draft pages (direct replacement), only code excerpt pages receive note overlays.
w=PdfWriter()
for i,old in enumerate(src.pages):
 if i in pages: w.add_page(pages[i]); continue
 if i in (12,13,14):
  b=BytesIO(); c=canvas.Canvas(b,pagesize=(W,H)); box(c,495,535,255,42,amber,HexColor('#f0d8ad')); P(c,'<b>PROPUESTA · STUB</b><br/>No integrado ni probado en el repositorio.',505,569,235,'small'); c.save(); b.seek(0); overlay=PdfReader(b).pages[0]; old.merge_page(overlay)
 w.add_page(old)
out=T/'documento_Sistema_revision.pdf'
with out.open('wb') as f:w.write(f)
r=PdfReader(out); print('pages',len(r.pages),'bytes',out.stat().st_size)
for ix in [0,1,4,5,6,7,8,9,10,11,12,13,14,15,16]: print(ix+1,(r.pages[ix].extract_text() or '')[:85].replace('\n',' | '))
