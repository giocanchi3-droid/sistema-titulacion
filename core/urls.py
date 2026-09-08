from django.urls import path

from . import views
from . import admin_views


app_name = "core"


urlpatterns = [
    path(
        "",
        views.dashboard,
        name="dashboard",
    ),
    path("administracion/usuarios/", admin_views.usuarios, name="usuarios"),
    path("administracion/usuarios/nuevo/", admin_views.usuario_nuevo, name="usuario_nuevo"),
    path("administracion/usuarios/<int:pk>/editar/", admin_views.usuario_editar, name="usuario_editar"),
    path("administracion/usuarios/<int:pk>/permisos/", admin_views.permisos_usuario, name="permisos_usuario"),
    path("administracion/backups/", admin_views.backups, name="backups"),
    path("administracion/backups/<int:pk>/descargar/", admin_views.descargar_backup, name="descargar_backup"),
]
