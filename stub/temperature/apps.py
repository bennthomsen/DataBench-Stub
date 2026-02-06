"""App configuration for temperature app."""

from django.apps import AppConfig

class TemperatureConfig(AppConfig):
    """Configuration for the temperature app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "stub.temperature"
    verbose_name = "Temperature Data"