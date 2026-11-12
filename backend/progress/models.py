from django.conf import settings
from django.db import models


class StudentProgress(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="progress",
    )
    xp = models.PositiveIntegerField(default=0)
    streak_days = models.PositiveIntegerField(default=1)
    tutor_state = models.JSONField(default=dict, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Progreso de {self.user.username} ({self.xp} XP)"
