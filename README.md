# Stub - Simplified Django Data Visualization Framework

DataBench-Stub is a lightweight Django-based web application framework for data management, analysis and visualization. It provides a simple setup with:

- **SQLite database** - No external database server required
- **Local file storage** - Files stored in the `media/` directory
- **No authentication** - All pages publicly accessible
- **Plotly charts** - Interactive data visualization

## Features

- **Temperature Data App:**
  - Upload and parse JSON temperature data files
  - Interactive Plotly temperature charts with:
    - Actual temperature vs date
    - Historical reference average, high, and low bands
- Django admin interface for data management
- Bootstrap 5 responsive UI

## Quick Start

### Prerequisites

- Python 3.12 or higher
- uv (see [Installing uv](#installing-uv) below)

### Installing uv

uv is a fast Python package and project manager. Install it using one of the methods described in the [official installation guide](https://docs.astral.sh/uv/getting-started/installation/#installation-methods).

**Quick install options:**

Windows (PowerShell):
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Linux/macOS:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Installation

1. **Clone the repository:**
   ```bash
   cd Stub
   ```

2. **Create a virtual environment and install dependencies:**
   ```bash
   uv sync
   ```
   This creates a `.venv` directory and installs all dependencies in editable mode.

3. **Run database migrations:**
   ```bash
   .venv\Scripts\activate  # Windows
   # source .venv/bin/activate  # Linux/Mac
   python manage.py migrate
   ```

4. **Create an admin superuser (optional, for admin access):**
   ```bash
   python manage.py createsuperuser
   ```
   You will be prompted to enter:
   - **Username** - choose a username for the admin account
   - **Email address** - optional, press Enter to skip
   - **Password** - enter twice to confirm (input is hidden)
   
   Once created, you can log into the Django admin panel at http://127.0.0.1:8000/admin/

5. **Start the development server:**
   ```bash
   python manage.py runserver
   ```

6. **Open your browser:**
   - Home page: http://127.0.0.1:8000/
   - Admin panel: http://127.0.0.1:8000/admin/

## Project Structure

```
Stub/
├── manage.py                 # Django management script
├── pyproject.toml            # Package configuration
├── README.md                 # This file
├── db.sqlite3                # SQLite database (created after migrate)
├── media/                    # Uploaded files storage
└── stub/
    ├── __init__.py
    ├── config/               # Django settings and configuration
    │   ├── settings.py       # Main settings file
    │   ├── urls.py           # URL routing
    │   ├── wsgi.py           # WSGI application
    │   └── templates/        # Base templates
    │       └── base.html     # Bootstrap base template
    ├── core/                 # Core app (home page)
    │   ├── views.py
    │   ├── urls.py
    │   └── templates/
    │       └── core/
    │           └── home.html # Dashboard
    ├── temperature/          # Temperature data app
    │   ├── models.py         # TemperatureDataFile, TemperatureReading
    │   ├── views.py          # Upload, list, chart views
    │   ├── forms.py          # File upload form
    │   ├── admin.py          # Admin interface
    │   └── templates/
    │       └── temperature/
    │           ├── upload.html
    │           ├── file_list.html
    │           └── chart.html
    └── static/               # Static files (CSS, JS)
```

## Usage

### Uploading Temperature Data

1. Go to **Temperature Data** → **Upload New File**
2. Enter a name and optional description
3. Select a JSON file with the following format:

```json
{
  "metadata": {
    "datasets": ["TEMP"]
  },
  "data": [
    {
      "measurementDate": "2025-12-31",
      "publishTime": "2025-12-31T16:45:00Z",
      "temperature": 2.7,
      "temperatureReferenceAverage": 6.1,
      "temperatureReferenceHigh": 9,
      "temperatureReferenceLow": 1.6
    }
  ]
}
```

4. Click **Upload & Parse**
5. View the interactive temperature chart

### Sample Data

A sample UK temperature data file (`UK_temp_2025.json`) is included in the project root for testing.

## Development

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
ruff check .
ruff format .
```

### Adding New Apps

1. Create the app structure:
   ```bash
   mkdir -p stub/myapp/templates/myapp
   ```

2. Add models, views, forms, and URLs following the `temperature` app pattern

3. Register the app in `stub/config/settings.py`:
   ```python
   INSTALLED_APPS = [
       ...
       "stub.myapp",
   ]
   ```

4. Add URL routing in `stub/config/urls.py`:
   ```python
   urlpatterns = [
       ...
       path("myapp/", include("stub.myapp.urls")),
   ]
   ```

5. Run migrations:
   ```bash
   python manage.py makemigrations myapp
   python manage.py migrate
   ```

## Configuration

Key settings in `stub/config/settings.py`:

| Setting | Default | Description |
|---------|---------|-------------|
| `DEBUG` | `True` | Debug mode (disable in production) |
| `DATABASES` | SQLite | Database configuration |
| `MEDIA_ROOT` | `media/` | File upload directory |
| `STATIC_ROOT` | `staticfiles/` | Collected static files |

## License

MIT License - feel free to use this as a starting point for your own projects.

## Acknowledgments

- Inspired by [DataBench](https://github.com/your-org/DataBench)
- Built with [Django](https://www.djangoproject.com/)
- Charts powered by [Plotly.js](https://plotly.com/javascript/)
- UI styled with [Bootstrap 5](https://getbootstrap.com/)