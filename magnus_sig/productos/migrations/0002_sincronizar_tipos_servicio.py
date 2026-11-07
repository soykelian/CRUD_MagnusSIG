"""Sincroniza el catálogo compartido de tipos de servicio sin alterar filas existentes."""

from django.db import migrations


TIPOS_SERVICIO = (
    'Diagnóstico del SG-SST',
    'Diseño e implementación del SG-SST',
    'Mantenimiento y administración del SG-SST',
    'Capacitación en primeros auxilios',
    'Capacitación en control de incendios',
    'Diagnóstico e intervención del riesgo psicosocial',
    'Batería psicosocial',
    'PESV',
    'Auditoría ISO 9001',
    'Auditoría ISO 14001',
    'Auditoría ISO 45001',
    'Auditoría a proveedores',
    'Auditoría PESV',
    'Profesiogramas',
    'Análisis de puestos de trabajo',
    'Asesoría en implementación del SG-SST',
    'Auditorías internas del SG-SST',
    'Evaluación de riesgos laborales',
    'Gestión de exámenes médicos ocupacionales',
)


def sincronizar_tipos_servicio(apps, schema_editor):
    TipoServicio = apps.get_model('productos', 'TipoServicio')
    database = schema_editor.connection.alias

    for nombre in TIPOS_SERVICIO:
        TipoServicio.objects.using(database).get_or_create(
            nombre=nombre,
            defaults={
                'descripcion': None,
                'estado': 'activo',
            },
        )


def conservar_catalogo(apps, schema_editor):
    # No borrar filas al revertir: pueden estar referenciadas por servicios.
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('productos', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(
            sincronizar_tipos_servicio,
            reverse_code=conservar_catalogo,
        ),
    ]
