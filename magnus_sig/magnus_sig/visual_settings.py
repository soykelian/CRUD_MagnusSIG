from .settings import *
DATABASES['default']['NAME'] = BASE_DIR.parent / 'tmp' / 'visual-preview.sqlite3'
STATIC_URL = '/static/'
ALLOWED_HOSTS = ['testserver', '127.0.0.1', 'localhost']
