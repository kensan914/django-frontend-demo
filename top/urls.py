from django.urls import path

from top import views as top_views

app_name = "top"


urlpatterns = [
    path("", top_views.TopView.as_view(), name="top"),
]
