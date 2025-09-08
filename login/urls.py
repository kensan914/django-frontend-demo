from django.urls import path

from login import views as login_views

app_name = "login"


urlpatterns = [
    path("login/", login_views.LoginView.as_view(), name="login"),
    path("logout/", login_views.LogoutView.as_view(), name="logout"),
]
