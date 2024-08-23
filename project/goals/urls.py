from django.urls import path

from . import views
from .apps import App_name

app_name = App_name


urlpatterns = [
    path("", views.Index.as_view(), name="index"),
    path("<int:year>/<int:month>/", views.Index.as_view(), name="index_month"),
    path("table/<int:year>/<int:month>/", views.Table.as_view(), name="table"),
    path('login/', views.Login.as_view(), name="login"),
    path('logout/', views.Logout.as_view(), name="logout"),
    path('admin/', views.Admin.as_view(), name="admin"),
]
