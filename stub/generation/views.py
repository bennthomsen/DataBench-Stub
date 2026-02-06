"""Views for generation app."""

import json
from datetime import datetime
from collections import defaultdict

from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum
import plotly.graph_objects as go

from .forms import GenerationDataFileUploadForm
from .models import GenerationDataFile, GenerationReading

# Define colors for each power source type
PSR_COLORS = {
    "Biomass": "#2ecc71",
    "Fossil Gas": "#e74c3c",
    "Fossil Hard coal": "#34495e",
    "Fossil Oil": "#8e44ad",
    "Hydro Pumped Storage": "#3498db",
    "Hydro Run-of-river and poundage": "#1abc9c",
    "Nuclear": "#f39c12",
    "Other": "#95a5a6",
    "Solar": "#f1c40f",
    "Wind Offshore": "#667eea",
    "Wind Onshore": "#764ba2",
}

def file_list(request):
    """Display list of all uploaded data files."""
    files = GenerationDataFile.objects.all()
    return render(request, "generation/file_list.html", {"files": files})

def upload(request):
    """Handle upload of data files."""
    if request.method == "POST":
        form = GenerationDataFileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            data_file = form.save()
            try:
                parse_data_file(data_file)
                messages.success(
                    request,
                    f"Successfully uploaded '{data_file.name}' with "
                    f"{data_file.readings.count()} readings.",
                )
                return redirect("generation:chart", file_id=data_file.id)
            except Exception as e:
                data_file.delete()
                messages.error(request, f"Error parsing file: {str(e)}")
    else:
        form = GenerationDataFileUploadForm()

    return render(request, "generation/upload.html", {"form": form})

def parse_data_file(data_file: GenerationDataFile) -> None:
    """Parse a JSON file and create GenerationReading objects.

    Expected JSON format:
    {
        "metadata": {...},
        "data": [
            {
                "startTime": "2025-01-01T00:00:00Z",
                "settlementPeriod": 1,
                "data": [
                    {
                        "businessType": "Production",
                        "psrType": "Biomass",
                        "quantity": 1716
                    },
                    ...
                ]
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
        start_time_str = item.get("startTime")
        settlement_period = item.get("settlementPeriod", 1)
        
        # Parse the start time
        start_time = datetime.fromisoformat(start_time_str.replace("Z", "+00:00"))
        
        # Process each generation reading for this time period
        for gen_data in item.get("data", []):
            reading = GenerationReading(
                data_file=data_file,
                start_time=start_time,
                settlement_period=settlement_period,
                business_type=gen_data.get("businessType", ""),
                psr_type=gen_data.get("psrType", ""),
                quantity=gen_data.get("quantity", 0),
            )
            readings_to_create.append(reading)

    GenerationReading.objects.bulk_create(readings_to_create)

def chart(request, file_id: int):
    """Display chart for a specific data file showing generation mix vs date."""
    data_file = get_object_or_404(GenerationDataFile, pk=file_id)
    
    # Get all readings grouped by date and psr_type
    readings = data_file.readings.order_by("start_time")
    
    # Aggregate data by date and psr_type
    data_by_date = defaultdict(lambda: defaultdict(int))
    all_psr_types = set()
    
    for reading in readings:
        date_key = reading.start_time.date()
        data_by_date[date_key][reading.psr_type] += reading.quantity
        all_psr_types.add(reading.psr_type)
    
    # Sort dates and psr_types
    dates = sorted(data_by_date.keys())
    psr_types = sorted(all_psr_types)
    
    # Create Plotly figure with stacked area chart
    fig = go.Figure()
    
    for psr_type in psr_types:
        values = [data_by_date[date][psr_type] for date in dates]
        color = PSR_COLORS.get(psr_type, "#999999")
        
        fig.add_trace(
            go.Scatter(
                x=dates,
                y=values,
                mode="lines",
                name=psr_type,
                stackgroup="one",
                line=dict(width=0.5, color=color),
                fillcolor=color,
                hovertemplate=f"{psr_type}<br>%{{x}}<br>%{{y:,.0f}} MW<extra></extra>",
            )
        )
    
    # Update layout
    fig.update_layout(
        title=dict(
            text=f"UK Electricity Generation Mix - {data_file.name}",
            font=dict(size=20),
        ),
        xaxis_title="Date",
        yaxis_title="Generation (MW)",
        hovermode="x unified",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.3,
            xanchor="center",
            x=0.5,
        ),
        margin=dict(l=60, r=30, t=80, b=120),
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
    total_readings = readings.count()
    date_range = f"{dates[0]} to {dates[-1]}" if dates else "N/A"
    
    # Calculate totals by source
    totals_by_source = (
        readings.values("psr_type")
        .annotate(total=Sum("quantity"))
        .order_by("-total")
    )
    
    # Calculate overall total
    overall_total = sum(item["total"] for item in totals_by_source)
    
    # Add percentage to each source
    source_stats = []
    for item in totals_by_source:
        percentage = (item["total"] / overall_total * 100) if overall_total > 0 else 0
        source_stats.append({
            "psr_type": item["psr_type"],
            "total": item["total"],
            "percentage": percentage,
            "color": PSR_COLORS.get(item["psr_type"], "#999999"),
        })
    
    stats = {
        "total_readings": total_readings,
        "date_range": date_range,
        "num_days": len(dates),
        "source_stats": source_stats,
        "overall_total": overall_total,
    }
    
    context = {
        "data_file": data_file,
        "plot_json": plot_json,
        "stats": stats,
    }
    return render(request, "generation/chart.html", context)

def delete_file(request, file_id: int):
    """Delete a data file and its readings."""
    data_file = get_object_or_404(GenerationDataFile, pk=file_id)

    if request.method == "POST":
        name = data_file.name
        data_file.delete()
        messages.success(request, f"Successfully deleted '{name}'.")
        return redirect("generation:file_list")

    return render(request, "generation/delete_confirm.html", {"data_file": data_file})