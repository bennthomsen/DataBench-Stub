"""Models for electricity generation data management."""

from django.db import models


class GenerationDataFile(models.Model):
    """Represents an uploaded electricity generation data file (JSON format).

    Stores the raw uploaded file and metadata about the upload.
    Individual readings are stored in related GenerationReading objects.
    """

    name = models.CharField(
        max_length=255,
        help_text="Filename of the uploaded data file.",
    )

    description = models.TextField(
        blank=True,
        help_text="Optional description of the data file.",
    )

    data_file = models.FileField(
        upload_to="generation/uploads/",
        help_text="The uploaded JSON data file.",
    )

    uploaded_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the file was uploaded.",
    )

    class Meta:
        ordering = ["-uploaded_at"]
        verbose_name = "Generation Data File"
        verbose_name_plural = "Generation Data Files"

    def __str__(self) -> str:
        return f"{self.name} (uploaded {self.uploaded_at.strftime('%Y-%m-%d')})"


class GenerationReading(models.Model):
    """Individual electricity generation reading parsed from an uploaded data file.

    Each reading represents the generation quantity for a specific power source type
    (psrType) at a specific date/time.
    """

    data_file = models.ForeignKey(
        GenerationDataFile,
        on_delete=models.CASCADE,
        related_name="readings",
        help_text="The data file this reading was parsed from.",
    )

    start_time = models.DateTimeField(
        help_text="The start time of the measurement period.",
    )

    settlement_period = models.IntegerField(
        help_text="The settlement period number.",
    )

    business_type = models.CharField(
        max_length=100,
        help_text="The business type (e.g., Production, Wind generation).",
    )

    psr_type = models.CharField(
        max_length=100,
        help_text="The power source type (e.g., Biomass, Solar, Wind Offshore).",
    )

    quantity = models.IntegerField(
        help_text="The generation quantity in MW.",
    )

    class Meta:
        ordering = ["start_time", "psr_type"]
        verbose_name = "Generation Reading"
        verbose_name_plural = "Generation Readings"

    def __str__(self) -> str:
        return f"{self.start_time.strftime('%Y-%m-%d')}: {self.psr_type} = {self.quantity} MW"