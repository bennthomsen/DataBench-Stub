# DataBench New App Generator Skill

## Purpose

Guide contributors through creating a new Django app in the Stub project,
following established patterns and ensuring consistency across applications.

## When to Activate

Trigger this skill when:

- User says "create a new app", "add an app", "new data type", or similar
- User wants to add a new type of data visualization
- User mentions wanting to upload and display a new kind of data
- User provides a data file and wants to build an app around it

## Core Principles

1. **Follow the temperature app pattern** - Use `stub/temperature/` as the canonical reference
2. **Maintain consistent styling** - Use `stub/static/css/base.css` for all views
3. **Use Bootstrap components** - Cards, tables, buttons, forms from Bootstrap 5
4. **Include Plotly charts** - Reference the `plotly-plots.md` skill for visualization
5. **Always run migrations** - Create and apply database migrations

---

## Workflow Steps

### Step 1: Gather Requirements

**Prompt the user for:**

1. **App name** - Should be lowercase, singular (e.g., `humidity`, `pressure`, `weight`)
2. **Data description** - What does the data represent?
3. **Example data file** - Ask the user to provide a sample JSON file

**Example prompt:**
> To create a new app, I need some information:
> 1. What should the app be called? (lowercase, singular, e.g., "humidity")
> 2. What does this data represent?
> 3. Can you provide an example JSON data file? This will help me design the model.

**Analyze the JSON structure to determine:**
- Field names and types (string, float, int, date, datetime)
- Which field represents the primary measurement
- Which field represents the date/time axis for charts
- Any reference or comparison values

---

### Step 2: Create App Directory Structure

Create the following structure under `stub/`:

```
stub/<app_name>/
├── __init__.py
├── admin.py
├── apps.py
├── forms.py
├── models.py
├── urls.py
├── views.py
├── migrations/
│   └── __init__.py
└── templates/
    └── <app_name>/
        ├── file_list.html
        ├── upload.html
        ├── chart.html
        └── delete_confirm.html
```

---

### Step 3: Create App Files

#### 3.1 `__init__.py`

```python
"""<AppName> app for Stub - handles <description> data upload and visualization."""
```

#### 3.2 `apps.py`

```python
"""App configuration for <app_name> app."""

from django.apps import AppConfig


class <AppName>Config(AppConfig):
    """Configuration for the <app_name> app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "stub.<app_name>"
    verbose_name = "<App Name> Data"
```

#### 3.3 `models.py`

Create two models following the temperature pattern:

```python
"""Models for <app_name> data management."""

from django.db import models


class <AppName>DataFile(models.Model):
    """Represents an uploaded <app_name> data file (JSON format).
    
    Stores the raw uploaded file and metadata about the upload.
    Individual readings are stored in related <AppName>Reading objects.
    """

    name = models.CharField(
        max_length=255,
        help_text="Filename of the uploaded data file.",
    )

    description = models.TextField(
        blank=True,
        help_text="Optional description of the data file.",
    )

    data_file = models.FileField(
        upload_to="<app_name>/uploads/",
        help_text="The uploaded JSON data file.",
    )

    uploaded_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the file was uploaded.",
    )

    class Meta:
        ordering = ["-uploaded_at"]
        verbose_name = "<App Name> Data File"
        verbose_name_plural = "<App Name> Data Files"

    def __str__(self) -> str:
        return f"{self.name} (uploaded {self.uploaded_at.strftime('%Y-%m-%d')})"


class <AppName>Reading(models.Model):
    """Individual <app_name> reading parsed from an uploaded data file.
    
    <Add description based on the data structure>
    """

    data_file = models.ForeignKey(
        <AppName>DataFile,
        on_delete=models.CASCADE,
        related_name="readings",
        help_text="The data file this reading was parsed from.",
    )

    # Add fields based on JSON structure:
    # measurement_date = models.DateField(...)
    # <primary_value> = models.FloatField(...)
    # <additional_fields> = ...

    class Meta:
        ordering = ["measurement_date"]  # Adjust based on date field name
        verbose_name = "<App Name> Reading"
        verbose_name_plural = "<App Name> Readings"
        unique_together = ["data_file", "measurement_date"]  # Adjust as needed

    def __str__(self) -> str:
        return f"{self.measurement_date}: {self.<primary_value>}"
```

#### 3.4 `forms.py`

```python
"""Forms for <app_name> app."""

from django import forms

from .models import <AppName>DataFile


class <AppName>DataFileUploadForm(forms.ModelForm):
    """Form for uploading <app_name> data files."""

    class Meta:
        model = <AppName>DataFile
        fields = ["name", "description", "data_file"]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter a name for this data file",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Optional description",
                    "rows": 3,
                }
            ),
            "data_file": forms.FileInput(
                attrs={
                    "class": "form-control",
                    "accept": ".json",
                }
            ),
        }

    def clean_data_file(self):
        """Validate the uploaded file is a JSON file."""
        data_file = self.cleaned_data.get("data_file")
        if data_file:
            if not data_file.name.endswith(".json"):
                raise forms.ValidationError("Only JSON files are accepted.")
            if data_file.size > 10 * 1024 * 1024:
                raise forms.ValidationError("File size must be less than 10MB.")
        return data_file
```

#### 3.5 `admin.py`

```python
"""Admin configuration for <app_name> app."""

from django.contrib import admin

from .models import <AppName>DataFile, <AppName>Reading


class <AppName>ReadingInline(admin.TabularInline):
    """Inline admin for readings within a data file."""

    model = <AppName>Reading
    extra = 0
    readonly_fields = [
        # List all reading fields here
    ]
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(<AppName>DataFile)
class <AppName>DataFileAdmin(admin.ModelAdmin):
    """Admin interface for <AppName>DataFile model."""

    list_display = [
        "name",
        "uploaded_at",
        "get_reading_count",
        "description",
    ]
    list_filter = ["uploaded_at"]
    search_fields = ["name", "description"]
    readonly_fields = ["uploaded_at"]
    inlines = [<AppName>ReadingInline]

    def get_reading_count(self, obj):
        """Return the number of readings in this file."""
        return obj.readings.count()

    get_reading_count.short_description = "Readings"


@admin.register(<AppName>Reading)
class <AppName>ReadingAdmin(admin.ModelAdmin):
    """Admin interface for <AppName>Reading model."""

    list_display = [
        # List key fields for display
    ]
    list_filter = ["data_file"]
    search_fields = ["data_file__name"]

    def has_add_permission(self, request):
        return False
```

#### 3.6 `urls.py`

```python
"""URL configuration for <app_name> app."""

from django.urls import path

from . import views

app_name = "<app_name>"

urlpatterns = [
    path("", views.file_list, name="file_list"),
    path("upload/", views.upload, name="upload"),
    path("chart/<int:file_id>/", views.chart, name="chart"),
    path("delete/<int:file_id>/", views.delete_file, name="delete"),
]
```

#### 3.7 `views.py`

```python
"""Views for <app_name> app."""

import json
from datetime import datetime

from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
import plotly.graph_objects as go

from .forms import <AppName>DataFileUploadForm
from .models import <AppName>DataFile, <AppName>Reading


def file_list(request):
    """Display list of all uploaded data files."""
    files = <AppName>DataFile.objects.all()
    return render(request, "<app_name>/file_list.html", {"files": files})


def upload(request):
    """Handle upload of data files."""
    if request.method == "POST":
        form = <AppName>DataFileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            data_file = form.save()
            try:
                parse_data_file(data_file)
                messages.success(
                    request,
                    f"Successfully uploaded '{data_file.name}' with "
                    f"{data_file.readings.count()} readings.",
                )
                return redirect("<app_name>:chart", file_id=data_file.id)
            except Exception as e:
                data_file.delete()
                messages.error(request, f"Error parsing file: {str(e)}")
    else:
        form = <AppName>DataFileUploadForm()

    return render(request, "<app_name>/upload.html", {"form": form})


def parse_data_file(data_file: <AppName>DataFile) -> None:
    """Parse a JSON file and create Reading objects.

    Expected JSON format:
    {
        "metadata": {...},
        "data": [
            {
                // Fields based on user's data structure
            },
            ...
        ]
    }
    """
    data_file.data_file.seek(0)
    content = data_file.data_file.read().decode("utf-8")
    json_data = json.loads(content)

    if "data" not in json_data:
        raise ValueError("JSON file must contain a 'data' array")

    readings_to_create = []
    for item in json_data["data"]:
        # Parse and create readings based on JSON structure
        reading = <AppName>Reading(
            data_file=data_file,
            # Map JSON fields to model fields
        )
        readings_to_create.append(reading)

    <AppName>Reading.objects.bulk_create(readings_to_create)


def chart(request, file_id: int):
    """Display chart for a specific data file."""
    data_file = get_object_or_404(<AppName>DataFile, pk=file_id)
    readings = data_file.readings.order_by("measurement_date")

    # Extract data for plotting
    # See plotly-plots.md skill for chart creation guidance

    # Create Plotly figure
    fig = go.Figure()

    # Add traces (reference plotly-plots.md for chart types)
    fig.add_trace(
        go.Scatter(
            x=dates,
            y=values,
            mode="lines+markers",
            name="<Data Series Name>",
            line=dict(color="#667eea", width=2),
            marker=dict(size=4),
        )
    )

    # Update layout
    fig.update_layout(
        title=dict(
            text=f"<Chart Title> - {data_file.name}",
            font=dict(size=20),
        ),
        xaxis_title="Date",
        yaxis_title="<Y Axis Label>",
        hovermode="x unified",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
        ),
        margin=dict(l=60, r=30, t=80, b=60),
        plot_bgcolor="white",
        paper_bgcolor="white",
    )

    fig.update_xaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor="rgba(128, 128, 128, 0.2)",
    )
    fig.update_yaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor="rgba(128, 128, 128, 0.2)",
    )

    plot_json = fig.to_json()

    # Calculate statistics
    stats = {
        "reading_count": len(readings),
        # Add relevant statistics
    }

    context = {
        "data_file": data_file,
        "plot_json": plot_json,
        "stats": stats,
    }
    return render(request, "<app_name>/chart.html", context)


def delete_file(request, file_id: int):
    """Delete a data file and its readings."""
    data_file = get_object_or_404(<AppName>DataFile, pk=file_id)

    if request.method == "POST":
        name = data_file.name
        data_file.delete()
        messages.success(request, f"Successfully deleted '{name}'.")
        return redirect("<app_name>:file_list")

    return render(request, "<app_name>/delete_confirm.html", {"data_file": data_file})
```

---

### Step 4: Create Templates

#### 4.1 `templates/<app_name>/file_list.html`

```html
{% extends "base.html" %}
{% load static %}

{% block title %}<App Name> Data - Stub{% endblock %}

{% block content %}
<div class="row">
    <div class="col-12">
        <div class="d-flex justify-content-between align-items-center mb-4">
            <h1>
                <i class="fas fa-<icon> me-2"></i><App Name> Data Files
            </h1>
            <a href="{% url '<app_name>:upload' %}" class="btn btn-primary">
                <i class="fas fa-upload me-2"></i>Upload New File
            </a>
        </div>
    </div>
</div>

<div class="row">
    <div class="col-12">
        <div class="card">
            <div class="card-header">
                <h3>
                    <i class="fas fa-folder-open"></i>
                    Uploaded Files
                </h3>
            </div>
            <div class="card-body">
                {% if files %}
                <div class="table-responsive">
                    <table class="table table-hover">
                        <thead>
                            <tr>
                                <th>Name</th>
                                <th>Uploaded</th>
                                <th>Readings</th>
                                <th>Description</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for file in files %}
                            <tr>
                                <td>
                                    <a href="{% url '<app_name>:chart' file.id %}">
                                        {{ file.name }}
                                    </a>
                                </td>
                                <td>{{ file.uploaded_at|date:"M d, Y H:i" }}</td>
                                <td>{{ file.readings.count }}</td>
                                <td>{{ file.description|default:"-"|truncatewords:10 }}</td>
                                <td>
                                    <a href="{% url '<app_name>:chart' file.id %}" 
                                       class="btn btn-sm btn-outline-primary">
                                        <i class="fas fa-chart-line"></i> View
                                    </a>
                                    <a href="{% url '<app_name>:delete' file.id %}" 
                                       class="btn btn-sm btn-outline-danger">
                                        <i class="fas fa-trash"></i>
                                    </a>
                                </td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
                {% else %}
                <div class="text-center py-5">
                    <i class="fas fa-inbox fa-3x text-muted mb-3"></i>
                    <p class="text-muted">No data files uploaded yet.</p>
                    <a href="{% url '<app_name>:upload' %}" class="btn btn-primary">
                        <i class="fas fa-upload me-2"></i>Upload Your First File
                    </a>
                </div>
                {% endif %}
            </div>
        </div>
    </div>
</div>
{% endblock %}
```

#### 4.2 `templates/<app_name>/upload.html`

**Important:** Include the upload spinner modal to show a loading indicator during file upload and processing.

```html
{% extends "base.html" %}
{% load static %}

{% block title %}Upload <App Name> Data - Stub{% endblock %}

{% block content %}
{% include "core/includes/upload_spinner_modal.html" %}

<div class="row">
    <div class="col-12">
        <nav aria-label="breadcrumb">
            <ol class="breadcrumb">
                <li class="breadcrumb-item"><a href="{% url 'core:home' %}">Home</a></li>
                <li class="breadcrumb-item"><a href="{% url '<app_name>:file_list' %}"><App Name> Data</a></li>
                <li class="breadcrumb-item active">Upload</li>
            </ol>
        </nav>
        
        <h1 class="mb-4">
            <i class="fas fa-upload me-2"></i>Upload <App Name> Data
        </h1>
    </div>
</div>

<div class="row">
    <div class="col-lg-8">
        <div class="card">
            <div class="card-header">
                <h3>
                    <i class="fas fa-file-upload"></i>
                    Select File
                </h3>
            </div>
            <div class="card-body">
                <form method="post" enctype="multipart/form-data" class="upload-form">
                    {% csrf_token %}
                    
                    <div class="mb-3">
                        <label for="id_name" class="form-label">Name *</label>
                        {{ form.name }}
                        {% if form.name.errors %}
                        <div class="text-danger">{{ form.name.errors }}</div>
                        {% endif %}
                    </div>
                    
                    <div class="mb-3">
                        <label for="id_description" class="form-label">Description</label>
                        {{ form.description }}
                    </div>
                    
                    <div class="mb-3">
                        <label for="id_data_file" class="form-label">Data File (JSON) *</label>
                        {{ form.data_file }}
                        {% if form.data_file.errors %}
                        <div class="text-danger">{{ form.data_file.errors }}</div>
                        {% endif %}
                        <div class="form-text">Upload a JSON file containing your data.</div>
                    </div>
                    
                    <div class="d-flex gap-2">
                        <button type="submit" class="btn btn-primary">
                            <i class="fas fa-upload me-2"></i>Upload
                        </button>
                        <a href="{% url '<app_name>:file_list' %}" class="btn btn-outline-secondary">
                            Cancel
                        </a>
                    </div>
                </form>
            </div>
        </div>
    </div>
    
    <div class="col-lg-4">
        <div class="card">
            <div class="card-header">
                <h3>
                    <i class="fas fa-info-circle"></i>
                    Expected Format
                </h3>
            </div>
            <div class="card-body">
                <p>Upload a JSON file with the following structure:</p>
                <pre class="bg-light p-3 rounded"><code>{
  "data": [
    {
      // Your data fields here
    }
  ]
}</code></pre>
            </div>
        </div>
    </div>
</div>
{% endblock %}
```

> **Upload Spinner Modal:** The `upload-form` class triggers the spinner modal automatically on form submit.
> To customize the message, use: `{% include "core/includes/upload_spinner_modal.html" with upload_spinner_message="Custom message..." %}`

#### 4.3 `templates/<app_name>/chart.html`

Reference `stub/temperature/templates/temperature/chart.html` for the complete structure. Include:
- Statistics cards row
- Chart container with Plotly
- File information card
- Legend card

#### 4.4 `templates/<app_name>/delete_confirm.html`

```html
{% extends "base.html" %}

{% block title %}Delete {{ data_file.name }} - Stub{% endblock %}

{% block content %}
<div class="row">
    <div class="col-md-6 offset-md-3">
        <div class="card">
            <div class="card-header bg-danger text-white">
                <h3>
                    <i class="fas fa-exclamation-triangle"></i>
                    Confirm Deletion
                </h3>
            </div>
            <div class="card-body">
                <p>Are you sure you want to delete <strong>{{ data_file.name }}</strong>?</p>
                <p class="text-muted">
                    This will permanently delete the file and all {{ data_file.readings.count }} 
                    associated readings. This action cannot be undone.
                </p>
                
                <form method="post">
                    {% csrf_token %}
                    <div class="d-flex gap-2">
                        <button type="submit" class="btn btn-danger">
                            <i class="fas fa-trash me-2"></i>Delete
                        </button>
                        <a href="{% url '<app_name>:file_list' %}" class="btn btn-outline-secondary">
                            Cancel
                        </a>
                    </div>
                </form>
            </div>
        </div>
    </div>
</div>
{% endblock %}
```

---

### Step 5: Register the App

Add to `stub/config/settings.py` in `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    # ... Django apps ...
    # Stub apps
    "stub.core",
    "stub.temperature",
    "stub.<app_name>",  # Add new app here
]
```

---

### Step 6: Wire Up URLs

Add to `stub/config/urls.py`:

```python
urlpatterns = [
    # ... existing paths ...
    path("<app_name>/", include("stub.<app_name>.urls")),
]
```

---

### Step 7: Run Migrations

Execute the following command to create database migrations:

```bash
python manage.py makemigrations <app_name>
```

**Important:** Review the generated migration file to ensure it correctly represents the model.

---

### Step 8: Prompt User to Apply Migrations

After creating migrations, prompt the user:

> Migrations have been created. To apply them to the database, run:
> ```bash
> python manage.py migrate
> ```
> Would you like me to run this command now?

---

### Step 9: Update Navigation

Add a link to the navbar in `stub/config/templates/base.html`:

```html
<li class="nav-item">
    <a class="nav-link" href="{% url '<app_name>:file_list' %}">
        <i class="fas fa-<icon> me-1"></i><App Name> Data
    </a>
</li>
```

---

## Styling Guidelines

All templates must use styles from `stub/static/css/base.css`:

| Element | Class/Style |
| ------- | ----------- |
| Cards | `.card` with `.card-header` and `.card-body` |
| Primary buttons | `.btn-primary` (uses project gradient) |
| Tables | `.table .table-hover` inside `.table-responsive` |
| Icons | FontAwesome 6.x (`fas fa-*`) |
| Spacing | Bootstrap utilities (`mb-4`, `py-3`, etc.) |

**Color Palette:**
- Primary: `#667eea`
- Secondary: `#764ba2`
- Success: `#28a745`
- Danger: `#dc3545`

If new styles are needed, add them to `stub/static/css/base.css` with clear comments.

---

## Quick Reference Checklist

When creating a new app, ensure all items are completed:

- [ ] Created app directory structure
- [ ] Created `__init__.py` with docstring
- [ ] Created `apps.py` with AppConfig
- [ ] Created `models.py` with DataFile and Reading models
- [ ] Created `forms.py` with upload form
- [ ] Created `admin.py` with admin configuration
- [ ] Created `views.py` with all views
- [ ] Created `urls.py` with URL patterns
- [ ] Created `migrations/__init__.py`
- [ ] Created all templates (file_list, upload, chart, delete_confirm) with upload spinner
- [ ] Added app to `INSTALLED_APPS` in settings.py
- [ ] Added URL include in main urls.py
- [ ] Ran `makemigrations`
- [ ] Prompted user to run `migrate`
- [ ] Added navigation link to base.html

---

## Canonical Reference

For a complete working example, see the temperature app:

- **Models**: `stub/temperature/models.py`
- **Views**: `stub/temperature/views.py`
- **Templates**: `stub/temperature/templates/temperature/`
- **Charts**: Reference `plotly-plots.md` skill