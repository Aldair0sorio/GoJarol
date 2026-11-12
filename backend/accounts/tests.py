from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import include, path
from rest_framework.authtoken.models import Token
from accounts.test_profile_api import database
from rest_framework.test import APIClient

User = get_user_model()


urlpatterns = [path('api/v1/auth/', include('accounts.urls'))]


@override_settings(ROOT_URLCONF=__name__)
class GoogleLoginTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_google_login_without_verified_credential_cannot_create_student(self):
        payload = {
            "email": "emiliano.valdes@estudiantes.sev.gob.mx",
            "name": "Emiliano Valdés",
            "role": "estudiante",
            "picture": "https://example.com/avatar.jpg",
            "grade": "3° de Secundaria",
        }
        res = self.client.post("/api/v1/auth/google/", payload, format="json")
        self.assertEqual(res.status_code, 400)
        self.assertNotIn('token', res.data)
        self.assertFalse(User.objects.filter(email=payload['email']).exists())

    def test_google_login_email_alone_cannot_take_over_existing_user(self):
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
        self.assertEqual(res.status_code, 400)
        self.assertNotIn('token', res.data)
        user = User.objects.get(email=payload['email'])
        self.assertEqual(user.rol, 'docente')
        self.assertFalse(Token.objects.filter(user=user).exists())

    def test_google_login_missing_credential_fails(self):
        res = self.client.post("/api/v1/auth/google/", {}, format="json")
        self.assertEqual(res.status_code, 400)
