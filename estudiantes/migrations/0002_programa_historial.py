from django.db import migrations, models
import django.db.models.deletion


PROGRAMAS = [
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
    Programa.objects.bulk_create(
        [Programa(codigo=codigo, descripcion=descripcion) for codigo, descripcion in PROGRAMAS]
    )


class Migration(migrations.Migration):
    dependencies = [("estudiantes", "0001_initial")]

    operations = [
        migrations.CreateModel(
            name="Programa",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("codigo", models.CharField(max_length=30, unique=True)),
                ("descripcion", models.CharField(max_length=250)),
                ("activo", models.BooleanField(default=True)),
            ],
            options={"ordering": ["codigo"], "verbose_name": "Programa", "verbose_name_plural": "Programas"},
        ),
        migrations.CreateModel(
            name="HistorialExpediente",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("responsable", models.CharField(default="Sistema", max_length=150)),
                ("campo", models.CharField(max_length=100)),
                ("valor_anterior", models.TextField(blank=True)),
                ("valor_nuevo", models.TextField(blank=True)),
                ("accion", models.CharField(default="EDICION", max_length=30)),
                ("observacion", models.TextField(blank=True)),
                ("fecha", models.DateTimeField(auto_now_add=True)),
                ("registro", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="historial_cambios", to="estudiantes.registrotitulacion")),
            ],
            options={"ordering": ["-fecha"], "verbose_name": "Cambio del expediente", "verbose_name_plural": "Cambios del expediente"},
        ),
        migrations.RunPython(cargar_programas, migrations.RunPython.noop),
    ]