from django.db.utils import OperationalError, ProgrammingError

from .models import ConfiguracionInventario
from .roles import es_administrador, es_vendedor


def roles_inventario(request):
    user = request.user
    administrador = es_administrador(user)
    vendedor = es_vendedor(user)
    try:
        organizacion = ConfiguracionInventario.objects.filter(pk=1).values_list('nombre_organizacion', flat=True).first() or 'Magnus SIG'
    except (OperationalError, ProgrammingError):
        organizacion = 'Magnus SIG'
    return {
        'es_administrador': administrador,
        'organizacion_inventario': organizacion,
        'rol_inventario': (
            'Administrador' if administrador else 'Vendedor' if vendedor else ''
        ),
    }
