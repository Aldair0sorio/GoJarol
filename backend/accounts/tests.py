from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

User = get_user_model()


class GoogleLoginTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_google_login_creates_new_student(self):
        payload = {
            "email": "emiliano.valdes@estudiantes.sev.gob.mx",
            "name": "Emiliano Valdés",
            "role": "estudiante",
            "picture": "https://example.com/avatar.jpg",
            "grade": "3° de Secundaria",
        }
        res = self.client.post("/api/v1/auth/google/", payload, format="json")
        self.assertEqual(res.status_code, 200)
        self.assertIn("token", res.data)
        self.assertEqual(res.data["user"]["email"], "emiliano.valdes@estudiantes.sev.gob.mx")
        self.assertEqual(res.data["user"]["rol"], "estudiante")

    def test_google_login_existing_user(self):
        # Crear primero
        User.objects.create_user(
            username="lauramendoza",
            email="laura.mendoza@docentes.sev.gob.mx",
            rol="docente",
            alias="Prof. Laura Mendoza",
        )
        payload = {
            "email": "laura.mendoza@docentes.sev.gob.mx",
            "name": "Prof. Laura Mendoza",
            "role": "docente",
        }
        res = self.client.post("/api/v1/auth/google/", payload, format="json")
        self.assertEqual(res.status_code, 200)
        self.assertIn("token", res.data)
        self.assertEqual(res.data["user"]["email"], "laura.mendoza@docentes.sev.gob.mx")
        self.assertEqual(res.data["user"]["rol"], "docente")

    def test_google_login_missing_email_fails(self):
        res = self.client.post("/api/v1/auth/google/", {}, format="json")
        self.assertEqual(res.status_code, 400)
