"""Admin configuration for generation app."""

from django.contrib import admin

from .models import GenerationDataFile, GenerationReading

class GenerationReadingInline(admin.TabularInline):
    """Inline admin for readings within a data file."""

    model = GenerationReading
    extra = 0
    readonly_fields = [
        "start_time",
        "settlement_period",
        "business_type",
        "psr_type",
        "quantity",
    ]
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False

@admin.register(GenerationDataFile)
class GenerationDataFileAdmin(admin.ModelAdmin):
    """Admin interface for GenerationDataFile model."""

    list_display = [
        "name",
        "uploaded_at",
        "get_reading_count",
        "description",
    ]
    list_filter = ["uploaded_at"]
    search_fields = ["name", "description"]
    readonly_fields = ["uploaded_at"]
    inlines = [GenerationReadingInline]

    def get_reading_count(self, obj):
        """Return the number of readings in this file."""
        return obj.readings.count()

    get_reading_count.short_description = "Readings"

@admin.register(GenerationReading)
class GenerationReadingAdmin(admin.ModelAdmin):
    """Admin interface for GenerationReading model."""

    list_display = [
        "start_time",
        "psr_type",
        "quantity",
        "business_type",
        "data_file",
    ]
    list_filter = ["psr_type", "business_type", "data_file"]
    search_fields = ["psr_type", "data_file__name"]

    def has_add_permission(self, request):
        return False