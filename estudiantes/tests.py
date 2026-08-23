from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import SimpleTestCase

from .import_forms import ImportarExcelForm
from .services_excel import convertir_nota


class ImportarExcelTests(SimpleTestCase):
	def test_rejects_non_xlsx_files(self):
		archivo = SimpleUploadedFile(
			"estudiantes.csv",
			b"nombre,cedula",
			content_type="text/csv",
		)

		form = ImportarExcelForm(files={"archivo": archivo})

		self.assertFalse(form.is_valid())
		self.assertIn(".xlsx", form.errors["archivo"][0])

	def test_rejects_notes_outside_supported_range(self):
		with self.assertRaises(ValueError):
			convertir_nota("11")
