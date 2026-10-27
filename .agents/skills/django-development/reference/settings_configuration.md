# Settings Configuration Reference

This reference provides comprehensive guidance for Django settings configuration.

## Table of Contents

- [Settings Fundamentals](#settings-fundamentals)
- [Core Settings](#core-settings)
- [Database Configuration](#database-configuration)
- [Static and Media Files](#static-and-media-files)
- [Middleware](#middleware)
- [Templates](#templates)
- [Internationalization](#internationalization)
- [Email Configuration](#email-configuration)
- [Caching](#caching)
- [Environment-Specific Settings](#environment-specific-settings)

---

## Settings Fundamentals

Django settings control all aspects of your application configuration. Settings are defined in `settings.py`.

### Basic Settings Structure

```python
# settings.py
from pathlib import Path
import os

# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent.parent

# Security settings
SECRET_KEY = 'your-secret-key-here'
DEBUG = True
ALLOWED_HOSTS = []

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Your apps
    'myapp',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'myproject.urls'

WSGI_APPLICATION = 'myproject.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = 'static/'
```

---

## Core Settings

### DEBUG Mode

```python
# Development
DEBUG = True

# Production
DEBUG = False

# Environment-based
import os
DEBUG = os.environ.get('DJANGO_DEBUG', 'False') == 'True'
```

**Important**: Never enable DEBUG in production. It exposes sensitive information.

### SECRET_KEY

**CRITICAL**: SECRET_KEY must be at least 50 characters long using strong randomization.

```python
# Bad: Hardcoded secret key
SECRET_KEY = 'django-insecure-hardcoded-key'

# Good: Load from environment (ensure 50+ characters)
import os
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')

if not SECRET_KEY or len(SECRET_KEY) < 50:
    raise ValueError('SECRET_KEY must be set and at least 50 characters long')

# Better: Use python-dotenv
# First: pip install python-dotenv
from dotenv import load_dotenv
load_dotenv()  # Load .env file

SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY or len(SECRET_KEY) < 50:
    raise ValueError('SECRET_KEY must be set in .env and at least 50 characters long')

# Generate new secret key (always 50+ characters)
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

### ALLOWED_HOSTS

```python
# Development
ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# Production
ALLOWED_HOSTS = ['example.com', 'www.example.com']

# Environment-based (using python-dotenv)
from dotenv import load_dotenv
load_dotenv()

ALLOWED_HOSTS_STR = os.environ.get('ALLOWED_HOSTS', '')
ALLOWED_HOSTS = [host.strip() for host in ALLOWED_HOSTS_STR.split(',') if host.strip()]

# In .env file:
# ALLOWED_HOSTS=example.com,www.example.com
```

### INSTALLED_APPS

```python
INSTALLED_APPS = [
    # Django built-in apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party apps
    'rest_framework',
    'crispy_forms',
    'django_filters',

    # Your apps (put last)
    'blog.apps.BlogConfig',  # Explicit AppConfig
    'accounts',
    'api',
]
```

**Best practice**: List Django apps first, third-party apps second, your apps last.

### MIDDLEWARE

```python
MIDDLEWARE = [
    # Security middleware (should be first)
    'django.middleware.security.SecurityMiddleware',

    # Session middleware
    'django.contrib.sessions.middleware.SessionMiddleware',

    # Common middleware
    'django.middleware.common.CommonMiddleware',

    # CSRF middleware
    'django.middleware.csrf.CsrfViewMiddleware',

    # Authentication middleware
    'django.contrib.auth.middleware.AuthenticationMiddleware',

    # Messages middleware
    'django.contrib.messages.middleware.MessageMiddleware',

    # Clickjacking middleware
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    # Custom middleware
    'myapp.middleware.CustomMiddleware',
]
```

**Order matters**: Middleware processes requests top-to-bottom and responses bottom-to-top.

### ROOT_URLCONF

```python
# Points to main URL configuration
ROOT_URLCONF = 'myproject.urls'
```

---

## Database Configuration

### SQLite (Development)

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

### PostgreSQL (Recommended for Production)

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'mydb',
        'USER': 'myuser',
        'PASSWORD': 'mypassword',
        'HOST': 'localhost',
        'PORT': '5432',
        'CONN_MAX_AGE': 600,  # Persistent connections
        'OPTIONS': {
            'options': '-c search_path=public',
        }
    }
}

# Environment-based
import os
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}

# Using dj-database-url
import dj_database_url
DATABASES = {
    'default': dj_database_url.config(
        default='postgresql://user:password@localhost/dbname',
        conn_max_age=600
    )
}
```

### MySQL

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'mydb',
        'USER': 'myuser',
        'PASSWORD': 'mypassword',
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            'charset': 'utf8mb4',
        }
    }
}
```

### Multiple Databases

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'primary_db',
        # ...
    },
    'users_db': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'users_db',
        # ...
    },
    'analytics': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'analytics_db',
        # ...
    }
}

# Database router
class DatabaseRouter:
    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'users':
            return 'users_db'
        return 'default'

    def db_for_write(self, model, **hints):
        if model._meta.app_label == 'users':
            return 'users_db'
        return 'default'

DATABASE_ROUTERS = ['myproject.routers.DatabaseRouter']
```

---

## Static and Media Files

### Static Files Configuration

```python
# URL prefix for static files
STATIC_URL = '/static/'

# Directory where collectstatic will collect files
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Additional locations of static files
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Static file finders
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]
```

### Media Files Configuration

```python
# URL prefix for media files
MEDIA_URL = '/media/'

# Directory where uploaded files are stored
MEDIA_ROOT = BASE_DIR / 'media'
```

### URLs Configuration for Media

```python
# urls.py (development only)
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Your URL patterns
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
```

### Production Static Files

```python
# Use WhiteNoise for serving static files
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Add after SecurityMiddleware
    # ...
]

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

---

## Middleware

### Common Middleware Settings

```python
# Security Middleware
SECURE_SSL_REDIRECT = True  # Redirect HTTP to HTTPS
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Session Middleware
SESSION_ENGINE = 'django.contrib.sessions.backends.db'  # Database-backed sessions
SESSION_COOKIE_AGE = 1209600  # 2 weeks in seconds
SESSION_COOKIE_SECURE = True  # Only send over HTTPS
SESSION_COOKIE_HTTPONLY = True  # Prevent JavaScript access
SESSION_COOKIE_SAMESITE = 'Lax'

# CSRF Middleware
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = False  # Must be False for AJAX
CSRF_COOKIE_SAMESITE = 'Lax'
CSRF_TRUSTED_ORIGINS = ['https://example.com']

# Common Middleware
APPEND_SLASH = True  # Append trailing slash to URLs
PREPEND_WWW = False  # Don't prepend www

# Clickjacking Protection
X_FRAME_OPTIONS = 'DENY'  # Or 'SAMEORIGIN'

# Content Type Nosniff
SECURE_CONTENT_TYPE_NOSNIFF = True

# Browser XSS Filter
SECURE_BROWSER_XSS_FILTER = True
```

---

## Templates

### Template Configuration

```python
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'templates',  # Project-level templates
        ],
        'APP_DIRS': True,  # Look for templates in app directories
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                # Custom context processors
                'myapp.context_processors.custom_context',
            ],
        },
    },
]
```

### Custom Context Processor

```python
# myapp/context_processors.py
def custom_context(request):
    """Add custom variables to all templates."""
    return {
        'site_name': 'My Site',
        'current_year': timezone.now().year,
    }
```

---

## Internationalization

### Basic i18n Configuration

```python
# Enable internationalization
USE_I18N = True

# Enable localization (date/time/number formatting)
USE_L10N = True  # Deprecated in Django 4.0

# Enable timezone support
USE_TZ = True

# Default language
LANGUAGE_CODE = 'en-us'

# Available languages
LANGUAGES = [
    ('en', 'English'),
    ('es', 'Spanish'),
    ('fr', 'French'),
]

# Locale paths for translation files
LOCALE_PATHS = [
    BASE_DIR / 'locale',
]

# Timezone
TIME_ZONE = 'UTC'  # Or 'America/New_York', 'Europe/London', etc.
```

### Date and Time Formatting

```python
# Date format
DATE_FORMAT = 'Y-m-d'
DATETIME_FORMAT = 'Y-m-d H:i:s'
TIME_FORMAT = 'H:i:s'

# Short date format
SHORT_DATE_FORMAT = 'm/d/Y'
SHORT_DATETIME_FORMAT = 'm/d/Y H:i'

# First day of week (0=Sunday, 1=Monday)
FIRST_DAY_OF_WEEK = 1
```

---

## Email Configuration

### Development Email Backend

```python
# Console backend (prints to console)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# File backend (saves to file)
EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
EMAIL_FILE_PATH = BASE_DIR / 'emails'
```

### SMTP Configuration

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-password'
DEFAULT_FROM_EMAIL = 'noreply@example.com'
SERVER_EMAIL = 'server@example.com'

# Timeout
EMAIL_TIMEOUT = 30

# Environment-based
import os
EMAIL_HOST = os.environ.get('EMAIL_HOST')
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
```

### Third-Party Email Services

```python
# SendGrid
EMAIL_BACKEND = 'sendgrid_backend.SendgridBackend'
SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY')

# Amazon SES
EMAIL_BACKEND = 'django_ses.SESBackend'
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_SES_REGION_NAME = 'us-east-1'
```

---

## Caching

### Development (Dummy Cache)

```python
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}
```

### Local Memory Cache

```python
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
        'TIMEOUT': 300,  # 5 minutes
        'OPTIONS': {
            'MAX_ENTRIES': 1000
        }
    }
}
```

### File-Based Cache

```python
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': '/var/tmp/django_cache',
        'TIMEOUT': 300,
        'OPTIONS': {
            'MAX_ENTRIES': 1000
        }
    }
}
```

### Redis Cache (Recommended for Production)

```python
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
        'KEY_PREFIX': 'myapp',
        'TIMEOUT': 300,
    }
}

# Multiple Redis databases
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    },
    'sessions': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/2',
    },
}

# Use Redis for sessions
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'sessions'
```

### Memcached

```python
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.PyMemcacheCache',
        'LOCATION': '127.0.0.1:11211',
    }
}
```

---

## Environment-Specific Settings

### Settings Organization

```
myproject/
├── settings/
│   ├── __init__.py
│   ├── base.py          # Base settings
│   ├── development.py   # Development settings
│   ├── production.py    # Production settings
│   └── testing.py       # Test settings
```

### Base Settings

```python
# settings/base.py
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    # ...
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # ...
]

ROOT_URLCONF = 'myproject.urls'

# Common settings...
```

### Development Settings

```python
# settings/development.py
from .base import *

DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Django Debug Toolbar
INSTALLED_APPS += ['debug_toolbar']
MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
INTERNAL_IPS = ['127.0.0.1']
```

### Production Settings

```python
# settings/production.py
from .base import *
import os

DEBUG = False

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST'),
        'PORT': '5432',
        'CONN_MAX_AGE': 600,
    }
}

# Security settings
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000

# Static files
STATIC_ROOT = '/var/www/example.com/static/'
MEDIA_ROOT = '/var/www/example.com/media/'

# Logging
LOGGING = {
    # Logging configuration
}
```

### Testing Settings

```python
# settings/testing.py
from .base import *

DEBUG = False

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',  # Fast for tests
]

EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
```

### Activating Settings

```python
# manage.py
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings.development')

# Or set environment variable
export DJANGO_SETTINGS_MODULE=myproject.settings.production

# Or command line
python manage.py runserver --settings=myproject.settings.development
```

---

## Authentication Settings

### Password Validation

```python
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 12,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]
```

### Authentication Backends

```python
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    # Custom backends
    'myapp.auth_backends.EmailBackend',
]
```

### Custom User Model

```python
# Use custom user model
AUTH_USER_MODEL = 'accounts.CustomUser'

# Login/logout redirects
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/'
```

---

## Logging Configuration

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'django.log',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
            'propagate': False,
        },
        'myapp': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}
```

---

## Best Practices

### Environment Variables

Use python-dotenv to load environment variables from a .env file:

```bash
# Install python-dotenv
pip install python-dotenv
```

```python
# settings.py
import os
from pathlib import Path
from dotenv import load_dotenv

# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env file
load_dotenv(BASE_DIR / '.env')

# Secret key
SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY or len(SECRET_KEY) < 50:
    raise ValueError('SECRET_KEY must be set in .env and at least 50 characters long')

# Debug mode
DEBUG_STR = os.environ.get('DEBUG', 'False')
DEBUG = DEBUG_STR.lower() in ('true', '1', 'yes')

# Allowed hosts
ALLOWED_HOSTS_STR = os.environ.get('ALLOWED_HOSTS', '')
ALLOWED_HOSTS = [host.strip() for host in ALLOWED_HOSTS_STR.split(',') if host.strip()]

# Database (if using DATABASE_URL)
DATABASE_URL = os.environ.get('DATABASE_URL')
```

```bash
# .env file (add to .gitignore!)
SECRET_KEY=your-50-plus-character-secret-key-here-generated-securely
DEBUG=False
ALLOWED_HOSTS=example.com,www.example.com
DATABASE_URL=postgresql://user:password@localhost/dbname
```

**Important**: Always add .env to .gitignore to prevent committing secrets:

```bash
# .gitignore
.env
*.env
```

### Settings Checklist

- [ ] `SECRET_KEY` from environment variable
- [ ] `DEBUG = False` in production
- [ ] `ALLOWED_HOSTS` configured
- [ ] Database settings secure
- [ ] Static/media files configured
- [ ] Security middleware enabled
- [ ] HTTPS settings configured
- [ ] Logging configured
- [ ] Email configured
- [ ] Caching configured (if needed)
- [ ] Timezone set correctly
- [ ] Authentication settings configured
