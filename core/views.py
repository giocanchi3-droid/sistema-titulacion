from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from documentos.models import Acta
from estudiantes.models import RegistroTitulacion


@login_required
def dashboard(request):

    registros = RegistroTitulacion.objects.all()

    actas_generadas = (
        Acta.objects
        .exclude(archivo_pdf="")
        .exclude(archivo_word="")
        .count()
    )

    contexto = {
        "total_estudiantes": registros.count(),

        "procesos_activos": registros.exclude(
            estado__in=[
                "APROBADO",
                "GRADUADO",
            ]
        ).count(),

        "procesos_aprobados": registros.filter(
            estado__in=[
                "APROBADO",
                "GRADUADO",
            ]
        ).count(),

        "actas_generadas": actas_generadas,
    }

    return render(
        request,
        "core/dashboard.html",
        contexto,
    )
