from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.views import LoginView
from django.urls import include, path, re_path
from django.views.static import serve

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


urlpatterns += static(
    settings.MEDIA_URL,
    document_root=settings.MEDIA_ROOT,
)

if not settings.DEBUG:
    urlpatterns += [
        re_path(
            r"^media/(?P<path>.*)$",
            serve,
            {"document_root": settings.MEDIA_ROOT},
        ),
    ]

