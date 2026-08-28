from django.urls import path

from . import import_views
from . import views
from . import expediente_views


app_name = "estudiantes"


urlpatterns = [
    path(
        "<int:pk>/expediente/",
        expediente_views.expediente_registro,
        name="expediente",
    ),
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
        "programas/nuevo/",
        views.crear_programa,
        name="crear_programa",
    ),

    path(
        "importar/",
        import_views.importar_registros_excel,
        name="importar",
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
        "<int:pk>/exportar-excel/",
        views.exportar_registro,
        name="exportar_excel",
    ),

    path(
        "<int:pk>/eliminar/",
        views.eliminar_registro,
        name="eliminar",
    ),
]

