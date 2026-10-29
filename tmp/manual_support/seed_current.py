import os, sys
from pathlib import Path
from decimal import Decimal
from datetime import timedelta
root=Path(r"C:\Users\Julian\Documents\CRUD_MagnusSIG")
sys.path.insert(0,str(root/"magnus_sig"))
sys.path.insert(0,str(root/"tmp"/"manual_support"))
os.environ["DJANGO_SETTINGS_MODULE"]="manual_settings_fresh"
import django
django.setup()
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.utils import timezone
from productos.models import Categoria, Producto, Inventario, Proveedor, Cliente, Compra, DetalleCompra, Venta, DetalleVenta, MovimientoInventario, TipoServicio, Servicio, ConfiguracionInventario, Usuario
# La base es desechable y existe solo para las capturas del manual.
MovimientoInventario.objects.all().delete()
DetalleCompra.objects.all().delete()
DetalleVenta.objects.all().delete()
Compra.objects.all().delete()
Venta.objects.all().delete()
Inventario.objects.all().delete()
Producto.objects.all().delete()
Categoria.objects.all().delete()
Proveedor.objects.all().delete()
Cliente.objects.all().delete()
Usuario.objects.all().delete()
User=get_user_model()
User.objects.filter(username__in=["manual_admin","manual_vendedor"]).delete()
admin=User.objects.create_superuser("manual_admin","admin@example.invalid","ManualDemo-2026!")
admin_db=Usuario.objects.create(id_usuario=admin.pk,username=admin.username,password_hash=admin.password,nombre="Administración",apellido="Demo",correo=admin.email,rol="administrador")
vendedor=User.objects.create_user("manual_vendedor","vendedor@example.invalid","ManualDemo-2026!")
vendedor_db=Usuario.objects.create(id_usuario=vendedor.pk,username=vendedor.username,password_hash=vendedor.password,nombre="Vendedor",apellido="Demo",correo=vendedor.email,rol="vendedor")
group,_=Group.objects.get_or_create(name="Vendedor"); vendedor.groups.add(group)
epp=Categoria.objects.create(nombre="Protección personal",descripcion="Cascos, guantes y elementos de protección individual.")
dot=Categoria.objects.create(nombre="Dotación y señalización",descripcion="Prendas de alta visibilidad y seguridad en áreas de trabajo.")
prov=Proveedor.objects.create(nit="900000000-1",razon_social="Suministros Seguros Demo",nombre_contacto="Laura Ejemplo",telefono="3000000000",correo="proveedor@example.invalid",ciudad="Bogotá")
cli=Cliente.objects.create(tipo_documento="NIT",numero_documento="800000000-1",razon_social="Proyecto de demostración",nombre_contacto="Carlos Ejemplo",telefono="3100000000",correo="cliente@example.invalid",ciudad="Bogotá")
items=[]
for codigo,nombre,cat,pc,pv,stock,minimo in [("EPP-CAS-01","Casco de seguridad clase E",epp,Decimal("52000"),Decimal("78000"),25,5),("EPP-GUA-03","Guantes anticorte nivel 3",epp,Decimal("18000"),Decimal("28000"),8,5),("DOT-CHA-01","Chaleco reflectivo",dot,Decimal("24000"),Decimal("35000"),2,5),("SEN-EXT-02","Señal de ruta de evacuación",dot,Decimal("12000"),Decimal("19000"),0,5)]:
 p=Producto.objects.create(id_categoria=cat,id_proveedor=prov,codigo=codigo,nombre=nombre,descripcion="Equipo para seguridad y salud en el trabajo. Verifica especificaciones del fabricante antes de asignar.",unidad_medida="Unidad",precio_compra=pc,precio_venta=pv,stock_minimo=Decimal(minimo),estado="activo")
 inv=Inventario.objects.create(id_producto=p,cantidad_actual=Decimal(stock),ubicacion="Bodega principal - Estante A1")
 items.append(p)
for p,n in [(items[0],25),(items[1],8),(items[2],2)]: MovimientoInventario.objects.create(id_producto=p,id_usuario=admin_db,tipo_movimiento="entrada",cantidad=Decimal(n),motivo="Existencia inicial de demostración")
compra=Compra.objects.create(id_proveedor=prov,id_usuario=admin_db,numero_factura="FAC-DEMO-001",subtotal=Decimal("312000"),total=Decimal("312000"),estado="recibida")
DetalleCompra.objects.create(id_compra=compra,id_producto=items[0],cantidad=Decimal("6"),costo_unitario=Decimal("52000"),subtotal=Decimal("312000"))
MovimientoInventario.objects.create(id_producto=items[0],id_usuario=admin_db,id_compra=compra,tipo_movimiento="entrada",cantidad=Decimal("6"),motivo="Recepción de compra de demostración")
venta=Venta.objects.create(id_cliente=cli,id_usuario=vendedor_db,subtotal=Decimal("156000"),total=Decimal("156000"),estado="confirmada",observaciones="Entrega demostrativa")
DetalleVenta.objects.create(id_venta=venta,id_producto=items[0],cantidad=Decimal("2"),precio_unitario=Decimal("78000"),subtotal=Decimal("156000"))
# El saldo inicial mostrado en el stock sirve como ilustración; movimiento representa la salida histórica.
MovimientoInventario.objects.create(id_producto=items[0],id_usuario=vendedor_db,id_venta=venta,tipo_movimiento="salida",cantidad=Decimal("-2"),motivo="Despacho de demostración")
TipoServicio.objects.get_or_create(nombre="Capacitación SG-SST",defaults={"descripcion":"Capacitación de seguridad laboral"})
ConfiguracionInventario.objects.get_or_create(pk=1,defaults={"nombre_organizacion":"Magnus SIG","stock_minimo":5})
print("Seed temporal actual preparado.")
