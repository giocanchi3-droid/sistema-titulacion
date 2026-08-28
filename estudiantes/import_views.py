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
                    form.cleaned_data["archivo"],
                    usuario=request.user,
                )

                mensaje = (
                    "La matriz fue procesada. "
                    f"Registros creados: {resultado['creados']}. "
                    f"Registros actualizados: "
                    f"{resultado['actualizados']}."
                )

                if resultado["errores"]:
                    messages.warning(
                        request,
                        (
                            f"{mensaje} "
                            f"Filas con errores: "
                            f"{len(resultado['errores'])}. "
                            "Revise el detalle antes de continuar."
                        ),
                    )
                else:
                    messages.success(
                        request,
                        mensaje,
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
