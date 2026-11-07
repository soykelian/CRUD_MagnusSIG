"""Vistas del inventario: CRUD de productos, categorías y servicios sobre MySQL magnussig_inventario."""

from decimal import Decimal
from datetime import date, datetime, time, timedelta
from calendar import monthrange

from django.contrib import messages
from django.core.paginator import Paginator
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Count, DecimalField, ExpressionWrapper, F, Q, Sum
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from django.utils import timezone

from .forms import (
    CategoriaForm,
    ClienteForm,
    ConfiguracionForm,
    EntradaForm,
    MovimientoForm,
    ProductoForm,
    ProveedorForm,
    SalidaForm,
    ServicioForm,
    validar_stock_reservado,
)
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
    obtener_stock_minimo,
    sincronizar_usuario_bd,
    Entrada,
    Salida,
    Movimiento,
)
from .roles import es_administrador, requiere_acceso_inventario, requiere_administrador
from .services.stock import (
    bloquear_producto,
    despachar_salida as servicio_despachar_salida,
    recibir_entrada as servicio_recibir_entrada,
    registrar_movimiento,
)

POR_PAGINA = 8


def exportar_csv(nombre: str, encabezados: list[str], filas) -> HttpResponse:
    import csv
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="{nombre}"'
    response.write('\ufeff')
    writer = csv.writer(response)
    writer.writerow(encabezados)
    writer.writerows(filas)
    return response


@requiere_acceso_inventario
def dashboard(request: HttpRequest) -> HttpResponse:
    administrador = es_administrador(request.user)
    stock_minimo = obtener_stock_minimo()
    hoy = timezone.localdate()

    total_productos = Producto.objects.count()
    resumen_inv = Inventario.objects.aggregate(
        total_unidades=Sum('cantidad_actual'),
        valor_inventario=Sum(
            ExpressionWrapper(
                F('cantidad_actual') * F('id_producto__precio_venta'),
                output_field=DecimalField(max_digits=16, decimal_places=2),
            )
        ),
    )
    total_unidades = int(resumen_inv['total_unidades'] or 0)
    valor_inventario = resumen_inv['valor_inventario'] or Decimal('0.00')

    total_requieren_atencion = Inventario.objects.filter(
        cantidad_actual__lte=F('id_producto__stock_minimo')
    ).count()
    total_stock_bajo = Inventario.objects.filter(
        cantidad_actual__gt=0, cantidad_actual__lte=F('id_producto__stock_minimo')
    ).count()
    total_agotados = Inventario.objects.filter(cantidad_actual__lte=0).count()
    total_stock_saludable = Inventario.objects.filter(
        cantidad_actual__gt=F('id_producto__stock_minimo')
    ).count()
    porcentaje_stock_saludable = (
        round(total_stock_saludable * 100 / total_productos) if total_productos else 0
    )
    total_categorias = Categoria.objects.count()

    periodos = {'7d': 7, '30d': 30, '90d': 90, '1a': 365}
    periodo = request.GET.get('periodo', '30d')
    if periodo not in periodos:
        periodo = '30d'

    if periodo == '1a':
        numero_mes_inicio = hoy.year * 12 + hoy.month - 1 - 11
        anio_inicio, mes_inicio = divmod(numero_mes_inicio, 12)
        fecha_inicio = date(anio_inicio, mes_inicio + 1, 1)
    else:
        fecha_inicio = hoy - timedelta(days=periodos[periodo] - 1)

    dias_periodo = (hoy - fecha_inicio).days + 1
    variacion_diaria = {fecha_inicio + timedelta(days=i): 0 for i in range(dias_periodo)}

    usuario_bd = sincronizar_usuario_bd(request.user)
    inicio_dt = timezone.make_aware(datetime.combine(fecha_inicio, time.min))
    fin_dt = timezone.make_aware(datetime.combine(hoy, time.max))
    movimientos_periodo = MovimientoInventario.objects.filter(
        fecha_movimiento__gte=inicio_dt, fecha_movimiento__lte=fin_dt
    )
    if not administrador and usuario_bd:
        movimientos_periodo = movimientos_periodo.filter(
            tipo_movimiento='salida', id_usuario=usuario_bd
        )

    registros_periodo = list(
        movimientos_periodo.values_list('fecha_movimiento', 'tipo_movimiento', 'cantidad')
    )
    for fecha, tipo, cantidad in registros_periodo:
        dia = timezone.localtime(fecha).date()
        if dia in variacion_diaria:
            signo = -1 if tipo == 'salida' else 1
            variacion_diaria[dia] += int(cantidad) * signo

    variacion_acumulada = sum(variacion_diaria.values())

    nombres_meses = ('Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic')
    intervalos = []
    if periodo == '1a':
        numero_mes_actual = hoy.year * 12 + hoy.month - 1
        for indice in range(12):
            numero_mes = numero_mes_actual - 11 + indice
            anio, mes_cero = divmod(numero_mes, 12)
            mes = mes_cero + 1
            inicio_mes = date(anio, mes, 1)
            fin_mes = min(date(anio, mes, monthrange(anio, mes)[1]), hoy)
            intervalos.append({'inicio': inicio_mes, 'fin': fin_mes, 'etiqueta': nombres_meses[mes - 1]})
    elif periodo == '90d':
        for desplazamiento in range(0, dias_periodo, 7):
            inicio = fecha_inicio + timedelta(days=desplazamiento)
            intervalos.append({
                'inicio': inicio,
                'fin': min(inicio + timedelta(days=6), hoy),
                'etiqueta': f'{inicio.day} {nombres_meses[inicio.month - 1].lower()}',
            })
    else:
        for desplazamiento in range(dias_periodo):
            dia = fecha_inicio + timedelta(days=desplazamiento)
            intervalos.append({
                'inicio': dia,
                'fin': dia,
                'etiqueta': f'{dia.day} {nombres_meses[dia.month - 1].lower()}',
            })

    indice_por_fecha = {}
    for indice, intervalo in enumerate(intervalos):
        dia = intervalo['inicio']
        while dia <= intervalo['fin']:
            indice_por_fecha[dia] = indice
            dia += timedelta(days=1)
        intervalo.update({'entradas': 0, 'salidas': 0})

    for fecha, tipo, cantidad in registros_periodo:
        dia = timezone.localtime(fecha).date()
        indice = indice_por_fecha.get(dia)
        if indice is None:
            continue
        if tipo == 'entrada':
            intervalos[indice]['entradas'] += int(cantidad)
        elif tipo == 'salida':
            intervalos[indice]['salidas'] += int(cantidad)

    escala_grafico = max(
        (max(intervalo['entradas'], intervalo['salidas']) for intervalo in intervalos),
        default=0,
    ) or 1
    escala_media = round(escala_grafico / 2)
    datos_linea = []
    for indice, intervalo in enumerate(intervalos):
        punto = dict(intervalo)
        if periodo == '1a':
            punto['x'] = round(55 + (indice + 0.5) * 835 / len(intervalos))
        else:
            punto['x'] = round(55 + indice * 835 / max(1, len(intervalos) - 1))
        punto['y_entradas'] = round(160 - intervalo['entradas'] * 130 / escala_grafico)
        punto['y_salidas'] = round(160 - intervalo['salidas'] * 130 / escala_grafico)
        datos_linea.append(punto)

    indices_etiqueta = (
        range(len(datos_linea)) if periodo == '1a'
        else sorted({round(indice * (len(datos_linea) - 1) / 4) for indice in range(5)})
    )
    etiquetas_linea = [
        {'x': datos_linea[indice]['x'], 'texto': datos_linea[indice]['etiqueta']}
        for indice in indices_etiqueta
    ]
    hay_actividad_periodo = bool(registros_periodo)
    total_entradas_periodo = sum(
        int(cantidad) for _, tipo, cantidad in registros_periodo if tipo == 'entrada'
    )
    total_salidas_periodo = sum(
        int(cantidad) for _, tipo, cantidad in registros_periodo if tipo == 'salida'
    )

    # Gráfico de barras de 6 meses
    primer_mes_numero = hoy.year * 12 + hoy.month - 1 - 5
    meses = []
    for indice in range(6):
        mes_numero = primer_mes_numero + indice
        anio, mes = divmod(mes_numero, 12)
        mes += 1
        meses.append({
            'llave': (anio, mes),
            'nombre': nombres_meses[mes - 1],
            'entradas': 0,
            'salidas': 0,
        })
    resumen_meses = {fila['llave']: fila for fila in meses}
    primer_dia = date(meses[0]['llave'][0], meses[0]['llave'][1], 1)
    primer_dia_dt = timezone.make_aware(datetime.combine(primer_dia, time.min))
    movimientos_seis_meses = MovimientoInventario.objects.filter(
        fecha_movimiento__gte=primer_dia_dt, fecha_movimiento__lte=fin_dt
    )
    if not administrador and usuario_bd:
        movimientos_seis_meses = movimientos_seis_meses.filter(
            tipo_movimiento='salida', id_usuario=usuario_bd
        )
    for fecha, tipo, cantidad in movimientos_seis_meses.values_list('fecha_movimiento', 'tipo_movimiento', 'cantidad'):
        local_fecha = timezone.localtime(fecha).date()
        fila_mes = resumen_meses.get((local_fecha.year, local_fecha.month))
        if not fila_mes:
            continue
        if tipo == 'entrada':
            fila_mes['entradas'] += int(cantidad)
        elif tipo == 'salida':
            fila_mes['salidas'] += int(cantidad)

    escala_mensual = max(
        (max(fila['entradas'], fila['salidas']) for fila in meses), default=0
    ) or 1
    for fila in meses:
        fila['entradas_pct'] = round(fila['entradas'] * 100 / escala_mensual)
        fila['salidas_pct'] = round(fila['salidas'] * 100 / escala_mensual)

    # Donut de categorías
    categorias = list(
        Categoria.objects.annotate(unidades=Sum('productos__inventario_rel__cantidad_actual'))
        .filter(unidades__gt=0).order_by('-unidades', 'nombre')
    )
    if len(categorias) > 5:
        unidades_otros = sum(c.unidades for c in categorias[4:])
        categorias = categorias[:4] + [
            {'nombre': 'Otras categorías', 'unidades': unidades_otros, 'pk': None}
        ]
    circunferencia = 276.46
    desplazamiento = 0
    colores_categorias = ('#2e3192', '#269dd8', '#ff931e', '#6268ba', '#72c8e8')
    for indice, categoria in enumerate(categorias):
        unidades = getattr(categoria, 'unidades', 0) if hasattr(categoria, 'unidades') else categoria.get('unidades', 0)
        porcentaje = round(unidades * 100 / total_unidades) if total_unidades else 0
        trazo = round(porcentaje * circunferencia / 100, 2)
        if isinstance(categoria, dict):
            categoria['porcentaje'] = porcentaje
            categoria['trazo'] = trazo
            categoria['offset'] = round(-desplazamiento, 2)
            categoria['restante'] = round(circunferencia - trazo, 2)
            categoria['color'] = colores_categorias[indice % len(colores_categorias)]
        else:
            categoria.porcentaje = porcentaje
            categoria.trazo = trazo
            categoria.offset = round(-desplazamiento, 2)
            categoria.restante = round(circunferencia - trazo, 2)
            categoria.color = colores_categorias[indice % len(colores_categorias)]
        desplazamiento += trazo

    movimientos_recientes = MovimientoInventario.objects.select_related('id_producto', 'id_usuario')
    salidas_pendientes = Venta.objects.filter(estado=Venta.Estado.BORRADOR)
    if not administrador and usuario_bd:
        movimientos_recientes = movimientos_recientes.filter(
            tipo_movimiento='salida', id_usuario=usuario_bd
        )
        salidas_pendientes = salidas_pendientes.filter(id_usuario=usuario_bd)

    productos_revision = Producto.objects.select_related('id_categoria', 'inventario_rel').filter(
        inventario_rel__cantidad_actual__lte=F('stock_minimo')
    ).order_by('inventario_rel__cantidad_actual', 'nombre')[:5]

    servicios_activos = Servicio.objects.filter(estado__in=['pendiente', 'en proceso']).count()

    contexto = {
        'total_productos': total_productos,
        'total_unidades': total_unidades,
        'valor_inventario': valor_inventario,
        'total_categorias': total_categorias,
        'nivel_minimo_stock': stock_minimo,
        'total_requieren_atencion': total_requieren_atencion,
        'total_stock_bajo': total_stock_bajo,
        'total_agotados': total_agotados,
        'total_stock_saludable': total_stock_saludable,
        'porcentaje_stock_saludable': porcentaje_stock_saludable,
        'periodo': periodo,
        'periodos': periodos,
        'datos_linea': datos_linea,
        'etiquetas_linea': etiquetas_linea,
        'escala_grafico': escala_grafico,
        'escala_media': escala_media,
        'hay_actividad_periodo': hay_actividad_periodo,
        'variacion_neta_periodo': variacion_acumulada,
        'total_entradas_periodo': total_entradas_periodo,
        'total_salidas_periodo': total_salidas_periodo,
        'meses': meses,
        'categorias_dashboard': categorias,
        'productos_revision': productos_revision,
        'movimientos_recientes': movimientos_recientes[:5],
        'entradas_pendientes': Compra.objects.filter(estado=Compra.Estado.BORRADOR).count() if administrador else 0,
        'salidas_pendientes': salidas_pendientes.count(),
        'servicios_activos': servicios_activos,
    }
    return render(request, 'productos/dashboard.html', contexto)


@requiere_acceso_inventario
def lista_productos(request: HttpRequest) -> HttpResponse:
    stock_minimo = obtener_stock_minimo()
    q = request.GET.get('q', '').strip()
    categoria = request.GET.get('categoria', '').strip()
    existencias = request.GET.get('existencias', '').strip()

    productos = Producto.objects.select_related('id_categoria', 'id_proveedor', 'inventario_rel').order_by(
        '-fecha_creacion', '-id_producto'
    )
    if q:
        productos = productos.filter(
            Q(nombre__icontains=q) | Q(codigo__icontains=q) | Q(descripcion__icontains=q)
        )
    if categoria.isdigit():
        productos = productos.filter(id_categoria_id=int(categoria))

    if existencias == 'out':
        productos = productos.filter(inventario_rel__cantidad_actual__lte=0)
    elif existencias == 'low':
        productos = productos.filter(
            inventario_rel__cantidad_actual__gt=0,
            inventario_rel__cantidad_actual__lte=F('stock_minimo'),
        )
    elif existencias == 'attention':
        productos = productos.filter(inventario_rel__cantidad_actual__lte=F('stock_minimo'))
    elif existencias == 'ok':
        productos = productos.filter(inventario_rel__cantidad_actual__gt=F('stock_minimo'))

    pagina = Paginator(productos, POR_PAGINA).get_page(request.GET.get('page'))

    params = request.GET.copy()
    params.pop('page', None)

    contexto = {
        'pagina': pagina,
        'q': q,
        'categoria_sel': categoria,
        'existencias_sel': existencias,
        'categorias': Categoria.objects.filter(estado='activo').order_by('nombre'),
        'querystring': params.urlencode(),
        'hay_filtros': bool(q or categoria or existencias),
        'nivel_minimo_stock': stock_minimo,
        'total_productos': Producto.objects.count(),
        'total_categorias': Categoria.objects.count(),
        'total_stock_bajo': Inventario.objects.filter(
            cantidad_actual__gt=0, cantidad_actual__lte=F('id_producto__stock_minimo')
        ).count(),
        'total_agotados': Inventario.objects.filter(cantidad_actual__lte=0).count(),
        'productos_revision': Producto.objects.select_related('id_categoria', 'inventario_rel').filter(
            inventario_rel__cantidad_actual__lte=F('stock_minimo')
        ).order_by('inventario_rel__cantidad_actual', 'nombre')[:5],
    }
    plantilla = (
        'productos/_product_results.html'
        if request.headers.get('HX-Request') == 'true'
        else 'productos/lista.html'
    )
    return render(request, plantilla, contexto)


@requiere_acceso_inventario
def catalogo_productos(request: HttpRequest) -> HttpResponse:
    q = request.GET.get('q', '').strip()
    productos = Producto.objects.select_related('id_categoria', 'id_proveedor', 'inventario_rel').order_by(
        '-fecha_creacion', '-id_producto'
    )
    if q:
        productos = productos.filter(
            Q(nombre__icontains=q) | Q(codigo__icontains=q) | Q(descripcion__icontains=q)
        )
    contexto = {
        'productos': productos,
        'q': q,
        'total_productos': Producto.objects.count(),
        'total_categorias': Categoria.objects.count(),
    }
    plantilla = (
        'productos/_catalog_results.html'
        if request.headers.get('HX-Request') == 'true'
        else 'productos/catalogo.html'
    )
    return render(request, plantilla, contexto)


@requiere_acceso_inventario
def detalle_producto(request: HttpRequest, pk: int) -> HttpResponse:
    producto = get_object_or_404(
        Producto.objects.select_related('id_categoria', 'id_proveedor', 'inventario_rel'),
        pk=pk,
    )
    movimientos = producto.movimientos.select_related('id_usuario').order_by('-fecha_movimiento')
    usuario_bd = sincronizar_usuario_bd(request.user)
    if not es_administrador(request.user) and usuario_bd:
        movimientos = movimientos.filter(tipo_movimiento='salida', id_usuario=usuario_bd)

    tiene_historial = producto.movimientos.exists() or producto.detalles_compra.exists() or producto.detalles_venta.exists()
    return render(request, 'productos/detalle.html', {
        'producto': producto,
        'movimientos': movimientos[:10],
        'tiene_historial': tiene_historial,
        'nivel_minimo_stock': obtener_stock_minimo(),
    })


@requiere_administrador
def crear_producto(request: HttpRequest) -> HttpResponse:
    if not Categoria.objects.filter(estado='activo').exists():
        messages.warning(request, 'Primero crea una categoría para clasificar los productos.')
        return redirect('productos:categoria_crear')

    form = ProductoForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        with transaction.atomic():
            producto = form.save()
            cantidad_inicial = form.cleaned_data.get('cantidad', 0)
            if cantidad_inicial > 0:
                usuario_bd = sincronizar_usuario_bd(request.user)
                MovimientoInventario.objects.create(
                    id_producto=producto,
                    id_usuario=usuario_bd,
                    tipo_movimiento='entrada',
                    cantidad=Decimal(str(cantidad_inicial)),
                    motivo='Existencias iniciales al registrar el producto',
                )
        messages.success(request, f'Producto “{producto.nombre}” ({producto.codigo}) creado correctamente.')
        return redirect('productos:lista')
    return render(request, 'productos/form.html', {'form': form, 'editando': False})


@requiere_administrador
def editar_producto(request: HttpRequest, pk: int) -> HttpResponse:
    producto = get_object_or_404(Producto, pk=pk)
    form = ProductoForm(request.POST or None, instance=producto)
    if request.method == 'POST' and form.is_valid():
        with transaction.atomic():
            cant_anterior = producto.cantidad
            producto = form.save()
            cant_nueva = form.cleaned_data.get('cantidad', cant_anterior)
            diferencia = cant_nueva - cant_anterior
            if diferencia != 0:
                usuario_bd = sincronizar_usuario_bd(request.user)
                tipo_mov = 'entrada' if diferencia > 0 else 'salida'
                MovimientoInventario.objects.create(
                    id_producto=producto,
                    id_usuario=usuario_bd,
                    tipo_movimiento=tipo_mov,
                    cantidad=Decimal(str(abs(diferencia))),
                    motivo='Ajuste de inventario al editar producto',
                )
        messages.success(request, f'Producto “{producto.nombre}” actualizado correctamente.')
        return redirect('productos:detalle', pk=producto.pk)
    return render(
        request, 'productos/form.html',
        {'form': form, 'editando': True, 'producto': producto},
    )


@requiere_administrador
def eliminar_producto(request: HttpRequest, pk: int) -> HttpResponse:
    producto = get_object_or_404(Producto.objects.select_related('id_categoria'), pk=pk)
    tiene_historial = producto.movimientos.exists() or producto.detalles_compra.exists() or producto.detalles_venta.exists()
    if request.method == 'POST':
        if tiene_historial:
            messages.error(
                request,
                'No se puede eliminar un producto con historial de movimientos, compras o ventas para preservar la trazabilidad.'
            )
            return redirect('productos:detalle', pk=producto.pk)
        nombre = producto.nombre
        Inventario.objects.filter(id_producto=producto).delete()
        producto.delete()
        messages.success(request, f'Producto “{nombre}” eliminado.')
        return redirect('productos:lista')
    return render(
        request,
        'productos/confirmar_eliminar.html',
        {'producto': producto, 'tiene_historial': tiene_historial},
    )


# ---------------------------- Categorías ----------------------------

@requiere_acceso_inventario
def lista_categorias(request: HttpRequest) -> HttpResponse:
    q = request.GET.get('q', '').strip()
    orden = 'desc' if request.GET.get('orden') == 'desc' else 'asc'

    categorias = Categoria.objects.annotate(total=Count('productos'))
    if q:
        categorias = categorias.filter(Q(nombre__icontains=q) | Q(descripcion__icontains=q))
    categorias = categorias.order_by('-nombre' if orden == 'desc' else 'nombre')

    return render(request, 'productos/categorias.html', {
        'categorias': categorias,
        'q': q,
        'orden': orden,
        'hay_categorias': Categoria.objects.exists(),
    })


@requiere_administrador
def crear_categoria(request: HttpRequest) -> HttpResponse:
    form = CategoriaForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        categoria = form.save()
        messages.success(request, f'Categoría “{categoria.nombre}” creada correctamente.')
        return redirect('productos:categorias')
    return render(request, 'productos/categoria_form.html', {'form': form, 'editando': False})


@requiere_administrador
def editar_categoria(request: HttpRequest, pk: int) -> HttpResponse:
    categoria = get_object_or_404(Categoria, pk=pk)
    form = CategoriaForm(request.POST or None, instance=categoria)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, f'Categoría “{categoria.nombre}” actualizada.')
        return redirect('productos:categorias')
    return render(
        request, 'productos/categoria_form.html',
        {'form': form, 'editando': True, 'categoria': categoria},
    )


@require_POST
@requiere_administrador
def eliminar_categoria(request: HttpRequest, pk: int) -> HttpResponse:
    categoria = get_object_or_404(Categoria, pk=pk)
    if categoria.productos.exists():
        messages.error(
            request,
            'No puedes eliminar una categoría que todavía tiene productos asociados.',
        )
    else:
        nombre = categoria.nombre
        categoria.delete()
        messages.success(request, f'Categoría “{nombre}” eliminada.')
    return redirect('productos:categorias')


# ---------------------------- Movimientos ----------------------------

@requiere_acceso_inventario
def movimientos(request: HttpRequest) -> HttpResponse:
    q = request.GET.get('q', '').strip()
    registros = MovimientoInventario.objects.select_related('id_producto', 'id_usuario')
    usuario_bd = sincronizar_usuario_bd(request.user)
    if not es_administrador(request.user) and usuario_bd:
        registros = registros.filter(tipo_movimiento='salida', id_usuario=usuario_bd)
    if q:
        registros = registros.filter(
            Q(id_producto__nombre__icontains=q)
            | Q(id_producto__codigo__icontains=q)
            | Q(motivo__icontains=q)
        )
    if request.GET.get('tipo'):
        registros = registros.filter(tipo_movimiento=request.GET['tipo'])

    if request.GET.get('export') == 'csv':
        return exportar_csv(
            'movimientos.csv',
            ['Fecha', 'Producto', 'Tipo', 'Cantidad', 'Referencia', 'Responsable', 'Motivo'],
            (
                [
                    m.fecha_movimiento,
                    m.id_producto.nombre,
                    m.get_tipo_movimiento_display(),
                    m.cantidad,
                    m.referencia,
                    m.id_usuario.username if m.id_usuario else '—',
                    m.motivo,
                ]
                for m in registros
            ),
        )

    hoy = timezone.localdate()
    return render(request, 'productos/modulo_lista.html', {
        'seccion': 'movimientos',
        'titulo': 'Movimientos de Inventario',
        'bajada': 'Trazabilidad completa de entradas, salidas y ajustes de inventario.',
        'registros': registros,
        'q': q,
        'total': registros.count(),
        'total_mes': registros.filter(
            fecha_movimiento__gte=timezone.make_aware(datetime.combine(date(hoy.year, hoy.month, 1), time.min)),
            fecha_movimiento__lte=timezone.make_aware(datetime.combine(hoy, time.max)),
        ).count(),
        'cta': 'Registrar movimiento' if es_administrador(request.user) else 'Registrar salida',
        'cta_url': 'productos:movimiento_nuevo' if es_administrador(request.user) else 'productos:salida_nueva',
        'entradas_mes': registros.filter(tipo_movimiento='entrada').count(),
        'salidas_mes': registros.filter(tipo_movimiento='salida').count(),
        'tipos_movimiento': [('entrada', 'Entrada'), ('salida', 'Salida'), ('ajuste', 'Ajuste')],
    })


@requiere_administrador
def crear_movimiento(request: HttpRequest) -> HttpResponse:
    form = MovimientoForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        datos = form.cleaned_data
        try:
            registrar_movimiento(
                producto_id=datos['producto'].pk,
                tipo=datos['tipo'],
                cantidad=datos['cantidad'],
                motivo=datos['motivo'],
                responsable=request.user,
            )
        except ValidationError as error:
            form.add_error('cantidad', error)
        if not form.errors:
            messages.success(request, 'El movimiento se registró y el stock en MySQL fue actualizado.')
            return redirect('productos:movimientos')
    return render(request, 'productos/registro_form.html', {
        'form': form,
        'titulo': 'Registrar movimiento',
        'regreso': 'productos:movimientos',
        'ayuda': 'Las entradas suman stock, las salidas lo descuentan y los ajustes corrigen variaciones de inventario.',
    })


# ---------------------------- Compras (Entradas) ----------------------------

@requiere_administrador
def entradas(request: HttpRequest) -> HttpResponse:
    registros = Compra.objects.select_related('id_proveedor', 'id_usuario').prefetch_related('detalles__id_producto')
    q = request.GET.get('q', '').strip()
    if q:
        registros = registros.filter(
            Q(numero_factura__icontains=q)
            | Q(id_proveedor__razon_social__icontains=q)
            | Q(detalles__id_producto__nombre__icontains=q)
        ).distinct()
    if request.GET.get('estado'):
        registros = registros.filter(estado=request.GET['estado'])

    pendientes = Compra.objects.filter(estado=Compra.Estado.BORRADOR).count()
    valor_recibido = Compra.objects.filter(estado=Compra.Estado.RECIBIDA).aggregate(
        total=Sum('total')
    )['total'] or Decimal('0.00')

    return render(request, 'productos/modulo_lista.html', {
        'seccion': 'entradas',
        'titulo': 'Entradas y Compras',
        'bajada': 'Gestiona las recepciones de proveedores y suma existencias a la base de datos.',
        'registros': registros,
        'q': q,
        'total': registros.count(),
        'pendientes': pendientes,
        'valor_recibido': valor_recibido,
        'cta': 'Registrar compra / entrada',
        'cta_url': 'productos:entrada_nueva',
    })


@requiere_administrador
def crear_entrada(request: HttpRequest) -> HttpResponse:
    if not Producto.objects.filter(estado='activo').exists():
        messages.warning(request, 'Primero registra al menos un producto en el inventario.')
        return redirect('productos:crear')
    if not Proveedor.objects.filter(estado='activo').exists():
        messages.warning(request, 'Primero registra un proveedor activo.')
        return redirect('productos:proveedor_nuevo')

    form = EntradaForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        with transaction.atomic():
            usuario_bd = sincronizar_usuario_bd(request.user)
            proveedor = form.cleaned_data['proveedor']
            producto = form.cleaned_data['producto']
            cantidad = form.cleaned_data['cantidad']
            costo_unitario = form.cleaned_data['costo_unitario']
            numero_factura = form.cleaned_data.get('numero_factura', '').strip()
            observaciones = form.cleaned_data.get('observaciones', '')
            subtotal = cantidad * costo_unitario

            compra = Compra.objects.create(
                id_proveedor=proveedor,
                id_usuario=usuario_bd,
                numero_factura=numero_factura or None,
                subtotal=subtotal,
                total=subtotal,
                estado=Compra.Estado.BORRADOR,
                observaciones=observaciones or None,
            )
            DetalleCompra.objects.create(
                id_compra=compra,
                id_producto=producto,
                cantidad=cantidad,
                costo_unitario=costo_unitario,
                subtotal=subtotal,
            )
        messages.success(request, f'Entrada/Compra {compra.referencia} registrada en estado borrador.')
        return redirect('productos:entradas')

    return render(request, 'productos/registro_form.html', {
        'form': form,
        'titulo': 'Registrar compra / entrada',
        'regreso': 'productos:entradas',
    })


@require_POST
@requiere_administrador
def recibir_entrada(request: HttpRequest, pk: int) -> HttpResponse:
    try:
        compra = servicio_recibir_entrada(entrada_id=pk, responsable=request.user)
    except ValidationError as error:
        messages.error(request, error.messages[0])
    else:
        messages.success(request, f'Compra {compra.referencia}: existencias acreditadas en inventario MySQL.')
    return redirect('productos:entradas')


# ---------------------------- Ventas (Salidas) ----------------------------

@requiere_acceso_inventario
def salidas(request: HttpRequest) -> HttpResponse:
    registros = Venta.objects.select_related('id_cliente', 'id_usuario').prefetch_related('detalles__id_producto')
    usuario_bd = sincronizar_usuario_bd(request.user)
    if not es_administrador(request.user) and usuario_bd:
        registros = registros.filter(id_usuario=usuario_bd)
    q = request.GET.get('q', '').strip()
    if q:
        registros = registros.filter(
            Q(id_cliente__razon_social__icontains=q)
            | Q(detalles__id_producto__nombre__icontains=q)
        ).distinct()
    if request.GET.get('estado'):
        registros = registros.filter(estado=request.GET['estado'])

    return render(request, 'productos/modulo_lista.html', {
        'seccion': 'salidas',
        'titulo': 'Salidas y Despachos',
        'bajada': 'Gestiona entregas a clientes y descuenta unidades de inventario al despachar.',
        'registros': registros,
        'q': q,
        'total': registros.count(),
        'cta': 'Registrar salida',
        'cta_url': 'productos:salida_nueva',
        'preparando': registros.filter(estado=Venta.Estado.BORRADOR).count(),
        'despachadas': registros.filter(estado=Venta.Estado.CONFIRMADA).count(),
    })


@requiere_acceso_inventario
def crear_salida(request: HttpRequest) -> HttpResponse:
    if not Producto.objects.filter(estado='activo').exists():
        messages.warning(request, 'Primero registra productos en el inventario.')
        return redirect('productos:lista')
    if not Cliente.objects.filter(estado='activo').exists():
        messages.warning(request, 'Primero registra al menos un cliente activo.')
        return redirect('productos:cliente_nuevo')

    form = SalidaForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        with transaction.atomic():
            usuario_bd = sincronizar_usuario_bd(request.user)
            cliente = form.cleaned_data['cliente']
            producto = form.cleaned_data['producto']
            cantidad = form.cleaned_data['cantidad']
            precio_unitario = form.cleaned_data.get('precio_unitario') or producto.precio_venta
            observaciones = form.cleaned_data.get('observaciones', '')
            subtotal = cantidad * precio_unitario

            venta = Venta.objects.create(
                id_cliente=cliente,
                id_usuario=usuario_bd,
                subtotal=subtotal,
                total=subtotal,
                estado=Venta.Estado.BORRADOR,
                observaciones=observaciones or None,
            )
            DetalleVenta.objects.create(
                id_venta=venta,
                id_producto=producto,
                cantidad=cantidad,
                precio_unitario=precio_unitario,
                subtotal=subtotal,
            )
        messages.success(request, f'Salida {venta.referencia} registrada y stock reservado.')
        return redirect('productos:salidas')

    return render(request, 'productos/registro_form.html', {
        'form': form,
        'titulo': 'Registrar salida',
        'regreso': 'productos:salidas',
    })


@require_POST
@requiere_acceso_inventario
def despachar_salida(request: HttpRequest, pk: int) -> HttpResponse:
    try:
        venta = servicio_despachar_salida(
            salida_id=pk,
            responsable=request.user,
            administrador=es_administrador(request.user),
        )
    except ValidationError as error:
        messages.error(request, error.messages[0])
    else:
        messages.success(request, f'Salida {venta.referencia} despachada y stock descontado.')
    return redirect('productos:salidas')


# ---------------------------- Proveedores ----------------------------

@requiere_administrador
def proveedores(request: HttpRequest) -> HttpResponse:
    registros = Proveedor.objects.annotate(total_entradas=Count('compras'))
    q = request.GET.get('q', '').strip()
    if q:
        registros = registros.filter(
            Q(razon_social__icontains=q)
            | Q(nit__icontains=q)
            | Q(nombre_contacto__icontains=q)
            | Q(correo__icontains=q)
        )
    return render(request, 'productos/modulo_lista.html', {
        'seccion': 'proveedores',
        'titulo': 'Proveedores',
        'bajada': 'Administra contactos y aliados de abastecimiento de dotación y EPP.',
        'registros': registros,
        'q': q,
        'total': registros.count(),
        'cta': 'Agregar proveedor',
        'cta_url': 'productos:proveedor_nuevo',
        'activos': Proveedor.objects.filter(estado='activo').count(),
    })


@requiere_administrador
def crear_proveedor(request: HttpRequest) -> HttpResponse:
    form = ProveedorForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        prov = form.save()
        messages.success(request, f'Proveedor “{prov.razon_social}” guardado correctamente.')
        return redirect('productos:proveedores')
    return render(request, 'productos/registro_form.html', {
        'form': form,
        'titulo': 'Agregar proveedor',
        'regreso': 'productos:proveedores',
    })


# ---------------------------- Clientes ----------------------------

@requiere_acceso_inventario
def clientes(request: HttpRequest) -> HttpResponse:
    registros = Cliente.objects.annotate(total_salidas=Count('ventas'))
    q = request.GET.get('q', '').strip()
    if q:
        registros = registros.filter(
            Q(razon_social__icontains=q)
            | Q(numero_documento__icontains=q)
            | Q(nombre_contacto__icontains=q)
            | Q(correo__icontains=q)
            | Q(ciudad__icontains=q)
        )
    return render(request, 'productos/modulo_lista.html', {
        'seccion': 'clientes',
        'titulo': 'Clientes',
        'bajada': 'Empresas y organizaciones a las que se suministra seguridad y dotación.',
        'registros': registros,
        'q': q,
        'total': registros.count(),
        'cta': 'Agregar cliente',
        'cta_url': 'productos:cliente_nuevo',
        'clientes_activos': Cliente.objects.filter(estado='activo').count(),
        'total_productos': Producto.objects.count(),
    })


@requiere_acceso_inventario
def crear_cliente(request: HttpRequest) -> HttpResponse:
    form = ClienteForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        cli = form.save()
        messages.success(request, f'Cliente “{cli.razon_social}” guardado correctamente.')
        return redirect('productos:clientes')
    return render(request, 'productos/registro_form.html', {
        'form': form,
        'titulo': 'Agregar cliente',
        'regreso': 'productos:clientes',
    })


# ---------------------------- Servicios SG-SST (Nuevo Módulo) ----------------------------

@requiere_acceso_inventario
def servicios(request: HttpRequest) -> HttpResponse:
    registros = Servicio.objects.select_related('id_cliente', 'id_tipo_servicio', 'id_usuario')
    q = request.GET.get('q', '').strip()
    if q:
        registros = registros.filter(
            Q(id_cliente__razon_social__icontains=q)
            | Q(id_tipo_servicio__nombre__icontains=q)
            | Q(observaciones__icontains=q)
        )
    if request.GET.get('estado'):
        registros = registros.filter(estado=request.GET['estado'])

    valor_total = registros.aggregate(total=Sum('valor'))['total'] or Decimal('0.00')

    return render(request, 'productos/modulo_lista.html', {
        'seccion': 'servicios',
        'titulo': 'Servicios de Seguridad y Salud en el Trabajo',
        'bajada': 'Capacitaciones, auditorías ISO/PESV, diagnósticos e intervenciones del SG-SST.',
        'registros': registros,
        'q': q,
        'total': registros.count(),
        'cta': 'Solicitar nuevo servicio',
        'cta_url': 'productos:servicio_nuevo',
        'pendientes': registros.filter(estado='pendiente').count(),
        'en_proceso': registros.filter(estado='en proceso').count(),
        'finalizados': registros.filter(estado='finalizado').count(),
        'valor_recibido': valor_total,
    })


@requiere_acceso_inventario
def crear_servicio(request: HttpRequest) -> HttpResponse:
    if not Cliente.objects.filter(estado='activo').exists():
        messages.warning(request, 'Primero registra al menos un cliente activo.')
        return redirect('productos:cliente_nuevo')

    form = ServicioForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        servicio = form.save(commit=False)
        servicio.id_usuario = sincronizar_usuario_bd(request.user)
        servicio.save()
        messages.success(request, f'Servicio {servicio.referencia} creado exitosamente.')
        return redirect('productos:servicios')

    return render(request, 'productos/registro_form.html', {
        'form': form,
        'titulo': 'Registrar servicio SG-SST',
        'regreso': 'productos:servicios',
    })


# ---------------------------- Reportes & Configuración ----------------------------

def _respuesta_reporte_pdf(datos):
    from io import BytesIO
    from xml.sax.saxutils import escape

    from reportlab.lib import colors
    from reportlab.lib.enums import TA_LEFT
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import mm
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

    buffer = BytesIO()
    documento = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        rightMargin=14 * mm,
        leftMargin=14 * mm,
        topMargin=14 * mm,
        bottomMargin=14 * mm,
        title="Reporte de inventario Magnus SIG",
        author="Magnus SIG",
    )
    estilos = getSampleStyleSheet()
    estilos.add(ParagraphStyle(
        name="CeldaReporte",
        parent=estilos["BodyText"],
        fontName="Helvetica",
        fontSize=8,
        leading=10,
        alignment=TA_LEFT,
    ))
    estilos.add(ParagraphStyle(
        name="EncabezadoReporte",
        parent=estilos["BodyText"],
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=10,
        textColor=colors.white,
    ))

    def tabla(encabezados, filas, anchos=None):
        contenido = [[
            Paragraph(escape(str(valor)), estilos["EncabezadoReporte"])
            for valor in encabezados
        ]]
        contenido.extend([
            [Paragraph(escape(str(valor)), estilos["CeldaReporte"]) for valor in fila]
            for fila in filas
        ])
        tabla_pdf = Table(contenido, colWidths=anchos, repeatRows=1, hAlign="LEFT")
        estilos_tabla = [
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#243B64")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#D7DFEA")),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ]
        if filas:
            estilos_tabla.append(("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F2F5F9")]))
        tabla_pdf.setStyle(TableStyle(estilos_tabla))
        return tabla_pdf

    historia = [
        Paragraph("Reporte de inventario", estilos["Title"]),
        Paragraph(f"Magnus SIG · Generado: {escape(datos['generado'])}", estilos["BodyText"]),
        Spacer(1, 7 * mm),
        Paragraph("Resumen general", estilos["Heading2"]),
        tabla(["Indicador", "Valor"], datos["indicadores"], [100 * mm, 150 * mm]),
        Spacer(1, 6 * mm),
        Paragraph("Valor estimado por categoría (COP)", estilos["Heading2"]),
        tabla(["Categoría", "Unidades", "Valor estimado (COP)"], datos["categorias"], [125 * mm, 45 * mm, 80 * mm]),
        Spacer(1, 6 * mm),
        Paragraph("Movimientos recientes (últimos 10)", estilos["Heading2"]),
        tabla(
            ["Fecha", "Código", "Producto", "Tipo", "Cantidad", "Responsable", "Referencia"],
            datos["movimientos"],
            [44 * mm, 28 * mm, 58 * mm, 32 * mm, 24 * mm, 40 * mm, 30 * mm],
        ),
    ]
    documento.build(historia)
    buffer.seek(0)
    respuesta = HttpResponse(buffer.getvalue(), content_type="application/pdf")
    respuesta["Content-Disposition"] = 'attachment; filename="reporte-inventario-magnus-sig.pdf"'
    return respuesta


def _respuesta_reporte_excel(datos):
    from io import BytesIO

    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Font, PatternFill
    from openpyxl.utils import get_column_letter

    libro = Workbook()
    resumen = libro.active
    resumen.title = "Resumen"
    resumen.append(["Reporte de inventario · Magnus SIG"])
    resumen.append(["Generado", datos["generado"]])
    resumen.append([])
    resumen.append(["Indicador", "Valor"])
    for fila in datos["indicadores"]:
        resumen.append(fila)

    categorias = libro.create_sheet("Categorías")
    categorias.append(["Categoría", "Unidades", "Valor estimado (COP)"])
    for fila in datos["categorias"]:
        categorias.append(fila)

    movimientos = libro.create_sheet("Movimientos recientes")
    movimientos.append(["Fecha", "Código", "Producto", "Tipo", "Cantidad", "Responsable", "Referencia"])
    for fila in datos["movimientos_excel"]:
        movimientos.append(fila)

    encabezado = PatternFill("solid", fgColor="243B64")
    blanco_negrita = Font(color="FFFFFF", bold=True)
    for hoja in libro.worksheets:
        hoja.freeze_panes = "A2" if hoja.title != "Resumen" else "A5"
        for celda in (hoja[4] if hoja.title == "Resumen" else hoja[1]):
            celda.fill = encabezado
            celda.font = blanco_negrita
            celda.alignment = Alignment(vertical="center")
        if hoja.title == "Resumen" and hoja.max_row > 4:
            hoja.auto_filter.ref = f"A4:B{hoja.max_row}"
        elif hoja.title != "Resumen" and hoja.max_row > 1:
            hoja.auto_filter.ref = hoja.dimensions
        for columna in hoja.columns:
            ancho = min(
                max(len(str(celda.value or "")) for celda in columna) + 2,
                42,
            )
            hoja.column_dimensions[get_column_letter(columna[0].column)].width = max(ancho, 12)

    resumen["B7"].number_format = '"$"#,##0.00'
    for fila in categorias.iter_rows(min_row=2, min_col=3, max_col=3):
        fila[0].number_format = '"$"#,##0.00'
    buffer = BytesIO()
    libro.save(buffer)
    respuesta = HttpResponse(
        buffer.getvalue(),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    respuesta["Content-Disposition"] = 'attachment; filename="reporte-inventario-magnus-sig.xlsx"'
    return respuesta


def _respuesta_reporte_word(datos):
    from io import BytesIO

    from docx import Document
    from docx.enum.table import WD_TABLE_ALIGNMENT
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.shared import Inches, Pt, RGBColor

    documento = Document()
    seccion = documento.sections[0]
    seccion.top_margin = Inches(0.65)
    seccion.bottom_margin = Inches(0.65)
    seccion.left_margin = Inches(0.7)
    seccion.right_margin = Inches(0.7)

    titulo = documento.add_heading("Reporte de inventario", level=0)
    titulo.alignment = WD_ALIGN_PARAGRAPH.LEFT
    subtitulo = documento.add_paragraph(f"Magnus SIG · Generado: {datos['generado']}")
    subtitulo.style = "Subtitle"

    def tabla(titulos, filas):
        tabla_doc = documento.add_table(rows=1, cols=len(titulos))
        tabla_doc.style = "Table Grid"
        tabla_doc.alignment = WD_TABLE_ALIGNMENT.CENTER
        for celda, texto in zip(tabla_doc.rows[0].cells, titulos):
            celda.text = str(texto)
            for run in celda.paragraphs[0].runs:
                run.bold = True
                run.font.color.rgb = RGBColor(255, 255, 255)
                run.font.size = Pt(9)
            from docx.oxml import OxmlElement
            from docx.oxml.ns import qn
            sombreado = OxmlElement("w:shd")
            sombreado.set(qn("w:fill"), "243B64")
            celda._tc.get_or_add_tcPr().append(sombreado)
        for fila in filas:
            celdas = tabla_doc.add_row().cells
            for celda, valor in zip(celdas, fila):
                celda.text = str(valor)
                for parrafo in celda.paragraphs:
                    for run in parrafo.runs:
                        run.font.size = Pt(8)
        documento.add_paragraph()

    documento.add_heading("Resumen general", level=1)
    tabla(["Indicador", "Valor"], datos["indicadores"])
    documento.add_heading("Valor estimado por categoría (COP)", level=1)
    tabla(["Categoría", "Unidades", "Valor estimado (COP)"], datos["categorias"])
    documento.add_heading("Movimientos recientes (últimos 10)", level=1)
    tabla(
        ["Fecha", "Código", "Producto", "Tipo", "Cantidad", "Responsable", "Referencia"],
        datos["movimientos"],
    )

    buffer = BytesIO()
    documento.save(buffer)
    respuesta = HttpResponse(
        buffer.getvalue(),
        content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )
    respuesta["Content-Disposition"] = 'attachment; filename="reporte-inventario-magnus-sig.docx"'
    return respuesta


def _exportar_reporte(request, contexto, formato):
    categorias = list(contexto["categorias"])
    movimientos = list(contexto["movimientos_recientes"])
    generado = timezone.localtime().strftime("%d/%m/%Y %H:%M")

    indicadores = [
        ["Productos registrados", contexto["total_productos"]],
        ["Unidades disponibles", contexto["total_unidades"]],
        ["Valor estimado del inventario (COP)", contexto["valor_inventario"]],
        ["Movimientos registrados", contexto["total_movimientos"]],
        ["Disponibles", contexto["total_disponibles"]],
        ["Stock bajo", contexto["total_stock_bajo"]],
        ["Agotados", contexto["total_agotados"]],
    ]
    filas_categorias = [
        [categoria.nombre, int(categoria.unidades or 0), float(categoria.valor or 0)]
        for categoria in categorias
    ]
    filas_movimientos = []
    filas_movimientos_excel = []
    for movimiento in movimientos:
        fecha = timezone.localtime(movimiento.fecha_movimiento)
        fecha_texto = fecha.strftime("%d/%m/%Y %H:%M")
        responsable = movimiento.id_usuario.username if movimiento.id_usuario else "—"
        tipo = movimiento.get_tipo_movimiento_display()
        cantidad = movimiento.cantidad
        filas_movimientos.append([
            fecha_texto,
            movimiento.id_producto.codigo,
            movimiento.id_producto.nombre,
            tipo,
            cantidad,
            responsable,
            movimiento.referencia,
        ])
        filas_movimientos_excel.append([
            fecha.replace(tzinfo=None),
            movimiento.id_producto.codigo,
            movimiento.id_producto.nombre,
            tipo,
            float(cantidad),
            responsable,
            movimiento.referencia,
        ])

    datos = {
        "generado": generado,
        "indicadores": indicadores,
        "categorias": filas_categorias,
        "movimientos": filas_movimientos,
        "movimientos_excel": filas_movimientos_excel,
    }
    exportadores = {
        "pdf": _respuesta_reporte_pdf,
        "excel": _respuesta_reporte_excel,
        "word": _respuesta_reporte_word,
    }
    return exportadores[formato](datos)


@requiere_administrador
def reportes(request: HttpRequest) -> HttpResponse:
    stock_minimo = obtener_stock_minimo()
    total_productos = Producto.objects.count()
    resumen = Inventario.objects.aggregate(
        total_unidades=Sum("cantidad_actual"),
        valor=Sum(
            ExpressionWrapper(
                F("cantidad_actual") * F("id_producto__precio_venta"),
                output_field=DecimalField(max_digits=16, decimal_places=2),
            )
        ),
    )
    total_unidades = int(resumen["total_unidades"] or 0)
    valor_inventario = resumen["valor"] or Decimal("0.00")

    categorias = Categoria.objects.annotate(
        unidades=Sum("productos__inventario_rel__cantidad_actual"),
        valor=Sum(
            ExpressionWrapper(
                F("productos__inventario_rel__cantidad_actual") * F("productos__precio_venta"),
                output_field=DecimalField(max_digits=16, decimal_places=2),
            )
        ),
    ).order_by("-valor", "nombre")

    exportaciones_csv = {
        "productos": (
            "inventario-productos.csv",
            ["Código", "Producto", "Categoría", "Precio Venta COP", "Existencias", "Estado"],
            Producto.objects.select_related("id_categoria", "inventario_rel").order_by("nombre"),
            lambda p: [
                p.codigo,
                p.nombre,
                p.id_categoria.nombre,
                p.precio_venta,
                p.cantidad,
                p.estado_etiqueta,
            ],
        ),
        "movimientos": (
            "historial-movimientos.csv",
            ["Fecha", "Código", "Producto", "Tipo", "Cantidad", "Responsable", "Motivo"],
            MovimientoInventario.objects.select_related(
                "id_producto", "id_usuario"
            ).order_by("-fecha_movimiento"),
            lambda m: [
                m.fecha_movimiento,
                m.id_producto.codigo,
                m.id_producto.nombre,
                m.get_tipo_movimiento_display(),
                m.cantidad,
                m.id_usuario.username if m.id_usuario else "—",
                m.motivo,
            ],
        ),
    }
    exportacion = request.GET.get("export")
    if exportacion in exportaciones_csv:
        nombre, encabezados, registros, convertir = exportaciones_csv[exportacion]
        return exportar_csv(nombre, encabezados, (convertir(registro) for registro in registros))

    contexto = {
        "total_productos": total_productos,
        "total_unidades": total_unidades,
        "valor_inventario": valor_inventario,
        "total_categorias": Categoria.objects.count(),
        "total_agotados": Inventario.objects.filter(cantidad_actual__lte=0).count(),
        "total_stock_bajo": Inventario.objects.filter(
            cantidad_actual__gt=0, cantidad_actual__lte=F("id_producto__stock_minimo")
        ).count(),
        "total_disponibles": Inventario.objects.filter(
            cantidad_actual__gt=F("id_producto__stock_minimo")
        ).count(),
        "total_movimientos": MovimientoInventario.objects.count(),
        "entradas": Compra.objects.count(),
        "salidas": Venta.objects.count(),
        "servicios_count": Servicio.objects.count(),
        "movimientos_recientes": MovimientoInventario.objects.select_related(
            "id_producto", "id_usuario"
        )[:10],
        "categorias": categorias,
        "chart_data": [
            {"nombre": c.nombre, "valor": float(c.valor or 0)}
            for c in categorias
        ],
    }
    if exportacion in {"pdf", "excel", "word"}:
        return _exportar_reporte(request, contexto, exportacion)
    return render(request, "productos/reportes.html", contexto)


@requiere_administrador
def configuracion(request: HttpRequest) -> HttpResponse:
    config, _ = ConfiguracionInventario.objects.get_or_create(pk=1)
    form = ConfiguracionForm(request.POST or None, instance=config)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'La configuración se guardó correctamente en MySQL.')
        return redirect('productos:configuracion')
    return render(request, 'productos/configuracion.html', {'form': form})


@requiere_acceso_inventario
def buscar_producto(request: HttpRequest) -> HttpResponse:
    return lista_productos(request)
