from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.views import LoginView
from django.urls import include, path

from core.forms import LoginForm


urlpatterns = [
    path(
        "admin/",
        admin.site.urls,
    ),

    path(
        "cuentas/login/",
        LoginView.as_view(authentication_form=LoginForm),
        name="login",
    ),

    path(
        "cuentas/",
        include("django.contrib.auth.urls"),
    ),

    path(
        "",
        include("core.urls"),
    ),

    path(
        "estudiantes/",
        include("estudiantes.urls"),
    ),

    path(
        "actas/",
        include("documentos.urls"),
    ),
]


if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )
