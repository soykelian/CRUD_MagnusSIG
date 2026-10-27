"""Rutas de la app de inventario."""

from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

app_name = 'productos'

urlpatterns = [
    path(
        'login/',
        auth_views.LoginView.as_view(
            template_name='productos/login.html',
            redirect_authenticated_user=True,
        ),
        name='login',
    ),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('productos/', views.catalogo_productos, name='catalogo'),
    path('movimientos/', views.movimientos, name='movimientos'),
    path('movimientos/nuevo/', views.crear_movimiento, name='movimiento_nuevo'),
    path('entradas/', views.entradas, name='entradas'),
    path('entradas/nueva/', views.crear_entrada, name='entrada_nueva'),
    path('entradas/<int:pk>/recibir/', views.recibir_entrada, name='entrada_recibir'),
    path('salidas/', views.salidas, name='salidas'),
    path('salidas/nueva/', views.crear_salida, name='salida_nueva'),
    path('salidas/<int:pk>/despachar/', views.despachar_salida, name='salida_despachar'),
    path('proveedores/', views.proveedores, name='proveedores'),
    path('proveedores/nuevo/', views.crear_proveedor, name='proveedor_nuevo'),
    path('clientes/', views.clientes, name='clientes'),
    path('clientes/nuevo/', views.crear_cliente, name='cliente_nuevo'),
    path('servicios/', views.servicios, name='servicios'),
    path('servicios/nuevo/', views.crear_servicio, name='servicio_nuevo'),
    path('reportes/', views.reportes, name='reportes'),
    path('configuracion/', views.configuracion, name='configuracion'),
    path('', views.lista_productos, name='lista'),
    path('buscar/', views.buscar_producto, name='buscar'),
    path('productos/nuevo/', views.crear_producto, name='crear'),
    path('productos/<int:pk>/', views.detalle_producto, name='detalle'),
    path('productos/<int:pk>/editar/', views.editar_producto, name='editar'),
    path('productos/<int:pk>/eliminar/', views.eliminar_producto, name='eliminar'),
    path('categorias/', views.lista_categorias, name='categorias'),
    path('categorias/nueva/', views.crear_categoria, name='categoria_crear'),
    path('categorias/<int:pk>/editar/', views.editar_categoria, name='categoria_editar'),
    path('categorias/<int:pk>/eliminar/', views.eliminar_categoria, name='categoria_eliminar'),
]
