from django.urls import path

from . import views
from .apps import App_name

app_name = App_name


urlpatterns = [
    path("", views.Index.as_view(), name="index"),
    path("<int:year>/<int:month>/", views.Index.as_view(), name="index_month"),
    path("table/<int:year>/<int:month>/", views.Table.as_view(), name="table"),
    path("login/", views.Login.as_view(), name="login"),
    path("logout/", views.Logout.as_view(), name="logout"),
    path("admin/", views.Admin.as_view(), name="admin"),
    path("admin/goal/list/", views.GoalList.as_view(), name="goal_list"),
    path("admin/goal/add/<int:month>/", views.GoalAdd.as_view(), name="goal_add"),
    path("admin/goal/update/<int:pk>/", views.GoalUpdate.as_view(), name="goal_update"),
    path("admin/goal/delete/<int:pk>/", views.GoalDelete.as_view(), name="goal_delete"),
]
