"""Modelos del inventario de Magnus SIG adaptados al esquema MySQL magnussig_inventario."""

from decimal import Decimal
from functools import lru_cache
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.utils import OperationalError, ProgrammingError
from django.utils import timezone

STOCK_BAJO = 5
PORCENTAJE_MAXIMO = 100


class Categoria(models.Model):
    """Clasifica productos para facilitar su consulta."""
    id_categoria = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    estado = models.CharField(
        max_length=10,
        choices=[('activo', 'Activo'), ('inactivo', 'Inactivo')],
        default='activo',
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = True
        db_table = 'categorias'
        ordering = ['nombre']

    def __str__(self) -> str:
        """Devuelve una representación legible del registro."""
        return self.nombre

    def crear(self) -> None:
        """Guarda en la base de datos los cambios del registro."""
        self.save()

    def actualizar(self) -> None:
        """Guarda en la base de datos los cambios del registro."""
        self.save()

    def eliminar(self) -> None:
        """Elimina este registro mediante el ORM de Django."""
        self.delete()

    def obtener_productos(self) -> list:
        """Devuelve los productos asociados a esta categoría."""
        return list(self.productos.all())


class Proveedor(models.Model):
    """Representa un proveedor de productos."""
    id_proveedor = models.AutoField(primary_key=True)
    nit = models.CharField(max_length=30, unique=True)
    razon_social = models.CharField(max_length=180)
    nombre_contacto = models.CharField(max_length=150, blank=True, null=True)
    telefono = models.CharField(max_length=30, blank=True, null=True)
    correo = models.CharField(max_length=254, blank=True, null=True)
    direccion = models.CharField(max_length=255, blank=True, null=True)
    ciudad = models.CharField(max_length=100, blank=True, null=True)
    estado = models.CharField(
        max_length=10,
        choices=[('activo', 'Activo'), ('inactivo', 'Inactivo')],
        default='activo',
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = True
        db_table = 'proveedores'
        ordering = ['razon_social']

    def __str__(self):
        """Devuelve una representación legible del registro."""
        return self.razon_social

    # Compatibilidad con vistas previas
    @property
    def nombre(self):
        """Lee o actualiza el atributo nombre asociado al registro."""
        return self.razon_social

    @nombre.setter
    def nombre(self, valor):
        """Lee o actualiza el atributo nombre asociado al registro."""
        self.razon_social = valor

    @property
    def identificacion(self):
        """Lee o actualiza el atributo identificacion asociado al registro."""
        return self.nit

    @identificacion.setter
    def identificacion(self, valor):
        """Lee o actualiza el atributo identificacion asociado al registro."""
        self.nit = valor

    @property
    def contacto(self):
        """Lee o actualiza el atributo contacto asociado al registro."""
        return self.nombre_contacto or ''

    @contacto.setter
    def contacto(self, valor):
        """Lee o actualiza el atributo contacto asociado al registro."""
        self.nombre_contacto = valor

    @property
    def activo(self):
        """Lee o actualiza el atributo activo asociado al registro."""
        return self.estado == 'activo'

    @activo.setter
    def activo(self, valor):
        """Lee o actualiza el atributo activo asociado al registro."""
        self.estado = 'activo' if valor else 'inactivo'


class Cliente(models.Model):
    """Representa una organización o persona cliente."""
    id_cliente = models.AutoField(primary_key=True)
    tipo_documento = models.CharField(
        max_length=30,
        choices=[
            ('CC', 'Cédula de Ciudadanía'),
            ('NIT', 'NIT'),
            ('CE', 'Cédula de Extranjería'),
            ('PASAPORTE', 'Pasaporte'),
        ],
        default='NIT',
    )
    numero_documento = models.CharField(max_length=30, unique=True)
    razon_social = models.CharField(max_length=180)
    nombre_contacto = models.CharField(max_length=150, blank=True, null=True)
    telefono = models.CharField(max_length=30, blank=True, null=True)
    correo = models.CharField(max_length=254, blank=True, null=True)
    direccion = models.CharField(max_length=255, blank=True, null=True)
    ciudad = models.CharField(max_length=100, blank=True, null=True)
    estado = models.CharField(
        max_length=10,
        choices=[('activo', 'Activo'), ('inactivo', 'Inactivo')],
        default='activo',
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = True
        db_table = 'clientes'
        ordering = ['razon_social']

    def __str__(self):
        """Devuelve una representación legible del registro."""
        return self.razon_social

    @property
    def nombre(self):
        """Lee o actualiza el atributo nombre asociado al registro."""
        return self.razon_social

    @nombre.setter
    def nombre(self, valor):
        """Lee o actualiza el atributo nombre asociado al registro."""
        self.razon_social = valor

    @property
    def contacto(self):
        """Lee o actualiza el atributo contacto asociado al registro."""
        return self.nombre_contacto or ''

    @contacto.setter
    def contacto(self, valor):
        """Lee o actualiza el atributo contacto asociado al registro."""
        self.nombre_contacto = valor

    @property
    def identificacion(self):
        """Lee o actualiza el atributo identificacion asociado al registro."""
        return self.numero_documento


class Usuario(models.Model):
    """Vincula la cuenta Django con el usuario operativo del inventario."""
    id_usuario = models.AutoField(primary_key=True)
    username = models.CharField(max_length=50, unique=True)
    password_hash = models.CharField(max_length=255)
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    correo = models.CharField(max_length=254, unique=True)
    telefono = models.CharField(max_length=30, blank=True, null=True)
    rol = models.CharField(
        max_length=13,
        choices=[
            ('administrador', 'Administrador'),
            ('vendedor', 'Vendedor'),
            ('empleado', 'Empleado'),
        ],
        default='empleado',
    )
    estado = models.CharField(
        max_length=10,
        choices=[('activo', 'Activo'), ('inactivo', 'Inactivo')],
        default='activo',
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = True
        db_table = 'usuarios'
        ordering = ['nombre', 'apellido']

    def __str__(self):
        """Devuelve una representación legible del registro."""
        return f'{self.nombre} {self.apellido} ({self.username})'


def sincronizar_usuario_bd(user):
    """Busca o crea la representación local del usuario autenticado."""
    if not user or not user.is_authenticated:
        return None
    usuario = Usuario.objects.filter(id_usuario=user.id).first()
    if not usuario:
        usuario = Usuario.objects.filter(username=user.username).first()
    if not usuario:
        es_admin = (
            user.is_superuser
            or user.groups.filter(name='Administrador').exists()
        )
        rol = 'administrador' if es_admin else 'vendedor'
        usuario = Usuario.objects.create(
            id_usuario=user.id,
            username=user.username[:50],
            password_hash=user.password or 'pbkdf2_sha256$local',
            nombre=user.first_name or user.username,
            apellido=user.last_name or 'Usuario',
            correo=user.email or f'{user.username}@magnussig.local',
            rol=rol,
            estado='activo',
        )
    return usuario


class Producto(models.Model):
    """Define los datos comerciales y reglas derivadas del producto."""
    id_producto = models.AutoField(primary_key=True)
    id_categoria = models.ForeignKey(
        Categoria, on_delete=models.PROTECT, db_column='id_categoria', related_name='productos'
    )
    id_proveedor = models.ForeignKey(
        Proveedor,
        on_delete=models.SET_NULL,
        db_column='id_proveedor',
        blank=True,
        null=True,
        related_name='productos',
    )
    codigo = models.CharField(max_length=60, unique=True)
    nombre = models.CharField(max_length=180)
    descripcion = models.TextField(blank=True, null=True)
    unidad_medida = models.CharField(max_length=40, default='Unidad')
    precio_compra = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal('0.00'))
    precio_venta = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal('0.00'))
    stock_minimo = models.DecimalField(
        max_digits=12, decimal_places=3, default=Decimal(STOCK_BAJO))
    estado = models.CharField(
        max_length=10,
        choices=[('activo', 'Activo'), ('inactivo', 'Inactivo')],
        default='activo',
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = 'productos'
        ordering = ['-fecha_creacion', '-id_producto']

    def __str__(self) -> str:
        """Devuelve una representación legible del registro."""
        return f'{self.codigo} - {self.nombre}' if self.codigo else self.nombre

    # Compatibilidad con relaciones anteriores
    @property
    def categoria(self):
        """Lee o actualiza el atributo categoria asociado al registro."""
        return self.id_categoria

    @categoria.setter
    def categoria(self, val):
        """Lee o actualiza el atributo categoria asociado al registro."""
        self.id_categoria = val

    @property
    def proveedor(self):
        """Lee o actualiza el atributo proveedor asociado al registro."""
        return self.id_proveedor

    @proveedor.setter
    def proveedor(self, val):
        """Lee o actualiza el atributo proveedor asociado al registro."""
        self.id_proveedor = val

    @property
    def precio(self):
        """Lee o actualiza el atributo precio asociado al registro."""
        return self.precio_venta

    @precio.setter
    def precio(self, val):
        """Lee o actualiza el atributo precio asociado al registro."""
        self.precio_venta = Decimal(str(val))

    @property
    def sku(self) -> str:
        """Lee o actualiza el atributo sku asociado al registro."""
        return self.codigo or (f'PRD-{self.pk:04d}' if self.pk else '—')

    @property
    def cantidad(self) -> int:
        """Lee o actualiza el atributo cantidad asociado al registro."""
        inv = Inventario.objects.filter(id_producto=self.pk).first()
        return int(inv.cantidad_actual) if inv else 0

    @cantidad.setter
    def cantidad(self, val):
        """Lee o actualiza el atributo cantidad asociado al registro."""
        val_dec = Decimal(str(val))
        if self.pk:
            inv, _ = Inventario.objects.get_or_create(id_producto_id=self.pk)
            inv.cantidad_actual = val_dec
            inv.save(update_fields=['cantidad_actual', 'fecha_actualizacion'])

    @property
    def ubicacion(self) -> str:
        """Lee o actualiza el atributo ubicacion asociado al registro."""
        inv = Inventario.objects.filter(id_producto=self.pk).first()
        return inv.ubicacion if inv and inv.ubicacion else 'Bodega Principal'

    @property
    def estado_stock(self) -> str:
        """Lee o actualiza el atributo estado_stock asociado al registro."""
        cant = self.cantidad
        minimo = int(
            self.stock_minimo) if self.stock_minimo else obtener_stock_minimo()
        if cant <= 0:
            return 'out'
        if cant <= minimo:
            return 'low'
        return 'ok'

    @property
    def estado_etiqueta(self) -> str:
        """Lee o actualiza el atributo estado_etiqueta asociado al registro."""
        return {'ok': 'Disponible', 'low': 'Stock bajo', 'out': 'Agotado'}[self.estado_stock]

    @property
    def porcentaje_stock(self) -> int:
        """Lee o actualiza el atributo porcentaje_stock asociado al registro."""
        cant = self.cantidad
        minimo = int(
            self.stock_minimo) if self.stock_minimo else obtener_stock_minimo()
        if cant <= 0:
            return 0
        porcentaje = round(cant * PORCENTAJE_MAXIMO / (minimo + 1))
        return min(PORCENTAJE_MAXIMO, porcentaje)

    def crear(self) -> None:
        """Guarda en la base de datos los cambios del registro."""
        self.save()

    def actualizar(self) -> None:
        """Guarda en la base de datos los cambios del registro."""
        self.save()

    def eliminar(self) -> None:
        """Elimina este registro mediante el ORM de Django."""
        self.delete()

    def validar_datos(self) -> bool:
        """Comprueba los requisitos básicos antes de persistir un producto."""
        return bool(
            self.nombre.strip()
            and self.id_categoria_id
            and self.precio_venta is not None and self.precio_venta >= 0
        )

    @staticmethod
    def buscar(termino: str) -> list:
        """Busca productos por texto y devuelve los resultados ordenados."""
        termino = (termino or '').strip()
        consulta = Producto.objects.select_related('id_categoria').order_by(
            '-fecha_creacion', '-id_producto'
        )
        if termino:
            consulta = consulta.filter(
                models.Q(nombre__icontains=termino)
                | models.Q(codigo__icontains=termino)
                | models.Q(descripcion__icontains=termino)
            )
        return list(consulta)


class Inventario(models.Model):
    """Guarda el saldo y la ubicación física de un producto."""
    id_inventario = models.AutoField(primary_key=True)
    id_producto = models.OneToOneField(
        Producto, on_delete=models.CASCADE, db_column='id_producto', related_name='inventario_rel'
    )
    cantidad_actual = models.DecimalField(
        max_digits=12, decimal_places=3, default=Decimal('0.000')
    )
    ubicacion = models.CharField(max_length=120, blank=True, null=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = 'inventario'

    def __str__(self):
        """Devuelve una representación legible del registro."""
        return f'{self.id_producto.nombre}: {self.cantidad_actual}'


class Compra(models.Model):
    """Representa una entrada de mercancía desde un proveedor."""
    class Estado(models.TextChoices):
        BORRADOR = 'borrador', 'Borrador'
        RECIBIDA = 'recibida', 'Recibida'
        CANCELADA = 'cancelada', 'Cancelada'

    id_compra = models.AutoField(primary_key=True)
    id_proveedor = models.ForeignKey(
        Proveedor, on_delete=models.PROTECT, db_column='id_proveedor',
        related_name='compras',
    )
    id_usuario = models.ForeignKey(
        Usuario, on_delete=models.PROTECT, db_column='id_usuario',
        related_name='compras',
    )
    numero_factura = models.CharField(max_length=80, blank=True, null=True)
    fecha_compra = models.DateTimeField(default=timezone.now)
    subtotal = models.DecimalField(
        max_digits=14, decimal_places=2, default=Decimal('0.00'))
    iva = models.DecimalField(
        max_digits=14, decimal_places=2, default=Decimal('0.00'))
    total = models.DecimalField(
        max_digits=14, decimal_places=2, default=Decimal('0.00'))
    estado = models.CharField(
        max_length=12, choices=Estado.choices, default=Estado.BORRADOR)
    observaciones = models.TextField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'compras'
        ordering = ['-fecha_compra', '-id_compra']

    def __str__(self):
        """Devuelve una representación legible del registro."""
        return self.referencia

    @property
    def referencia(self):
        """Lee o actualiza el atributo referencia asociado al registro."""
        return self.numero_factura or f'COM-{self.id_compra:05d}'

    @property
    def proveedor(self):
        """Lee o actualiza el atributo proveedor asociado al registro."""
        return self.id_proveedor

    @property
    def responsable(self):
        """Lee o actualiza el atributo responsable asociado al registro."""
        return self.id_usuario

    @property
    def creada(self):
        """Lee o actualiza el atributo creada asociado al registro."""
        return self.fecha_compra

    @property
    def recibida(self):
        """Lee o actualiza el atributo recibida asociado al registro."""
        return self.fecha_compra if self.estado == self.Estado.RECIBIDA else None

    @property
    def importe(self):
        """Lee o actualiza el atributo importe asociado al registro."""
        return self.total

    @property
    def cantidad(self):
        """Lee o actualiza el atributo cantidad asociado al registro."""
        total_items = self.detalles.aggregate(
            total=models.Sum('cantidad'))['total']
        return int(total_items) if total_items else 0

    @property
    def costo_unitario(self):
        """Lee o actualiza el atributo costo_unitario asociado al registro."""
        det = self.detalles.first()
        return det.costo_unitario if det else Decimal('0.00')

    @property
    def producto(self):
        """Devuelve el primer producto incluido en la compra."""
        det = self.detalles.select_related('id_producto').first()
        return det.id_producto if det else None


class DetalleCompra(models.Model):
    """Asocia productos y cantidades con una compra."""
    id_detalle_compra = models.AutoField(primary_key=True)
    id_compra = models.ForeignKey(
        Compra, on_delete=models.CASCADE, db_column='id_compra',
        related_name='detalles',
    )
    id_producto = models.ForeignKey(
        Producto, on_delete=models.PROTECT, db_column='id_producto',
        related_name='detalles_compra',
    )
    cantidad = models.DecimalField(max_digits=12, decimal_places=3)
    costo_unitario = models.DecimalField(max_digits=12, decimal_places=2)
    subtotal = models.DecimalField(max_digits=14, decimal_places=2)

    class Meta:
        managed = True
        db_table = 'detalle_compra'

    @property
    def producto(self):
        """Devuelve el producto asociado al detalle de compra."""
        return self.id_producto


class Venta(models.Model):
    """Representa una salida o despacho asociado a un cliente."""
    class Estado(models.TextChoices):
        BORRADOR = 'borrador', 'Borrador'
        CONFIRMADA = 'confirmada', 'Confirmada'
        CANCELADA = 'cancelada', 'Cancelada'

    id_venta = models.AutoField(primary_key=True)
    id_cliente = models.ForeignKey(
        Cliente, on_delete=models.PROTECT, db_column='id_cliente',
        related_name='ventas',
    )
    id_usuario = models.ForeignKey(
        Usuario, on_delete=models.PROTECT, db_column='id_usuario',
        related_name='ventas',
    )
    fecha_venta = models.DateTimeField(default=timezone.now)
    subtotal = models.DecimalField(
        max_digits=14, decimal_places=2, default=Decimal('0.00'))
    iva = models.DecimalField(
        max_digits=14, decimal_places=2, default=Decimal('0.00'))
    total = models.DecimalField(
        max_digits=14, decimal_places=2, default=Decimal('0.00'))
    estado = models.CharField(
        max_length=12, choices=Estado.choices, default=Estado.BORRADOR)
    observaciones = models.TextField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'ventas'
        ordering = ['-fecha_venta', '-id_venta']

    def __str__(self):
        """Devuelve una representación legible del registro."""
        return self.referencia

    @property
    def referencia(self):
        """Lee o actualiza el atributo referencia asociado al registro."""
        return f'VEN-{self.id_venta:05d}'

    @property
    def cliente(self):
        """Lee o actualiza el atributo cliente asociado al registro."""
        return self.id_cliente

    @property
    def responsable(self):
        """Lee o actualiza el atributo responsable asociado al registro."""
        return self.id_usuario

    @property
    def creada(self):
        """Lee o actualiza el atributo creada asociado al registro."""
        return self.fecha_venta

    @property
    def despachada(self):
        """Devuelve la fecha de despacho si la venta está confirmada."""
        return self.fecha_venta if self.estado == self.Estado.CONFIRMADA else None

    @property
    def cantidad(self):
        """Lee o actualiza el atributo cantidad asociado al registro."""
        total_items = self.detalles.aggregate(
            total=models.Sum('cantidad'))['total']
        return int(total_items) if total_items else 0

    @property
    def producto(self):
        """Devuelve el producto asociado al detalle de venta."""
        det = self.detalles.select_related('id_producto').first()
        return det.id_producto if det else None


class DetalleVenta(models.Model):
    """Asocia productos y cantidades con una venta."""
    id_detalle_venta = models.AutoField(primary_key=True)
    id_venta = models.ForeignKey(
        Venta, on_delete=models.CASCADE, db_column='id_venta',
        related_name='detalles',
    )
    id_producto = models.ForeignKey(
        Producto, on_delete=models.PROTECT, db_column='id_producto',
        related_name='detalles_venta',
    )
    cantidad = models.DecimalField(max_digits=12, decimal_places=3)
    precio_unitario = models.DecimalField(max_digits=12, decimal_places=2)
    subtotal = models.DecimalField(max_digits=14, decimal_places=2)

    class Meta:
        managed = True
        db_table = 'detalle_venta'

    @property
    def producto(self):
        """Devuelve el producto asociado al detalle de venta."""
        return self.id_producto


class MovimientoInventario(models.Model):
    """Registra la trazabilidad de cambios en las existencias."""
    class Tipo(models.TextChoices):
        ENTRADA = 'entrada', 'Entrada'
        SALIDA = 'salida', 'Salida'
        AJUSTE = 'ajuste', 'Ajuste'

    id_movimiento = models.AutoField(primary_key=True)
    id_producto = models.ForeignKey(
        Producto, on_delete=models.PROTECT, db_column='id_producto',
        related_name='movimientos',
    )
    id_usuario = models.ForeignKey(
        Usuario, on_delete=models.PROTECT, db_column='id_usuario',
        related_name='movimientos',
    )
    id_compra = models.ForeignKey(
        Compra, on_delete=models.SET_NULL, db_column='id_compra',
        blank=True, null=True,
    )
    id_venta = models.ForeignKey(
        Venta, on_delete=models.SET_NULL, db_column='id_venta',
        blank=True, null=True,
    )
    tipo_movimiento = models.CharField(max_length=10, choices=Tipo.choices)
    cantidad = models.DecimalField(max_digits=12, decimal_places=3)
    motivo = models.CharField(max_length=180)
    observacion = models.TextField(blank=True, null=True)
    fecha_movimiento = models.DateTimeField(default=timezone.now)

    class Meta:
        managed = True
        db_table = 'movimientos_inventario'
        ordering = ['-fecha_movimiento', '-id_movimiento']

    def __str__(self):
        """Devuelve una representación legible del registro."""
        return f'{self.tipo_movimiento.title()} · {self.id_producto.nombre} · {self.cantidad}'

    @property
    def referencia(self):
        """Lee o actualiza el atributo referencia asociado al registro."""
        return f'MOV-{self.id_movimiento:05d}'

    @property
    def producto(self):
        """Devuelve el producto asociado al movimiento."""
        return self.id_producto

    @property
    def responsable(self):
        """Lee o actualiza el atributo responsable asociado al registro."""
        return self.id_usuario

    @property
    def tipo(self):
        """Devuelve el tipo del movimiento registrado."""
        return self.tipo_movimiento

    @property
    def fecha(self):
        """Devuelve la fecha y hora del movimiento."""
        return self.fecha_movimiento


class TipoServicio(models.Model):
    """Define una clase de servicio SG-SST."""
    id_tipo_servicio = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=180, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    estado = models.CharField(
        max_length=10,
        choices=[('activo', 'Activo'), ('inactivo', 'Inactivo')],
        default='activo',
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = True
        db_table = 'tipos_servicio'
        ordering = ['nombre']

    def __str__(self):
        """Devuelve una representación legible del registro."""
        return self.nombre


class Servicio(models.Model):
    """Representa un servicio contratado por un cliente."""
    class Estado(models.TextChoices):
        PENDIENTE = 'pendiente', 'Pendiente'
        EN_PROCESO = 'en proceso', 'En proceso'
        FINALIZADO = 'finalizado', 'Finalizado'
        CANCELADO = 'cancelado', 'Cancelado'

    id_servicio = models.AutoField(primary_key=True)
    id_cliente = models.ForeignKey(
        Cliente, on_delete=models.PROTECT, db_column='id_cliente',
        related_name='servicios',
    )
    id_tipo_servicio = models.ForeignKey(
        TipoServicio, on_delete=models.PROTECT, db_column='id_tipo_servicio',
        related_name='servicios',
    )
    id_usuario = models.ForeignKey(
        Usuario, on_delete=models.PROTECT, db_column='id_usuario',
        related_name='servicios',
    )
    fecha_solicitud = models.DateTimeField(default=timezone.now)
    fecha_inicio = models.DateTimeField(blank=True, null=True)
    fecha_finalizacion = models.DateTimeField(blank=True, null=True)
    valor = models.DecimalField(
        max_digits=14, decimal_places=2, default=Decimal('0.00'))
    estado = models.CharField(
        max_length=15, choices=Estado.choices, default=Estado.PENDIENTE)
    observaciones = models.TextField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'servicios'
        ordering = ['-fecha_solicitud', '-id_servicio']

    def __str__(self):
        """Devuelve una representación legible del registro."""
        return f'{self.id_tipo_servicio.nombre} - {self.id_cliente.razon_social}'

    @property
    def referencia(self):
        """Lee o actualiza el atributo referencia asociado al registro."""
        return f'SRV-{self.id_servicio:05d}'

    @property
    def cliente(self):
        """Lee o actualiza el atributo cliente asociado al registro."""
        return self.id_cliente

    @property
    def tipo_servicio(self):
        """Lee o actualiza el atributo tipo_servicio asociado al registro."""
        return self.id_tipo_servicio

    @property
    def responsable(self):
        """Lee o actualiza el atributo responsable asociado al registro."""
        return self.id_usuario


class ConfiguracionInventario(models.Model):
    """Guarda parámetros generales del inventario."""
    id = models.AutoField(primary_key=True)
    nombre_organizacion = models.CharField(
        max_length=140, default='Magnus SIG')
    stock_minimo = models.PositiveIntegerField(default=STOCK_BAJO)
    alertas_stock_bajo = models.BooleanField(default=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = 'configuracion_inventario'

    def __str__(self):
        """Devuelve una representación legible del registro."""
        return self.nombre_organizacion

    def save(self, *args, **kwargs):
        """Guarda el modelo y actualiza los valores derivados necesarios."""
        self.pk = 1
        super().save(*args, **kwargs)
        obtener_stock_minimo.cache_clear()


@lru_cache(maxsize=1)
def obtener_stock_minimo() -> int:
    """Obtiene el valor de configuración vigente."""
    try:
        configurado = ConfiguracionInventario.objects.filter(pk=1).values_list(
            'stock_minimo', flat=True
        ).first()
        return STOCK_BAJO if configurado is None else configurado
    except (OperationalError, ProgrammingError):
        return STOCK_BAJO


# Alias para compatibilidad con código existente
Entrada = Compra
Salida = Venta
Movimiento = MovimientoInventario
