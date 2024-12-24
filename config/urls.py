from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path

urlpatterns = [
    path("mails/", include("mail.urls")),
    path("", include("django_components.urls")),
    *static(settings.STATIC_URL, document_root=settings.STATIC_ROOT),
]
