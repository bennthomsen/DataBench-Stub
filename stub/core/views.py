"""Views for core app."""

from django.shortcuts import render

from stub.temperature.models import TemperatureDataFile

def home(request):
    """Home page view showing dashboard with recent data files."""
    recent_files = TemperatureDataFile.objects.order_by("-uploaded_at")[:5]
    
    context = {
        "recent_files": recent_files,
        "total_files": TemperatureDataFile.objects.count(),
    }
    return render(request, "core/home.html", context)