"""Views for temperature app."""

import json
from datetime import datetime

from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
import plotly.graph_objects as go

from .forms import TemperatureDataFileUploadForm
from .models import TemperatureDataFile, TemperatureReading

def file_list(request):
    """Display list of all uploaded temperature data files."""
    files = TemperatureDataFile.objects.all()
    return render(request, "temperature/file_list.html", {"files": files})

def upload(request):
    """Handle upload of temperature data files."""
    if request.method == "POST":
        form = TemperatureDataFileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            # Save the file
            data_file = form.save()

            # Parse the JSON and create temperature readings
            try:
                parse_temperature_file(data_file)
                messages.success(
                    request,
                    f"Successfully uploaded '{data_file.name}' with "
                    f"{data_file.readings.count()} temperature readings.",
                )
                return redirect("temperature:chart", file_id=data_file.id)
            except Exception as e:
                # If parsing fails, delete the file and show error
                data_file.delete()
                messages.error(request, f"Error parsing file: {str(e)}")
    else:
        form = TemperatureDataFileUploadForm()

    return render(request, "temperature/upload.html", {"form": form})

def parse_temperature_file(data_file: TemperatureDataFile) -> None:
    """Parse a temperature JSON file and create TemperatureReading objects.

    Expected JSON format:
    {
        "metadata": {...},
        "data": [
            {
                "measurementDate": "2025-12-31",
                "publishTime": "2025-12-31T16:45:00Z",
                "temperature": 2.7,
                "temperatureReferenceAverage": 6.1,
                "temperatureReferenceHigh": 9,
                "temperatureReferenceLow": 1.6
            },
            ...
        ]
    }
    """
    # Read and parse JSON
    data_file.data_file.seek(0)
    content = data_file.data_file.read().decode("utf-8")
    json_data = json.loads(content)

    if "data" not in json_data:
        raise ValueError("JSON file must contain a 'data' array")

    readings_to_create = []
    for item in json_data["data"]:
        # Parse dates
        measurement_date = datetime.strptime(
            item["measurementDate"], "%Y-%m-%d"
        ).date()
        publish_time = datetime.fromisoformat(
            item["publishTime"].replace("Z", "+00:00")
        )

        reading = TemperatureReading(
            data_file=data_file,
            measurement_date=measurement_date,
            publish_time=publish_time,
            temperature=item["temperature"],
            temperature_reference_average=item["temperatureReferenceAverage"],
            temperature_reference_high=item["temperatureReferenceHigh"],
            temperature_reference_low=item["temperatureReferenceLow"],
        )
        readings_to_create.append(reading)

    # Bulk create all readings
    TemperatureReading.objects.bulk_create(readings_to_create)

def chart(request, file_id: int):
    """Display temperature chart for a specific data file."""
    data_file = get_object_or_404(TemperatureDataFile, pk=file_id)
    readings = data_file.readings.order_by("measurement_date")

    # Extract data for plotting
    dates = [r.measurement_date.isoformat() for r in readings]
    temperatures = [r.temperature for r in readings]
    ref_averages = [r.temperature_reference_average for r in readings]
    ref_highs = [r.temperature_reference_high for r in readings]
    ref_lows = [r.temperature_reference_low for r in readings]

    # Create Plotly figure
    fig = go.Figure()

    # Add reference band (high/low range)
    fig.add_trace(
        go.Scatter(
            x=dates + dates[::-1],
            y=ref_highs + ref_lows[::-1],
            fill="toself",
            fillcolor="rgba(173, 216, 230, 0.3)",
            line=dict(color="rgba(173, 216, 230, 0)"),
            name="Reference Range (High-Low)",
            hoverinfo="skip",
        )
    )

    # Add reference average line
    fig.add_trace(
        go.Scatter(
            x=dates,
            y=ref_averages,
            mode="lines",
            name="Reference Average",
            line=dict(color="rgba(100, 100, 100, 0.5)", dash="dash"),
        )
    )

    # Add reference high line
    fig.add_trace(
        go.Scatter(
            x=dates,
            y=ref_highs,
            mode="lines",
            name="Reference High",
            line=dict(color="rgba(255, 100, 100, 0.4)", dash="dot"),
        )
    )

    # Add reference low line
    fig.add_trace(
        go.Scatter(
            x=dates,
            y=ref_lows,
            mode="lines",
            name="Reference Low",
            line=dict(color="rgba(100, 100, 255, 0.4)", dash="dot"),
        )
    )

    # Add actual temperature line (on top)
    fig.add_trace(
        go.Scatter(
            x=dates,
            y=temperatures,
            mode="lines+markers",
            name="Actual Temperature",
            line=dict(color="#667eea", width=2),
            marker=dict(size=4),
        )
    )

    # Update layout
    fig.update_layout(
        title=dict(
            text=f"UK Temperature Data - {data_file.name}",
            font=dict(size=20),
        ),
        xaxis_title="Date",
        yaxis_title="Temperature (°C)",
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

    # Add gridlines
    fig.update_xaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor="rgba(128, 128, 128, 0.2)",
        showline=True,
        linewidth=1,
        linecolor="rgba(128, 128, 128, 0.4)",
    )
    fig.update_yaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor="rgba(128, 128, 128, 0.2)",
        showline=True,
        linewidth=1,
        linecolor="rgba(128, 128, 128, 0.4)",
    )

    # Convert to JSON for template
    plot_json = json.dumps(fig.to_dict())

    # Calculate statistics
    if temperatures:
        stats = {
            "min_temp": min(temperatures),
            "max_temp": max(temperatures),
            "avg_temp": sum(temperatures) / len(temperatures),
            "reading_count": len(temperatures),
            "date_range_start": dates[0] if dates else None,
            "date_range_end": dates[-1] if dates else None,
        }
    else:
        stats = None

    context = {
        "data_file": data_file,
        "plot_json": plot_json,
        "stats": stats,
    }
    return render(request, "temperature/chart.html", context)

def delete_file(request, file_id: int):
    """Delete a temperature data file and its readings."""
    data_file = get_object_or_404(TemperatureDataFile, pk=file_id)

    if request.method == "POST":
        name = data_file.name
        data_file.delete()
        messages.success(request, f"Successfully deleted '{name}'.")
        return redirect("temperature:file_list")

    return render(request, "temperature/delete_confirm.html", {"data_file": data_file})