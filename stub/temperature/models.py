"""Models for temperature data management."""

from django.db import models

class TemperatureDataFile(models.Model):
    """Represents an uploaded temperature data file (JSON format).
    
    Stores the raw uploaded file and metadata about the upload.
    Individual temperature readings are stored in related TemperatureReading objects.
    """

    name = models.CharField(
        max_length=255,
        help_text="Filename of the uploaded data file.",
    )
    """Filename of the uploaded data file."""

    description = models.TextField(
        blank=True,
        help_text="Optional description of the data file.",
    )
    """Optional description of the data file."""

    data_file = models.FileField(
        upload_to="temperature/uploads/",
        help_text="The uploaded JSON data file.",
    )
    """The uploaded JSON data file."""

    uploaded_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the file was uploaded.",
    )
    """When the file was uploaded."""

    class Meta:
        ordering = ["-uploaded_at"]
        verbose_name = "Temperature Data File"
        verbose_name_plural = "Temperature Data Files"

    def __str__(self) -> str:
        return f"{self.name} (uploaded {self.uploaded_at.strftime('%Y-%m-%d')})"

class TemperatureReading(models.Model):
    """Individual temperature reading parsed from an uploaded data file.
    
    Stores the temperature measurement and reference values for a specific date.
    Based on UK temperature data format with measurement date, actual temperature,
    and reference values (average, high, low).
    """

    data_file = models.ForeignKey(
        TemperatureDataFile,
        on_delete=models.CASCADE,
        related_name="readings",
        help_text="The data file this reading was parsed from.",
    )
    """The data file this reading was parsed from."""

    measurement_date = models.DateField(
        help_text="The date of the temperature measurement.",
    )
    """The date of the temperature measurement."""

    publish_time = models.DateTimeField(
        help_text="When the measurement was published.",
    )
    """When the measurement was published."""

    temperature = models.FloatField(
        help_text="The measured temperature in degrees Celsius.",
    )
    """The measured temperature in degrees Celsius."""

    temperature_reference_average = models.FloatField(
        help_text="Historical average temperature for this date.",
    )
    """Historical average temperature for this date."""

    temperature_reference_high = models.FloatField(
        help_text="Historical high temperature reference for this date.",
    )
    """Historical high temperature reference for this date."""

    temperature_reference_low = models.FloatField(
        help_text="Historical low temperature reference for this date.",
    )
    """Historical low temperature reference for this date."""

    class Meta:
        ordering = ["measurement_date"]
        verbose_name = "Temperature Reading"
        verbose_name_plural = "Temperature Readings"
        # Ensure no duplicate readings for same date in same file
        unique_together = ["data_file", "measurement_date"]

    def __str__(self) -> str:
        return f"{self.measurement_date}: {self.temperature}°C"