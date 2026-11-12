from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from chat.services.runtime import get_runtime

User = get_user_model()
URL = "/api/v1/chat/messages/"


class ExplanationMenuViewTests(TestCase):
    """Jarol pregunta qué parte se complica antes de explicar (vista completa)."""

    def setUp(self):
        self.client = APIClient()
        self.student = User.objects.create_user(
            username="alumno_menu",
            password="Password123!",
            rol=User.Rol.ESTUDIANTE,
            nivel=User.Nivel.SECUNDARIA,
            grado=1,
        )
        self.client.force_authenticate(user=self.student)
        self.knowledge = get_runtime().knowledge

    def send(self, message):
        response = self.client.post(URL, {"message": message}, format="json")
        self.assertEqual(response.status_code, 200)
        return response.json()

    def test_menu_comes_first_with_menu_field_and_text_options(self):
        data = self.send("no entiendo las fracciones")

        self.assertEqual(data["type"], "explanation_menu")
        self.assertEqual(data["menu"], self.knowledge.get_explanation_menu("mat_fracciones")["options"])
        for option in data["menu"]:
            self.assertEqual(set(option), {"label", "text"})
            self.assertIn(f"{option['label']}) {option['text']}", data["reply"])
        self.assertIsNone(data["exercise"])

    def test_letter_answer_is_interpreted_and_has_no_menu_field(self):
        self.send("explícame los porcentajes")
        data = self.send("b")

        self.assertEqual(data["type"], "explanation")
        self.assertEqual(data["reply"], self.knowledge.get_menu_explanation("mat_porcentajes", "B"))
        self.assertNotIn("Hasta pronto", data["reply"])
        self.assertNotIn("menu", data)

    def test_option_text_is_not_hijacked_by_operation_guides(self):
        self.send("no entiendo las fracciones")
        data = self.send("Sumar o restar fracciones con distinto denominador")

        self.assertEqual(data["reply"], self.knowledge.get_menu_explanation("mat_fracciones", "C"))

    def test_second_request_without_choosing_gets_full_explanation(self):
        self.send("no entiendo las fracciones")
        data = self.send("no entiendo las fracciones")

        self.assertEqual(data["type"], "explanation")
        self.assertEqual(data["reply"], self.knowledge.get_explanation("mat_fracciones", "basic"))
        self.assertNotIn("menu", data)

    def test_starting_an_exercise_clears_pending_menu(self):
        self.send("explícame la ortografía")
        data = self.send("Ponme un ejercicio de ortografía")

        self.assertEqual(data["type"], "exercise")
        self.assertNotIn("expected_answer", str(data["exercise"]))
        self.student.progress.refresh_from_db()
        self.assertIsNone(self.student.progress.tutor_state["pending_explanation_menu"])


class GuidedProblemViewTests(TestCase):
    """El alumno trae su problema y Jarol lo acompaña paso a paso (vista completa)."""

    def setUp(self):
        self.client = APIClient()
        self.student = User.objects.create_user(
            username="alumno_guiado",
            password="Password123!",
            rol=User.Rol.ESTUDIANTE,
            nivel=User.Nivel.SECUNDARIA,
            grado=1,
        )
        self.client.force_authenticate(user=self.student)

    def send(self, message):
        response = self.client.post(URL, {"message": message}, format="json")
        self.assertEqual(response.status_code, 200)
        return response.json()

    def test_not_knowing_a_step_keeps_the_problem_and_never_gives_the_result(self):
        replies = [self.send(message)["reply"] for message in (
            "¿Cuánto es 1/2 + 3/4?",
            "No sé buscar un denominador común",
            "dame la respuesta",
            "4",
            "2/4",
        )]

        self.assertIn("Denominador común", replies[0])
        self.assertNotIn("¿Sobre qué tema", replies[1])
        self.assertIn("tabla del **2** y la del **4**", replies[1])
        self.assertTrue(replies[2].startswith("No te voy a dar el resultado"))
        self.assertIn("Convertir 1/2", replies[3])
        self.assertIn("**2/4 + 3/4**", replies[4])
        for reply in replies:
            self.assertNotIn("5/4", reply)

        final = self.send("5/4")
        self.assertIn("¡Exacto!", final["reply"])
        self.assertEqual(final["xpEarned"], 0)
        self.student.progress.refresh_from_db()
        self.assertNotIn("custom_problem", self.student.progress.tutor_state)

    def test_expected_result_is_kept_on_the_server(self):
        data = self.send("¿Cuánto es 1/2 + 3/4?")

        self.assertNotIn("5/4", str(data))
        self.assertNotIn("expected", str(data))
