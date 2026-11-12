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


class ExerciseAttempt(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="exercise_attempts",
    )
    topic_id = models.CharField(max_length=64, db_index=True)
    exercise_id = models.CharField(max_length=64, db_index=True)
    exercise_question = models.TextField()
    exercise_type = models.CharField(max_length=32, default="numeric")
    difficulty = models.PositiveSmallIntegerField(default=1)
    submitted_answer = models.CharField(max_length=255, blank=True)
    is_correct = models.BooleanField(default=False)
    hints_used = models.PositiveSmallIntegerField(default=0)
    feedback = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        status = "OK" if self.is_correct else "ERR"
        return f"{self.user.username} · {self.exercise_id} [{status}]"
