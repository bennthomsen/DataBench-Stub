"""Admin configuration for temperature app."""

from django.contrib import admin

from .models import TemperatureDataFile, TemperatureReading

class TemperatureReadingInline(admin.TabularInline):
    """Inline admin for temperature readings within a data file."""

    model = TemperatureReading
    extra = 0
    readonly_fields = [
        "measurement_date",
        "publish_time",
        "temperature",
        "temperature_reference_average",
        "temperature_reference_high",
        "temperature_reference_low",
    ]
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False

@admin.register(TemperatureDataFile)
class TemperatureDataFileAdmin(admin.ModelAdmin):
    """Admin interface for TemperatureDataFile model."""

    list_display = [
        "name",
        "uploaded_at",
        "get_reading_count",
        "description",
    ]
    list_filter = ["uploaded_at"]
    search_fields = ["name", "description"]
    readonly_fields = ["uploaded_at"]
    inlines = [TemperatureReadingInline]

    fieldsets = (
        (
            "File Information",
            {
                "fields": ("name", "description", "data_file", "uploaded_at"),
            },
        ),
    )

    def get_reading_count(self, obj):
        """Return the number of readings in this file."""
        return obj.readings.count()

    get_reading_count.short_description = "Readings"

@admin.register(TemperatureReading)
class TemperatureReadingAdmin(admin.ModelAdmin):
    """Admin interface for TemperatureReading model."""

    list_display = [
        "measurement_date",
        "temperature",
        "temperature_reference_average",
        "temperature_reference_high",
        "temperature_reference_low",
        "data_file",
    ]
    list_filter = ["data_file", "measurement_date"]
    search_fields = ["data_file__name"]
    date_hierarchy = "measurement_date"

    readonly_fields = [
        "data_file",
        "measurement_date",
        "publish_time",
        "temperature",
        "temperature_reference_average",
        "temperature_reference_high",
        "temperature_reference_low",
    ]

    def has_add_permission(self, request):
        # Readings should only be created through file upload
        return False