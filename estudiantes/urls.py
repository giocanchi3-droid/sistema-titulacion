from django.urls import path

from . import views


app_name = "estudiantes"


urlpatterns = [
    path(
        "",
        views.lista_registros,
        name="lista",
    ),
    path(
        "nuevo/",
        views.crear_registro,
        name="crear",
    ),
    path(
        "<int:pk>/",
        views.detalle_registro,
        name="detalle",
    ),
    path(
        "<int:pk>/editar/",
        views.editar_registro,
        name="editar",
    ),
    path(
        "<int:pk>/eliminar/",
        views.eliminar_registro,
        name="eliminar",
    ),
]
