import re
import unicodedata
from datetime import date, datetime
from decimal import Decimal, InvalidOperation

from django.core.exceptions import ValidationError
from django.db import transaction
from openpyxl import load_workbook

from .models import RegistroTitulacion


ENCABEZADOS_ESPERADOS = {
    "ID BANNER",
    "NOMBRES COMPLETOS",
    "CEDULA",
    "CELULAR",
    "CORREO PERSONAL",
    "CORREO INSTITUC",
    "SEDE",
    "PROGRAMA",
    "PROGAMA DESC",
    "NUMERO DE COHORTE",
    "PERIODO DE INGRESO",
    "NIVEL2",
    "MODALIDAD DE TITULACION",
    "MATRICULA UIC",
    "PERIODO DE TITULACION SENESCYT",
    "ESTADO",
    "CUMPLIMIENTO DE IDIOMA",
    "MATERIA PRACTICAS PRE PROFESIONALES",
    "HORAS 240",
    "MATERIA SERVICIO COMUNITARIO",
    "HORAS 120",
    "NOMBRES COMPLETOS TUTOR",
    "ID TUTOR",
    "TEMA",
    (
        "1ER MIEMBREO DE TRIBUNAL "
        "APELLIDOS Y NOMBRES COMPLETOS"
    ),
    "1ER MIEMBRO DE TRIBUNAL ID DOCENTE",
    (
        "2DO MIEMBRO DE TRIBUNAL "
        "APELLIDOS Y NOMBRES COMPLETOS"
    ),
    "2DO MIEMBRO DE TRIBUNAL ID DOCENTE",
    (
        "3TER MIEMBRO DE TRIBUNAL "
        "NOMBRES COMPLETOS"
    ),
    "3TER MIEMBRO DE TRIBUNAL ID DOCENTE",
    "4TO MIEMBRO DE TRIBUNAL",
    "4TO MIEMBRO DE TRIBUNAL ID DOCENTE",
    "PROYECTO ESCRITO",
    "DEFENSA ORAL",
    "NOTA FINAL",
    "EXAMEN TEORICO COMPLEXIVO",
    "EXAMEN TEORICO PRACTICO",
    "NOTA FINAL2",
    "OBSERVACION PUCE TEC",
    "OBSERVACIONES DE SECRETARIA GENERAL",
    "NUEVA OBSERVACION PUCE TEC",
    "ESTADO DE ENVIO DE REGISTRO",
    "FECHA DE GRADO",
    "OBSERVACION SECRETARIA",
}


def normalizar(valor):
    """
    Normaliza encabezados eliminando acentos, saltos de línea,
    guiones, signos especiales y diferencias entre mayúsculas.
    """

    valor = str(valor or "").strip().upper()
    valor = unicodedata.normalize("NFD", valor)

    valor = "".join(
        caracter
        for caracter in valor
        if unicodedata.category(caracter) != "Mn"
    )

    valor = valor.replace("_", " ")
    valor = valor.replace("\n", " ")
    valor = valor.replace("\r", " ")

    valor = re.sub(
        r"[^A-Z0-9 ]",
        " ",
        valor,
    )

    valor = re.sub(
        r"\s+",
        " ",
        valor,
    )

    return valor.strip()


def convertir_texto(valor):
    if valor is None:
        return ""

    if isinstance(valor, float) and valor.is_integer():
        return str(int(valor))

    return str(valor).strip()


def convertir_cedula(valor):
    if valor is None:
        return ""

    if isinstance(valor, (int, float)):
        cedula = str(int(valor))
        cedula = cedula.zfill(10)
    else:
        cedula = str(valor).strip()
        cedula = cedula.replace(".0", "")
        cedula = re.sub(r"\D", "", cedula)

    return cedula


def convertir_entero(valor, valor_predeterminado=None):
    if valor in (None, ""):
        return valor_predeterminado

    try:
        numero = int(float(valor))
    except (TypeError, ValueError) as error:
        raise ValueError(
            f"El valor '{valor}' no es un número entero."
        ) from error

    if numero < 0:
        raise ValueError(
            "Las horas no pueden ser negativas."
        )

    return numero


def convertir_nota(valor):
    if valor in (None, ""):
        return None

    try:
        nota = Decimal(
            str(valor).strip().replace(",", ".")
        )
    except (InvalidOperation, TypeError, ValueError) as error:
        raise ValueError(
            f"La nota '{valor}' no es válida."
        ) from error

    if nota < 0 or nota > 10:
        raise ValueError(
            f"La nota {nota} debe estar entre 0 y 10."
        )

    return nota


def convertir_fecha(valor):
    if valor in (None, ""):
        return None

    if isinstance(valor, datetime):
        return valor.date()

    if isinstance(valor, date):
        return valor

    texto_fecha = str(valor).strip()

    formatos = [
        "%Y-%m-%d",
        "%d/%m/%Y",
        "%d-%m-%Y",
        "%m/%d/%Y",
    ]

    for formato in formatos:
        try:
            return datetime.strptime(
                texto_fecha,
                formato,
            ).date()
        except ValueError:
            continue

    raise ValueError(
        f"La fecha '{texto_fecha}' no tiene un formato válido."
    )


def convertir_modalidad(valor):
    modalidad = normalizar(valor)

    if not modalidad:
        return ""

    if "COMPLEX" in modalidad:
        return "EXAMEN_COMPLEXIVO"

    if (
        "TRABAJO" in modalidad
        or "ESCRITO" in modalidad
        or "PROYECTO" in modalidad
    ):
        return "TRABAJO_ESCRITO"

    raise ValueError(
        f"La modalidad '{valor}' no está reconocida."
    )


def convertir_estado(valor):
    estado = normalizar(valor)

    equivalencias = {
        "": "",
        "REGISTRADO": "REGISTRADO",
        "REGISTRO": "REGISTRADO",
        "INSCRITO": "REGISTRADO",
        "INSCRIPCION": "REGISTRADO",
        "EN PROCESO": "EN_PROCESO",
        "PROCESO": "EN_PROCESO",
        "REVISION": "REVISION",
        "EN REVISION": "REVISION",
        "DEFENSA": "DEFENSA",
        "APROBADO": "APROBADO",
        "APROBADA": "APROBADO",
        "GRADUADO": "GRADUADO",
        "GRADUADA": "GRADUADO",
        "OBSERVADO": "OBSERVADO",
        "OBSERVADA": "OBSERVADO",
    }

    if estado not in equivalencias:
        raise ValueError(
            f"El estado '{valor}' no está reconocido."
        )

    return equivalencias[estado]


def convertir_cumplimiento(valor):
    cumplimiento = normalizar(valor)

    equivalencias = {
        "": "",
        "SI": "SI",
        "S": "SI",
        "CUMPLE": "SI",
        "APROBADO": "SI",
        "NO": "NO",
        "N": "NO",
        "NO CUMPLE": "NO",
        "PENDIENTE": "PENDIENTE",
        "EN PROCESO": "PENDIENTE",
    }

    if cumplimiento not in equivalencias:
        raise ValueError(
            f"El cumplimiento de idioma '{valor}' no es válido."
        )

    return equivalencias[cumplimiento]


def convertir_estado_envio(valor):
    estado = normalizar(valor)

    equivalencias = {
        "": "",
        "NO ENVIADO": "NO_ENVIADO",
        "PENDIENTE": "NO_ENVIADO",
        "ENVIADO": "ENVIADO",
        "OBSERVADO": "OBSERVADO",
        "OBSERVADA": "OBSERVADO",
        "APROBADO": "APROBADO",
        "APROBADA": "APROBADO",
    }

    if estado not in equivalencias:
        raise ValueError(
            f"El estado de envío '{valor}' no es válido."
        )

    return equivalencias[estado]


def obtener(datos, encabezado):
    return datos.get(
        normalizar(encabezado)
    )


def guardar_registro(datos):
    cedula = convertir_cedula(
        obtener(datos, "CEDULA")
    )

    nombres = convertir_texto(
        obtener(datos, "NOMBRES COMPLETOS")
    )

    programa = convertir_texto(
        obtener(datos, "PROGRAMA")
    )

    if not cedula:
        raise ValueError(
            "La cédula está vacía."
        )

    if len(cedula) != 10 or not cedula.isdigit():
        raise ValueError(
            f"La cédula '{cedula}' debe tener 10 dígitos."
        )

    if not nombres:
        raise ValueError(
            "El nombre del estudiante está vacío."
        )

    if not programa:
        raise ValueError(
            "El programa está vacío."
        )

    valores = {
        "id_banner": convertir_texto(
            obtener(datos, "ID_BANNER")
        ),
        "nombres_completos": nombres,
        "celular": convertir_texto(
            obtener(datos, "CELULAR")
        ),
        "correo_personal": convertir_texto(
            obtener(datos, "CORREO_PERSONAL")
        ),
        "correo_instituc": convertir_texto(
            obtener(datos, "CORREO_INSTITUC")
        ),
        "sede": convertir_texto(
            obtener(datos, "SEDE")
        ),
        "programa": programa,
        "programa_desc": convertir_texto(
            obtener(datos, "PROGAMA_DESC")
        ),
        "numero_cohorte": convertir_texto(
            obtener(datos, "NÚMERO DE COHORTE")
        ),
        "periodo_ingreso": convertir_texto(
            obtener(datos, "PERIODO DE INGRESO")
        ),
        "nivel2": convertir_texto(
            obtener(datos, "NIVEL2")
        ),
        "modalidad_titulacion": convertir_modalidad(
            obtener(datos, "MODALIDAD DE TITULACIÓN")
        ),
        "matricula_uic": convertir_texto(
            obtener(datos, "MATRICULA UIC")
        ),
        "periodo_titulacion_senescyt": convertir_texto(
            obtener(
                datos,
                "PERIODO DE TITULACIÓN SENESCYT",
            )
        ),
        "estado": convertir_estado(
            obtener(datos, "ESTADO")
        ),
        "cumplimiento_idioma": convertir_cumplimiento(
            obtener(datos, "CUMPLIMIENTO DE IDIOMA")
        ),
        "materia_practicas_pre_profesionales": convertir_texto(
            obtener(
                datos,
                "MATERIA PRÁCTICAS PRE PROFESIONALES",
            )
        ),
        "horas_240": convertir_entero(
            obtener(datos, "HORAS 240"),
            240,
        ),
        "materia_servicio_comunitario": convertir_texto(
            obtener(
                datos,
                "MATERIA SERVICIO COMUNITARIO",
            )
        ),
        "horas_120": convertir_entero(
            obtener(datos, "HORAS 120"),
            120,
        ),
        "nombres_completos_tutor": convertir_texto(
            obtener(
                datos,
                "NOMBRES COMPLETOS TUTOR",
            )
        ),
        "id_tutor": convertir_texto(
            obtener(datos, "ID TUTOR")
        ),
        "tema": convertir_texto(
            obtener(datos, "TEMA")
        ),
        "primer_miembro_tribunal": convertir_texto(
            obtener(
                datos,
                (
                    "1er MIEMBREO DE TRIBUNAL "
                    "APELLIDOS Y NOMBRES COMPLETOS"
                ),
            )
        ),
        "primer_miembro_id_docente": convertir_texto(
            obtener(
                datos,
                "1er MIEMBRO DE TRIBUNAL ID DOCENTE",
            )
        ),
        "segundo_miembro_tribunal": convertir_texto(
            obtener(
                datos,
                (
                    "2do MIEMBRO DE TRIBUNAL "
                    "APELLIDOS Y NOMBRES COMPLETOS"
                ),
            )
        ),
        "segundo_miembro_id_docente": convertir_texto(
            obtener(
                datos,
                "2do MIEMBRO DE TRIBUNAL ID DOCENTE",
            )
        ),
        "tercer_miembro_tribunal": convertir_texto(
            obtener(
                datos,
                (
                    "3ter MIEMBRO DE TRIBUNAL "
                    "NOMBRES COMPLETOS"
                ),
            )
        ),
        "tercer_miembro_id_docente": convertir_texto(
            obtener(
                datos,
                "3ter MIEMBRO DE TRIBUNAL ID DOCENTE",
            )
        ),
        "cuarto_miembro_tribunal": convertir_texto(
            obtener(
                datos,
                "4to MIEMBRO DE TRIBUNAL",
            )
        ),
        "cuarto_miembro_id_docente": convertir_texto(
            obtener(
                datos,
                "4to MIEMBRO DE TRIBUNAL ID DOCENTE",
            )
        ),
        "proyecto_escrito": convertir_nota(
            obtener(datos, "PROYECTO ESCRITO")
        ),
        "defensa_oral": convertir_nota(
            obtener(datos, "DEFENSA ORAL")
        ),
        "nota_final": convertir_nota(
            obtener(datos, "NOTA FINAL")
        ),
        "examen_teorico_complexivo": convertir_nota(
            obtener(
                datos,
                "EXAMEN TEÓRICO COMPLEXIVO",
            )
        ),
        "examen_teorico_practico": convertir_nota(
            obtener(
                datos,
                "EXAMEN TEÓRICO PRÁCTICO",
            )
        ),
        "nota_final2": convertir_nota(
            obtener(datos, "NOTA FINAL2")
        ),
        "observacion_puce_tec": convertir_texto(
            obtener(datos, "OBSERVACIÓN PUCE TEC")
        ),
        "observaciones_secretaria_general": convertir_texto(
            obtener(
                datos,
                "OBSERVACIONES DE SECRETARÍA GENERAL",
            )
        ),
        "nueva_observacion_puce_tec": convertir_texto(
            obtener(
                datos,
                "NUEVA OBSERVACIÓN PUCE TEC",
            )
        ),
        "estado_envio_registro": convertir_estado_envio(
            obtener(
                datos,
                "ESTADO DE ENVÍO DE REGISTRO",
            )
        ),
        "fecha_grado": convertir_fecha(
            obtener(datos, "Fecha de Grado")
        ),
        "observacion_secretaria": convertir_texto(
            obtener(datos, "Observación Secretaría")
        ),
    }

    registro = RegistroTitulacion.objects.filter(
        cedula=cedula
    ).first()

    creado = registro is None

    if creado:
        registro = RegistroTitulacion(
            cedula=cedula
        )

    for campo, valor in valores.items():
        setattr(
            registro,
            campo,
            valor,
        )

    registro.full_clean()
    registro.save()

    return registro, creado


def importar_excel(archivo):
    try:
        libro = load_workbook(
            archivo,
            read_only=True,
            data_only=True,
        )
    except Exception as error:
        raise ValueError(
            "El archivo no pudo ser leído como una matriz Excel."
        ) from error

    hoja = libro.active
    filas = hoja.iter_rows(values_only=True)

    encabezados_originales = next(
        filas,
        None,
    )

    if not encabezados_originales:
        raise ValueError(
            "El archivo Excel está vacío."
        )

    encabezados = [
        normalizar(encabezado)
        for encabezado in encabezados_originales
    ]

    encabezados_encontrados = {
        encabezado
        for encabezado in encabezados
        if encabezado
    }

    faltantes = sorted(
        ENCABEZADOS_ESPERADOS
        - encabezados_encontrados
    )

    if faltantes:
        raise ValueError(
            "La matriz no tiene todos los encabezados requeridos. "
            "Faltan: "
            + ", ".join(faltantes)
        )

    creados = 0
    actualizados = 0
    errores = []
    cedulas_procesadas = set()

    for numero_fila, valores_fila in enumerate(
        filas,
        start=2,
    ):
        if not any(
            valor not in (None, "")
            for valor in valores_fila
        ):
            continue

        datos = dict(
            zip(
                encabezados,
                valores_fila,
            )
        )

        cedula_fila = convertir_cedula(
            obtener(datos, "CEDULA")
        )

        if cedula_fila in cedulas_procesadas:
            errores.append(
                {
                    "fila": numero_fila,
                    "error": (
                        f"La cédula {cedula_fila} "
                        "está repetida dentro del Excel."
                    ),
                }
            )
            continue

        try:
            with transaction.atomic():
                registro, creado = guardar_registro(
                    datos
                )

                cedulas_procesadas.add(
                    registro.cedula
                )

                if creado:
                    creados += 1
                else:
                    actualizados += 1

        except (
            ValueError,
            ValidationError,
        ) as error:
            if hasattr(
                error,
                "message_dict",
            ):
                mensaje = "; ".join(
                    (
                        f"{campo}: "
                        f"{', '.join(mensajes)}"
                    )
                    for campo, mensajes
                    in error.message_dict.items()
                )
            else:
                mensaje = str(error)

            errores.append(
                {
                    "fila": numero_fila,
                    "error": mensaje,
                }
            )

        except Exception as error:
            errores.append(
                {
                    "fila": numero_fila,
                    "error": (
                        "Error inesperado al procesar la fila: "
                        f"{error}"
                    ),
                }
            )

    libro.close()

    return {
        "creados": creados,
        "actualizados": actualizados,
        "errores": errores,
        "total_correctos": creados + actualizados,
    }
