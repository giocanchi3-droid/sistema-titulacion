from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]
    operations = [
        migrations.CreateModel(
            name="BackupArtifact",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("archivo", models.FileField(upload_to="backups/")),
                ("fecha_creacion", models.DateTimeField(auto_now_add=True)),
                ("tamano", models.PositiveBigIntegerField(default=0)),
                ("formato", models.CharField(default="django-dumpdata", max_length=30)),
                ("generado_por", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="backups_generados", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["-fecha_creacion"]},
        ),
        migrations.CreateModel(
            name="FieldPermission",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("model_name", models.CharField(choices=[("estudiantes.registrotitulacion", "Estudiante"), ("documentos.acta", "Acta")], max_length=100)),
                ("field_name", models.CharField(max_length=100)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="field_permissions", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["model_name", "field_name"]},
        ),
        migrations.AddConstraint(
            model_name="fieldpermission",
            constraint=models.UniqueConstraint(fields=("user", "model_name", "field_name"), name="unique_user_field_permission"),
        ),
    ]