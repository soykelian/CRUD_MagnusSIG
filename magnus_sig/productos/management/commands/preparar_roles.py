from django.contrib.auth.models import Group
from django.contrib.auth.models import Permission
from django.core.management.base import BaseCommand

from productos.roles import GRUPO_ADMINISTRADOR, GRUPO_VENDEDOR


class Command(BaseCommand):
    help = 'Crea los grupos Administrador y Vendedor para el prototipo web.'

    def handle(self, *args, **options):
        administrador, creado = Group.objects.get_or_create(name=GRUPO_ADMINISTRADOR)
        administrador.permissions.set(Permission.objects.all())
        estado = 'creado' if creado else 'ya existía'
        self.stdout.write(f'Grupo {GRUPO_ADMINISTRADOR}: {estado}, con permisos completos.')

        _, creado = Group.objects.get_or_create(name=GRUPO_VENDEDOR)
        estado = 'creado' if creado else 'ya existía'
        self.stdout.write(f'Grupo {GRUPO_VENDEDOR}: {estado}, acceso de consulta.')
