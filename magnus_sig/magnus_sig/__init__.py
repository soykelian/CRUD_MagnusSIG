import pymysql

pymysql.install_as_MySQLdb()

# Django 6.1 incrementó el requisito mínimo oficial a MySQL 8.4+.
# Aplicamos compatibilidad para soportar la versión instalada (MySQL 8.0.46) de forma nativa.
try:
    from django.db.backends.mysql.features import DatabaseFeatures
    DatabaseFeatures.minimum_database_version = (8, 0)
except Exception:
    pass
