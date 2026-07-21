def _tiene_valor(valor):
    """
    Comprueba si un campo contiene información válida.
    """
    if valor is None:
        return False

    if isinstance(valor, str):
        return bool(valor.strip())

    return True


def _numero(valor):
    """
    Convierte un valor numérico de forma segura.
    """
    if valor in (None, ""):
        return 0

    try:
        return float(valor)
    except (TypeError, ValueError):
        return 0


def construir_requisitos(registro):
    """
    Genera el checklist institucional y calcula
    el porcentaje de avance del expediente.
    """

    cedula_registrada = _tiene_valor(
        getattr(registro, "cedula", "")
    )

    correo_institucional = _tiene_valor(
        getattr(registro, "correo_instituc", "")
    )

    cumplimiento_idioma = (
        str(
            getattr(
                registro,
                "cumplimiento_idioma",
                "",
            )
        ).strip().upper()
        in {
            "SI",
            "SÍ",
            "CUMPLE",
            "APROBADO",
        }
    )

    practicas_completas = (
        _numero(
            getattr(
                registro,
                "horas_240",
                0,
            )
        )
        >= 240
    )

    servicio_comunitario = (
        _numero(
            getattr(
                registro,
                "horas_120",
                0,
            )
        )
        >= 120
    )

    tutor_asignado = _tiene_valor(
        getattr(
            registro,
            "nombres_completos_tutor",
            "",
        )
    )

    tribunal_completo = all(
        [
            _tiene_valor(
                getattr(
                    registro,
                    "primer_miembro_tribunal",
                    "",
                )
            ),
            _tiene_valor(
                getattr(
                    registro,
                    "segundo_miembro_tribunal",
                    "",
                )
            ),
            _tiene_valor(
                getattr(
                    registro,
                    "tercer_miembro_tribunal",
                    "",
                )
            ),
        ]
    )

    modalidad = str(
        getattr(
            registro,
            "modalidad_titulacion",
            "",
        )
    ).upper()

    if "COMPLEX" in modalidad:
        nota_final_registrada = _tiene_valor(
            getattr(
                registro,
                "nota_final2",
                None,
            )
        )
    else:
        nota_final_registrada = _tiene_valor(
            getattr(
                registro,
                "nota_final",
                None,
            )
        )

    tema_registrado = _tiene_valor(
        getattr(
            registro,
            "tema",
            "",
        )
    )

    fecha_grado_registrada = _tiene_valor(
        getattr(
            registro,
            "fecha_grado",
            None,
        )
    )

    requisitos = [
        {
            "nombre": "Cédula registrada",
            "cumplido": cedula_registrada,
            "detalle": (
                getattr(registro, "cedula", "")
                or "No registrada"
            ),
        },
        {
            "nombre": "Correo institucional",
            "cumplido": correo_institucional,
            "detalle": (
                getattr(
                    registro,
                    "correo_instituc",
                    "",
                )
                or "No registrado"
            ),
        },
        {
            "nombre": "Cumplimiento de idioma",
            "cumplido": cumplimiento_idioma,
            "detalle": (
                getattr(
                    registro,
                    "cumplimiento_idioma",
                    "",
                )
                or "Pendiente"
            ),
        },
        {
            "nombre": "Prácticas preprofesionales",
            "cumplido": practicas_completas,
            "detalle": (
                f"{int(_numero(getattr(registro, 'horas_240', 0)))} "
                "de 240 horas"
            ),
        },
        {
            "nombre": "Servicio comunitario",
            "cumplido": servicio_comunitario,
            "detalle": (
                f"{int(_numero(getattr(registro, 'horas_120', 0)))} "
                "de 120 horas"
            ),
        },
        {
            "nombre": "Tutor asignado",
            "cumplido": tutor_asignado,
            "detalle": (
                getattr(
                    registro,
                    "nombres_completos_tutor",
                    "",
                )
                or "No asignado"
            ),
        },
        {
            "nombre": "Tema de titulación",
            "cumplido": tema_registrado,
            "detalle": (
                getattr(registro, "tema", "")
                or "No registrado"
            ),
        },
        {
            "nombre": "Tribunal completo",
            "cumplido": tribunal_completo,
            "detalle": (
                "Miembros principales registrados"
                if tribunal_completo
                else "Faltan miembros del tribunal"
            ),
        },
        {
            "nombre": "Nota final registrada",
            "cumplido": nota_final_registrada,
            "detalle": (
                "Calificación registrada"
                if nota_final_registrada
                else "Calificación pendiente"
            ),
        },
        {
            "nombre": "Fecha de grado",
            "cumplido": fecha_grado_registrada,
            "detalle": (
                getattr(
                    registro,
                    "fecha_grado",
                    None,
                )
                or "Pendiente"
            ),
        },
    ]

    total = len(requisitos)

    completados = sum(
        1
        for requisito in requisitos
        if requisito["cumplido"]
    )

    porcentaje = round(
        completados * 100 / total
    ) if total else 0

    pendientes = [
        requisito
        for requisito in requisitos
        if not requisito["cumplido"]
    ]

    return {
        "requisitos": requisitos,
        "completados": completados,
        "total": total,
        "porcentaje": porcentaje,
        "pendientes": pendientes,
        "puede_generar_acta": len(pendientes) == 0,
    }
