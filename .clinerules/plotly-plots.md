# DataBench Plotly Visualization Skill

## Purpose

Guide contributors to add interactive data visualizations using Plotly, following
the project's established patterns and ensuring consistency across the application.

## When to Activate

Trigger this skill when:

- User says "add a plot", "add a chart", "visualize data", "create a graph", or similar
- User asks about data visualization, dashboards, or graphical display
- User modifies a view that should display data graphically
- User mentions wanting to show data trends, comparisons, or distributions

## Core Principles

1. **Always use Plotly** - Do not use matplotlib, seaborn, or other libraries
2. **Server-side figure creation** - Build charts in Python views using `plotly.graph_objects`
3. **JSON serialization** - Pass chart data to templates as JSON
4. **Client-side rendering** - Use Plotly.js CDN in templates for rendering
5. **Follow existing patterns** - Reference `temperature/views.py` and `temperature/templates/temperature/chart.html`

---

## Architecture Pattern

The project follows this flow for all Plotly visualizations:

```
Django View (Python)          →    Template (HTML/JS)
─────────────────────────────      ─────────────────────
1. Query data from database        1. Load Plotly.js from CDN
2. Create go.Figure()              2. Parse JSON from Django
3. Add traces and layout           3. Call Plotly.newPlot()
4. Serialize: fig.to_json()
5. Pass to template context
```

---

## Workflow Steps

### Step 1: Identify Requirements

Determine what needs to be visualized:

- **Data source**: Model query, file upload, API response?
- **Chart type**: Line, bar, scatter, pie, heatmap?
- **Interactivity**: Hover info, zoom, pan, click events?

### Step 2: Create or Update the View

Add Plotly figure creation to your Django view:

```python
"""Views for <app_name> app."""
from django.shortcuts import render
import plotly.graph_objects as go

def chart_view(request):
    """Display <description> chart."""
    # 1. Query your data
    data = YourModel.objects.all()
    
    # 2. Extract data for plotting
    x_values = [item.x_field for item in data]
    y_values = [item.y_field for item in data]
    
    # 3. Create Plotly figure
    fig = go.Figure()
    
    # 4. Add traces
    fig.add_trace(
        go.Scatter(  # or go.Bar, go.Pie, etc.
            x=x_values,
            y=y_values,
            mode="lines+markers",
            name="Data Series",
            line=dict(color="#667eea", width=2),
            marker=dict(size=6),
        )
    )
    
    # 5. Update layout
    fig.update_layout(
        title=dict(text="Chart Title", font=dict(size=20)),
        xaxis_title="X Axis Label",
        yaxis_title="Y Axis Label",
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
    
    # 6. Add gridlines (optional but recommended)
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
    
    # 7. Serialize to JSON
    plot_json = fig.to_json()
    
    return render(request, "<app>/chart.html", {"plot_json": plot_json})
```

### Step 3: Create the Template

Create a template that renders the Plotly chart:

```html
{% extends "base.html" %}

{% block title %}Chart Title - Stub{% endblock %}

{% block content %}
<div class="row">
    <div class="col-12">
        <div class="card">
            <div class="card-header">
                <h3>
                    <i class="fas fa-chart-line"></i>
                    Chart Title
                </h3>
            </div>
            <div class="card-body">
                <div id="chart-container" style="width: 100%; height: 500px;"></div>
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block extra_js %}
<!-- Plotly.js CDN -->
<script src="https://cdn.plot.ly/plotly-2.32.0.min.js"></script>

<script>
document.addEventListener('DOMContentLoaded', function() {
    // Parse the plot data from Django
    var plotData = {{ plot_json|safe }};
    
    // Render the plot
    Plotly.newPlot('chart-container', plotData.data, plotData.layout, {
        responsive: true,
        displayModeBar: true,
        modeBarButtonsToRemove: ['lasso2d', 'select2d'],
        displaylogo: false
    });
});
</script>
{% endblock %}
```

### Step 4: Wire Up URLs

Add the view to your app's `urls.py`:

```python
from django.urls import path
from . import views

app_name = "<app_name>"

urlpatterns = [
    path("chart/", views.chart_view, name="chart"),
]
```

---

## Common Chart Types

### Line Chart (Time Series)

```python
fig.add_trace(
    go.Scatter(
        x=dates,
        y=values,
        mode="lines+markers",
        name="Series Name",
        line=dict(color="#667eea", width=2),
    )
)
```

### Bar Chart (Comparisons)

```python
fig.add_trace(
    go.Bar(
        x=categories,
        y=values,
        name="Series Name",
        marker_color="#667eea",
    )
)
```

### Scatter Plot (Correlations)

```python
fig.add_trace(
    go.Scatter(
        x=x_values,
        y=y_values,
        mode="markers",
        name="Data Points",
        marker=dict(size=10, color=color_values, colorscale="Viridis"),
    )
)
```

### Pie Chart (Proportions)

```python
fig.add_trace(
    go.Pie(
        labels=categories,
        values=values,
        hole=0.3,  # Makes it a donut chart
    )
)
```

### Filled Area / Range Band

```python
# Useful for confidence intervals or reference ranges
fig.add_trace(
    go.Scatter(
        x=dates + dates[::-1],  # x, then x reversed
        y=upper_bound + lower_bound[::-1],  # upper, then lower reversed
        fill="toself",
        fillcolor="rgba(173, 216, 230, 0.3)",
        line=dict(color="rgba(173, 216, 230, 0)"),
        name="Range",
        hoverinfo="skip",
    )
)
```

---

## Quick Reference

| Data Pattern | Chart Type | Plotly Class |
| ------------ | ---------- | ------------ |
| Change over time | Line chart | `go.Scatter(mode="lines")` |
| Category comparison | Bar chart | `go.Bar` |
| Part-to-whole | Pie/Donut chart | `go.Pie` |
| Two variable relationship | Scatter plot | `go.Scatter(mode="markers")` |
| Distribution | Histogram | `go.Histogram` |
| Range/confidence | Filled area | `go.Scatter(fill="toself")` |
| Multiple series | Multi-trace | Add multiple `fig.add_trace()` |

---

## Project Color Palette

Use these colors for consistency with the DataBench theme:

| Use Case | Color Code |
| -------- | ---------- |
| Primary series | `#667eea` |
| Secondary series | `#764ba2` |
| Success/positive | `#28a745` |
| Warning | `#ffc107` |
| Danger/negative | `#dc3545` |
| Muted/reference | `rgba(100, 100, 100, 0.5)` |
| Fill areas | Use 0.3 alpha, e.g., `rgba(102, 126, 234, 0.3)` |

---

## Best Practices

### Responsive Design

Always include responsive config in `Plotly.newPlot()`:

```javascript
Plotly.newPlot('container', plotData.data, plotData.layout, {
    responsive: true,
    displayModeBar: true,
    displaylogo: false
});
```

### Accessibility

- Use sufficient color contrast
- Include text labels where possible
- Provide hover info with `hovertemplate`
- Add `aria-label` to chart container

### Performance

- For large datasets (>10,000 points), use `go.Scattergl` instead of `go.Scatter`
- Limit initial data load; consider pagination or date filtering
- Use `hoverinfo="skip"` for decorative traces (like range bands)

### Statistics Cards

Pair charts with summary statistics cards (see `temperature/chart.html`):

```html
<div class="row mb-4">
    <div class="col-md-3">
        <div class="card text-center">
            <div class="card-body py-3">
                <h4 class="text-primary mb-0">{{ stats.count }}</h4>
                <small class="text-muted">Total Records</small>
            </div>
        </div>
    </div>
    <!-- Add more stat cards -->
</div>
```

---

## Canonical Example

For a complete working example, see:

- **View**: `stub/temperature/views.py` → `chart()` function
- **Template**: `stub/temperature/templates/temperature/chart.html`

This implementation demonstrates:
- Multi-trace charts (actual values + reference lines + range band)
- Proper layout configuration
- Statistics calculation and display
- Responsive design
- Legend customization