import tempfile
from io import BytesIO
from zipfile import ZipFile

from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.urls import reverse

from documentos.models import Acta
from estudiantes.models import HistorialExpediente, RegistroTitulacion

from .models import BackupArtifact, FieldPermission


class SeguridadYDescargasTests(TestCase):
	def setUp(self):
		self.superuser = User.objects.create_superuser(
			username="root", password="testpass123", email="root@test.local"
		)
		self.usuario_horas = User.objects.create_user(
			username="horas", password="testpass123"
		)
		self.usuario_actas = User.objects.create_user(
			username="actas", password="testpass123"
		)
		self.registro = RegistroTitulacion.objects.create(
			nombres_completos="Ana Prueba", cedula="0912345678", programa="TEST"
		)
		self.acta = Acta.objects.create(
			registro=self.registro, tipo_acta="TRABAJO_ESCRITO"
		)
		self._grant(self.usuario_horas, RegistroTitulacion, ["horas_240", "horas_120"])
		self._grant(
			self.usuario_actas,
			RegistroTitulacion,
			["fecha_grado", "observacion_puce_tec"],
		)
		self._grant(
			self.usuario_actas,
			Acta,
			["estado", "observaciones"],
		)

	def _grant(self, user, model, fields):
		for field in fields:
			FieldPermission.objects.create(
				user=user,
				model_name=f"{model._meta.app_label}.{model._meta.model_name}",
				field_name=field,
			)

	def test_superuser_administra_usuarios_y_asigna_permisos(self):
		self.client.force_login(self.superuser)
		response = self.client.post(reverse("core:usuario_nuevo"), {
			"username": "nuevo", "password": "testpass123", "is_active": "on"
		})
		self.assertEqual(response.status_code, 302)
		usuario = User.objects.get(username="nuevo")
		response = self.client.post(reverse("core:permisos_usuario", args=[usuario.pk]), {
			"estudiantes.registrotitulacion": ["horas_240"]
		})
		self.assertEqual(response.status_code, 302)
		self.assertTrue(FieldPermission.objects.filter(user=usuario, field_name="horas_240").exists())

	def test_usuario_horas_solo_edita_horas(self):
		self.client.force_login(self.usuario_horas)
		response = self.client.post(reverse("estudiantes:editar", args=[self.registro.pk]), {
			"horas_240": "100"
		})
		self.assertEqual(response.status_code, 302)
		self.registro.refresh_from_db()
		self.assertEqual(self.registro.horas_240, 100)

	def test_usuario_horas_no_edita_otro_campo(self):
		self.client.force_login(self.usuario_horas)
		response = self.client.post(reverse("estudiantes:editar", args=[self.registro.pk]), {
			"nombres_completos": "Intruso"
		})
		self.assertEqual(response.status_code, 403)

	def test_usuario_actas_edita_observacion_estado_y_fecha(self):
		self.client.force_login(self.usuario_actas)
		response = self.client.post(reverse("estudiantes:editar", args=[self.registro.pk]), {
			"fecha_grado": "2026-09-08", "observacion_puce_tec": "Revisado"
		})
		self.assertEqual(response.status_code, 302)
		response = self.client.post(reverse("documentos:editar_acta", args=[self.acta.pk]), {
			"estado": "GENERADA", "observaciones": "Validada"
		})
		self.assertEqual(response.status_code, 302)
		self.acta.refresh_from_db()
		self.assertEqual(self.acta.estado, "GENERADA")
		self.assertEqual(self.acta.observaciones, "Validada")

	def test_usuario_actas_no_edita_otro_campo(self):
		self.client.force_login(self.usuario_actas)
		response = self.client.post(reverse("documentos:editar_acta", args=[self.acta.pk]), {
			"tipo_acta": "EXAMEN_COMPLEXIVO"
		})
		self.assertEqual(response.status_code, 403)

	def test_cambios_limitados_quedan_en_auditoria(self):
		self.client.force_login(self.usuario_horas)
		self.client.post(reverse("estudiantes:editar", args=[self.registro.pk]), {"horas_240": "90"})
		cambio = HistorialExpediente.objects.get(registro=self.registro, campo="HORAS 240")
		self.assertEqual(cambio.responsable, "horas")
		self.assertEqual(cambio.valor_nuevo, "90")

	def test_rutas_administrativas_rechazan_usuario_limitado(self):
		self.client.force_login(self.usuario_horas)
		self.assertEqual(self.client.get(reverse("core:usuarios")).status_code, 403)
		self.assertEqual(self.client.get(reverse("core:backups")).status_code, 403)

	@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
	def test_superuser_genera_y_descarga_backup(self):
		self.client.force_login(self.superuser)
		response = self.client.post(reverse("core:backups"))
		self.assertEqual(response.status_code, 302)
		backup = BackupArtifact.objects.get()
		response = self.client.get(reverse("core:descargar_backup", args=[backup.pk]))
		self.assertEqual(response.status_code, 200)
		response.close()
		backup.archivo.delete(save=False)

	def test_descargas_individuales_pdf_y_word(self):
		self.client.force_login(self.usuario_horas)
		for nombre, tipo in (("documentos:generar_pdf_memoria", "application/pdf"), ("documentos:generar_word_memoria", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")):
			response = self.client.get(reverse(nombre, args=[self.acta.pk]))
			self.assertEqual(response.status_code, 200)
			self.assertEqual(response["Content-Type"], tipo)

	def test_descargas_masivas_pdf_y_word_generan_zip(self):
		self.client.force_login(self.usuario_horas)
		for formato, extension in (("pdf", ".pdf"), ("word", ".docx")):
			response = self.client.post(reverse("documentos:descargar_seleccionadas"), {
				"formato": formato, "acta_ids": [str(self.acta.pk)]
			})
			self.assertEqual(response.status_code, 200)
			with ZipFile(BytesIO(response.content)) as archivo_zip:
				self.assertTrue(any(nombre.endswith(extension) for nombre in archivo_zip.namelist()))
