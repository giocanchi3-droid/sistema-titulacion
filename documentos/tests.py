from django.urls import reverse
from django.test import SimpleTestCase

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
