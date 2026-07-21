from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .import_forms import ImportarExcelForm
from .services_excel import importar_excel


@login_required
def importar_registros_excel(request):
    resultado = None

    if request.method == "POST":
        form = ImportarExcelForm(
            request.POST,
            request.FILES,
        )

        if form.is_valid():
            try:
                resultado = importar_excel(
                    form.cleaned_data["archivo"]
                )

                messages.success(
                    request,
                    (
                        "La matriz fue procesada correctamente. "
                        f"Registros creados: "
                        f"{resultado['creados']}. "
                        f"Registros actualizados: "
                        f"{resultado['actualizados']}."
                    ),
                )

            except ValueError as error:
                messages.error(
                    request,
                    str(error),
                )

    else:
        form = ImportarExcelForm()

    return render(
        request,
        "estudiantes/importar_excel.html",
        {
            "form": form,
            "resultado": resultado,
        },
    )
