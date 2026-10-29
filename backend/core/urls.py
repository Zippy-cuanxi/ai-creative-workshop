from django.urls import path

from . import views

app_name = "api"

urlpatterns = [
    path("models", views.ModelsView.as_view(), name="models"),
    path("templates", views.TemplatesView.as_view(), name="templates"),
    path("generate", views.GenerateView.as_view(), name="generate"),
    path("usage", views.UsageView.as_view(), name="usage"),
    path("health", views.HealthView.as_view(), name="health"),
]
