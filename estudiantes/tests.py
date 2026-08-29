import io

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from openpyxl import Workbook

from .import_forms import ImportarExcelForm
from .models import Programa, RegistroTitulacion
from .services_excel import convertir_nota, importar_excel


class ImportarExcelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )

    def _crear_archivo_excel(self, filas):
        libro = Workbook()
        hoja = libro.active
        hoja.append(filas[0])
        for fila in filas[1:]:
            hoja.append(fila)
        buffer = io.BytesIO()
        libro.save(buffer)
        buffer.seek(0)
        return SimpleUploadedFile(
            "estudiantes.xlsx",
            buffer.getvalue(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

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

    def test_import_valid_xlsx_creates_students(self):
        filas = [
            [
                "CEDULA",
                "NOMBRES COMPLETOS",
                "ID_BANNER",
                "CELULAR",
                "CORREO_PERSONAL",
                "CORREO_INSTITUC",
                "SEDE",
                "PROGRAMA",
                "PROGAMA_DESC",
                "ESTADO",
            ],
            [
                "0102030405",
                "Juan Pérez",
                "12345",
                "0999999999",
                "juan@gmail.com",
                "juan@puce.edu.ec",
                "Quito",
                "TQ02",
                "TG Desarrollo de Software",
                "REGISTRADO",
            ],
            [
                "0102030406",
                "María López",
                "12346",
                "0988888888",
                "maria@gmail.com",
                "maria@puce.edu.ec",
                "Quito",
                "TQ01",
                "TG Administración OEPS",
                "EN_PROCESO",
            ],
        ]

        archivo = self._crear_archivo_excel(filas)
        resultado = importar_excel(archivo)

        self.assertEqual(resultado["creados"], 2)
        self.assertEqual(resultado["actualizados"], 0)
        self.assertEqual(RegistroTitulacion.objects.count(), 2)
        self.assertTrue(RegistroTitulacion.objects.filter(cedula="0102030405").exists())
        self.assertTrue(Programa.objects.filter(codigo="TQ02").exists())

    def test_import_updates_existing_student_without_duplicate(self):
        RegistroTitulacion.objects.create(
            cedula="0102030405",
            nombres_completos="Juan Pérez",
            programa="TQ02",
            programa_desc="TG Desarrollo de Software",
            correo_personal="juan@viejo.com",
            correo_instituc="juan@puce.edu.ec",
            estado="REGISTRADO",
        )

        filas = [
            [
                "CEDULA",
                "NOMBRES COMPLETOS",
                "ID_BANNER",
                "SEDE",
                "PROGRAMA",
                "PROGAMA_DESC",
                "ESTADO",
            ],
            [
                "0102030405",
                "Juan Pérez Actualizado",
                "12345",
                "Guayaquil",
                "TQ02",
                "TG Desarrollo de Software",
                "APROBADO",
            ],
        ]

        archivo = self._crear_archivo_excel(filas)
        resultado = importar_excel(archivo)

        self.assertEqual(resultado["creados"], 0)
        self.assertEqual(resultado["actualizados"], 1)
        self.assertEqual(RegistroTitulacion.objects.filter(cedula="0102030405").count(), 1)
        self.assertEqual(
            RegistroTitulacion.objects.get(cedula="0102030405").nombres_completos,
            "Juan Pérez Actualizado",
        )

    def test_import_rejects_empty_xlsx_or_missing_headers(self):
        wb = Workbook()
        ws = wb.active
        ws.append(["CEDULA", "NOMBRES COMPLETOS"])
        buffer = io.BytesIO()
        wb.save(buffer)
        buffer.seek(0)
        archivo = SimpleUploadedFile(
            "vacio.xlsx",
            buffer.getvalue(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

        with self.assertRaises(ValueError):
            importar_excel(archivo)

        empty_file = SimpleUploadedFile(
            "vacío.xlsx",
            b"",
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        with self.assertRaises(ValueError):
            importar_excel(empty_file)

    def test_import_counts_ignored_rows_and_errors(self):
        filas = [
            [
                "CEDULA",
                "NOMBRES COMPLETOS",
                "PROGRAMA",
                "PROGAMA_DESC",
            ],
            ["", "Ana García", "TQ02", "TG Desarrollo de Software"],
            ["0102030407", "Pedro Paredes", "TQ02", "TG Desarrollo de Software"],
            ["0102030407", "Pedro Paredes Duplicado", "TQ02", "TG Desarrollo de Software"],
            ["0102030408", "", "TQ02", "TG Desarrollo de Software"],
        ]

        archivo = self._crear_archivo_excel(filas)
        resultado = importar_excel(archivo)

        self.assertEqual(resultado["creados"], 1)
        self.assertEqual(resultado["actualizados"], 0)
        self.assertEqual(resultado["ignoradas"], 1)
        self.assertGreater(len(resultado["errores"]), 0)

    def test_importar_excel_get_request_returns_200(self):
        """GET /estudiantes/importar-excel/ debe devolver 200 y mostrar el formulario."""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get("/estudiantes/importar-excel/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Importar estudiantes", response.content)
        self.assertIn(b"Procesar matriz", response.content)

    def test_importar_excel_get_request_contains_form(self):
        """El formulario debe estar presente en GET."""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get("/estudiantes/importar-excel/")
        self.assertIn(b"multipart/form-data", response.content)

    def test_importar_excel_requires_login(self):
        """Acceso sin autenticación debe redirigir a login."""
        response = self.client.get("/estudiantes/importar-excel/")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/cuentas/login/", response.url)

    def test_post_with_valid_excel_creates_students(self):
        """POST con un Excel válido debe crear estudiantes y mostrar resultado."""
        self.client.login(username="testuser", password="testpass123")

        filas = [
            [
                "CEDULA",
                "NOMBRES COMPLETOS",
                "PROGRAMA",
                "PROGAMA_DESC",
            ],
            [
                "0102030409",
                "Carlos López",
                "TQ02",
                "TG Desarrollo de Software",
            ],
        ]

        archivo = self._crear_archivo_excel(filas)
        response = self.client.post(
            "/estudiantes/importar-excel/",
            {"archivo": archivo},
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(RegistroTitulacion.objects.filter(cedula="0102030409").exists())

    def test_post_without_file_shows_form(self):
        """POST sin archivo debe mostrar formulario con error."""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.post("/estudiantes/importar-excel/", {})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Importar estudiantes", response.content)

