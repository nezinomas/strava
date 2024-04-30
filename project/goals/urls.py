from django.urls import path

from . import views
from .apps import App_name

app_name = App_name


urlpatterns = [
    path("", views.Index.as_view(), name="index"),
    path("<int:year>/<int:month>/", views.Index.as_view(), name="index"),
]
