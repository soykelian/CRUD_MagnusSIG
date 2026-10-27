# Views and URL Routing Reference

This reference provides comprehensive guidance for Django views, URL configuration, and request/response handling.

## Table of Contents

- [View Fundamentals](#view-fundamentals)
- [Function-Based Views](#function-based-views)
- [Class-Based Views](#class-based-views)
- [Generic Views](#generic-views)
- [URL Configuration](#url-configuration)
- [Request and Response](#request-and-response)
- [Middleware](#middleware)
- [View Decorators](#view-decorators)

---

## View Fundamentals

Views handle web requests and return web responses. A view is a Python callable that takes a request and returns a response.

### Basic View Structure

```python
from django.http import HttpResponse
from django.shortcuts import render

def my_view(request):
    """Basic view function."""
    # Process request
    context = {'message': 'Hello, World!'}
    # Return response
    return render(request, 'template.html', context)
```

### View Types

Django offers two primary view patterns:

1. **Function-Based Views (FBVs)**: Simple functions that take a request and return a response
2. **Class-Based Views (CBVs)**: Classes that provide reusable, extensible view logic

**When to use FBVs:**
- Simple, unique logic
- Complex workflows that don't fit standard patterns
- One-off views with specific requirements
- When explicit control is needed

**When to use CBVs:**
- Standard CRUD operations
- When reusing common patterns
- When extending existing functionality
- When leveraging generic views

---

## Function-Based Views

### Basic Patterns

```python
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from .models import Article

def article_list(request):
    """Display list of articles."""
    articles = Article.objects.filter(status='published')
    context = {'articles': articles}
    return render(request, 'blog/article_list.html', context)

def article_detail(request, pk):
    """Display single article."""
    article = get_object_or_404(Article, pk=pk)
    context = {'article': article}
    return render(request, 'blog/article_detail.html', context)

def article_create(request):
    """Create new article."""
    if request.method == 'POST':
        form = ArticleForm(request.POST)
        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user
            article.save()
            return redirect('article-detail', pk=article.pk)
    else:
        form = ArticleForm()
    return render(request, 'blog/article_form.html', {'form': form})
```

### Handling Different HTTP Methods

```python
from django.views.decorators.http import require_http_methods
from django.views.decorators.http import require_GET, require_POST

@require_http_methods(['GET', 'POST'])
def article_create(request):
    """Handle both GET and POST."""
    if request.method == 'POST':
        # Handle form submission
        pass
    else:
        # Display form
        pass

@require_GET
def article_list(request):
    """Only allow GET requests."""
    pass

@require_POST
def article_delete(request, pk):
    """Only allow POST requests."""
    article = get_object_or_404(Article, pk=pk)
    article.delete()
    return redirect('article-list')
```

### Returning Different Response Types

```python
from django.http import HttpResponse, JsonResponse, FileResponse
from django.core import serializers
import json

def json_response_view(request):
    """Return JSON response."""
    data = {'status': 'success', 'message': 'Data retrieved'}
    return JsonResponse(data)

def json_list_view(request):
    """Return list as JSON."""
    articles = Article.objects.all()
    data = serializers.serialize('json', articles)
    return HttpResponse(data, content_type='application/json')

def download_file_view(request, filename):
    """Return file download."""
    file_path = f'/path/to/files/{filename}'
    return FileResponse(open(file_path, 'rb'), as_attachment=True)

def xml_response_view(request):
    """Return XML response."""
    xml_data = '<response><status>success</status></response>'
    return HttpResponse(xml_data, content_type='application/xml')
```

### Pagination in FBVs

```python
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

def article_list(request):
    """Paginated article list."""
    article_list = Article.objects.all()
    paginator = Paginator(article_list, 25)  # 25 articles per page

    page = request.GET.get('page')
    try:
        articles = paginator.page(page)
    except PageNotAnInteger:
        articles = paginator.page(1)
    except EmptyPage:
        articles = paginator.page(paginator.num_pages)

    context = {'articles': articles}
    return render(request, 'blog/article_list.html', context)
```

---

## Class-Based Views

Class-based views provide reusable, extensible view logic through inheritance.

### Basic CBV Structure

```python
from django.views import View
from django.shortcuts import render
from django.http import HttpResponse

class ArticleListView(View):
    """Basic class-based view."""

    def get(self, request):
        """Handle GET requests."""
        articles = Article.objects.all()
        return render(request, 'blog/article_list.html', {'articles': articles})

    def post(self, request):
        """Handle POST requests."""
        # Process form data
        return HttpResponse('POST request processed')
```

### Using as_view()

```python
# In urls.py
from django.urls import path
from .views import ArticleListView

urlpatterns = [
    path('articles/', ArticleListView.as_view(), name='article-list'),
]
```

### Method Override Pattern

```python
from django.views.generic import ListView

class ArticleListView(ListView):
    """Customize generic ListView."""
    model = Article
    template_name = 'blog/article_list.html'
    context_object_name = 'articles'
    paginate_by = 25

    def get_queryset(self):
        """Override queryset."""
        return Article.objects.filter(status='published').select_related('author')

    def get_context_data(self, **kwargs):
        """Add extra context."""
        context = super().get_context_data(**kwargs)
        context['featured_article'] = Article.objects.filter(featured=True).first()
        return context
```

### Mixins

Reusable functionality through multiple inheritance:

```python
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import CreateView

class LoginRequiredMixin:
    """Require login for this view."""
    pass

class StaffRequiredMixin(UserPassesTestMixin):
    """Require staff status."""
    def test_func(self):
        return self.request.user.is_staff

class ArticleCreateView(LoginRequiredMixin, StaffRequiredMixin, CreateView):
    """Create view with multiple mixins."""
    model = Article
    fields = ['title', 'content']

    def form_valid(self, form):
        """Set author before saving."""
        form.instance.author = self.request.user
        return super().form_valid(form)
```

### Common Built-in Mixins

```python
from django.contrib.auth.mixins import (
    LoginRequiredMixin,      # Require authentication
    PermissionRequiredMixin, # Require specific permission
    UserPassesTestMixin,     # Custom test function
)
from django.views.generic.base import ContextMixin

class ArticleDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = Article
    permission_required = 'blog.view_article'
    # Redirect to login if not authenticated
    login_url = '/login/'
    # Redirect parameter name
    redirect_field_name = 'next'
```

---

## Generic Views

Django provides generic views for common patterns.

### Display Views

#### ListView

```python
from django.views.generic import ListView

class ArticleListView(ListView):
    """Display list of articles."""
    model = Article
    template_name = 'blog/article_list.html'
    context_object_name = 'articles'
    paginate_by = 20
    ordering = ['-published_date']

    def get_queryset(self):
        """Filter by category if provided."""
        queryset = super().get_queryset()
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(category=category)
        return queryset
```

#### DetailView

```python
from django.views.generic import DetailView

class ArticleDetailView(DetailView):
    """Display single article."""
    model = Article
    template_name = 'blog/article_detail.html'
    context_object_name = 'article'

    def get_queryset(self):
        """Optimize with select_related."""
        return super().get_queryset().select_related('author', 'category')

    def get_context_data(self, **kwargs):
        """Add related comments."""
        context = super().get_context_data(**kwargs)
        context['comments'] = self.object.comments.all()
        return context
```

### Editing Views

#### CreateView

```python
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy

class ArticleCreateView(LoginRequiredMixin, CreateView):
    """Create new article."""
    model = Article
    fields = ['title', 'content', 'category']
    template_name = 'blog/article_form.html'
    success_url = reverse_lazy('article-list')

    def form_valid(self, form):
        """Set author before saving."""
        form.instance.author = self.request.user
        return super().form_valid(form)
```

#### UpdateView

```python
from django.views.generic.edit import UpdateView

class ArticleUpdateView(LoginRequiredMixin, UpdateView):
    """Update existing article."""
    model = Article
    fields = ['title', 'content', 'category']
    template_name = 'blog/article_form.html'

    def get_queryset(self):
        """Users can only edit their own articles."""
        return super().get_queryset().filter(author=self.request.user)

    def get_success_url(self):
        """Redirect to article detail."""
        return reverse_lazy('article-detail', kwargs={'pk': self.object.pk})
```

#### DeleteView

```python
from django.views.generic.edit import DeleteView

class ArticleDeleteView(LoginRequiredMixin, DeleteView):
    """Delete article."""
    model = Article
    template_name = 'blog/article_confirm_delete.html'
    success_url = reverse_lazy('article-list')

    def get_queryset(self):
        """Users can only delete their own articles."""
        return super().get_queryset().filter(author=self.request.user)
```

### FormView

```python
from django.views.generic.edit import FormView
from django.contrib import messages

class ContactFormView(FormView):
    """Handle contact form."""
    template_name = 'contact.html'
    form_class = ContactForm
    success_url = reverse_lazy('contact-success')

    def form_valid(self, form):
        """Process valid form."""
        # Send email
        form.send_email()
        messages.success(self.request, 'Message sent successfully!')
        return super().form_valid(form)
```

### TemplateView

```python
from django.views.generic import TemplateView

class AboutView(TemplateView):
    """Simple template view."""
    template_name = 'about.html'

    def get_context_data(self, **kwargs):
        """Add context data."""
        context = super().get_context_data(**kwargs)
        context['team_members'] = TeamMember.objects.all()
        return context
```

---

## URL Configuration

URL patterns map URLs to views.

### Basic URL Patterns

```python
# urls.py
from django.urls import path
from . import views

app_name = 'blog'  # Namespace for URL names

urlpatterns = [
    # Function-based view
    path('', views.article_list, name='list'),

    # Class-based view
    path('articles/', views.ArticleListView.as_view(), name='article-list'),

    # URL with parameter
    path('article/<int:pk>/', views.article_detail, name='article-detail'),

    # URL with slug
    path('article/<slug:slug>/', views.article_detail_slug, name='article-slug'),

    # Multiple parameters
    path('category/<str:category>/page/<int:page>/', views.category_page, name='category-page'),
]
```

### Path Converters

```python
from django.urls import path

urlpatterns = [
    # int: Matches positive integers
    path('article/<int:pk>/', views.article_detail),

    # str: Matches any non-empty string (excluding '/')
    path('category/<str:category>/', views.category_list),

    # slug: Matches slugs (letters, numbers, hyphens, underscores)
    path('article/<slug:slug>/', views.article_slug),

    # uuid: Matches UUID format
    path('object/<uuid:id>/', views.object_detail),

    # path: Matches any string (including '/')
    path('file/<path:filepath>/', views.file_view),
]
```

### Including Other URL Configs

```python
# project/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('blog/', include('blog.urls')),  # Include blog URLs
    path('api/', include('api.urls')),    # Include API URLs
]

# blog/urls.py
from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.ArticleListView.as_view(), name='list'),
    path('<int:pk>/', views.ArticleDetailView.as_view(), name='detail'),
]

# Usage in templates: {% url 'blog:list' %} or {% url 'blog:detail' pk=article.pk %}
```

### URL Reversing

```python
from django.urls import reverse
from django.shortcuts import redirect

def my_view(request):
    # Reverse by name
    url = reverse('blog:article-detail', kwargs={'pk': 1})
    # Redirect using reverse
    return redirect('blog:article-list')

# In models
class Article(models.Model):
    def get_absolute_url(self):
        return reverse('blog:article-detail', kwargs={'pk': self.pk})

# In templates
# {% url 'blog:article-detail' pk=article.pk %}
```

### Custom Path Converters

```python
# converters.py
class FourDigitYearConverter:
    regex = '[0-9]{4}'

    def to_python(self, value):
        return int(value)

    def to_url(self, value):
        return '%04d' % value

# urls.py
from django.urls import path, register_converter
from . import converters, views

register_converter(converters.FourDigitYearConverter, 'yyyy')

urlpatterns = [
    path('articles/<yyyy:year>/', views.year_archive, name='year-archive'),
]
```

### Regular Expression Patterns

```python
from django.urls import re_path

urlpatterns = [
    # Match 4-digit year
    re_path(r'^articles/(?P<year>[0-9]{4})/$', views.year_archive),

    # Match year and month
    re_path(r'^articles/(?P<year>[0-9]{4})/(?P<month>[0-9]{2})/$', views.month_archive),

    # Optional trailing slash
    re_path(r'^about/?$', views.about),
]
```

---

## Request and Response

### Request Object

```python
def my_view(request):
    # HTTP method
    if request.method == 'GET':
        pass
    elif request.method == 'POST':
        pass

    # GET parameters
    search = request.GET.get('search', '')  # ?search=query
    page = request.GET.get('page', 1)

    # POST data
    username = request.POST.get('username')
    password = request.POST.get('password')

    # Uploaded files
    file = request.FILES.get('document')

    # User
    if request.user.is_authenticated:
        username = request.user.username

    # Headers
    user_agent = request.headers.get('User-Agent')
    content_type = request.headers.get('Content-Type')

    # Path info
    path = request.path  # /blog/article/1/
    full_path = request.get_full_path()  # /blog/article/1/?page=2

    # Query string
    query_string = request.META.get('QUERY_STRING')

    # Request body (for APIs)
    import json
    data = json.loads(request.body)

    # Cookies
    session_id = request.COOKIES.get('sessionid')

    # Session
    request.session['key'] = 'value'
    value = request.session.get('key')
```

### Response Objects

```python
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.shortcuts import render, redirect

def response_examples(request):
    # Simple text response
    response = HttpResponse('Simple text')

    # HTML response
    response = HttpResponse('<h1>HTML content</h1>')
    response['Content-Type'] = 'text/html'

    # JSON response
    data = {'status': 'success', 'data': [1, 2, 3]}
    response = JsonResponse(data)

    # Render template
    context = {'message': 'Hello'}
    response = render(request, 'template.html', context)

    # Redirect
    response = redirect('article-list')
    response = redirect('article-detail', pk=1)
    response = HttpResponseRedirect('/articles/')

    # Custom status code
    response = HttpResponse('Not Found', status=404)

    # Set cookies
    response = HttpResponse('Content')
    response.set_cookie('key', 'value', max_age=3600)

    # Set headers
    response['Cache-Control'] = 'no-cache'
    response['X-Custom-Header'] = 'value'

    return response
```

### HTTP Status Codes

```python
from django.http import (
    HttpResponse,
    HttpResponseNotFound,      # 404
    HttpResponseBadRequest,    # 400
    HttpResponseForbidden,     # 403
    HttpResponseServerError,   # 500
)
from django.shortcuts import get_object_or_404

def status_code_examples(request):
    # 200 OK (default)
    return HttpResponse('Success')

    # 201 Created
    return HttpResponse('Created', status=201)

    # 204 No Content
    return HttpResponse(status=204)

    # 400 Bad Request
    return HttpResponseBadRequest('Invalid input')

    # 403 Forbidden
    return HttpResponseForbidden('Access denied')

    # 404 Not Found
    return HttpResponseNotFound('Page not found')
    # Or use get_object_or_404
    article = get_object_or_404(Article, pk=pk)

    # 500 Internal Server Error
    return HttpResponseServerError('Server error')
```

---

## Middleware

Middleware processes requests and responses globally.

### Custom Middleware

```python
# middleware.py
class SimpleMiddleware:
    """Basic middleware structure."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Code executed before view
        response = self.get_response(request)
        # Code executed after view
        return response

class TimingMiddleware:
    """Measure request processing time."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        import time
        start_time = time.time()

        response = self.get_response(request)

        duration = time.time() - start_time
        response['X-Processing-Time'] = str(duration)
        return response

class CustomHeaderMiddleware:
    """Add custom headers to all responses."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response['X-Custom-Header'] = 'My Value'
        return response
```

### Register Middleware

```python
# settings.py
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'myapp.middleware.TimingMiddleware',  # Custom middleware
]
```

---

## View Decorators

Decorators modify view behavior.

### Common Decorators

```python
from django.contrib.auth.decorators import login_required, permission_required
from django.views.decorators.http import require_http_methods, require_GET, require_POST
from django.views.decorators.cache import cache_page

@login_required
def protected_view(request):
    """Require authentication."""
    return HttpResponse('Authenticated')

@login_required(login_url='/custom-login/')
def custom_login_view(request):
    """Custom login URL."""
    return HttpResponse('Authenticated')

@permission_required('blog.add_article')
def create_article_view(request):
    """Require specific permission."""
    return HttpResponse('Can create articles')

@require_GET
def get_only_view(request):
    """Only allow GET requests."""
    return HttpResponse('GET request')

@require_POST
def post_only_view(request):
    """Only allow POST requests."""
    return HttpResponse('POST request')

@require_http_methods(['GET', 'POST'])
def get_post_view(request):
    """Allow GET and POST only."""
    if request.method == 'GET':
        return HttpResponse('GET')
    else:
        return HttpResponse('POST')

@cache_page(60 * 15)  # Cache for 15 minutes
def cached_view(request):
    """Cache this view."""
    return HttpResponse('Cached content')
```

### Applying Decorators to CBVs

```python
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import ListView

# Method 1: Decorate dispatch method
class ArticleListView(ListView):
    model = Article

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

# Method 2: Use decorators attribute
@method_decorator(login_required, name='dispatch')
class ArticleListView(ListView):
    model = Article

# Method 3: In urls.py
from django.urls import path
from django.contrib.auth.decorators import login_required

urlpatterns = [
    path('articles/', login_required(ArticleListView.as_view()), name='article-list'),
]
```

### Custom Decorators

```python
from functools import wraps
from django.http import HttpResponseForbidden

def staff_required(view_func):
    """Require staff status."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_staff:
            return HttpResponseForbidden('Staff access required')
        return view_func(request, *args, **kwargs)
    return wrapper

@staff_required
def admin_view(request):
    """Only accessible to staff."""
    return HttpResponse('Admin content')

def ajax_required(view_func):
    """Require AJAX request."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return HttpResponseForbidden('AJAX request required')
        return view_func(request, *args, **kwargs)
    return wrapper
```

---

## Best Practices

### View Organization

```python
# Good: Organized by functionality
# blog/views/article_views.py
class ArticleListView(ListView): pass
class ArticleDetailView(DetailView): pass
class ArticleCreateView(CreateView): pass

# blog/views/comment_views.py
class CommentCreateView(CreateView): pass
class CommentDeleteView(DeleteView): pass

# blog/views/__init__.py
from .article_views import *
from .comment_views import *
```

### Avoid Business Logic in Views

```python
# Bad: Business logic in view
def publish_article(request, pk):
    article = Article.objects.get(pk=pk)
    article.status = 'published'
    article.published_date = timezone.now()
    # Send notifications
    # Update search index
    article.save()

# Good: Business logic in model method
class Article(models.Model):
    def publish(self):
        """Publish this article."""
        self.status = 'published'
        self.published_date = timezone.now()
        self.save()
        self.send_notifications()
        self.update_search_index()

def publish_article(request, pk):
    article = get_object_or_404(Article, pk=pk)
    article.publish()
    return redirect('article-detail', pk=pk)
```

### Use get_object_or_404

```python
# Good: Automatic 404 handling
from django.shortcuts import get_object_or_404

def article_detail(request, pk):
    article = get_object_or_404(Article, pk=pk)
    return render(request, 'article_detail.html', {'article': article})

# Also works with multiple filters
article = get_object_or_404(Article, pk=pk, status='published')
```

### Optimize Queries

```python
# Bad: N+1 queries
class ArticleListView(ListView):
    model = Article

# Good: Optimized queries
class ArticleListView(ListView):
    model = Article

    def get_queryset(self):
        return Article.objects.select_related('author').prefetch_related('tags')
```
