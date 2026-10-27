# Templates and Forms Reference

This reference provides comprehensive guidance for Django templates and forms.

## Table of Contents

- [Template Fundamentals](#template-fundamentals)
- [Template Inheritance](#template-inheritance)
- [Template Tags](#template-tags)
- [Template Filters](#template-filters)
- [Forms Fundamentals](#forms-fundamentals)
- [ModelForms](#modelforms)
- [Form Validation](#form-validation)
- [Form Rendering](#form-rendering)
- [Formsets](#formsets)

---

## Template Fundamentals

Django templates separate presentation from logic. Templates contain HTML with Django template language (DTL) for dynamic content.

### Basic Template Syntax

```django
{# This is a comment #}

{# Variables - output with {{ }} #}
<h1>{{ article.title }}</h1>
<p>Author: {{ article.author.username }}</p>

{# Tags - logic with {% %} #}
{% if user.is_authenticated %}
    <p>Welcome, {{ user.username }}!</p>
{% else %}
    <p>Please log in.</p>
{% endif %}

{# Filters - modify variables with | #}
<p>{{ article.content|truncatewords:30 }}</p>
<p>Published: {{ article.published_date|date:"F d, Y" }}</p>
```

### Template Context

```python
# In views.py
def article_detail(request, pk):
    article = Article.objects.get(pk=pk)
    context = {
        'article': article,
        'related_articles': Article.objects.filter(category=article.category)[:5],
        'user': request.user,
    }
    return render(request, 'blog/article_detail.html', context)
```

```django
<!-- In template -->
<h1>{{ article.title }}</h1>

{% for related in related_articles %}
    <li><a href="{{ related.get_absolute_url }}">{{ related.title }}</a></li>
{% endfor %}
```

---

## Template Inheritance

Template inheritance promotes code reuse through base templates.

### Base Template Pattern

```django
<!-- templates/base.html -->
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}My Site{% endblock %}</title>

    {% load static %}
    <link rel="stylesheet" href="{% static 'css/style.css' %}">

    {% block extra_css %}{% endblock %}
</head>
<body>
    <header>
        <nav>
            <a href="{% url 'home' %}">Home</a>
            <a href="{% url 'blog:article-list' %}">Articles</a>
            {% if user.is_authenticated %}
                <a href="{% url 'logout' %}">Logout</a>
            {% else %}
                <a href="{% url 'login' %}">Login</a>
            {% endif %}
        </nav>
    </header>

    <main>
        {% block content %}
        <!-- Child templates override this -->
        {% endblock %}
    </main>

    <footer>
        <p>&copy; 2024 My Site</p>
    </footer>

    {% load static %}
    <script src="{% static 'js/main.js' %}"></script>
    {% block extra_js %}{% endblock %}
</body>
</html>
```

### Child Template

```django
<!-- templates/blog/article_detail.html -->
{% extends "base.html" %}
{% load static %}

{% block title %}{{ article.title }} - {{ block.super }}{% endblock %}

{% block extra_css %}
    <link rel="stylesheet" href="{% static 'css/article.css' %}">
{% endblock %}

{% block content %}
    <article>
        <h1>{{ article.title }}</h1>
        <p class="meta">
            By {{ article.author.username }} on {{ article.published_date|date:"F d, Y" }}
        </p>
        <div class="content">
            {{ article.content|linebreaks }}
        </div>
    </article>
{% endblock %}

{% block extra_js %}
    <script src="{% static 'js/article.js' %}"></script>
{% endblock %}
```

### Multi-Level Inheritance

```django
<!-- templates/base.html -->
{% block content %}{% endblock %}

<!-- templates/blog/base.html -->
{% extends "base.html" %}

{% block content %}
    <div class="blog-container">
        {% block blog_content %}{% endblock %}
    </div>
{% endblock %}

<!-- templates/blog/article_detail.html -->
{% extends "blog/base.html" %}

{% block blog_content %}
    <h1>{{ article.title }}</h1>
{% endblock %}
```

---

## Template Tags

### Built-in Tags

#### Control Flow

```django
{# if/elif/else #}
{% if user.is_authenticated %}
    <p>Welcome back!</p>
{% elif user.is_anonymous %}
    <p>Please log in.</p>
{% else %}
    <p>Something went wrong.</p>
{% endif %}

{# Logical operators #}
{% if user.is_authenticated and user.is_staff %}
    <a href="{% url 'admin:index' %}">Admin</a>
{% endif %}

{% if article.featured or article.is_new %}
    <span class="badge">Special</span>
{% endif %}

{% if not user.is_authenticated %}
    <a href="{% url 'login' %}">Login</a>
{% endif %}
```

#### Loops

```django
{# for loop #}
<ul>
{% for article in articles %}
    <li>{{ article.title }}</li>
{% empty %}
    <li>No articles found.</li>
{% endfor %}
</ul>

{# Loop variables #}
{% for article in articles %}
    <div class="article {% if forloop.first %}first{% endif %} {% if forloop.last %}last{% endif %}">
        <span>{{ forloop.counter }}. {{ article.title }}</span>
        {# forloop.counter: 1-indexed counter #}
        {# forloop.counter0: 0-indexed counter #}
        {# forloop.revcounter: Reverse counter #}
        {# forloop.first: True if first iteration #}
        {# forloop.last: True if last iteration #}
        {# forloop.parentloop: Access parent loop #}
    </div>
{% endfor %}
```

#### URL Generation

```django
{# Simple URL #}
<a href="{% url 'article-list' %}">Articles</a>

{# URL with parameters #}
<a href="{% url 'article-detail' pk=article.pk %}">{{ article.title }}</a>

{# URL with namespace #}
<a href="{% url 'blog:article-detail' pk=article.pk %}">Read More</a>

{# URL with query parameters #}
<a href="{% url 'article-list' %}?page=2&sort=date">Page 2</a>

{# Store URL in variable #}
{% url 'article-detail' pk=article.pk as article_url %}
<a href="{{ article_url }}">View</a>
```

#### Static Files

```django
{% load static %}

{# CSS #}
<link rel="stylesheet" href="{% static 'css/style.css' %}">

{# JavaScript #}
<script src="{% static 'js/main.js' %}"></script>

{# Images #}
<img src="{% static 'images/logo.png' %}" alt="Logo">

{# Get static URL as variable #}
{% static 'images/icon.png' as icon_url %}
<img src="{{ icon_url }}" alt="Icon">
```

#### Include

```django
{# Include another template #}
{% include 'partials/header.html' %}

{# Include with context #}
{% include 'partials/article_card.html' with article=featured_article %}

{# Include with only specified context #}
{% include 'partials/sidebar.html' with user=request.user only %}
```

#### With

```django
{# Create temporary variables #}
{% with total=articles.count featured=articles.first %}
    <p>Total articles: {{ total }}</p>
    <p>Featured: {{ featured.title }}</p>
{% endwith %}

{# Multiple variables #}
{% with author=article.author published=article.published_date %}
    <p>By {{ author.name }} on {{ published|date:"Y-m-d" }}</p>
{% endwith %}
```

#### CSRF Token

```django
{# Required in all POST forms #}
<form method="post">
    {% csrf_token %}
    <!-- Form fields -->
    <button type="submit">Submit</button>
</form>
```

---

## Template Filters

Filters modify variable output.

### Common Filters

```django
{# String filters #}
{{ article.title|upper }}                 {# UPPERCASE #}
{{ article.title|lower }}                 {# lowercase #}
{{ article.title|title }}                 {# Title Case #}
{{ article.title|capfirst }}              {# Capitalize first letter #}
{{ article.content|truncatewords:30 }}    {# First 30 words #}
{{ article.content|truncatechars:100 }}   {# First 100 characters #}
{{ article.slug|slugify }}                {# Convert to slug #}
{{ article.content|linebreaks }}          {# Convert newlines to <p> tags #}
{{ article.content|linebreaksbr }}        {# Convert newlines to <br> tags #}
{{ article.content|striptags }}           {# Remove HTML tags #}

{# Date/time filters #}
{{ article.published_date|date:"Y-m-d" }}           {# 2024-01-15 #}
{{ article.published_date|date:"F d, Y" }}          {# January 15, 2024 #}
{{ article.published_date|time:"H:i" }}             {# 14:30 #}
{{ article.created_at|timesince }}                  {# "2 days ago" #}
{{ article.published_date|timeuntil }}              {# "in 3 hours" #}

{# Number filters #}
{{ product.price|floatformat:2 }}         {# 19.99 #}
{{ count|add:"5" }}                       {# Add 5 #}

{# List filters #}
{{ tags|join:", " }}                      {# tag1, tag2, tag3 #}
{{ articles|length }}                     {# Number of items #}
{{ articles|first }}                      {# First item #}
{{ articles|last }}                       {# Last item #}
{{ articles|slice:":5" }}                 {# First 5 items #}

{# Default values #}
{{ article.subtitle|default:"No subtitle" }}
{{ user.profile.bio|default_if_none:"No bio available" }}

{# URL encoding #}
{{ search_query|urlencode }}

{# Safe HTML #}
{{ article.content|safe }}                {# Mark as safe HTML (use cautiously) #}

{# Chaining filters #}
{{ article.title|lower|truncatewords:5 }}
```

### Custom Filters

```python
# blog/templatetags/blog_filters.py
from django import template

register = template.Library()

@register.filter
def multiply(value, arg):
    """Multiply value by arg."""
    return value * arg

@register.filter(name='split')
def split_string(value, delimiter=' '):
    """Split string by delimiter."""
    return value.split(delimiter)

@register.filter
def reading_time(content):
    """Calculate reading time in minutes."""
    word_count = len(content.split())
    minutes = word_count // 200  # Average reading speed
    return max(1, minutes)
```

```django
{% load blog_filters %}

<p>Price: ${{ product.price|multiply:1.1 }}</p>
<p>Reading time: {{ article.content|reading_time }} min</p>
```

---

## Forms Fundamentals

Django forms handle user input, validation, and rendering.

### Basic Form

```python
# forms.py
from django import forms

class ContactForm(forms.Form):
    """Basic contact form."""
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your name'})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    subject = forms.CharField(max_length=200)
    message = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 5, 'class': 'form-control'})
    )
    subscribe = forms.BooleanField(required=False)

    def clean_email(self):
        """Validate email domain."""
        email = self.cleaned_data['email']
        if not email.endswith('@example.com'):
            raise forms.ValidationError('Must use @example.com email')
        return email

    def send_email(self):
        """Send the contact email."""
        # Email sending logic
        pass
```

```python
# views.py
from django.shortcuts import render, redirect
from .forms import ContactForm

def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.send_email()
            return redirect('contact-success')
    else:
        form = ContactForm()
    return render(request, 'contact.html', {'form': form})
```

```django
<!-- templates/contact.html -->
<form method="post">
    {% csrf_token %}
    {{ form.as_p }}
    <button type="submit">Send</button>
</form>
```

### Form Fields

```python
from django import forms

class ExampleForm(forms.Form):
    # Text inputs
    char_field = forms.CharField(max_length=100)
    text_field = forms.CharField(widget=forms.Textarea)
    email_field = forms.EmailField()
    url_field = forms.URLField()
    slug_field = forms.SlugField()

    # Numeric inputs
    integer_field = forms.IntegerField(min_value=0, max_value=100)
    float_field = forms.FloatField()
    decimal_field = forms.DecimalField(max_digits=10, decimal_places=2)

    # Boolean
    boolean_field = forms.BooleanField(required=False)

    # Date/time
    date_field = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    time_field = forms.TimeField()
    datetime_field = forms.DateTimeField()

    # Choices
    CHOICES = [('val1', 'Label 1'), ('val2', 'Label 2')]
    choice_field = forms.ChoiceField(choices=CHOICES)
    multiple_choice = forms.MultipleChoiceField(choices=CHOICES)

    # File uploads
    file_field = forms.FileField()
    image_field = forms.ImageField()

    # Hidden
    hidden_field = forms.CharField(widget=forms.HiddenInput())
```

---

## ModelForms

ModelForms automatically generate forms from models.

### Basic ModelForm

```python
# forms.py
from django import forms
from .models import Article

class ArticleForm(forms.ModelForm):
    """Form for Article model."""

    class Meta:
        model = Article
        fields = ['title', 'content', 'category', 'tags']
        # Or exclude specific fields
        # exclude = ['author', 'created_at']
        # Or use all fields
        # fields = '__all__'

        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 10}),
            'category': forms.Select(attrs={'class': 'form-control'}),
        }

        labels = {
            'title': 'Article Title',
            'content': 'Article Content',
        }

        help_texts = {
            'title': 'Enter a descriptive title',
            'tags': 'Select relevant tags',
        }

    def clean_title(self):
        """Custom validation for title."""
        title = self.cleaned_data['title']
        if len(title) < 5:
            raise forms.ValidationError('Title must be at least 5 characters')
        return title
```

```python
# views.py
from django.shortcuts import render, redirect
from .forms import ArticleForm

def article_create(request):
    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES)
        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user
            article.save()
            form.save_m2m()  # Required when commit=False with M2M fields
            return redirect('article-detail', pk=article.pk)
    else:
        form = ArticleForm()
    return render(request, 'article_form.html', {'form': form})

def article_update(request, pk):
    article = get_object_or_404(Article, pk=pk)
    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES, instance=article)
        if form.is_valid():
            form.save()
            return redirect('article-detail', pk=article.pk)
    else:
        form = ArticleForm(instance=article)
    return render(request, 'article_form.html', {'form': form})
```

---

## Form Validation

### Field-Level Validation

```python
class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['title', 'content', 'slug']

    def clean_title(self):
        """Validate title field."""
        title = self.cleaned_data['title']
        if 'spam' in title.lower():
            raise forms.ValidationError('Title cannot contain spam keywords')
        return title

    def clean_slug(self):
        """Validate slug uniqueness."""
        slug = self.cleaned_data['slug']
        if Article.objects.filter(slug=slug).exists():
            raise forms.ValidationError('This slug already exists')
        return slug
```

### Form-Level Validation

```python
class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['title', 'content', 'published_date']

    def clean(self):
        """Cross-field validation."""
        cleaned_data = super().clean()
        title = cleaned_data.get('title')
        content = cleaned_data.get('content')

        if title and content and title in content:
            raise forms.ValidationError('Title should not appear in content')

        return cleaned_data
```

### Custom Validators

```python
from django.core.exceptions import ValidationError
import re

def validate_no_special_chars(value):
    """Ensure value contains no special characters."""
    if not re.match(r'^[a-zA-Z0-9\s]*$', value):
        raise ValidationError('Only letters, numbers, and spaces allowed')

class ArticleForm(forms.ModelForm):
    title = forms.CharField(
        validators=[validate_no_special_chars]
    )

    class Meta:
        model = Article
        fields = ['title', 'content']
```

---

## Form Rendering

### Manual Form Rendering

```django
<form method="post" enctype="multipart/form-data">
    {% csrf_token %}

    {# Display non-field errors #}
    {% if form.non_field_errors %}
        <div class="alert alert-danger">
            {{ form.non_field_errors }}
        </div>
    {% endif %}

    {# Render each field manually #}
    <div class="form-group">
        <label for="{{ form.title.id_for_label }}">{{ form.title.label }}</label>
        {{ form.title }}
        {% if form.title.errors %}
            <div class="error">{{ form.title.errors }}</div>
        {% endif %}
        {% if form.title.help_text %}
            <small>{{ form.title.help_text }}</small>
        {% endif %}
    </div>

    <div class="form-group">
        <label for="{{ form.content.id_for_label }}">{{ form.content.label }}</label>
        {{ form.content }}
        {% if form.content.errors %}
            <div class="error">{{ form.content.errors }}</div>
        {% endif %}
    </div>

    <button type="submit">Submit</button>
</form>
```

### Automatic Form Rendering

```django
{# Render as paragraph tags #}
<form method="post">
    {% csrf_token %}
    {{ form.as_p }}
    <button type="submit">Submit</button>
</form>

{# Render as table #}
<form method="post">
    {% csrf_token %}
    <table>
        {{ form.as_table }}
    </table>
    <button type="submit">Submit</button>
</form>

{# Render as unordered list #}
<form method="post">
    {% csrf_token %}
    <ul>
        {{ form.as_ul }}
    </ul>
    <button type="submit">Submit</button>
</form>
```

### Looping Through Fields

```django
<form method="post">
    {% csrf_token %}

    {% for field in form %}
        <div class="form-group {% if field.errors %}has-error{% endif %}">
            <label for="{{ field.id_for_label }}">
                {{ field.label }}
                {% if field.field.required %}*{% endif %}
            </label>
            {{ field }}
            {% if field.errors %}
                <div class="error">
                    {{ field.errors }}
                </div>
            {% endif %}
            {% if field.help_text %}
                <small>{{ field.help_text }}</small>
            {% endif %}
        </div>
    {% endfor %}

    <button type="submit">Submit</button>
</form>
```

---

## Formsets

Formsets handle multiple forms on a single page.

### Basic Formset

```python
from django.forms import formset_factory
from .forms import ArticleForm

# Create formset with 3 extra blank forms
ArticleFormSet = formset_factory(ArticleForm, extra=3, max_num=10)

def article_bulk_create(request):
    if request.method == 'POST':
        formset = ArticleFormSet(request.POST)
        if formset.is_valid():
            for form in formset:
                if form.cleaned_data:
                    article = form.save(commit=False)
                    article.author = request.user
                    article.save()
            return redirect('article-list')
    else:
        formset = ArticleFormSet()
    return render(request, 'article_bulk_create.html', {'formset': formset})
```

```django
<form method="post">
    {% csrf_token %}
    {{ formset.management_form }}

    {% for form in formset %}
        <div class="form-instance">
            {{ form.as_p }}
        </div>
    {% endfor %}

    <button type="submit">Save All</button>
</form>
```

### Model Formset

```python
from django.forms import modelformset_factory
from .models import Article

ArticleFormSet = modelformset_factory(
    Article,
    fields=['title', 'content'],
    extra=2,
    can_delete=True
)

def article_bulk_edit(request):
    queryset = Article.objects.filter(author=request.user)
    if request.method == 'POST':
        formset = ArticleFormSet(request.POST, queryset=queryset)
        if formset.is_valid():
            formset.save()
            return redirect('article-list')
    else:
        formset = ArticleFormSet(queryset=queryset)
    return render(request, 'article_bulk_edit.html', {'formset': formset})
```

### Inline Formset

```python
from django.forms import inlineformset_factory
from .models import Article, Comment

CommentFormSet = inlineformset_factory(
    Article,
    Comment,
    fields=['text', 'author'],
    extra=3,
    can_delete=True
)

def article_with_comments(request, pk):
    article = get_object_or_404(Article, pk=pk)
    if request.method == 'POST':
        formset = CommentFormSet(request.POST, instance=article)
        if formset.is_valid():
            formset.save()
            return redirect('article-detail', pk=pk)
    else:
        formset = CommentFormSet(instance=article)
    return render(request, 'article_comments.html', {
        'article': article,
        'formset': formset
    })
```

```django
<form method="post">
    {% csrf_token %}
    <h1>{{ article.title }}</h1>

    <h2>Comments</h2>
    {{ formset.management_form }}

    {% for form in formset %}
        <div class="comment-form">
            {{ form.as_p }}
        </div>
    {% endfor %}

    <button type="submit">Save Comments</button>
</form>
```

---

## Best Practices

### Form Best Practices

```python
# Use ModelForm when possible
class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['title', 'content']

# Add custom validation
def clean_title(self):
    title = self.cleaned_data['title']
    # Validation logic
    return title

# Use widgets for custom rendering
widgets = {
    'content': forms.Textarea(attrs={'class': 'editor'}),
}

# Set initial values
form = ArticleForm(initial={'title': 'Default Title'})

# Handle file uploads
form = ArticleForm(request.POST, request.FILES)
```

### Template Best Practices

```django
{# Always use {% csrf_token %} in POST forms #}
<form method="post">
    {% csrf_token %}
    <!-- form fields -->
</form>

{# Use {% load static %} for static files #}
{% load static %}
<link rel="stylesheet" href="{% static 'css/style.css' %}">

{# Use {% url %} for URL generation #}
<a href="{% url 'article-detail' pk=article.pk %}">View</a>

{# Use template inheritance #}
{% extends "base.html" %}

{# Keep logic minimal - move complex logic to views/models #}

{# Use custom template tags for reusable components #}
{% load blog_tags %}
{% article_card article %}
```
