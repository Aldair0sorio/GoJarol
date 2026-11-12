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


class TutorEvent(models.Model):
    """Evento del tutor para las señales de copia. NO guarda el texto de los mensajes del alumno."""

    class Kind(models.TextChoices):
        ANSWER_REQUEST = "answer_request", "Pidió la respuesta directa"
        BYPASS_ATTEMPT = "bypass_attempt", "Intentó saltarse las reglas"
        STEP_SOLVED = "step_solved", "Resolvió un paso o ejercicio por su cuenta"
        HINT_USED = "hint_used", "Pidió una pista o ayuda"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="tutor_events",
    )
    topic_id = models.CharField(max_length=64, blank=True, default="")
    kind = models.CharField(max_length=32, choices=Kind.choices)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created"]
        indexes = [models.Index(fields=["user", "created"])]

    def __str__(self):
        return f"{self.user_id} · {self.kind}"
