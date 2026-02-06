"""App configuration for generation app."""

from django.apps import AppConfig


class GenerationConfig(AppConfig):
    """Configuration for the generation app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "stub.generation"
    verbose_name = "Electricity Generation Data"