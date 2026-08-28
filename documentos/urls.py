from .views_oficial import (
    generar_oficial,
    generar_pdf_memoria,
    generar_word_memoria,
)
from django.urls import path

from . import views


app_name = "documentos"


urlpatterns = [

    # GENERADOR OFICIAL PUCE TEC - PRIORIDAD
    path(
        "<int:pk>/generar/",
        generar_oficial,
        name="generar_oficial_prioridad",
    ),

    path(
        "<int:pk>/generar-oficial/",
        views.generar_documentos_oficiales,
        name="generar_documentos_oficiales",
    ),
    path(
        "<int:pk>/vista-previa/",
        views.vista_previa_acta,
        name="vista_previa_acta",
    ),
    path(
        "<int:pk>/descargar/<str:tipo>/",
        views.descargar_documento,
        name="descargar_documento",
    ),
    path(
        "<int:pk>/generar-word/",
        generar_word_memoria,
        name="generar_word_memoria",
    ),
    path(
        "<int:pk>/generar-pdf/",
        generar_pdf_memoria,
        name="generar_pdf_memoria",
    ),
    path(
        "",
        views.lista_actas,
        name="lista_actas",
    ),

    path(
        "nueva/",
        views.crear_acta,
        name="crear_acta",
    ),

    path(
        "<int:pk>/",
        views.detalle_acta,
        name="detalle_acta",
    ),

    path(
        "<int:pk>/editar/",
        views.editar_acta,
        name="editar_acta",
    ),

    path(
        "<int:pk>/generar-legacy/",
        views.generar_acta,
        name="generar_acta",
    ),

    path(
        "<int:pk>/aprobar/",
        views.aprobar_acta,
        name="aprobar_acta",
    ),

    path(
        "<int:pk>/anular/",
        views.anular_acta,
        name="anular_acta",
    ),

    path(
        "<int:pk>/eliminar/",
        views.eliminar_acta,
        name="eliminar_acta",
    ),
]


