from django.urls import path

from mail import views as mail_views

app_name = "mail"


urlpatterns = [
    path("", mail_views.IndexView.as_view(), name="index"),
    path("new/", mail_views.NewView.as_view(), name="new"),
    path("<int:mail_id>/", mail_views.DetailView.as_view(), name="detail"),
]
