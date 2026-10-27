"""Operaciones transaccionales que cambian las existencias del inventario en MySQL."""

from decimal import Decimal
from django.core.exceptions import ValidationError
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone

from ..models import (
    Compra,
    DetalleCompra,
    DetalleVenta,
    Inventario,
    MovimientoInventario,
    Producto,
    Venta,
    sincronizar_usuario_bd,
)


def obtener_inventario_producto(producto_id: int) -> Inventario:
    """Retorna o crea el registro de inventario con bloqueo transaccional."""
    inv, _ = Inventario.objects.select_for_update().get_or_create(
        id_producto_id=producto_id,
        defaults={'cantidad_actual': Decimal('0.000'), 'ubicacion': 'Bodega Principal'}
    )
    return inv


bloquear_producto = obtener_inventario_producto


@transaction.atomic
def registrar_movimiento(
    *, producto_id: int, tipo: str, cantidad: int | float | Decimal, motivo: str, responsable
) -> MovimientoInventario:
    """Aplica una entrada, salida o ajuste y deja su trazabilidad."""
    producto = get_object_or_404(Producto.objects.select_for_update(), pk=producto_id)
    inv = obtener_inventario_producto(producto_id)
    usuario_bd = sincronizar_usuario_bd(responsable)

    cant_dec = Decimal(str(abs(cantidad)))
    if cant_dec <= 0:
        raise ValidationError('La cantidad del movimiento debe ser mayor a cero.')

    if tipo == 'ajuste':
        # El ajuste manual puede ser positivo o negativo
        if cantidad < 0:
            if inv.cantidad_actual - cant_dec < 0:
                raise ValidationError('No hay existencias suficientes para este ajuste negativo.')
            inv.cantidad_actual -= cant_dec
            tipo_mov = 'salida'
        else:
            inv.cantidad_actual += cant_dec
            tipo_mov = 'entrada'
    elif tipo in ('salida', 'devolucion_salida'):
        if inv.cantidad_actual < cant_dec:
            raise ValidationError(
                f'Existencias insuficientes para este movimiento. Disponibles: {inv.cantidad_actual}.'
            )
        inv.cantidad_actual -= cant_dec
        tipo_mov = 'salida'
    elif tipo in ('entrada', 'devolucion'):
        inv.cantidad_actual += cant_dec
        tipo_mov = 'entrada'
    else:
        raise ValidationError('El tipo de movimiento no es válido.')

    inv.save(update_fields=['cantidad_actual', 'fecha_actualizacion'])

    return MovimientoInventario.objects.create(
        id_producto=producto,
        id_usuario=usuario_bd,
        tipo_movimiento=tipo_mov,
        cantidad=cant_dec,
        motivo=motivo or f'Movimiento de {tipo_mov}',
        fecha_movimiento=timezone.now(),
    )


@transaction.atomic
def recibir_entrada(*, entrada_id: int, responsable) -> Compra:
    """Cambia una compra a recibida y acredita el inventario en MySQL."""
    compra = get_object_or_404(
        Compra.objects.select_for_update().prefetch_related('detalles__id_producto'),
        pk=entrada_id,
    )
    if compra.estado == Compra.Estado.RECIBIDA:
        raise ValidationError('Esta compra ya fue recibida anteriormente.')
    if compra.estado == Compra.Estado.CANCELADA:
        raise ValidationError('No puedes recibir una compra cancelada.')

    usuario_bd = sincronizar_usuario_bd(responsable)

    for detalle in compra.detalles.all():
        inv = obtener_inventario_producto(detalle.id_producto_id)
        inv.cantidad_actual += detalle.cantidad
        inv.save(update_fields=['cantidad_actual', 'fecha_actualizacion'])

        MovimientoInventario.objects.create(
            id_producto=detalle.id_producto,
            id_usuario=usuario_bd,
            id_compra=compra,
            tipo_movimiento=MovimientoInventario.Tipo.ENTRADA,
            cantidad=detalle.cantidad,
            motivo=f'Recepción de {compra.referencia}',
            fecha_movimiento=timezone.now(),
        )

    compra.estado = Compra.Estado.RECIBIDA
    compra.save(update_fields=['estado'])
    return compra


@transaction.atomic
def despachar_salida(*, salida_id: int, responsable, administrador: bool) -> Venta:
    """Despacha una venta y descuenta el stock dentro de una transacción atómica."""
    ventas_q = Venta.objects.select_for_update().prefetch_related('detalles__id_producto')
    if not administrador:
        usuario_bd = sincronizar_usuario_bd(responsable)
        ventas_q = ventas_q.filter(id_usuario=usuario_bd)

    venta = get_object_or_404(ventas_q, pk=salida_id)
    if venta.estado == Venta.Estado.CONFIRMADA:
        raise ValidationError('Esta salida ya fue despachada anteriormente.')
    if venta.estado == Venta.Estado.CANCELADA:
        raise ValidationError('No puedes despachar una salida cancelada.')

    usuario_bd = sincronizar_usuario_bd(responsable)

    # Validar existencias de todos los items antes de descontar
    for detalle in venta.detalles.all():
        inv = obtener_inventario_producto(detalle.id_producto_id)
        if inv.cantidad_actual < detalle.cantidad:
            raise ValidationError(
                f'Stock insuficiente para "{detalle.id_producto.nombre}". '
                f'Disponible: {inv.cantidad_actual}, Requerido: {detalle.cantidad}.'
            )

    # Aplicar descuentos y trazabilidad
    for detalle in venta.detalles.all():
        inv = obtener_inventario_producto(detalle.id_producto_id)
        inv.cantidad_actual -= detalle.cantidad
        inv.save(update_fields=['cantidad_actual', 'fecha_actualizacion'])

        MovimientoInventario.objects.create(
            id_producto=detalle.id_producto,
            id_usuario=usuario_bd,
            id_venta=venta,
            tipo_movimiento=MovimientoInventario.Tipo.SALIDA,
            cantidad=detalle.cantidad,
            motivo=f'Despacho de {venta.referencia}',
            fecha_movimiento=timezone.now(),
        )

    venta.estado = Venta.Estado.CONFIRMADA
    venta.save(update_fields=['estado'])
    return venta
