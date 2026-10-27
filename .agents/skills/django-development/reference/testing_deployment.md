# Testing and Deployment Reference

This reference provides comprehensive guidance for testing Django applications and deploying to production.

## Table of Contents

- [Testing Fundamentals](#testing-fundamentals)
- [Unit Tests](#unit-tests)
- [Model Testing](#model-testing)
- [View Testing](#view-testing)
- [Form Testing](#form-testing)
- [Test Coverage](#test-coverage)
- [Deployment Preparation](#deployment-preparation)
- [Production Configuration](#production-configuration)
- [Monitoring and Maintenance](#monitoring-and-maintenance)

---

## Testing Fundamentals

Django provides a comprehensive testing framework built on Python's unittest.

### Test Structure

```python
# tests.py
from django.test import TestCase
from django.contrib.auth.models import User
from .models import Article

class ArticleModelTest(TestCase):
    """Test Article model."""

    @classmethod
    def setUpTestData(cls):
        """Set up data for the whole TestCase."""
        cls.user = User.objects.create_user(username='testuser', password='12345')
        cls.article = Article.objects.create(
            title='Test Article',
            content='Test content',
            author=cls.user
        )

    def setUp(self):
        """Set up for each test method."""
        # Runs before each test method
        pass

    def test_article_creation(self):
        """Test article was created correctly."""
        self.assertEqual(self.article.title, 'Test Article')
        self.assertEqual(self.article.author, self.user)

    def test_article_str(self):
        """Test __str__ method."""
        self.assertEqual(str(self.article), 'Test Article')

    def tearDown(self):
        """Clean up after each test method."""
        # Runs after each test method
        pass
```

### Running Tests

```bash
# Run all tests
python manage.py test

# Run tests for specific app
python manage.py test blog

# Run specific test case
python manage.py test blog.tests.ArticleModelTest

# Run specific test method
python manage.py test blog.tests.ArticleModelTest.test_article_creation

# Run with verbosity
python manage.py test --verbosity=2

# Keep test database
python manage.py test --keepdb

# Run tests in parallel
python manage.py test --parallel
```

### Test Types

**TestCase**: Most common, uses database transactions
```python
from django.test import TestCase

class MyTest(TestCase):
    """Full-featured test with database access."""
    pass
```

**TransactionTestCase**: For testing database transactions
```python
from django.test import TransactionTestCase

class MyTransactionTest(TransactionTestCase):
    """Test database transactions and constraints."""
    pass
```

**SimpleTestCase**: For tests that don't need database
```python
from django.test import SimpleTestCase

class SimpleTest(SimpleTestCase):
    """Fast tests without database access."""
    pass
```

**LiveServerTestCase**: Runs live server for Selenium tests
```python
from django.test import LiveServerTestCase

class SeleniumTest(LiveServerTestCase):
    """Integration tests with Selenium."""
    pass
```

---

## Unit Tests

### Testing Utility Functions

```python
# utils.py
def slugify_title(title):
    """Convert title to URL-friendly slug."""
    from django.utils.text import slugify
    return slugify(title)

def calculate_reading_time(content):
    """Calculate reading time in minutes."""
    word_count = len(content.split())
    return max(1, word_count // 200)

# tests.py
from django.test import SimpleTestCase
from .utils import slugify_title, calculate_reading_time

class UtilityTest(SimpleTestCase):
    """Test utility functions."""

    def test_slugify_title(self):
        """Test title slugification."""
        result = slugify_title('Hello World!')
        self.assertEqual(result, 'hello-world')

    def test_reading_time_short(self):
        """Test reading time for short content."""
        content = ' '.join(['word'] * 100)
        self.assertEqual(calculate_reading_time(content), 1)

    def test_reading_time_long(self):
        """Test reading time for long content."""
        content = ' '.join(['word'] * 600)
        self.assertEqual(calculate_reading_time(content), 3)
```

---

## Model Testing

### Basic Model Tests

```python
from django.test import TestCase
from django.core.exceptions import ValidationError
from .models import Article, Category

class ArticleModelTest(TestCase):
    """Test Article model."""

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='testuser')
        cls.category = Category.objects.create(name='Tech')

    def test_article_creation(self):
        """Test creating an article."""
        article = Article.objects.create(
            title='Test Article',
            content='Test content',
            author=self.user,
            category=self.category
        )
        self.assertEqual(Article.objects.count(), 1)
        self.assertEqual(article.title, 'Test Article')

    def test_article_str(self):
        """Test string representation."""
        article = Article.objects.create(
            title='My Article',
            author=self.user
        )
        self.assertEqual(str(article), 'My Article')

    def test_get_absolute_url(self):
        """Test get_absolute_url method."""
        article = Article.objects.create(
            title='Test',
            slug='test',
            author=self.user
        )
        expected_url = f'/articles/{article.slug}/'
        self.assertEqual(article.get_absolute_url(), expected_url)

    def test_slug_uniqueness(self):
        """Test slug must be unique."""
        Article.objects.create(title='Test', slug='test-slug', author=self.user)
        with self.assertRaises(Exception):
            Article.objects.create(title='Test 2', slug='test-slug', author=self.user)

    def test_default_values(self):
        """Test default field values."""
        article = Article.objects.create(title='Test', author=self.user)
        self.assertFalse(article.is_published)
        self.assertIsNotNone(article.created_at)
```

### Testing Model Methods

```python
class ArticleMethodTest(TestCase):
    """Test Article model methods."""

    def setUp(self):
        self.user = User.objects.create_user(username='testuser')
        self.article = Article.objects.create(
            title='Test Article',
            content='This is test content.',
            author=self.user
        )

    def test_word_count(self):
        """Test word count calculation."""
        self.assertEqual(self.article.get_word_count(), 4)

    def test_publish_method(self):
        """Test publish method."""
        self.assertFalse(self.article.is_published)
        self.article.publish()
        self.assertTrue(self.article.is_published)
        self.assertIsNotNone(self.article.published_date)

    def test_can_edit_by_author(self):
        """Test author can edit."""
        self.assertTrue(self.article.can_edit(self.user))

    def test_cannot_edit_by_other_user(self):
        """Test other user cannot edit."""
        other_user = User.objects.create_user(username='other')
        self.assertFalse(self.article.can_edit(other_user))

    def test_staff_can_edit(self):
        """Test staff can edit any article."""
        staff_user = User.objects.create_user(username='staff', is_staff=True)
        self.assertTrue(self.article.can_edit(staff_user))
```

### Testing Relationships

```python
class ArticleRelationshipTest(TestCase):
    """Test Article relationships."""

    def setUp(self):
        self.user = User.objects.create_user(username='testuser')
        self.category = Category.objects.create(name='Tech')

    def test_category_relationship(self):
        """Test article-category relationship."""
        article = Article.objects.create(
            title='Test',
            author=self.user,
            category=self.category
        )
        self.assertEqual(article.category, self.category)
        self.assertIn(article, self.category.articles.all())

    def test_author_relationship(self):
        """Test article-author relationship."""
        article = Article.objects.create(title='Test', author=self.user)
        self.assertEqual(article.author, self.user)
        self.assertIn(article, self.user.articles.all())

    def test_tags_many_to_many(self):
        """Test many-to-many tags relationship."""
        article = Article.objects.create(title='Test', author=self.user)
        tag1 = Tag.objects.create(name='Python')
        tag2 = Tag.objects.create(name='Django')

        article.tags.add(tag1, tag2)
        self.assertEqual(article.tags.count(), 2)
        self.assertIn(tag1, article.tags.all())
        self.assertIn(article, tag1.articles.all())
```

---

## View Testing

### Testing Function-Based Views

```python
from django.test import TestCase, Client
from django.urls import reverse

class ArticleViewTest(TestCase):
    """Test article views."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.article = Article.objects.create(
            title='Test Article',
            slug='test-article',
            content='Test content',
            author=self.user,
            status='published'
        )

    def test_article_list_view(self):
        """Test article list view."""
        url = reverse('blog:article-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/article_list.html')
        self.assertContains(response, 'Test Article')
        self.assertIn('articles', response.context)

    def test_article_detail_view(self):
        """Test article detail view."""
        url = reverse('blog:article-detail', kwargs={'slug': self.article.slug})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/article_detail.html')
        self.assertEqual(response.context['article'], self.article)

    def test_article_not_found(self):
        """Test 404 for non-existent article."""
        url = reverse('blog:article-detail', kwargs={'slug': 'non-existent'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_login_required(self):
        """Test login required for protected view."""
        url = reverse('blog:article-create')
        response = self.client.get(url)

        # Should redirect to login
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_authenticated_access(self):
        """Test authenticated user can access protected view."""
        self.client.login(username='testuser', password='12345')
        url = reverse('blog:article-create')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
```

### Testing Class-Based Views

```python
class ArticleCBVTest(TestCase):
    """Test article class-based views."""

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.article = Article.objects.create(
            title='Test Article',
            author=self.user
        )

    def test_list_view(self):
        """Test ListView."""
        response = self.client.get(reverse('blog:article-list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['articles']), 1)

    def test_detail_view(self):
        """Test DetailView."""
        url = reverse('blog:article-detail', kwargs={'pk': self.article.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['article'], self.article)

    def test_create_view_get(self):
        """Test CreateView GET request."""
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('blog:article-create'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)

    def test_create_view_post(self):
        """Test CreateView POST request."""
        self.client.login(username='testuser', password='12345')
        data = {
            'title': 'New Article',
            'content': 'New content',
            'category': self.category.id
        }
        response = self.client.post(reverse('blog:article-create'), data)

        # Should redirect after successful creation
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Article.objects.count(), 2)

    def test_update_view(self):
        """Test UpdateView."""
        self.client.login(username='testuser', password='12345')
        url = reverse('blog:article-update', kwargs={'pk': self.article.pk})
        data = {
            'title': 'Updated Title',
            'content': 'Updated content'
        }
        response = self.client.post(url, data)

        self.article.refresh_from_db()
        self.assertEqual(self.article.title, 'Updated Title')

    def test_delete_view(self):
        """Test DeleteView."""
        self.client.login(username='testuser', password='12345')
        url = reverse('blog:article-delete', kwargs={'pk': self.article.pk})
        response = self.client.post(url)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Article.objects.count(), 0)
```

### Testing Permissions

```python
class PermissionTest(TestCase):
    """Test view permissions."""

    def setUp(self):
        self.user = User.objects.create_user(username='user', password='12345')
        self.staff = User.objects.create_user(username='staff', password='12345', is_staff=True)
        self.article = Article.objects.create(title='Test', author=self.user)

    def test_anonymous_cannot_create(self):
        """Test anonymous user cannot create article."""
        response = self.client.get(reverse('blog:article-create'))
        self.assertEqual(response.status_code, 302)

    def test_user_can_edit_own_article(self):
        """Test user can edit their own article."""
        self.client.login(username='user', password='12345')
        url = reverse('blog:article-update', kwargs={'pk': self.article.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_user_cannot_edit_others_article(self):
        """Test user cannot edit other user's article."""
        other_user = User.objects.create_user(username='other', password='12345')
        self.client.login(username='other', password='12345')
        url = reverse('blog:article-update', kwargs={'pk': self.article.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_staff_can_edit_any_article(self):
        """Test staff can edit any article."""
        self.client.login(username='staff', password='12345')
        url = reverse('blog:article-update', kwargs={'pk': self.article.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
```

---

## Form Testing

### Testing Form Validation

```python
from django.test import TestCase
from .forms import ArticleForm

class ArticleFormTest(TestCase):
    """Test ArticleForm."""

    def setUp(self):
        self.user = User.objects.create_user(username='testuser')
        self.category = Category.objects.create(name='Tech')

    def test_valid_form(self):
        """Test form with valid data."""
        data = {
            'title': 'Test Article',
            'content': 'Test content',
            'category': self.category.id
        }
        form = ArticleForm(data=data)
        self.assertTrue(form.is_valid())

    def test_invalid_form_missing_title(self):
        """Test form fails without title."""
        data = {
            'content': 'Test content',
            'category': self.category.id
        }
        form = ArticleForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)

    def test_title_max_length(self):
        """Test title max length validation."""
        data = {
            'title': 'x' * 201,  # Exceeds max_length
            'content': 'Test content',
            'category': self.category.id
        }
        form = ArticleForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)

    def test_custom_validation(self):
        """Test custom clean method."""
        data = {
            'title': 'spam article',  # Contains 'spam'
            'content': 'Test content',
            'category': self.category.id
        }
        form = ArticleForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('Title cannot contain spam', str(form.errors))

    def test_form_save(self):
        """Test form save creates object."""
        data = {
            'title': 'Test Article',
            'content': 'Test content',
            'category': self.category.id
        }
        form = ArticleForm(data=data)
        self.assertTrue(form.is_valid())

        article = form.save(commit=False)
        article.author = self.user
        article.save()

        self.assertEqual(Article.objects.count(), 1)
        self.assertEqual(Article.objects.first().title, 'Test Article')
```

---

## Test Coverage

### Measuring Coverage

```bash
# Install coverage
pip install coverage

# Run tests with coverage
coverage run --source='.' manage.py test

# View coverage report
coverage report

# Generate HTML report
coverage html
# Open htmlcov/index.html

# Show missing lines
coverage report --show-missing
```

### Coverage Configuration

```ini
# .coveragerc
[run]
source = .
omit =
    */migrations/*
    */tests/*
    */test_*.py
    */__pycache__/*
    */venv/*
    manage.py

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError
    if __name__ == .__main__.:
    if settings.DEBUG:
    pass
```

---

## Deployment Preparation

### Pre-Deployment Checklist

```bash
# Run deployment check
python manage.py check --deploy

# Collect static files
python manage.py collectstatic --noinput

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run tests
python manage.py test

# Check for security issues
pip install django-upgrade
django-upgrade --target-version 5.2 .
```

### Environment Variables

```bash
# .env file (never commit this!)
DEBUG=False
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://user:password@localhost/dbname
ALLOWED_HOSTS=example.com,www.example.com
```

```python
# settings.py
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')

# Security
DEBUG_STR = os.environ.get('DEBUG', 'False')
DEBUG = DEBUG_STR.lower() in ('true', '1', 'yes')

SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY or len(SECRET_KEY) < 50:
    raise ValueError('SECRET_KEY must be set in .env and at least 50 characters long')

ALLOWED_HOSTS_STR = os.environ.get('ALLOWED_HOSTS', '')
ALLOWED_HOSTS = [host.strip() for host in ALLOWED_HOSTS_STR.split(',') if host.strip()]

# Database (if using dj-database-url)
import dj_database_url
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.parse(DATABASE_URL)
    }
```

---

## Production Configuration

### Production Settings

```python
# settings/production.py
from .base import *

DEBUG = False

ALLOWED_HOSTS = ['example.com', 'www.example.com']

# Security
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True

# Database
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

# Static files
STATIC_ROOT = '/var/www/example.com/static/'
MEDIA_ROOT = '/var/www/example.com/media/'

# Caching
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': '/var/log/django/error.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
}

# Email
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST')
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
```

### Static Files in Production

```python
# settings.py
STATIC_URL = '/static/'
STATIC_ROOT = '/var/www/example.com/static/'

STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Collect static files
# python manage.py collectstatic
```

```nginx
# Nginx configuration
server {
    listen 80;
    server_name example.com;

    location /static/ {
        alias /var/www/example.com/static/;
    }

    location /media/ {
        alias /var/www/example.com/media/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## Monitoring and Maintenance

### Logging Configuration

```python
# settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': 'django.log',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
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

### Error Monitoring

```python
# Using Sentry for error monitoring
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

sentry_sdk.init(
    dsn=os.environ.get('SENTRY_DSN'),
    integrations=[DjangoIntegration()],
    traces_sample_rate=0.1,
    send_default_pii=False,
)
```

### Performance Monitoring

```python
# Using Django Debug Toolbar in development
if DEBUG:
    INSTALLED_APPS += ['debug_toolbar']
    MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
    INTERNAL_IPS = ['127.0.0.1']

# Query monitoring
from django.db import connection

def print_queries():
    """Print all database queries."""
    for query in connection.queries:
        print(f"{query['time']}: {query['sql']}")
```

### Database Maintenance

```bash
# Backup database
python manage.py dumpdata > backup.json

# Restore database
python manage.py loaddata backup.json

# Optimize database (PostgreSQL)
python manage.py dbshell
VACUUM ANALYZE;

# Clear expired sessions
python manage.py clearsessions
```

### Cron Jobs

```python
# Management command for scheduled tasks
# myapp/management/commands/cleanup_old_articles.py
from django.core.management.base import BaseCommand
from myapp.models import Article
from django.utils import timezone
from datetime import timedelta

class Command(BaseCommand):
    help = 'Delete articles older than 1 year'

    def handle(self, *args, **options):
        cutoff_date = timezone.now() - timedelta(days=365)
        deleted = Article.objects.filter(created_at__lt=cutoff_date).delete()
        self.stdout.write(f'Deleted {deleted[0]} old articles')
```

```bash
# Crontab entry
0 2 * * * /path/to/venv/bin/python /path/to/manage.py cleanup_old_articles
```
