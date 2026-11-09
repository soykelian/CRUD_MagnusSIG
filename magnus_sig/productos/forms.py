"""Formularios con las validaciones de negocio del inventario adaptados a MySQL."""

from decimal import Decimal
from django import forms
from django.db import transaction
from django.db.models import Sum

from .models import (
    Categoria,
    Cliente,
    Compra,
    ConfiguracionInventario,
    DetalleCompra,
    DetalleVenta,
    Inventario,
    MovimientoInventario,
    Producto,
    Proveedor,
    Servicio,
    TipoServicio,
    Usuario,
    Venta,
)

from .validators import (
    validar_ciudad,
    validar_direccion,
    validar_documento_cliente,
    validar_nit,
    validar_telefono_colombiano,
)


def validar_stock_reservado(producto, cantidad, salida_pk=None):
    """Rechaza reservas que, sumadas, superan las existencias actuales."""
    reservas = Venta.objects.filter(
        detalles__id_producto=producto, estado=Venta.Estado.BORRADOR,
    )
    if salida_pk:
        reservas = reservas.exclude(pk=salida_pk)
    reservado = reservas.aggregate(total=Sum('detalles__cantidad'))[
        'total'] or Decimal('0.000')
    disponible = Decimal(str(producto.cantidad))
    requerido = Decimal(str(cantidad))
    if requerido + reservado > disponible:
        raise forms.ValidationError(
            f'Existencias insuficientes. Disponibles: {disponible}; reservadas: {reservado}.'
        )


class ProductoForm(forms.ModelForm):
    """Formulario de creación y edición de productos."""
    estado = forms.ChoiceField(
        choices=[('activo', 'Activo'), ('inactivo', 'Inactivo')],
        initial='activo',
        required=False,
        label='Estado del producto',
    )
    cantidad = forms.IntegerField(
        label='Cantidad inicial en stock',
        min_value=0,
        initial=0,
        help_text='Existencias físicas en bodega',
    )
    ubicacion = forms.CharField(
        label='Ubicación en bodega',
        max_length=120,
        required=False,
        initial='Bodega Principal',
        help_text='Ej: Pasillo A - Estante 2',
    )

    class Meta:
        model = Producto
        fields = [
            'codigo',
            'nombre',
            'descripcion',
            'id_categoria',
            'id_proveedor',
            'unidad_medida',
            'precio_compra',
            'precio_venta',
            'stock_minimo',
            'estado',
        ]
        labels = {
            'codigo': 'Código / SKU',
            'nombre': 'Nombre del producto',
            'descripcion': 'Descripción técnica',
            'id_categoria': 'Categoría',
            'id_proveedor': 'Proveedor sugerido',
            'unidad_medida': 'Unidad de medida',
            'precio_compra': 'Precio de compra (COP)',
            'precio_venta': 'Precio de venta (COP)',
            'stock_minimo': 'Stock mínimo de alerta',
            'estado': 'Estado del producto',
        }
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        """Configura el formulario con opciones acordes al registro."""
        super().__init__(*args, **kwargs)
        self.fields['id_categoria'].queryset = Categoria.objects.filter(
            estado='activo'
        ).order_by('nombre')
        self.fields['id_proveedor'].queryset = Proveedor.objects.filter(
            estado='activo'
        ).order_by('razon_social')
        if self.instance and self.instance.pk:
            self.fields['cantidad'].initial = self.instance.cantidad
            self.fields['ubicacion'].initial = self.instance.ubicacion

    def clean_codigo(self) -> str:
        """Valida que el código del producto sea único."""
        codigo = self.cleaned_data['codigo'].strip().upper()
        if not codigo:
            raise forms.ValidationError('El código o SKU es obligatorio.')
        repetido = Producto.objects.filter(codigo__iexact=codigo)
        if self.instance.pk:
            repetido = repetido.exclude(pk=self.instance.pk)
        if repetido.exists():
            raise forms.ValidationError(
                'Ya existe un producto con este código.')
        return codigo

    def clean_nombre(self) -> str:
        """Normaliza y valida el nombre ingresado."""
        nombre = self.cleaned_data['nombre'].strip()
        if not nombre:
            raise forms.ValidationError(
                'El nombre del producto es obligatorio.')
        return nombre

    def clean_estado(self) -> str:
        """Valida el estado seleccionado."""
        return self.cleaned_data.get('estado') or 'activo'

    def clean_precio_venta(self):
        """Comprueba que el precio de venta sea válido."""
        precio = self.cleaned_data['precio_venta']
        if precio is None or precio < 0:
            raise forms.ValidationError(
                'El precio de venta no puede ser negativo.')
        return precio

    def clean_precio_compra(self):
        """Comprueba que el costo de compra sea válido."""
        precio = self.cleaned_data['precio_compra']
        if precio is None or precio < 0:
            raise forms.ValidationError(
                'El precio de compra no puede ser negativo.')
        return precio

    @transaction.atomic
    def save(self, commit=True):
        """Guarda el modelo con los valores validados."""
        producto = super().save(commit=commit)
        if commit:
            cantidad_val = self.cleaned_data.get('cantidad', 0)
            ubicacion_val = self.cleaned_data.get(
                'ubicacion', 'Bodega Principal')
            inv, _ = Inventario.objects.get_or_create(id_producto=producto)
            inv.cantidad_actual = Decimal(str(cantidad_val))
            inv.ubicacion = ubicacion_val
            inv.save()
        return producto


class CategoriaForm(forms.ModelForm):
    """Formulario para validar y guardar categorías."""
    estado = forms.ChoiceField(
        choices=[('activo', 'Activo'), ('inactivo', 'Inactivo')],
        initial='activo',
        required=False,
        label='Estado',
    )

    class Meta:
        model = Categoria
        fields = ['nombre', 'descripcion', 'estado']
        labels = {
            'nombre': 'Nombre de la categoría',
            'descripcion': 'Descripción',
            'estado': 'Estado',
        }
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 3}),
        }

    def clean_estado(self) -> str:
        """Valida el estado seleccionado."""
        return self.cleaned_data.get('estado') or 'activo'

    def clean_nombre(self) -> str:
        """Normaliza y valida el nombre ingresado."""
        nombre = self.cleaned_data['nombre'].strip()
        if not nombre:
            raise forms.ValidationError(
                'El nombre de la categoría es obligatorio.')
        repetida = Categoria.objects.filter(nombre__iexact=nombre)
        if self.instance.pk:
            repetida = repetida.exclude(pk=self.instance.pk)
        if repetida.exists():
            raise forms.ValidationError(
                'Ya existe una categoría con ese nombre.')
        return nombre


class ContactoValidationMixin:
    """Comparte la validación de datos de contacto."""

    def clean_telefono(self):
        """Valida el formato del teléfono de contacto."""
        telefono = (self.cleaned_data.get("telefono") or "").strip()
        validar_telefono_colombiano(telefono)
        return telefono or None

    def clean_direccion(self):
        """Valida y normaliza la dirección de contacto."""
        return validar_direccion(self.cleaned_data.get("direccion") or "")

    def clean_ciudad(self):
        """Valida y normaliza la ciudad."""
        return validar_ciudad(self.cleaned_data.get("ciudad") or "")


class ProveedorForm(ContactoValidationMixin, forms.ModelForm):
    """Formulario de registro y validación de proveedores."""
    telefono = forms.CharField(
        label="Teléfono de contacto",
        required=True,
        max_length=30,
        widget=forms.TextInput(attrs={"type": "tel", "autocomplete": "tel"}),
        help_text="Colombia: 10 dígitos. Se acepta +57 o formato internacional.",
    )
    correo = forms.EmailField(
        label="Correo electrónico",
        required=True,
        max_length=254,
        widget=forms.EmailInput(attrs={"autocomplete": "email"}),
    )
    direccion = forms.CharField(
        label="Dirección",
        required=True,
        max_length=255,
        widget=forms.TextInput(attrs={"autocomplete": "street-address"}),
        help_text="Mínimo 5 caracteres; se permiten nomenclaturas como Calle 10 # 20-30.",
    )
    ciudad = forms.CharField(
        label="Ciudad",
        required=True,
        max_length=100,
        widget=forms.TextInput(attrs={"autocomplete": "address-level2"}),
    )

    class Meta:
        model = Proveedor
        fields = [
            'nit',
            'razon_social',
            'nombre_contacto',
            'telefono',
            'correo',
            'direccion',
            'ciudad',
            'estado',
        ]
        labels = {
            'nit': 'NIT / Identificación fiscal',
            'razon_social': 'Razón Social / Nombre',
            'nombre_contacto': 'Nombre del contacto',
            'telefono': 'Teléfono de contacto',
            'correo': 'Correo electrónico',
            'direccion': 'Dirección',
            'ciudad': 'Ciudad',
            'estado': 'Estado',
        }

    def clean_nit(self):
        """Valida el NIT del proveedor."""
        nit = validar_nit(self.cleaned_data["nit"])
        existentes = Proveedor.objects.filter(nit__iexact=nit)
        if self.instance.pk:
            existentes = existentes.exclude(pk=self.instance.pk)
        if existentes.exists():
            raise forms.ValidationError('Ya existe un proveedor con ese NIT.')
        return nit

    def clean_razon_social(self):
        """Valida y normaliza la razón social."""
        razon = self.cleaned_data['razon_social'].strip()
        if not razon:
            raise forms.ValidationError('La razón social es obligatoria.')
        return razon


class ClienteForm(ContactoValidationMixin, forms.ModelForm):
    """Formulario de registro y validación de clientes."""
    telefono = forms.CharField(
        label="Teléfono",
        required=True,
        max_length=30,
        widget=forms.TextInput(attrs={"type": "tel", "autocomplete": "tel"}),
        help_text="Colombia: 10 dígitos. Se acepta +57 o formato internacional.",
    )
    correo = forms.EmailField(
        label="Correo electrónico",
        required=True,
        max_length=254,
        widget=forms.EmailInput(attrs={"autocomplete": "email"}),
    )
    direccion = forms.CharField(
        label="Dirección",
        required=True,
        max_length=255,
        widget=forms.TextInput(attrs={"autocomplete": "street-address"}),
        help_text="Mínimo 5 caracteres; se permiten nomenclaturas como Calle 10 # 20-30.",
    )
    ciudad = forms.CharField(
        label="Ciudad",
        required=True,
        max_length=100,
        widget=forms.TextInput(attrs={"autocomplete": "address-level2"}),
    )

    class Meta:
        model = Cliente
        fields = [
            'tipo_documento',
            'numero_documento',
            'razon_social',
            'nombre_contacto',
            'telefono',
            'correo',
            'direccion',
            'ciudad',
            'estado',
        ]
        labels = {
            'tipo_documento': 'Tipo de documento',
            'numero_documento': 'Número de documento',
            'razon_social': 'Razón Social / Nombre',
            'nombre_contacto': 'Contacto comercial',
            'telefono': 'Teléfono',
            'correo': 'Correo electrónico',
            'direccion': 'Dirección',
            'ciudad': 'Ciudad',
            'estado': 'Estado',
        }

    def clean_numero_documento(self):
        """Valida el documento de identificación del cliente."""
        tipo = self.cleaned_data.get("tipo_documento")
        doc = validar_documento_cliente(
            tipo,
            self.cleaned_data["numero_documento"],
        )
        existentes = Cliente.objects.filter(numero_documento__iexact=doc)
        if self.instance.pk:
            existentes = existentes.exclude(pk=self.instance.pk)
        if existentes.exists():
            raise forms.ValidationError(
                'Ya existe un cliente con ese número de documento.')
        return doc

    def clean_razon_social(self):
        """Valida y normaliza la razón social."""
        razon = self.cleaned_data['razon_social'].strip()
        if not razon:
            raise forms.ValidationError(
                'La razón social o nombre del cliente es obligatorio.')
        return razon


class EntradaForm(forms.Form):
    """Valida los datos de una compra o entrada de mercancía."""
    proveedor = forms.ModelChoiceField(
        queryset=Proveedor.objects.filter(
            estado='activo').order_by('razon_social'),
        label='Proveedor',
    )
    producto = forms.ModelChoiceField(
        queryset=Producto.objects.filter(estado='activo').order_by('nombre'),
        label='Producto que ingresa',
    )
    cantidad = forms.DecimalField(
        label='Cantidad a ingresar',
        min_value=Decimal('0.001'),
        max_digits=12,
        decimal_places=3,
        initial=1,
    )
    costo_unitario = forms.DecimalField(
        label='Costo unitario de compra (COP)',
        min_value=Decimal('0.01'),
        max_digits=12,
        decimal_places=2,
    )
    numero_factura = forms.CharField(
        label='Número de factura / Remisión',
        max_length=80,
        required=False,
    )
    observaciones = forms.CharField(
        label='Observaciones',
        widget=forms.Textarea(attrs={'rows': 2}),
        required=False,
    )

    def clean_cantidad(self):
        """Comprueba que la cantidad ingresada sea positiva."""
        cant = self.cleaned_data['cantidad']
        if cant <= 0:
            raise forms.ValidationError('La cantidad debe ser mayor que cero.')
        return cant

    def clean_costo_unitario(self):
        """Comprueba que el costo unitario sea positivo."""
        costo = self.cleaned_data['costo_unitario']
        if costo <= 0:
            raise forms.ValidationError(
                'El costo unitario debe ser mayor que cero.')
        return costo


class SalidaForm(forms.Form):
    """Valida un despacho y comprueba las existencias reservadas."""
    cliente = forms.ModelChoiceField(
        queryset=Cliente.objects.filter(
            estado='activo').order_by('razon_social'),
        label='Cliente destinatario',
    )
    producto = forms.ModelChoiceField(
        queryset=Producto.objects.filter(estado='activo').order_by('nombre'),
        label='Producto a despachar',
    )
    cantidad = forms.DecimalField(
        label='Cantidad a despachar',
        min_value=Decimal('0.001'),
        max_digits=12,
        decimal_places=3,
        initial=1,
    )
    precio_unitario = forms.DecimalField(
        label='Precio de venta unitario (COP)',
        min_value=Decimal('0.01'),
        max_digits=12,
        decimal_places=2,
        required=False,
    )
    observaciones = forms.CharField(
        label='Observaciones / Motivo de salida',
        widget=forms.Textarea(attrs={'rows': 2}),
        required=False,
    )

    def clean(self):
        """Valida los campos relacionados y devuelve los datos limpios."""
        datos = super().clean()
        producto = datos.get('producto')
        cantidad = datos.get('cantidad')
        if producto and cantidad:
            validar_stock_reservado(producto, cantidad)
        return datos


class MovimientoForm(forms.Form):
    """Valida los movimientos manuales de existencias."""
    producto = forms.ModelChoiceField(
        queryset=Producto.objects.filter(estado='activo').order_by('nombre'),
        label='Producto',
    )
    tipo = forms.ChoiceField(
        choices=[
            ('entrada', 'Entrada'),
            ('salida', 'Salida'),
            ('ajuste', 'Ajuste de inventario'),
        ],
        label='Tipo de movimiento',
    )
    cantidad = forms.DecimalField(
        label='Cantidad',
        max_digits=12,
        decimal_places=3,
    )
    motivo = forms.CharField(
        label='Motivo',
        max_length=180,
    )
    observacion = forms.CharField(
        label='Observaciones adicionales',
        widget=forms.Textarea(attrs={'rows': 2}),
        required=False,
    )

    def clean_cantidad(self):
        """Comprueba que la cantidad ingresada sea positiva."""
        cant = self.cleaned_data['cantidad']
        if cant == 0:
            raise forms.ValidationError(
                'La cantidad debe ser diferente de cero.')
        return cant


class ServicioForm(forms.ModelForm):
    """Valida los servicios asociados a clientes."""
    valor = forms.DecimalField(
        label="Valor del servicio (COP)",
        max_digits=14,
        decimal_places=2,
        min_value=Decimal("0.00"),
    )

    class Meta:
        model = Servicio
        fields = [
            'id_cliente',
            'id_tipo_servicio',
            'valor',
            'fecha_inicio',
            'fecha_finalizacion',
            'estado',
            'observaciones',
        ]
        labels = {
            'id_cliente': 'Cliente solicitante',
            'id_tipo_servicio': 'Tipo de servicio de seguridad / SG-SST',
            'valor': 'Valor del servicio (COP)',
            'fecha_inicio': 'Fecha de inicio',
            'fecha_finalizacion': 'Fecha de finalización',
            'estado': 'Estado del servicio',
            'observaciones': 'Observaciones y alcance',
        }
        widgets = {
            'fecha_inicio': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'fecha_finalizacion': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'observaciones': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        """Configura el formulario con opciones acordes al registro."""
        super().__init__(*args, **kwargs)
        self.fields['id_cliente'].queryset = Cliente.objects.filter(
            estado='activo'
        ).order_by('razon_social')
        self.fields['id_tipo_servicio'].queryset = TipoServicio.objects.filter(
            estado='activo'
        ).order_by('nombre')

    def clean(self):
        """Valida los campos relacionados y devuelve los datos limpios."""
        datos = super().clean()
        inicio = datos.get("fecha_inicio")
        finalizacion = datos.get("fecha_finalizacion")
        if inicio and finalizacion and finalizacion < inicio:
            self.add_error(
                "fecha_finalizacion",
                "La fecha de finalización no puede ser anterior a la fecha de inicio.",
            )
        return datos


class ConfiguracionForm(forms.ModelForm):
    """Formulario de parámetros generales del inventario."""
    class Meta:
        model = ConfiguracionInventario
        fields = ['nombre_organizacion', 'stock_minimo', 'alertas_stock_bajo']
        labels = {
            'nombre_organizacion': 'Nombre de la organización',
            'stock_minimo': 'Umbral general de stock bajo',
            'alertas_stock_bajo': 'Activar alertas visuales de stock bajo',
        }


class UsuarioForm(ContactoValidationMixin, forms.ModelForm):
    """Formulario para datos de usuario y contacto."""
    correo = forms.EmailField(
        label="Correo electrónico",
        required=True,
        max_length=254,
        widget=forms.EmailInput(attrs={"autocomplete": "email"}),
    )
    telefono = forms.CharField(
        label="Teléfono",
        required=False,
        max_length=30,
        widget=forms.TextInput(attrs={"type": "tel", "autocomplete": "tel"}),
        help_text="Colombia: 10 dígitos. Se acepta +57 o formato internacional.",
    )

    class Meta:
        model = Usuario
        fields = [
            "username",
            "password_hash",
            "nombre",
            "apellido",
            "correo",
            "telefono",
            "rol",
            "estado",
        ]
