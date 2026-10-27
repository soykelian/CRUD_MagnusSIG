from pathlib import Path
from io import BytesIO
from pypdf import PdfReader, PdfWriter
from pypdf.generic import DictionaryObject, NameObject, ArrayObject, FloatObject, TextStringObject
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph, Table, TableStyle
from reportlab.lib.utils import simpleSplit

ROOT=Path(__file__).resolve().parents[4]
REVISION=ROOT/'docs'/'planeacion'/'revision'/'pdf'
W,H=792,612; NAVY=HexColor('#0b3f91'); INK=HexColor('#172b4d'); MUTED=HexColor('#73819a'); LINE=HexColor('#dce5f0'); PALE=HexColor('#f3f7fc'); AMBER=HexColor('#fff5e5')
styles={'body':ParagraphStyle('body',fontName='Helvetica',fontSize=9,leading=12,textColor=INK),'small':ParagraphStyle('small',fontName='Helvetica',fontSize=7.8,leading=10,textColor=MUTED),'cell':ParagraphStyle('cell',fontName='Helvetica',fontSize=7.8,leading=9.5,textColor=INK),'code':ParagraphStyle('code',fontName='Courier',fontSize=7.3,leading=9,textColor=INK),'h':ParagraphStyle('h',fontName='Helvetica-Bold',fontSize=11,leading=14,textColor=NAVY)}
def makepage(n,title,sub=None):
 b=BytesIO(); c=canvas.Canvas(b,pagesize=(W,H)); c.setFillColor(colors.white); c.rect(0,0,W,H,fill=1,stroke=0)
 c.setFillColor(NAVY); c.setFont('Helvetica-Bold',16); c.drawString(42,H-38,title)
 if sub: c.setFillColor(MUTED); c.setFont('Helvetica',8.5); c.drawString(42,H-55,sub)
 c.setStrokeColor(LINE); c.line(42,H-66,750,H-66); c.line(42,33,750,33); c.setFillColor(MUTED); c.setFont('Helvetica',7); c.drawString(42,20,'Sistema Web de Gestión de Inventario · Magnus SIG'); c.drawRightString(750,20,f'Página {n}')
 return b,c
def para(c,s,x,top,w,style='body'):
 p=Paragraph(s,styles[style]); _,h=p.wrap(w,500); p.drawOn(c,x,top-h); return top-h
def note(c,s,x,y,w,h,fill=PALE):
 c.setFillColor(fill); c.setStrokeColor(fill); c.roundRect(x,y,w,h,7,fill=1,stroke=1); para(c,s,x+10,y+h-8,w-20,'small')
def done(b,c): c.save(); b.seek(0); return PdfReader(b).pages[0]
def codebox(c,code,x,y,w,h):
 c.setFillColor(PALE); c.setStrokeColor(LINE); c.roundRect(x,y,w,h,6,fill=1,stroke=1); para(c,code.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;').replace('\n','<br/>'),x+10,y+h-10,w-20,'code')
repl={}
# Page 2: status reflects integrated stubs.
b,c=makepage(2,'Contenido y alcance','Entrega inicial: modelado, prototipo visual y esqueleto ejecutable.')
para(c,'CONTENIDO',42,520,330,'h'); y=490
for s in ['1. Modelado: flujos, casos de uso, clases y arquitectura.','2. Prototipado: navegación y seis pantallas de referencia.','3. Esqueleto: app Django, modelos, stubs, rutas y configuración.','4. Estado, datos y enlace al repositorio.']:
 y=para(c,s,50,y,335)-9
para(c,'ALCANCE FUNCIONAL PROPUESTO',420,520,330,'h'); para(c,'Gestionar productos y categorías: registrar, consultar, buscar, actualizar y eliminar productos; validar datos y representar existencias. Facturación, pagos y reportes complejos quedan fuera.',420,490,330)
note(c,'<b>Estado del código:</b> la app Django, las rutas, modelos y stubs están creados. Todavía no resuelven la lógica CRUD ni persisten productos. SQLite está configurado para desarrollo local.',42,150,708,56,AMBER)
note(c,'<b>Mockups:</b> las seis capturas son HTML/CSS estáticos. Sus productos, SKU, cantidades, métricas y estados son ejemplos visuales, no datos guardados.',42,82,708,54)
repl[1]=done(b,c)
# Page 7 architecture status.
b,c=makepage(7,'1.5 Arquitectura MVT','El repositorio contiene ahora el esqueleto Django; el prototipo visual sigue separado y estático.')
steps=[('1','Mockup HTML/CSS','Seis pantallas de referencia sin comportamiento dinámico.'),('2','Django MVT','App productos con modelos, forms, views, URLs y templates stub.'),('3','Django ORM','Modelos listos y migración inicial creada; CRUD pendiente.'),('4','Base de datos','SQLite configurado. MySQL queda como objetivo posterior.')]
for i,(a,t,d) in enumerate(steps):
 x=42+i*181; c.setFillColor(colors.white); c.setStrokeColor(LINE); c.roundRect(x,250,164,195,7,fill=1,stroke=1); c.setFillColor(NAVY); c.circle(x+22,420,11,fill=1,stroke=0); c.setFillColor(colors.white); c.setFont('Helvetica-Bold',8); c.drawCentredString(x+22,417,a); para(c,t,x+14,394,136,'h'); para(c,d,x+14,353,136,'small')
 if i<3: c.setStrokeColor(NAVY); c.line(x+164,345,x+178,345); c.line(x+173,349,x+178,345); c.line(x+173,341,x+178,345)
note(c,'Las vistas y plantillas responden, pero todavía no crean, consultan ni modifican datos. Las validaciones y MySQL también están pendientes.',42,145,708,47)
repl[6]=done(b,c)
# Page 12 current tree and validation evidence.
b,c=makepage(12,'3. Esqueleto del código y configuración','Estructura existente en el repositorio; los módulos de inventario están implementados como stubs.')
left='CRUD_MagnusSIG/<br/>├─ .gitignore<br/>├─ README.md<br/>├─ requirements.txt<br/>├─ documento_Sistema.pdf<br/>├─ mockups/<br/>│&nbsp;&nbsp; ├─ mockups-inventario.html<br/>│&nbsp;&nbsp; └─ mockups-inventario.css<br/>└─ magnus_sig/<br/>&nbsp;&nbsp; ├─ manage.py<br/>&nbsp;&nbsp; ├─ magnus_sig/{settings,urls,asgi,wsgi}.py<br/>&nbsp;&nbsp; └─ productos/<br/>&nbsp;&nbsp;&nbsp;&nbsp; ├─ models.py · forms.py · views.py<br/>&nbsp;&nbsp;&nbsp;&nbsp; ├─ urls.py · admin.py · tests.py<br/>&nbsp;&nbsp;&nbsp;&nbsp; ├─ migrations/0001_initial.py<br/>&nbsp;&nbsp;&nbsp;&nbsp; └─ templates/productos/*.html'
para(c,'ESTRUCTURA ACTUAL',42,520,330,'h'); para(c,left,52,488,330,'code')
para(c,'CONFIGURACIÓN Y VERIFICACIÓN',420,520,330,'h'); para(c,'Django está registrado en INSTALLED_APPS y las rutas de productos están incluidas en el proyecto.<br/><br/>SQLite está configurado para desarrollo. La migración inicial crea Categoria y Producto.<br/><br/><b>Verificado:</b> <font name="Courier">python manage.py check</font> sin errores y dos pruebas de humo aprobadas.',420,488,320)
note(c,'El esqueleto puede ejecutarse; las operaciones de negocio, búsqueda real y validaciones personalizadas se dejan para la siguiente fase.',420,275,330,57,AMBER)
repl[11]=done(b,c)
# Page 13 source stubs for models.
b,c=makepage(13,'3.3 Clases y funciones stub · modelos','Implementados en productos/models.py. Los métodos de negocio siguen vacíos o devuelven valores por defecto.')
model='''class Categoria(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    def crear(self) -> None: pass
    def actualizar(self) -> None: pass
    def eliminar(self) -> None: pass
    def obtener_productos(self) -> list: return []

class Producto(models.Model):
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT,
                                  related_name="productos")
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    cantidad = models.PositiveIntegerField(default=0)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    def crear(self) -> None: pass
    def actualizar(self) -> None: pass
    def eliminar(self) -> None: pass
    def validar_datos(self) -> bool: return False
    @staticmethod
    def buscar(termino: str) -> list: return []'''
codebox(c,model,42,115,708,397); note(c,'Los SKU, umbrales y contadores que aparecen en el mockup son ejemplos visuales; no forman parte de estos modelos.',42,65,708,37,AMBER); repl[12]=done(b,c)
# Page 14 form and view stubs.
b,c=makepage(14,'3.3 Formularios y vistas stub','Los formularios y vistas están conectados a templates placeholder; el procesamiento POST está pendiente.')
forms='''class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ["nombre", "descripcion", "categoria", "precio", "cantidad"]
    def clean(self) -> dict:
        # Pendiente: precio > 0 y validaciones de negocio.
        return super().clean()

class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ["nombre", "descripcion"]'''
views='''def lista_productos(request):
    return render(request, "productos/lista.html", {})

def buscar_producto(request):
    return render(request, "productos/lista.html", {})

def detalle_producto(request, pk):
    return render(request, "productos/detalle.html", {})

def crear_producto(request):
    return render(request, "productos/form.html", {})

# editar_producto, eliminar_producto y lista_categorias
# siguen el mismo patrón de respuesta placeholder.'''
para(c,'productos/forms.py',42,520,330,'h'); codebox(c,forms,42,300,330,195); para(c,'productos/views.py',420,520,330,'h'); codebox(c,views,420,300,330,195); note(c,'Los campos obligatorios básicos se derivan del modelo; las reglas de negocio personalizadas aún no se aplican.',42,85,708,42,AMBER); repl[13]=done(b,c)
# Page 15 urls/tests.
b,c=makepage(15,'3.3 Rutas y pruebas de humo','Rutas incluidas en el proyecto. Las pruebas solo comprueban respuestas HTTP de las plantillas stub.')
routes='''app_name = "productos"
urlpatterns = [
    path("", views.lista_productos, name="lista"),
    path("buscar/", views.buscar_producto, name="buscar"),
    path("productos/nuevo/", views.crear_producto, name="crear"),
    path("productos/<int:pk>/", views.detalle_producto, name="detalle"),
    path("productos/<int:pk>/editar/", views.editar_producto, name="editar"),
    path("productos/<int:pk>/eliminar/", views.eliminar_producto,
         name="eliminar"),
    path("categorias/", views.lista_categorias, name="categorias"),
]'''
tests='''class HumoTests(TestCase):
    def test_lista_responde(self):
        self.assertEqual(
            self.client.get(reverse("productos:lista")).status_code, 200
        )
    def test_formulario_responde(self):
        self.assertEqual(
            self.client.get(reverse("productos:crear")).status_code, 200
        )'''
para(c,'productos/urls.py',42,520,708,'h'); codebox(c,routes,42,310,708,185); para(c,'productos/tests.py',42,280,708,'h'); codebox(c,tests,42,125,708,133); repl[14]=done(b,c)
# Page 16 real schema/config facts, clarify mockup-only fields.
b,c=makepage(16,'3.4 Estructura de datos y configuración','Migración inicial de SQLite creada para los modelos del esqueleto.')
para(c,'MODELOS MIGRADOS',42,520,330,'h'); para(c,'<b>Categoria</b>: id, nombre VARCHAR(100), descripcion TEXT opcional.<br/><br/><b>Producto</b>: id, nombre VARCHAR(150), descripcion TEXT opcional, categoria_id FK protegida, precio DECIMAL(10,2), cantidad entero ≥ 0, fecha_creacion y fecha_actualizacion.<br/><br/>Una categoría tiene cero o muchos productos; cada producto pertenece a una categoría.',42,488,330)
para(c,'CONFIGURACIÓN',420,520,330,'h'); para(c,'<b>Actual:</b> SQLite en <font name="Courier">magnus_sig/settings.py</font>; Django 6.1.x en <font name="Courier">requirements.txt</font>.<br/><br/><b>Objetivo posterior:</b> MySQL mediante Django ORM; el conector y las variables de conexión no están configurados todavía.<br/><br/><b>.gitignore:</b> excluye entornos virtuales, bytecode, bases SQLite y archivos .env.',420,488,330)
note(c,'SKU, stock mínimo, métricas y paginación de las capturas son solo referencias visuales y aún no están modelados ni calculados.',42,112,708,48,AMBER); repl[15]=done(b,c)
# Page 17 README and repo link.
b,c=makepage(17,'README.md · repositorio y estado','Resumen del proyecto y enlace directo al repositorio.')
para(c,'Sistema Web de Gestión de Inventario · Magnus SIG',42,520,708,'h')
para(c,'<b>Asignatura:</b> Lenguaje de Programación 1 · 2026-2<br/><b>Integrantes:</b> Kevin Julian Sanchez Perez · Juan Jose Osorio Quitian · Luis Esteban Medina · Brayan Steven Sanchez · Sergio Neira · Hilver Galindo',42,490,708)
para(c,'<b>Estado:</b> Mockup HTML/CSS estático y esqueleto Django con app, modelos, formularios, rutas, vistas, templates, migración y pruebas de humo. Las operaciones CRUD y la lógica de negocio están pendientes.',42,420,708)
url='https://github.com/soykelian/CRUD_MagnusSIG'
para(c,'<b>Repositorio:</b>',42,340,708)
c.setFillColor(NAVY); c.setFont('Helvetica',10); c.drawString(42,310,url); c.setStrokeColor(NAVY); c.line(42,308,42+c.stringWidth(url,'Helvetica',10),308)
note(c,'Verificación local: `python manage.py check` y `python manage.py test productos` completan sin errores.',42,205,708,52); repl[16]=done(b,c)
# Compose preserving untouched pages, and make repository URL clickable.
r=PdfReader(ROOT/'docs'/'especificacion'/'documento_Sistema.pdf'); w=PdfWriter()
for i,p in enumerate(r.pages):
 if i in repl: w.add_page(repl[i])
 else: w.add_page(p)
out=REVISION/'documento_Sistema_actualizado.pdf'
with out.open('wb') as f:w.write(f)
# Add clickable URI to final page.
r=PdfReader(out); pg=r.pages[-1]
link=DictionaryObject({NameObject('/Type'):NameObject('/Annot'),NameObject('/Subtype'):NameObject('/Link'),NameObject('/Rect'):ArrayObject([FloatObject(42),FloatObject(303),FloatObject(42+canvas.Canvas(BytesIO()).stringWidth(url,'Helvetica',10)),FloatObject(317)]),NameObject('/Border'):ArrayObject([FloatObject(0),FloatObject(0),FloatObject(0)]),NameObject('/A'):DictionaryObject({NameObject('/S'):NameObject('/URI'),NameObject('/URI'):TextStringObject(url)})})
pg[NameObject('/Annots')]=ArrayObject([link]); w2=PdfWriter(); w2.append_pages_from_reader(r)
with out.open('wb') as f:w2.write(f)
check=PdfReader(out); print('pages',len(check.pages),'url clickable',len(check.pages[-1].get('/Annots',[])),'tests/check text', 'pruebas de humo' in (check.pages[11].extract_text() or ''))
