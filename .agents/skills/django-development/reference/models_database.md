# Models and Database Reference

This reference provides comprehensive guidance for Django model development, database design, and data management.

## Table of Contents

- [Model Basics](#model-basics)
- [Field Types and Options](#field-types-and-options)
- [Relationships](#relationships)
- [Model Meta Options](#model-meta-options)
- [Model Methods](#model-methods)
- [Custom Managers and QuerySets](#custom-managers-and-querysets)
- [Model Inheritance](#model-inheritance)
- [Migrations](#migrations)
- [Database Optimization](#database-optimization)

---

## Model Basics

Models are Python classes that define the structure of your database tables. Each model represents a single database table.

### Essential Structure

```python
from django.db import models

class Article(models.Model):
    """A news article with author and publication info."""
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    published_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField(default=False)

    class Meta:
        ordering = ['-published_date']
        verbose_name_plural = "articles"

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('article-detail', args=[str(self.id)])
```

### Core Principles

- **Single source of truth**: Models define data structure and business logic
- **Database agnostic**: Models work across different databases (PostgreSQL, MySQL, SQLite)
- **Automatic primary keys**: Django creates an `id` field automatically unless you specify `primary_key=True` on another field
- **Field names**: Use lowercase with underscores (`published_date`, not `publishedDate`)

---

## Field Types and Options

### Common Field Types

| Field Type | Purpose | Example |
|-----------|---------|---------|
| `CharField` | Short text, requires `max_length` | `models.CharField(max_length=100)` |
| `TextField` | Long text, no length limit | `models.TextField()` |
| `IntegerField` | Integer numbers | `models.IntegerField()` |
| `DecimalField` | Precise decimal numbers | `models.DecimalField(max_digits=10, decimal_places=2)` |
| `FloatField` | Floating point numbers | `models.FloatField()` |
| `BooleanField` | True/False values | `models.BooleanField(default=False)` |
| `DateField` | Date without time | `models.DateField()` |
| `DateTimeField` | Date with time | `models.DateTimeField()` |
| `EmailField` | Email address | `models.EmailField()` |
| `URLField` | URL | `models.URLField()` |
| `SlugField` | URL-friendly text | `models.SlugField(unique=True)` |
| `FileField` | File upload | `models.FileField(upload_to='uploads/')` |
| `ImageField` | Image upload | `models.ImageField(upload_to='images/')` |
| `JSONField` | JSON data | `models.JSONField(default=dict)` |

### Essential Field Options

```python
# Common field options
field_name = models.CharField(
    max_length=100,           # Maximum length (required for CharField)
    null=False,               # Allow NULL in database (default: False)
    blank=False,              # Allow empty in forms (default: False)
    default='',               # Default value
    unique=False,             # Enforce uniqueness (default: False)
    db_index=False,           # Create database index (default: False)
    verbose_name='Field Name', # Human-readable name
    help_text='Help text',    # Description for forms
    choices=None,             # Limit to predefined choices
    validators=[],            # Custom validators
    editable=True,            # Show in forms (default: True)
)
```

### null vs blank

**Critical distinction:**
- `null=True`: Database allows NULL values (database-level)
- `blank=True`: Forms allow empty values (validation-level)

```python
# Text fields: Use blank=True, NOT null=True
title = models.CharField(max_length=100, blank=True, default='')

# Non-text fields: Use both null=True and blank=True for optional
birth_date = models.DateField(null=True, blank=True)
```

**Best practice**: For string-based fields (`CharField`, `TextField`), avoid `null=True` to prevent two possible empty values (NULL and empty string).

### Choices Pattern

```python
class Article(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'DR', 'Draft'
        PUBLISHED = 'PB', 'Published'
        ARCHIVED = 'AR', 'Archived'

    status = models.CharField(
        max_length=2,
        choices=Status.choices,
        default=Status.DRAFT,
    )

    def is_published(self):
        return self.status == self.Status.PUBLISHED
```

### Auto Timestamp Pattern

```python
class TimestampedModel(models.Model):
    """Abstract model providing timestamp fields."""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class Article(TimestampedModel):
    title = models.CharField(max_length=200)
    # Inherits created_at and updated_at
```

---

## Relationships

### ForeignKey (Many-to-One)

One parent, many children. Most common relationship type.

```python
class Author(models.Model):
    name = models.CharField(max_length=100)

class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.ForeignKey(
        Author,
        on_delete=models.CASCADE,  # Required parameter
        related_name='books',       # Access author.books.all()
    )

# Usage
author = Author.objects.get(name='Jane Doe')
books = author.books.all()  # Get all books by this author
book = Book.objects.get(title='Some Title')
author_name = book.author.name  # Access related author
```

### on_delete Options

**Critical**: Always specify `on_delete` for ForeignKey.

```python
# CASCADE: Delete related objects
author = models.ForeignKey(Author, on_delete=models.CASCADE)

# PROTECT: Prevent deletion if related objects exist
category = models.ForeignKey(Category, on_delete=models.PROTECT)

# SET_NULL: Set to NULL (requires null=True)
editor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

# SET_DEFAULT: Set to default value (requires default)
status = models.ForeignKey(Status, on_delete=models.SET_DEFAULT, default=1)

# SET(): Set to specific value or callable
author = models.ForeignKey(Author, on_delete=models.SET(get_sentinel_author))

# DO_NOTHING: Do nothing (can cause database integrity errors)
```

### ManyToManyField

Bidirectional many-to-many relationship.

```python
class Student(models.Model):
    name = models.CharField(max_length=100)
    courses = models.ManyToManyField('Course', related_name='students')

class Course(models.Model):
    name = models.CharField(max_length=100)

# Usage
student = Student.objects.get(name='John')
student.courses.add(course1, course2)  # Add multiple courses
student.courses.remove(course1)         # Remove a course
courses = student.courses.all()         # Get all courses

course = Course.objects.get(name='Math')
students = course.students.all()        # Reverse relation
```

**Best practice**: Put `ManyToManyField` in the model that will be edited most frequently.

### ManyToMany with Through Model

For additional data on the relationship:

```python
class Student(models.Model):
    name = models.CharField(max_length=100)
    courses = models.ManyToManyField('Course', through='Enrollment')

class Course(models.Model):
    name = models.CharField(max_length=100)

class Enrollment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    date_enrolled = models.DateField()
    grade = models.CharField(max_length=1)

    class Meta:
        unique_together = ['student', 'course']

# Usage
enrollment = Enrollment.objects.create(
    student=student,
    course=course,
    date_enrolled=date.today(),
    grade='A'
)
```

### OneToOneField

Exclusive one-to-one relationship, typically for extending models.

```python
class User(models.Model):
    username = models.CharField(max_length=100)
    email = models.EmailField()

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField()
    avatar = models.ImageField(upload_to='avatars/')

# Usage
user = User.objects.get(username='john')
profile = user.userprofile  # Automatic reverse relation
bio = user.userprofile.bio
```

---

## Model Meta Options

Configure model behavior with the `Meta` class:

```python
class Article(models.Model):
    title = models.CharField(max_length=200)
    published_date = models.DateTimeField()

    class Meta:
        # Database table name
        db_table = 'blog_articles'

        # Default ordering
        ordering = ['-published_date', 'title']

        # Human-readable names
        verbose_name = 'article'
        verbose_name_plural = 'articles'

        # Unique together constraint
        unique_together = [['author', 'title']]

        # Index together for query optimization
        index_together = [['author', 'published_date']]

        # Database constraints (Django 2.2+)
        constraints = [
            models.CheckConstraint(
                check=models.Q(published_date__lte=timezone.now()),
                name='published_date_not_future'
            ),
            models.UniqueConstraint(
                fields=['author', 'slug'],
                name='unique_author_slug'
            )
        ]

        # Indexes (Django 1.11+)
        indexes = [
            models.Index(fields=['published_date', '-title']),
            models.Index(fields=['author', 'published_date']),
        ]

        # Permissions
        permissions = [
            ('can_publish', 'Can publish articles'),
            ('can_feature', 'Can feature articles'),
        ]

        # Abstract model (no database table)
        abstract = False

        # Proxy model (same database table, different Python behavior)
        proxy = False
```

---

## Model Methods

### Essential Methods

```python
class Article(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)

    def __str__(self):
        """String representation (used in admin and shell)."""
        return self.title

    def get_absolute_url(self):
        """Return the URL for this object."""
        from django.urls import reverse
        return reverse('article-detail', args=[str(self.slug)])

    def save(self, *args, **kwargs):
        """Override save to add custom logic."""
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)  # Always call super()

    def delete(self, *args, **kwargs):
        """Override delete to add custom logic."""
        # Perform cleanup (e.g., delete related files)
        if self.image:
            self.image.delete()
        super().delete(*args, **kwargs)  # Always call super()
```

### Property Methods

```python
class Order(models.Model):
    items = models.ManyToManyField('Item', through='OrderItem')

    @property
    def total_price(self):
        """Calculate total from related items."""
        return sum(item.price for item in self.items.all())

    @property
    def is_recent(self):
        """Check if order is recent."""
        from django.utils import timezone
        return self.created_at >= timezone.now() - timezone.timedelta(days=7)
```

### Custom Methods

```python
class Article(models.Model):
    content = models.TextField()
    author = models.ForeignKey('auth.User', on_delete=models.CASCADE)

    def get_word_count(self):
        """Return word count of content."""
        return len(self.content.split())

    def can_edit(self, user):
        """Check if user can edit this article."""
        return user == self.author or user.is_staff

    def publish(self):
        """Publish this article."""
        self.status = self.Status.PUBLISHED
        self.published_date = timezone.now()
        self.save()
```

---

## Custom Managers and QuerySets

Managers provide database query methods. Custom managers encapsulate reusable queries.

### Custom QuerySet

```python
from django.db import models
from django.utils import timezone

class ArticleQuerySet(models.QuerySet):
    """Custom queryset with reusable filters."""

    def published(self):
        """Return only published articles."""
        return self.filter(status='PB', published_date__lte=timezone.now())

    def draft(self):
        """Return only draft articles."""
        return self.filter(status='DR')

    def by_author(self, author):
        """Return articles by specific author."""
        return self.filter(author=author)

    def recent(self, days=7):
        """Return recent articles."""
        since = timezone.now() - timezone.timedelta(days=days)
        return self.filter(published_date__gte=since)

class Article(models.Model):
    title = models.CharField(max_length=200)
    status = models.CharField(max_length=2)
    published_date = models.DateTimeField()
    author = models.ForeignKey('auth.User', on_delete=models.CASCADE)

    objects = ArticleQuerySet.as_manager()

# Usage
Article.objects.published()  # Get published articles
Article.objects.draft().by_author(user)  # Chain filters
Article.objects.published().recent(30)  # Recent published articles
```

### Custom Manager

```python
class ArticleManager(models.Manager):
    """Custom manager with additional methods."""

    def get_queryset(self):
        """Override base queryset."""
        return super().get_queryset().select_related('author')

    def published(self):
        """Return published articles."""
        return self.get_queryset().filter(status='PB')

    def create_article(self, title, author, content):
        """Custom creation method."""
        article = self.create(
            title=title,
            author=author,
            content=content,
            status='DR'
        )
        return article

class Article(models.Model):
    # Fields...
    objects = ArticleManager()

# Usage
Article.objects.published()
article = Article.objects.create_article('Title', user, 'Content')
```

### Multiple Managers

```python
class Article(models.Model):
    # Fields...

    objects = models.Manager()  # Default manager
    published = PublishedManager()  # Custom manager
    drafts = DraftManager()  # Another custom manager

# Usage
Article.objects.all()  # All articles
Article.published.all()  # Published articles
Article.drafts.all()  # Draft articles
```

---

## Model Inheritance

### Abstract Base Classes

Share fields without creating database tables:

```python
class TimestampedModel(models.Model):
    """Abstract base class with timestamp fields."""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True  # No database table created

class Article(TimestampedModel):
    title = models.CharField(max_length=200)
    # Inherits created_at and updated_at

class Comment(TimestampedModel):
    text = models.TextField()
    # Also inherits created_at and updated_at
```

### Multi-Table Inheritance

Each model gets its own table with automatic OneToOneField:

```python
class Place(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=200)

class Restaurant(Place):
    """Inherits Place fields plus adds own fields."""
    serves_hot_dogs = models.BooleanField(default=False)
    serves_pizza = models.BooleanField(default=False)

# Usage
restaurant = Restaurant.objects.get(name='Pizza Palace')
print(restaurant.address)  # Inherited field
print(restaurant.serves_pizza)  # Own field

# Automatic parent access
place = restaurant.place_ptr
```

### Proxy Models

Same database table, different Python behavior:

```python
class Article(models.Model):
    title = models.CharField(max_length=200)
    status = models.CharField(max_length=2)

    class Meta:
        ordering = ['title']

class PublishedArticle(Article):
    """Proxy model with different default manager."""

    class Meta:
        proxy = True
        ordering = ['-published_date']

    objects = PublishedManager()

    def publish(self):
        self.status = 'PB'
        self.save()

# Same database table, different behavior
Article.objects.all()  # All articles
PublishedArticle.objects.all()  # Only published articles
```

---

## Migrations

Migrations propagate model changes to the database schema.

### Creating Migrations

```bash
# Create migrations for all apps
python manage.py makemigrations

# Create migrations for specific app
python manage.py makemigrations myapp

# Create named migration
python manage.py makemigrations myapp --name add_status_field

# Create empty migration for data migration
python manage.py makemigrations myapp --empty --name populate_slugs
```

### Applying Migrations

```bash
# Apply all migrations
python manage.py migrate

# Apply migrations for specific app
python manage.py migrate myapp

# Apply specific migration
python manage.py migrate myapp 0002

# Unapply migrations (rollback)
python manage.py migrate myapp 0001

# Show migration status
python manage.py showmigrations

# Show SQL for migration
python manage.py sqlmigrate myapp 0001
```

### Data Migrations

```python
# Generated by makemigrations --empty
from django.db import migrations

def populate_slugs(apps, schema_editor):
    """Populate slug fields from titles."""
    Article = apps.get_model('blog', 'Article')
    from django.utils.text import slugify

    for article in Article.objects.all():
        article.slug = slugify(article.title)
        article.save()

def reverse_populate_slugs(apps, schema_editor):
    """Reverse migration."""
    Article = apps.get_model('blog', 'Article')
    Article.objects.all().update(slug='')

class Migration(migrations.Migration):
    dependencies = [
        ('blog', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(populate_slugs, reverse_populate_slugs),
    ]
```

### Migration Best Practices

- **Review before applying**: Always check generated migrations
- **Small, focused migrations**: One logical change per migration
- **Test data migrations**: Use development data before production
- **Never edit applied migrations**: Create new migrations instead
- **Squash old migrations**: Use `squashmigrations` for long chains
- **Backup before migrating**: Always backup production databases

---

## Database Optimization

### Select Related (for ForeignKey and OneToOne)

Reduce queries with JOIN:

```python
# Bad: N+1 queries
articles = Article.objects.all()
for article in articles:
    print(article.author.name)  # Separate query each time

# Good: Single query with JOIN
articles = Article.objects.select_related('author')
for article in articles:
    print(article.author.name)  # No additional query

# Multiple relations
Article.objects.select_related('author', 'category')

# Nested relations
Comment.objects.select_related('article__author')
```

### Prefetch Related (for ManyToMany and reverse ForeignKey)

Reduce queries with separate lookup:

```python
# Bad: N+1 queries
articles = Article.objects.all()
for article in articles:
    tags = article.tags.all()  # Separate query each time

# Good: Two queries total
articles = Article.objects.prefetch_related('tags')
for article in articles:
    tags = article.tags.all()  # No additional query

# Multiple prefetches
Article.objects.prefetch_related('tags', 'comments')

# Nested prefetches
Article.objects.prefetch_related('comments__author')
```

### Only and Defer

Load specific fields:

```python
# Only load specific fields
Article.objects.only('title', 'published_date')

# Defer loading specific fields
Article.objects.defer('content')  # Don't load large text field
```

### Database Indexes

```python
class Article(models.Model):
    title = models.CharField(max_length=200, db_index=True)  # Single field
    slug = models.SlugField(unique=True)  # Unique creates index

    class Meta:
        indexes = [
            models.Index(fields=['published_date', '-title']),  # Compound index
            models.Index(fields=['author', 'status']),
        ]
```

### Query Optimization Checklist

- [ ] Use `select_related()` for ForeignKey and OneToOne
- [ ] Use `prefetch_related()` for ManyToMany and reverse relations
- [ ] Add database indexes for frequently queried fields
- [ ] Use `only()` or `defer()` for large fields
- [ ] Use `count()` instead of `len()` on querysets
- [ ] Use `exists()` instead of `count() > 0`
- [ ] Use `iterator()` for large querysets
- [ ] Use bulk operations (`bulk_create`, `bulk_update`)
- [ ] Monitor queries with Django Debug Toolbar

```python
# Use count() not len()
Article.objects.filter(status='PB').count()  # Database COUNT
len(Article.objects.all())  # Loads all records into memory

# Use exists() for existence checks
Article.objects.filter(slug=slug).exists()  # Fast EXISTS query
Article.objects.filter(slug=slug).count() > 0  # Slower COUNT query

# Bulk create
Article.objects.bulk_create([
    Article(title='Title 1'),
    Article(title='Title 2'),
])

# Bulk update (Django 2.2+)
articles = Article.objects.all()
for article in articles:
    article.status = 'PB'
Article.objects.bulk_update(articles, ['status'])
```

---

## Common Patterns and Anti-Patterns

### ✅ Good Patterns

```python
# Use get_or_create for idempotent operations
article, created = Article.objects.get_or_create(
    slug='my-article',
    defaults={'title': 'My Article', 'author': user}
)

# Use update_or_create
article, created = Article.objects.update_or_create(
    slug='my-article',
    defaults={'title': 'Updated Title'}
)

# Use F expressions for atomic updates
from django.db.models import F
Article.objects.filter(id=article_id).update(view_count=F('view_count') + 1)

# Use Q objects for complex queries
from django.db.models import Q
Article.objects.filter(Q(title__contains='Django') | Q(content__contains='Django'))

# Use annotate for aggregation
from django.db.models import Count
authors = Author.objects.annotate(num_articles=Count('articles'))
```

### ❌ Anti-Patterns

```python
# Don't do queries in loops
for article in Article.objects.all():
    author = article.author  # N+1 queries
# Use select_related instead

# Don't load all objects to count
count = len(Article.objects.all())  # Loads all into memory
# Use count() instead
count = Article.objects.count()

# Don't use save() in loops
for article in articles:
    article.status = 'PB'
    article.save()  # Separate query each time
# Use bulk_update instead

# Don't ignore database constraints
# Bad: No unique constraint
slug = models.CharField(max_length=200)
# Good: Database-level constraint
slug = models.SlugField(unique=True)

# Don't use null=True on string fields
# Bad:
title = models.CharField(max_length=200, null=True)
# Good:
title = models.CharField(max_length=200, blank=True, default='')
```
