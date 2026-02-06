"""Forms for temperature app."""

from django import forms

from .models import TemperatureDataFile

class TemperatureDataFileUploadForm(forms.ModelForm):
    """Form for uploading temperature data files."""

    class Meta:
        model = TemperatureDataFile
        fields = ["name", "description", "data_file"]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter a name for this data file",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Optional description",
                    "rows": 3,
                }
            ),
            "data_file": forms.FileInput(
                attrs={
                    "class": "form-control",
                    "accept": ".json",
                }
            ),
        }

    def clean_data_file(self):
        """Validate the uploaded file is a JSON file."""
        data_file = self.cleaned_data.get("data_file")
        if data_file:
            if not data_file.name.endswith(".json"):
                raise forms.ValidationError("Only JSON files are accepted.")
            # Check file size (max 10MB)
            if data_file.size > 10 * 1024 * 1024:
                raise forms.ValidationError("File size must be less than 10MB.")
        return data_file