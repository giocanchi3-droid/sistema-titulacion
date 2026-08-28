from django.db import migrations


PROGRAMAS_BASE = [
    ("TQ01", "TG Administración OEPS"),
    ("TQ02", "TG Desarrollo de Software"),
    ("TQ03", "Fotografía TG"),
    ("TQ04", "TC Enfermería"),
    ("TQ05", "TG Gestión Culinaria"),
    ("TQ06", "TG Acción Pastoral"),
    ("TQ07", "TG Atenc Integ Adultos Mayores"),
    ("TQ08", "TG Construcción"),
    ("TQ10", "TGU Interpret Lengua de Señas"),
    ("TQ11", "TG Negociación y Ventas"),
    ("TQ12", "TG Gestión del Talento Humano"),
    ("TQ13", "TG Marketing Digital"),
    ("TQ15", "TGU Gastronomía"),
    ("TQ16", "TGU Desarrollo de Software"),
    ("TQ17", "TG Gestión de Talento Humano"),
    ("TQ18", "TG Fotografía"),
    ("TQ19", "TGU Interpret Lengua de Señas"),
    ("TQ20", "TGU Acción Pastoral"),
    ("TQ21", "TGU Administración"),
    ("TQ22", "TC Enfermería"),
    ("TQ23", "TG Construcción"),
    ("TQPI", "Plan de Integración Nac TEC"),
    ("TS08", "TG Negociación y Ventas"),
]


def cargar_programas(apps, schema_editor):
    Programa = apps.get_model("estudiantes", "Programa")
    for codigo, descripcion in PROGRAMAS_BASE:
        Programa.objects.update_or_create(
            codigo=codigo,
            defaults={
                "descripcion": descripcion,
                "activo": True,
            },
        )


class Migration(migrations.Migration):
    dependencies = [("estudiantes", "0003_alter_registrotitulacion_fecha_grado_and_more")]

    operations = [
        migrations.RunPython(cargar_programas, migrations.RunPython.noop),
    ]
