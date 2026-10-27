"""Reglas de acceso para los perfiles del inventario."""

from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

GRUPO_ADMINISTRADOR = 'Administrador'
GRUPO_VENDEDOR = 'Vendedor'


def es_administrador(user):
    return user.is_authenticated and (
        user.is_superuser or user.groups.filter(name=GRUPO_ADMINISTRADOR).exists()
    )


def es_vendedor(user):
    return user.is_authenticated and user.groups.filter(name=GRUPO_VENDEDOR).exists()


def requiere_acceso_inventario(view):
    """Permite entrar solo a usuarios autenticados con uno de los dos roles."""
    @login_required
    @wraps(view)
    def wrapped(request, *args, **kwargs):
        if not (es_administrador(request.user) or es_vendedor(request.user)):
            raise PermissionDenied
        return view(request, *args, **kwargs)

    return wrapped


def requiere_administrador(view):
    """Restringe operaciones que modifican el inventario al administrador."""
    @login_required
    @wraps(view)
    def wrapped(request, *args, **kwargs):
        if not es_administrador(request.user):
            raise PermissionDenied
        return view(request, *args, **kwargs)

    return wrapped
