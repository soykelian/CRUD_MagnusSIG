from django.contrib import admin

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


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'id_categoria', 'precio_venta', 'stock_minimo', 'estado', 'fecha_actualizacion')
    list_filter = ('id_categoria', 'estado')
    search_fields = ('codigo', 'nombre', 'descripcion')
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion')


@admin.register(Inventario)
class InventarioAdmin(admin.ModelAdmin):
    list_display = ('id_producto', 'cantidad_actual', 'ubicacion', 'fecha_actualizacion')
    search_fields = ('id_producto__nombre', 'id_producto__codigo', 'ubicacion')


@admin.register(MovimientoInventario)
class MovimientoInventarioAdmin(admin.ModelAdmin):
    list_display = ('fecha_movimiento', 'id_producto', 'tipo_movimiento', 'cantidad', 'motivo', 'id_usuario')
    list_filter = ('tipo_movimiento', 'fecha_movimiento')
    search_fields = ('id_producto__nombre', 'motivo', 'id_usuario__username')
    readonly_fields = tuple(field.name for field in MovimientoInventario._meta.fields)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class DetalleCompraInline(admin.TabularInline):
    model = DetalleCompra
    extra = 0
    readonly_fields = ('id_producto', 'cantidad', 'costo_unitario', 'subtotal')


@admin.register(Compra)
class CompraAdmin(admin.ModelAdmin):
    list_display = ('numero_factura', 'id_proveedor', 'total', 'estado', 'fecha_compra')
    list_filter = ('estado', 'fecha_compra')
    search_fields = ('numero_factura', 'id_proveedor__razon_social')
    inlines = [DetalleCompraInline]


class DetalleVentaInline(admin.TabularInline):
    model = DetalleVenta
    extra = 0
    readonly_fields = ('id_producto', 'cantidad', 'precio_unitario', 'subtotal')


@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = ('id_venta', 'id_cliente', 'total', 'estado', 'fecha_venta')
    list_filter = ('estado', 'fecha_venta')
    search_fields = ('id_cliente__razon_social',)
    inlines = [DetalleVentaInline]


@admin.register(Servicio)
class ServicioAdmin(admin.ModelAdmin):
    list_display = ('id_servicio', 'id_cliente', 'id_tipo_servicio', 'valor', 'estado', 'fecha_solicitud')
    list_filter = ('estado', 'id_tipo_servicio', 'fecha_solicitud')
    search_fields = ('id_cliente__razon_social', 'observaciones')


@admin.register(TipoServicio)
class TipoServicioAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'estado', 'fecha_creacion')
    list_filter = ('estado',)
    search_fields = ('nombre',)


@admin.register(ConfiguracionInventario)
class ConfiguracionInventarioAdmin(admin.ModelAdmin):
    list_display = ('nombre_organizacion', 'stock_minimo', 'alertas_stock_bajo', 'actualizado')

    def has_add_permission(self, request):
        return not ConfiguracionInventario.objects.filter(pk=1).exists()

    def get_queryset(self, request):
        return super().get_queryset(request).filter(pk=1)


admin.site.register(Categoria)
admin.site.register(Proveedor)
admin.site.register(Cliente)
admin.site.register(Usuario)
