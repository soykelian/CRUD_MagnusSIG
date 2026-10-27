# Security Best Practices Reference

This reference provides comprehensive security guidance for Django applications.

## Table of Contents

- [Security Fundamentals](#security-fundamentals)
- [CSRF Protection](#csrf-protection)
- [XSS Protection](#xss-protection)
- [SQL Injection Prevention](#sql-injection-prevention)
- [Clickjacking Protection](#clickjacking-protection)
- [Authentication and Authorization](#authentication-and-authorization)
- [HTTPS and Security Headers](#https-and-security-headers)
- [File Upload Security](#file-upload-security)
- [Common Vulnerabilities](#common-vulnerabilities)

---

## Security Fundamentals

Django is designed to help developers avoid common security mistakes. However, proper configuration and coding practices are essential.

### Django Security Check Command

Run Django's security check before deployment:

```bash
python manage.py check --deploy
```

This command identifies security issues in your settings.

### Core Security Principles

1. **Defense in depth**: Multiple layers of security
2. **Least privilege**: Grant minimum necessary permissions
3. **Fail securely**: Errors should not expose sensitive information
4. **Don't trust user input**: Validate and sanitize all input
5. **Keep secrets secret**: Never commit credentials to version control
6. **Stay updated**: Keep Django and dependencies current

### Required Middleware Configuration

Django's security middleware must be properly configured and ordered. The following middleware components are essential:

```python
# settings.py
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',  # Must be first - sets security headers
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',  # CSRF protection
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',  # Clickjacking protection
]
```

**SecurityMiddleware** handles:
- HTTPS redirects (`SECURE_SSL_REDIRECT`)
- HTTP Strict Transport Security (HSTS)
- Secure cookie settings
- Content type options

**Middleware ordering matters**: SecurityMiddleware should be near the top to ensure security headers are applied to all responses.

### Authentication System Setup

Include these required apps for Django's authentication system:

```python
# settings.py
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',  # Authentication framework
    'django.contrib.contenttypes',  # Content types framework
    'django.contrib.sessions',  # Session framework
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Your apps...
]
```

These apps work together to provide secure authentication, session management, and permission handling.

---

## CSRF Protection

Cross-Site Request Forgery (CSRF) attacks trick authenticated users into performing unwanted actions.

### How Django Protects Against CSRF

Django's CSRF middleware provides automatic protection:

```python
# settings.py
MIDDLEWARE = [
    # ...
    'django.middleware.csrf.CsrfViewMiddleware',  # Enabled by default
    # ...
]
```

### Using CSRF Protection in Templates

**Always include `{% csrf_token %}` in POST forms:**

```django
<form method="post">
    {% csrf_token %}
    <!-- form fields -->
    <button type="submit">Submit</button>
</form>
```

### AJAX Requests with CSRF

```javascript
// Get CSRF token from cookie
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const csrftoken = getCookie('csrftoken');

// Include in AJAX request
fetch('/api/endpoint/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrftoken,
    },
    body: JSON.stringify(data),
});
```

### Exempting Views from CSRF

**Caution**: Only exempt views when absolutely necessary, such as API endpoints with alternative authentication.

```python
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

@csrf_exempt  # Use with caution
def api_endpoint(request):
    """API endpoint with alternative auth."""
    # Verify authentication token
    if not verify_api_token(request):
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    # Process request
    return JsonResponse({'status': 'success'})
```

### CSRF Settings

```python
# settings.py

# Cookie name
CSRF_COOKIE_NAME = 'csrftoken'

# Make cookie accessible only over HTTPS in production
CSRF_COOKIE_SECURE = True  # Set True in production

# Prevent JavaScript access to CSRF cookie
CSRF_COOKIE_HTTPONLY = False  # Must be False for AJAX

# CSRF cookie age (default: None = expires when browser closes)
CSRF_COOKIE_AGE = 31449600  # One year

# Domains that can make CSRF-protected requests
CSRF_TRUSTED_ORIGINS = [
    'https://example.com',
    'https://www.example.com',
]
```

---

## XSS Protection

Cross-Site Scripting (XSS) attacks inject malicious scripts into web pages.

### Django's Auto-Escaping

Django templates automatically escape HTML characters:

```django
{# Automatically escaped - safe from XSS #}
<p>{{ user_input }}</p>

{# This becomes: #}
<p>&lt;script&gt;alert('XSS')&lt;/script&gt;</p>
```

### When Auto-Escaping Isn't Enough

**Dangerous contexts where auto-escaping doesn't fully protect:**

```django
{# Bad: Unquoted attribute - still vulnerable #}
<div class={{ css_class }}>Content</div>

{# Good: Quoted attribute #}
<div class="{{ css_class }}">Content</div>

{# Bad: JavaScript context - escaping doesn't help #}
<script>
    var name = "{{ user_name }}";  // Still vulnerable
</script>

{# Good: Use json_script tag #}
{{ user_data|json_script:"user-data" }}
<script>
    const userData = JSON.parse(document.getElementById('user-data').textContent);
</script>
```

### Marking Content as Safe

**Use `mark_safe` and `safe` filter with extreme caution:**

```python
from django.utils.safestring import mark_safe

# Only mark content safe if you've sanitized it yourself
def my_view(request):
    # Bad: Marking user input as safe
    unsafe_html = mark_safe(request.POST.get('content'))  # Dangerous!

    # Good: Sanitize first with a library like bleach
    import bleach
    allowed_tags = ['p', 'br', 'strong', 'em', 'a']
    allowed_attrs = {'a': ['href', 'title']}
    clean_html = bleach.clean(
        request.POST.get('content'),
        tags=allowed_tags,
        attributes=allowed_attrs,
        strip=True
    )
    safe_html = mark_safe(clean_html)

    return render(request, 'template.html', {'content': safe_html})
```

### Content Security Policy (CSP)

Add CSP headers to restrict script sources:

```python
# settings.py or middleware
SECURE_CONTENT_TYPE_NOSNIFF = True

# Using django-csp package
CSP_DEFAULT_SRC = ("'self'",)
CSP_SCRIPT_SRC = ("'self'", "'unsafe-inline'", "cdn.example.com")
CSP_STYLE_SRC = ("'self'", "'unsafe-inline'")
CSP_IMG_SRC = ("'self'", "data:", "*.example.com")
```

---

## SQL Injection Prevention

SQL injection attacks insert malicious SQL code into queries.

### Django's QuerySet API

Django's ORM automatically parameterizes queries:

```python
# Safe: Uses parameterized query
Article.objects.filter(title=user_input)
# Executes: SELECT ... WHERE title = %s with parameter user_input

# Safe: Multiple filters
Article.objects.filter(author=author_name, status='published')

# Safe: Complex queries with Q objects
from django.db.models import Q
Article.objects.filter(Q(title__contains=query) | Q(content__contains=query))
```

### Dangerous Practices

**Avoid string formatting in queries:**

```python
# Bad: SQL injection vulnerability
Article.objects.raw(f"SELECT * FROM articles WHERE title = '{user_input}'")

# Bad: String concatenation
query = "SELECT * FROM articles WHERE id = " + str(article_id)
Article.objects.raw(query)
```

### Safe Raw SQL

If you must use raw SQL, use parameterization:

```python
# Good: Parameterized raw query
Article.objects.raw("SELECT * FROM articles WHERE title = %s", [user_input])

# Good: Using connection.cursor()
from django.db import connection

with connection.cursor() as cursor:
    cursor.execute("SELECT * FROM articles WHERE author = %s", [author_name])
    results = cursor.fetchall()
```

### Extra() Method Caution

The `extra()` method requires careful parameter handling:

```python
# Safer: Use params argument
Article.objects.extra(
    where=['published_date > %s'],
    params=[start_date]
)

# Avoid: Don't interpolate user input directly
# Article.objects.extra(where=[f'title = {user_input}'])  # Vulnerable
```

---

## Clickjacking Protection

Clickjacking tricks users into clicking something different from what they perceive.

### X-Frame-Options Middleware

Django provides built-in protection:

```python
# settings.py
MIDDLEWARE = [
    # ...
    'django.middleware.clickjacking.XFrameOptionsMiddleware',  # Enabled by default
    # ...
]

# Prevent site from being framed
X_FRAME_OPTIONS = 'DENY'  # Cannot be framed at all
# Or
X_FRAME_OPTIONS = 'SAMEORIGIN'  # Can only be framed by same origin
```

### Per-View Configuration

```python
from django.views.decorators.clickjacking import (
    xframe_options_deny,
    xframe_options_sameorigin,
    xframe_options_exempt
)

@xframe_options_deny
def protected_view(request):
    """Cannot be framed."""
    return render(request, 'template.html')

@xframe_options_sameorigin
def same_origin_view(request):
    """Can be framed by same origin."""
    return render(request, 'template.html')

@xframe_options_exempt
def embeddable_view(request):
    """Can be framed by anyone (use with caution)."""
    return render(request, 'template.html')
```

---

## Authentication and Authorization

### User Authentication

```python
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

def login_view(request):
    """Handle user login."""
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid credentials')

    return render(request, 'login.html')

def logout_view(request):
    """Handle user logout."""
    logout(request)
    return redirect('home')

@login_required
def protected_view(request):
    """Require authentication."""
    return render(request, 'protected.html')

@login_required(login_url='/custom-login/')
def custom_login_redirect(request):
    """Custom login URL."""
    return render(request, 'protected.html')
```

### Password Security

```python
# settings.py

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 12,  # Increase minimum length
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Password hashing
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.Argon2PasswordHasher',  # Recommended
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
]
```

### Permission-Based Authorization

```python
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin

@permission_required('blog.add_article')
def create_article(request):
    """Require specific permission."""
    # Only users with 'blog.add_article' permission can access
    pass

@permission_required('blog.delete_article', raise_exception=True)
def delete_article(request, pk):
    """Raise 403 if permission denied."""
    pass

# For class-based views
class ArticleCreateView(PermissionRequiredMixin, CreateView):
    permission_required = 'blog.add_article'
    model = Article
    fields = ['title', 'content']
```

### Custom User Permission Checks

```python
from django.core.exceptions import PermissionDenied

def article_edit(request, pk):
    """Only allow author or staff to edit."""
    article = get_object_or_404(Article, pk=pk)

    if request.user != article.author and not request.user.is_staff:
        raise PermissionDenied

    # Process edit
    pass
```

---

## HTTPS and Security Headers

### Force HTTPS

```python
# settings.py for production

# Redirect all HTTP to HTTPS
SECURE_SSL_REDIRECT = True

# Seconds for HSTS (HTTP Strict Transport Security)
SECURE_HSTS_SECONDS = 31536000  # 1 year

# Include subdomains in HSTS
SECURE_HSTS_INCLUDE_SUBDOMAINS = True

# Allow browser to preload HSTS
SECURE_HSTS_PRELOAD = True

# Only send cookies over HTTPS
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Prevent MIME type sniffing
SECURE_CONTENT_TYPE_NOSNIFF = True

# Enable XSS filter in older browsers
SECURE_BROWSER_XSS_FILTER = True

# Require secure proxy headers
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
```

### Security Headers Middleware

```python
# Custom middleware for additional headers
class SecurityHeadersMiddleware:
    """Add security headers to all responses."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Prevent MIME type sniffing
        response['X-Content-Type-Options'] = 'nosniff'

        # Enable XSS protection
        response['X-XSS-Protection'] = '1; mode=block'

        # Referrer policy
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'

        # Permissions policy
        response['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'

        return response
```

---

## File Upload Security

### Validate File Uploads

```python
from django.core.exceptions import ValidationError

def validate_file_extension(value):
    """Validate uploaded file extension."""
    import os
    ext = os.path.splitext(value.name)[1].lower()
    valid_extensions = ['.pdf', '.jpg', '.jpeg', '.png']

    if ext not in valid_extensions:
        raise ValidationError('Unsupported file extension.')

def validate_file_size(value):
    """Validate uploaded file size."""
    filesize = value.size
    max_size_mb = 5

    if filesize > max_size_mb * 1024 * 1024:
        raise ValidationError(f'File size cannot exceed {max_size_mb}MB.')

class Document(models.Model):
    file = models.FileField(
        upload_to='documents/',
        validators=[validate_file_extension, validate_file_size]
    )
```

### Handle Uploads Securely

```python
# settings.py

# Media files configuration
MEDIA_ROOT = '/path/to/media/'
MEDIA_URL = '/media/'

# Limit upload size (in bytes)
DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5 MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5 MB

# In forms
from django import forms

class UploadForm(forms.Form):
    file = forms.FileField()

    def clean_file(self):
        file = self.cleaned_data['file']

        # Check file type
        content_type = file.content_type
        if content_type not in ['image/jpeg', 'image/png', 'application/pdf']:
            raise forms.ValidationError('Unsupported file type.')

        # Check file size
        if file.size > 5 * 1024 * 1024:
            raise forms.ValidationError('File too large.')

        return file
```

### Serve Files Securely

```python
# views.py
from django.http import FileResponse
from django.contrib.auth.decorators import login_required
import os

@login_required
def protected_file(request, filename):
    """Serve file with permission check."""
    # Verify user has permission
    if not request.user.has_perm('app.view_document'):
        raise PermissionDenied

    # Prevent directory traversal
    safe_filename = os.path.basename(filename)
    file_path = os.path.join(settings.MEDIA_ROOT, 'documents', safe_filename)

    # Verify file exists and is within allowed directory
    if not os.path.exists(file_path):
        raise Http404

    real_path = os.path.realpath(file_path)
    expected_prefix = os.path.realpath(os.path.join(settings.MEDIA_ROOT, 'documents'))
    if not real_path.startswith(expected_prefix):
        raise PermissionDenied

    return FileResponse(open(file_path, 'rb'))
```

---

## Common Vulnerabilities

### Secret Key Management

**CRITICAL**: SECRET_KEY must be at least 50 characters long using strong randomization. Never use predictable values or commit SECRET_KEY to version control.

```python
# Bad: Secret key in settings.py
SECRET_KEY = 'hardcoded-secret-key-bad'

# Good: Generate strong SECRET_KEY (50+ chars)
# Use this command to generate: python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'

# Good: Load from environment variable
import os
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')

if not SECRET_KEY:
    raise ValueError('DJANGO_SECRET_KEY environment variable not set')

# Validate length (recommended)
if len(SECRET_KEY) < 50:
    raise ValueError('SECRET_KEY must be at least 50 characters long')

# Good: Use python-dotenv
from dotenv import load_dotenv
load_dotenv()

SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY or len(SECRET_KEY) < 50:
    raise ValueError('SECRET_KEY must be set in .env and at least 50 characters long')
```

**Generate a secure SECRET_KEY:**
```bash
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

### Debug Mode in Production

```python
# settings.py

# Bad: Debug enabled in production
DEBUG = True  # Never do this in production

# Good: Environment-based debug
import os
DEBUG = os.environ.get('DJANGO_DEBUG', 'False') == 'True'

# Better: Separate settings files
# settings/production.py
DEBUG = False
```

### Allowed Hosts

```python
# settings.py

# Bad: Allowing all hosts
ALLOWED_HOSTS = ['*']  # Vulnerable to Host header attacks

# Good: Specific domains
ALLOWED_HOSTS = ['example.com', 'www.example.com']

# For development
if DEBUG:
    ALLOWED_HOSTS = ['localhost', '127.0.0.1']
```

### Admin URL

```python
# urls.py

# Bad: Default admin URL
urlpatterns = [
    path('admin/', admin.site.urls),  # Predictable URL
]

# Better: Custom admin URL
urlpatterns = [
    path('secure-admin-path/', admin.site.urls),
]
```

### Sensitive Data in Logs

```python
# Bad: Logging sensitive data
import logging
logger = logging.getLogger(__name__)

def process_payment(request):
    card_number = request.POST['card_number']
    logger.info(f'Processing payment with card {card_number}')  # Exposed in logs!

# Good: Redact sensitive data
def process_payment(request):
    card_number = request.POST['card_number']
    masked = f'****{card_number[-4:]}'
    logger.info(f'Processing payment with card ending in {masked}')
```

### Mass Assignment

```python
# Bad: Accepting all POST data
def update_profile(request):
    user = request.user
    for key, value in request.POST.items():
        setattr(user, key, value)  # User could set is_staff=True!
    user.save()

# Good: Explicitly list allowed fields
def update_profile(request):
    user = request.user
    allowed_fields = ['first_name', 'last_name', 'email']

    for field in allowed_fields:
        if field in request.POST:
            setattr(user, field, request.POST[field])
    user.save()

# Better: Use forms
def update_profile(request):
    form = ProfileForm(request.POST, instance=request.user)
    if form.is_valid():
        form.save()  # Only saves fields defined in form
```

---

## Security Checklist

Before deploying to production:

### Settings

- [ ] `DEBUG = False`
- [ ] `SECRET_KEY` loaded from environment variable
- [ ] `ALLOWED_HOSTS` configured with specific domains
- [ ] `SECURE_SSL_REDIRECT = True`
- [ ] `SESSION_COOKIE_SECURE = True`
- [ ] `CSRF_COOKIE_SECURE = True`
- [ ] `SECURE_HSTS_SECONDS` set (e.g., 31536000)
- [ ] `SECURE_HSTS_INCLUDE_SUBDOMAINS = True`
- [ ] `SECURE_CONTENT_TYPE_NOSNIFF = True`
- [ ] `X_FRAME_OPTIONS = 'DENY'` or `'SAMEORIGIN'`

### Authentication

- [ ] Strong password validation configured
- [ ] Login rate limiting implemented
- [ ] Account lockout after failed attempts
- [ ] Password reset mechanism secure
- [ ] Session timeout configured
- [ ] Two-factor authentication (if applicable)

### Database

- [ ] Database user has minimal required permissions
- [ ] Database password is strong and secret
- [ ] Database accessible only from application server
- [ ] Regular backups configured

### Code

- [ ] All forms include `{% csrf_token %}`
- [ ] User input is validated and sanitized
- [ ] SQL queries use ORM or parameterization
- [ ] File uploads are validated and restricted
- [ ] Error messages don't expose sensitive information
- [ ] Logging doesn't include sensitive data
- [ ] Third-party packages are up to date
- [ ] `python manage.py check --deploy` passes

### Infrastructure

- [ ] HTTPS properly configured
- [ ] Security headers configured
- [ ] Static files served separately
- [ ] Media files protected if necessary
- [ ] Rate limiting on endpoints
- [ ] Monitoring and alerting configured
- [ ] Backup and disaster recovery plan
