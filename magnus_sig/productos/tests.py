from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse

from .models import (
    Categoria,
    Cliente,
    Compra,
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
    sincronizar_usuario_bd,
)


class CrudProductosTests(TestCase):
    def setUp(self):
        usuario = get_user_model().objects.create_superuser(
            username='admin_pruebas', email='admin@example.test', password='Pruebas-123!'
        )
        sincronizar_usuario_bd(usuario)
        self.client.force_login(usuario)
        self.cat = Categoria.objects.create(nombre='Periféricos', descripcion='Teclados y ratones')

    def _producto(self, **kw):
        datos = dict(
            codigo=kw.pop('codigo', f'PRD-{Producto.objects.count() + 1:04d}'),
            nombre=kw.pop('nombre', 'Teclado USB'),
            id_categoria=kw.pop('categoria', self.cat),
            precio_compra=kw.pop('precio_compra', Decimal('25000')),
            precio_venta=kw.pop('precio', Decimal('45000')),
            stock_minimo=Decimal('5'),
            unidad_medida='Unidad',
        )
        cantidad = kw.pop('cantidad', 20)
        datos.update(kw)
        p = Producto.objects.create(**datos)
        p.cantidad = cantidad
        return p

    def test_paginas_responden(self):
        p = self._producto()
        for nombre, args in [
            ('lista', []),
            ('crear', []),
            ('categorias', []),
            ('categoria_crear', []),
            ('detalle', [p.pk]),
            ('editar', [p.pk]),
            ('eliminar', [p.pk]),
        ]:
            with self.subTest(nombre):
                self.assertEqual(
                    self.client.get(reverse(f'productos:{nombre}', args=args)).status_code, 200
                )

    def test_crear_producto(self):
        r = self.client.post(
            reverse('productos:crear'),
            {
                'codigo': 'MS-001',
                'nombre': 'Mouse Ergonómico',
                'descripcion': '',
                'id_categoria': self.cat.pk,
                'precio_compra': '15000',
                'precio_venta': '25000.50',
                'unidad_medida': 'Unidad',
                'cantidad': '3',
                'stock_minimo': '5',
                'ubicacion': 'Bodega A',
            },
        )
        self.assertRedirects(r, reverse('productos:lista'))
        p = Producto.objects.get(codigo='MS-001')
        self.assertEqual(p.precio_venta, Decimal('25000.50'))
        self.assertEqual(p.cantidad, 3)

    def test_validaciones(self):
        r = self.client.post(
            reverse('productos:crear'),
            {
                'codigo': '',
                'nombre': '  ',
                'id_categoria': self.cat.pk,
                'precio_venta': '-5',
                'precio_compra': '0',
                'unidad_medida': 'Unidad',
                'cantidad': '0',
                'stock_minimo': '5',
            },
        )
        self.assertEqual(r.status_code, 200)
        self.assertEqual(Producto.objects.count(), 0)

    def test_editar_precarga_y_guarda(self):
        p = self._producto(codigo='TEC-001', nombre='Teclado USB', precio=Decimal('45000'), cantidad=20)
        r = self.client.get(reverse('productos:editar', args=[p.pk]))
        self.assertContains(r, 'value="Teclado USB"')
        self.assertContains(r, 'value="45000.00"')

        r = self.client.post(
            reverse('productos:editar', args=[p.pk]),
            {
                'codigo': 'TEC-001',
                'nombre': 'Teclado Pro',
                'descripcion': 'x',
                'id_categoria': self.cat.pk,
                'precio_compra': '30000',
                'precio_venta': '50000',
                'unidad_medida': 'Unidad',
                'cantidad': '7',
                'stock_minimo': '5',
                'ubicacion': 'Bodega B',
            },
        )
        self.assertRedirects(r, reverse('productos:detalle', args=[p.pk]))
        p.refresh_from_db()
        self.assertEqual((p.nombre, p.cantidad), ('Teclado Pro', 7))

    def test_eliminar_producto_por_post(self):
        p = self._producto()
        self.assertEqual(self.client.get(reverse('productos:eliminar', args=[p.pk])).status_code, 200)
        self.assertEqual(Producto.objects.count(), 1)
        self.client.post(reverse('productos:eliminar', args=[p.pk]))
        self.assertEqual(Producto.objects.count(), 0)

    def test_producto_inexistente_404(self):
        self.assertEqual(self.client.get(reverse('productos:detalle', args=[999])).status_code, 404)

    def test_busqueda_filtros_y_paginacion(self):
        for i in range(10):
            self._producto(codigo=f'ITM-{i}', nombre=f'Item {i}', cantidad=0 if i == 0 else 3 if i == 1 else 50)
        r = self.client.get(reverse('productos:lista'))
        self.assertEqual(len(r.context['pagina']), 8)
        self.assertEqual(r.context['total_productos'], 10)
        self.assertEqual(len(self.client.get(reverse('productos:lista') + '?page=2').context['pagina']), 2)
        self.assertEqual(len(self.client.get(reverse('productos:buscar') + '?q=Item 3').context['pagina']), 1)
        self.assertEqual(len(self.client.get(reverse('productos:lista') + '?existencias=out').context['pagina']), 1)
        self.assertEqual(len(self.client.get(reverse('productos:lista') + '?existencias=low').context['pagina']), 1)
        self.assertEqual(len(self.client.get(reverse('productos:lista') + f'?categoria={self.cat.pk}').context['pagina']), 8)

    def test_sin_categorias_redirige(self):
        Categoria.objects.all().delete()
        self.assertRedirects(self.client.get(reverse('productos:crear')), reverse('productos:categoria_crear'))


class CrudCategoriasTests(TestCase):
    def setUp(self):
        usuario = get_user_model().objects.create_superuser(
            username='admin_pruebas', email='admin@example.test', password='Pruebas-123!'
        )
        sincronizar_usuario_bd(usuario)
        self.client.force_login(usuario)

    def test_crear_y_nombre_repetido(self):
        self.client.post(reverse('productos:categoria_crear'), {'nombre': 'Audio', 'descripcion': '', 'estado': 'activo'})
        r = self.client.post(reverse('productos:categoria_crear'), {'nombre': 'audio', 'descripcion': '', 'estado': 'activo'})
        self.assertContains(r, 'Ya existe una categoría con ese nombre.')
        self.assertEqual(Categoria.objects.count(), 1)

    def test_editar(self):
        c = Categoria.objects.create(nombre='Audio')
        self.client.post(reverse('productos:categoria_editar', args=[c.pk]), {'nombre': 'Sonido', 'descripcion': 'd', 'estado': 'activo'})
        c.refresh_from_db()
        self.assertEqual(c.nombre, 'Sonido')

    def test_no_elimina_con_productos(self):
        c = Categoria.objects.create(nombre='Audio')
        Producto.objects.create(codigo='P1', nombre='P', id_categoria=c, precio_compra=1, precio_venta=1, unidad_medida='Unidad')
        self.client.post(reverse('productos:categoria_eliminar', args=[c.pk]))
        self.assertTrue(Categoria.objects.filter(pk=c.pk).exists())

    def test_elimina_vacia_solo_por_post(self):
        c = Categoria.objects.create(nombre='Audio')
        self.assertEqual(self.client.get(reverse('productos:categoria_eliminar', args=[c.pk])).status_code, 405)
        self.client.post(reverse('productos:categoria_eliminar', args=[c.pk]))
        self.assertFalse(Categoria.objects.exists())

    def test_busqueda_y_orden(self):
        for n in ('Beta', 'Alfa'):
            Categoria.objects.create(nombre=n)
        r = self.client.get(reverse('productos:categorias') + '?orden=desc')
        self.assertEqual([c.nombre for c in r.context['categorias']], ['Beta', 'Alfa'])
        r = self.client.get(reverse('productos:categorias') + '?q=alf')
        self.assertEqual(len(r.context['categorias']), 1)


class PersistenciaOperacionesTests(TestCase):
    def setUp(self):
        self.admin = get_user_model().objects.create_superuser(
            username='admin_operaciones', email='operaciones@example.test', password='Pruebas-123!'
        )
        sincronizar_usuario_bd(self.admin)
        self.client.force_login(self.admin)
        self.categoria = Categoria.objects.create(nombre='Equipos')
        self.producto = Producto.objects.create(
            codigo='EQ-MON-01',
            nombre='Monitor',
            id_categoria=self.categoria,
            precio_compra=Decimal('300000'),
            precio_venta=Decimal('550000'),
            stock_minimo=Decimal('5'),
            unidad_medida='Unidad',
        )
        self.producto.cantidad = 10

    def test_entrada_pendiente_se_guarda_y_al_recibir_suma_stock(self):
        proveedor = Proveedor.objects.create(nit='900111222', razon_social='Proveedor Uno', estado='activo')
        response = self.client.post(
            reverse('productos:entrada_nueva'),
            {
                'proveedor': proveedor.pk,
                'producto': self.producto.pk,
                'cantidad': 4,
                'costo_unitario': '300000',
                'numero_factura': 'FAC-001',
            },
        )
        self.assertRedirects(response, reverse('productos:entradas'))
        entrada = Compra.objects.get()
        self.assertEqual(entrada.estado, 'borrador')
        self.assertEqual(self.producto.cantidad, 10)

        self.client.post(reverse('productos:entrada_recibir', args=[entrada.pk]))
        entrada.refresh_from_db()
        self.assertEqual(entrada.estado, 'recibida')
        self.assertEqual(self.producto.cantidad, 14)
        self.assertEqual(MovimientoInventario.objects.get().cantidad, Decimal('4'))

    def test_salida_se_guarda_y_solo_descuenta_al_despachar(self):
        cliente = Cliente.objects.create(
            tipo_documento='NIT', numero_documento='800111222', razon_social='Cliente Uno', estado='activo'
        )
        response = self.client.post(
            reverse('productos:salida_nueva'),
            {
                'cliente': cliente.pk,
                'producto': self.producto.pk,
                'cantidad': 3,
                'precio_unitario': '550000',
            },
        )
        self.assertRedirects(response, reverse('productos:salidas'))
        salida = Venta.objects.get()
        self.assertEqual(salida.estado, 'borrador')
        self.assertEqual(self.producto.cantidad, 10)

        self.client.post(reverse('productos:salida_despachar', args=[salida.pk]))
        salida.refresh_from_db()
        self.assertEqual(salida.estado, 'confirmada')
        self.assertEqual(self.producto.cantidad, 7)
        self.assertEqual(MovimientoInventario.objects.get().cantidad, Decimal('3'))

    def test_no_se_puede_registrar_salida_mayor_al_stock(self):
        cliente = Cliente.objects.create(
            tipo_documento='NIT', numero_documento='800333444', razon_social='Cliente Dos', estado='activo'
        )
        response = self.client.post(
            reverse('productos:salida_nueva'),
            {
                'cliente': cliente.pk,
                'producto': self.producto.pk,
                'cantidad': 11,
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Existencias insuficientes')
        self.assertFalse(Venta.objects.exists())

    def test_movimiento_entrada_persiste_y_actualiza_existencias(self):
        response = self.client.post(
            reverse('productos:movimiento_nuevo'),
            {
                'producto': self.producto.pk,
                'tipo': 'entrada',
                'cantidad': 2,
                'motivo': 'Reposición',
            },
        )
        self.assertRedirects(response, reverse('productos:movimientos'))
        self.assertEqual(self.producto.cantidad, 12)
        self.assertEqual(MovimientoInventario.objects.get().motivo, 'Reposición')

    def test_modulo_servicios_responde_y_guarda(self):
        cliente = Cliente.objects.create(
            tipo_documento='NIT', numero_documento='900999888', razon_social='Constructora Bolivar', estado='activo'
        )
        tipo_srv = TipoServicio.objects.create(nombre='Auditoría ISO 45001')
        r = self.client.get(reverse('productos:servicios'))
        self.assertEqual(r.status_code, 200)

        r_post = self.client.post(
            reverse('productos:servicio_nuevo'),
            {
                'id_cliente': cliente.pk,
                'id_tipo_servicio': tipo_srv.pk,
                'valor': '2500000',
                'estado': 'pendiente',
                'observaciones': 'Auditoría inicial en obra principal',
            },
        )
        self.assertRedirects(r_post, reverse('productos:servicios'))
        self.assertEqual(Servicio.objects.count(), 1)
        srv = Servicio.objects.get()
        self.assertEqual(srv.id_cliente, cliente)
        self.assertEqual(srv.valor, Decimal('2500000'))

    def test_nuevas_paginas_menu_responden_con_datos_reales(self):
        for nombre in (
            'dashboard',
            'catalogo',
            'lista',
            'categorias',
            'movimientos',
            'entradas',
            'salidas',
            'proveedores',
            'clientes',
            'servicios',
            'reportes',
            'configuracion',
        ):
            with self.subTest(pagina=nombre):
                self.assertEqual(self.client.get(reverse(f'productos:{nombre}')).status_code, 200)

    def test_vendedor_ve_sus_secciones_y_no_puede_administrar_catalogos(self):
        vendedor = get_user_model().objects.create_user(username='vendedor', password='Pruebas-123!')
        vendedor.groups.add(Group.objects.create(name='Vendedor'))
        sincronizar_usuario_bd(vendedor)
        self.client.force_login(vendedor)
        self.assertEqual(self.client.get(reverse('productos:dashboard')).status_code, 200)
        self.assertEqual(self.client.get(reverse('productos:salidas')).status_code, 200)
        self.assertEqual(self.client.get(reverse('productos:clientes')).status_code, 200)
        self.assertEqual(self.client.get(reverse('productos:servicios')).status_code, 200)
        self.assertEqual(self.client.get(reverse('productos:entradas')).status_code, 403)
        self.assertEqual(self.client.get(reverse('productos:proveedores')).status_code, 403)
        self.assertEqual(self.client.get(reverse('productos:configuracion')).status_code, 403)
