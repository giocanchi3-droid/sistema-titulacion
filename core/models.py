from django.conf import settings
from django.db import models

class FieldPermission(models.Model):
	MODEL_CHOICES = [
		("estudiantes.registrotitulacion", "Estudiante"),
		("documentos.acta", "Acta"),
	]

	user = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.CASCADE,
		related_name="field_permissions",
	)
	model_name = models.CharField(max_length=100, choices=MODEL_CHOICES)
	field_name = models.CharField(max_length=100)

	class Meta:
		constraints = [
			models.UniqueConstraint(
				fields=["user", "model_name", "field_name"],
				name="unique_user_field_permission",
			)
		]
		ordering = ["model_name", "field_name"]

	def __str__(self):
		return f"{self.user} - {self.model_name}.{self.field_name}"


class BackupArtifact(models.Model):
	archivo = models.FileField(upload_to="backups/")
	generado_por = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.PROTECT,
		related_name="backups_generados",
	)
	fecha_creacion = models.DateTimeField(auto_now_add=True)
	tamano = models.PositiveBigIntegerField(default=0)
	formato = models.CharField(max_length=30, default="django-dumpdata")

	class Meta:
		ordering = ["-fecha_creacion"]

	def __str__(self):
		return self.archivo.name
