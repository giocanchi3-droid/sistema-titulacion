from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


VALIDADORES_NOTA = [
    MinValueValidator(0),
    MaxValueValidator(10),
]


class RegistroTitulacion(models.Model):

    MODALIDADES = [
        ("TRABAJO_ESCRITO", "Trabajo escrito"),
        ("EXAMEN_COMPLEXIVO", "Examen complexivo"),
    ]

    ESTADOS = [
        ("REGISTRADO", "Registrado"),
        ("EN_PROCESO", "En proceso"),
        ("REVISION", "En revisión"),
        ("DEFENSA", "Defensa"),
        ("APROBADO", "Aprobado"),
        ("GRADUADO", "Graduado"),
        ("OBSERVADO", "Observado"),
    ]

    CUMPLIMIENTO_IDIOMA = [
        ("SI", "Sí"),
        ("NO", "No"),
        ("PENDIENTE", "Pendiente"),
    ]

    ESTADOS_ENVIO = [
        ("NO_ENVIADO", "No enviado"),
        ("ENVIADO", "Enviado"),
        ("OBSERVADO", "Observado"),
        ("APROBADO", "Aprobado"),
    ]

    # 1-9: Información personal e institucional

    id_banner = models.CharField(
        "ID_BANNER",
        max_length=30,
        blank=True,
        db_index=True,
    )

    nombres_completos = models.CharField(
        "NOMBRES COMPLETOS",
        max_length=200,
    )

    cedula = models.CharField(
        "CEDULA",
        max_length=10,
        unique=True,
    )

    celular = models.CharField(
        "CELULAR",
        max_length=20,
        blank=True,
    )

    correo_personal = models.EmailField(
        "CORREO_PERSONAL",
        blank=True,
    )

    correo_instituc = models.EmailField(
        "CORREO_INSTITUC",
        blank=True,
    )

    sede = models.CharField(
        "SEDE",
        max_length=100,
        blank=True,
    )

    programa = models.CharField(
        "PROGRAMA",
        max_length=150,
    )

    programa_desc = models.CharField(
        "PROGAMA_DESC",
        max_length=250,
        blank=True,
    )

    # 10-17: Información académica

    numero_cohorte = models.CharField(
        "NÚMERO DE COHORTE",
        max_length=50,
        blank=True,
    )

    periodo_ingreso = models.CharField(
        "PERIODO DE INGRESO",
        max_length=100,
        blank=True,
    )

    nivel2 = models.CharField(
        "NIVEL2",
        max_length=50,
        blank=True,
    )

    modalidad_titulacion = models.CharField(
        "MODALIDAD DE TITULACIÓN",
        max_length=30,
        choices=MODALIDADES,
        blank=True,
    )

    matricula_uic = models.CharField(
        "MATRICULA UIC",
        max_length=100,
        blank=True,
    )

    periodo_titulacion_senescyt = models.CharField(
        "PERIODO DE TITULACIÓN SENESCYT",
        max_length=100,
        blank=True,
    )

    estado = models.CharField(
        "ESTADO",
        max_length=30,
        choices=ESTADOS,
        blank=True,
    )

    cumplimiento_idioma = models.CharField(
        "CUMPLIMIENTO DE IDIOMA",
        max_length=20,
        choices=CUMPLIMIENTO_IDIOMA,
        blank=True,
    )

    # 18-21: Prácticas y servicio comunitario

    materia_practicas_pre_profesionales = models.CharField(
        "MATERIA PRÁCTICAS PRE PROFESIONALES",
        max_length=200,
        blank=True,
    )

    horas_240 = models.PositiveIntegerField(
        "HORAS 240",
        default=240,
        null=True,
        blank=True,
    )

    materia_servicio_comunitario = models.CharField(
        "MATERIA SERVICIO COMUNITARIO",
        max_length=200,
        blank=True,
    )

    horas_120 = models.PositiveIntegerField(
        "HORAS 120",
        default=120,
        null=True,
        blank=True,
    )

    # 22-24: Tutor y tema

    nombres_completos_tutor = models.CharField(
        "NOMBRES COMPLETOS TUTOR",
        max_length=200,
        blank=True,
    )

    id_tutor = models.CharField(
        "ID TUTOR",
        max_length=30,
        blank=True,
    )

    tema = models.TextField(
        "TEMA",
        blank=True,
    )

    # 25-32: Miembros del tribunal

    primer_miembro_tribunal = models.CharField(
        "1er MIEMBRO DE TRIBUNAL - APELLIDOS Y NOMBRES COMPLETOS",
        max_length=200,
        blank=True,
    )

    primer_miembro_id_docente = models.CharField(
        "1er MIEMBRO DE TRIBUNAL - ID DOCENTE",
        max_length=30,
        blank=True,
    )

    segundo_miembro_tribunal = models.CharField(
        "2do MIEMBRO DE TRIBUNAL - APELLIDOS Y NOMBRES COMPLETOS",
        max_length=200,
        blank=True,
    )

    segundo_miembro_id_docente = models.CharField(
        "2do MIEMBRO DE TRIBUNAL - ID DOCENTE",
        max_length=30,
        blank=True,
    )

    tercer_miembro_tribunal = models.CharField(
        "3ter MIEMBRO DE TRIBUNAL - NOMBRES COMPLETOS",
        max_length=200,
        blank=True,
    )

    tercer_miembro_id_docente = models.CharField(
        "3ter MIEMBRO DE TRIBUNAL - ID DOCENTE",
        max_length=30,
        blank=True,
    )

    cuarto_miembro_tribunal = models.CharField(
        "4to MIEMBRO DE TRIBUNAL",
        max_length=200,
        blank=True,
    )

    cuarto_miembro_id_docente = models.CharField(
        "4to MIEMBRO DE TRIBUNAL - ID DOCENTE",
        max_length=30,
        blank=True,
    )

    # 33-38: Calificaciones

    proyecto_escrito = models.DecimalField(
        "PROYECTO ESCRITO",
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=VALIDADORES_NOTA,
    )

    defensa_oral = models.DecimalField(
        "DEFENSA ORAL",
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=VALIDADORES_NOTA,
    )

    nota_final = models.DecimalField(
        "NOTA FINAL",
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=VALIDADORES_NOTA,
    )

    examen_teorico_complexivo = models.DecimalField(
        "EXAMEN TEÓRICO COMPLEXIVO",
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=VALIDADORES_NOTA,
    )

    examen_teorico_practico = models.DecimalField(
        "EXAMEN TEÓRICO PRÁCTICO",
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=VALIDADORES_NOTA,
    )

    nota_final2 = models.DecimalField(
        "NOTA FINAL2",
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=VALIDADORES_NOTA,
    )

    # 39-44: Observaciones, envío y grado

    observacion_puce_tec = models.TextField(
        "OBSERVACIÓN PUCE TEC",
        blank=True,
    )

    observaciones_secretaria_general = models.TextField(
        "OBSERVACIONES DE SECRETARÍA GENERAL",
        blank=True,
    )

    nueva_observacion_puce_tec = models.TextField(
        "NUEVA OBSERVACIÓN PUCE TEC",
        blank=True,
    )

    estado_envio_registro = models.CharField(
        "ESTADO DE ENVÍO DE REGISTRO",
        max_length=30,
        choices=ESTADOS_ENVIO,
        blank=True,
    )

    fecha_grado = models.DateField(
        "Fecha de Grado",
        null=True,
        blank=True,
    )

    observacion_secretaria = models.TextField(
        "Observación Secretaría",
        blank=True,
    )

    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
    )

    fecha_actualizacion = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["-fecha_actualizacion"]
        verbose_name = "Registro de titulación"
        verbose_name_plural = "Registros de titulación"

    def __str__(self):
        return f"{self.cedula} - {self.nombres_completos}"
