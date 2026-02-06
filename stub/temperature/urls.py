"""URL configuration for temperature app."""

from django.urls import path

from . import views

app_name = "temperature"

urlpatterns = [
    path("", views.file_list, name="file_list"),
    path("upload/", views.upload, name="upload"),
    path("chart/<int:file_id>/", views.chart, name="chart"),
    path("delete/<int:file_id>/", views.delete_file, name="delete"),
]