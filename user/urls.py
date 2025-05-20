from django.urls import path

from user import views as user_views

app_name = "user"


urlpatterns = [
    path(
        "pro-users/",
        user_views.ProUsersIndexView.as_view(),
        name="pro-users",
    ),
    path(
        "admin-users/",
        user_views.AdminUsersIndexView.as_view(),
        name="admin-users",
    ),
    path(
        "contractors/",
        user_views.ContractorsIndexView.as_view(),
        name="contractors",
    ),
]
