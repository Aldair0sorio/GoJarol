import secrets

from django.conf import settings
from django.db import models

from accounts.models import User

# Sin 0, O, 1, I ni L, para que nadie confunda caracteres al escribir el código
ALFABETO = "ABCDEFGHJKMNPQRSTUVWXYZ23456789"


def generar_codigo():
    return "JAROL-" + "".join(secrets.choice(ALFABETO) for _ in range(5))


class Classroom(models.Model):
    docente = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="clases_creadas"
    )
    nombre = models.CharField(max_length=100)
    nivel = models.CharField(max_length=20, choices=User.Nivel.choices)
    grado = models.PositiveSmallIntegerField()
    subject = models.ForeignKey(
        "curriculum.Subject", on_delete=models.PROTECT, related_name="classrooms"
    )
    codigo = models.CharField(max_length=20, unique=True, editable=False)
    codigo_activo = models.BooleanField(default=True)
    creada = models.DateTimeField(auto_now_add=True)

    def regenerate_code(self, save: bool = True) -> str:
        while True:
            candidato = generar_codigo()
            if not Classroom.objects.filter(codigo=candidato).exists():
                self.codigo = candidato
                break
        if save and self.pk:
            self.save(update_fields=["codigo"])
        return self.codigo

    def save(self, *args, **kwargs):
        if not self.codigo:
            self.regenerate_code(save=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nombre} ({self.codigo})"


class Enrollment(models.Model):
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE, related_name="enrollments")
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="inscripciones"
    )
    unido = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("classroom", "student")

    def __str__(self):
        return f"{self.student} en {self.classroom}"


class ClassAnnouncement(models.Model):
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE, related_name="announcements")
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="class_announcements"
    )
    title = models.CharField(max_length=140)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"[{self.classroom.codigo}] {self.title}"


class ClassChallenge(models.Model):
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE, related_name="challenges")
    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="assigned_challenges"
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="personal_challenges",
    )
    topic_id = models.CharField(max_length=64)
    title = models.CharField(max_length=140)
    instructions = models.TextField(blank=True)
    target_exercises = models.PositiveSmallIntegerField(default=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        scope = self.student.username if self.student else "Grupo completo"
        return f"[{self.classroom.codigo}] {self.title} ({scope})"
