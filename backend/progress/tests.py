from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from progress.models import StudentProgress

User = get_user_model()


class ProgressLeagueViewsTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.student_gold = User.objects.create_user(
            username="ana_oro",
            password="Password123!",
            rol=User.Rol.ESTUDIANTE,
            nivel=User.Nivel.SECUNDARIA,
            grado=2,
            alias="Ana",
        )
        progress_gold, _ = StudentProgress.objects.get_or_create(user=self.student_gold)
        progress_gold.xp = 1250
        progress_gold.save()

        self.student_silver = User.objects.create_user(
            username="luis_plata",
            password="Password123!",
            rol=User.Rol.ESTUDIANTE,
            nivel=User.Nivel.BACHILLERATO,
            grado=3,
            alias="Luis",
        )
        progress_silver, _ = StudentProgress.objects.get_or_create(user=self.student_silver)
        progress_silver.xp = 650
        progress_silver.save()

    def test_progress_me_includes_league_rank(self):
        self.client.force_authenticate(user=self.student_gold)
        res = self.client.get("/api/v1/progress/me/")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["xp"], 1250)
        self.assertEqual(res.data["league"]["id"], "oro")
        self.assertEqual(res.data["league"]["name"], "Oro")
        self.assertEqual(res.data["league"]["nextRank"], "Diamante")
        self.assertEqual(res.data["league"]["xpToNext"], 1250)

    def test_leaderboard_includes_league_for_each_student(self):
        self.client.force_authenticate(user=self.student_gold)
        res = self.client.get("/api/v1/progress/leaderboard/")
        self.assertEqual(res.status_code, 200)
        by_username = {row["username"]: row for row in res.data}
        self.assertEqual(by_username["ana_oro"]["rank"], 1)
        self.assertEqual(by_username["ana_oro"]["league"]["id"], "oro")
        self.assertEqual(by_username["luis_plata"]["rank"], 2)
        self.assertEqual(by_username["luis_plata"]["league"]["id"], "plata")
