import os
from decimal import Decimal
from pathlib import Path
import sys

project_dir = Path(r"C:\Users\Julian\Documents\CRUD_MagnusSIG")
sys.path.insert(0, str(project_dir / "magnus_sig"))
sys.path.insert(0, str(project_dir / "tmp" / "manual_support"))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "manual_settings")
import django
django.setup()
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management import call_command
from django.utils import timezone
from productos.models import Categoria, Cliente, ConfiguracionInventario, Entrada, Movimiento, Producto, Proveedor, Salida

call_command("migrate", interactive=False, verbosity=0)
User = get_user_model()
admin = User.objects.create_superuser("manual_admin", "admin@example.invalid", "ManualDemo-2026!")
seller = User.objects.create_user("manual_vendedor", "vendedor@example.invalid", "ManualDemo-2026!")
seller.groups.add(Group.objects.get_or_create(name="Vendedor")[0])
Categoria.objects.bulk_create([
    Categoria(nombre="Elementos de protección personal", descripcion="Cascos, guantes y protección individual."),
    Categoria(nombre="Dotación de trabajo", descripcion="Prendas y accesorios de dotación."),
])
epp, dotacion = Categoria.objects.order_by("pk")
provider = Proveedor.objects.create(nombre="Suministros Seguros Demo", identificacion="900000000-1", contacto="Laura Ejemplo", correo="proveedor@example.invalid", telefono="3000000000")
client = Cliente.objects.create(nombre="Proyecto de demostración", contacto="Carlos Ejemplo", correo="cliente@example.invalid", telefono="3100000000", ciudad="Bogotá")
helmet = Producto.objects.create(nombre="Casco de seguridad clase E", descripcion="Casco de protección para trabajo en obra.", categoria=epp, precio=Decimal("78000.00"), cantidad=25)
gloves = Producto.objects.create(nombre="Guantes anticorte nivel 3", descripcion="Guantes de protección para manipulación de materiales.", categoria=epp, precio=Decimal("28000.00"), cantidad=8)
vest = Producto.objects.create(nombre="Chaleco reflectivo", descripcion="Chaleco de alta visibilidad.", categoria=dotacion, precio=Decimal("35000.00"), cantidad=0)
Movimiento.objects.create(producto=helmet, tipo=Movimiento.Tipo.ENTRADA, cantidad=25, responsable=admin, motivo="Existencias iniciales")
Movimiento.objects.create(producto=gloves, tipo=Movimiento.Tipo.ENTRADA, cantidad=8, responsable=admin, motivo="Existencias iniciales")
Entrada.objects.create(proveedor=provider, producto=helmet, cantidad=5, costo_unitario=Decimal("52000.00"), responsable=admin)
Salida.objects.create(cliente=client, producto=helmet, cantidad=2, responsable=seller)
Salida.objects.create(cliente=client, producto=gloves, cantidad=1, estado=Salida.Estado.ENTREGADA, responsable=admin, despachada=timezone.now())
Movimiento.objects.create(producto=gloves, tipo=Movimiento.Tipo.SALIDA, cantidad=-1, responsable=admin, motivo="Entrega al cliente")
ConfiguracionInventario.objects.get_or_create(pk=1, defaults={"nombre_organizacion": "Magnus SIG", "stock_minimo": 5})
print("Base temporal preparada con cuentas y registros ilustrativos.")
