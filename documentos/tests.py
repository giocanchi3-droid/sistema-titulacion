from django.urls import reverse
from django.contrib.auth.models import User
from django.test import SimpleTestCase, TestCase

from .models import Acta


class ActaRoutingTests(SimpleTestCase):
	def test_generation_routes_are_distinct(self):
		self.assertEqual(
			reverse("documentos:generar_oficial_prioridad", args=[7]),
			"/actas/7/generar/",
		)
		self.assertEqual(
			reverse("documentos:generar_acta", args=[7]),
			"/actas/7/generar-legacy/",
		)

	def test_new_actas_start_as_drafts(self):
		estado = Acta._meta.get_field("estado")

		self.assertEqual(estado.default, "BORRADOR")


class ActaCreationFrontendTests(TestCase):
	def test_creation_form_hides_status_field(self):
		User.objects.create_user(
			username="acta-user",
			password="testpass123",
		)
		self.client.login(username="acta-user", password="testpass123")

		response = self.client.get(reverse("documentos:crear_acta"))

		self.assertEqual(response.status_code, 200)
		self.assertNotContains(response, 'name="estado"')
