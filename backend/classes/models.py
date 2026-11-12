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

    def save(self, *args, **kwargs):
        if not self.codigo:
            while True:
                candidato = generar_codigo()
                if not Classroom.objects.filter(codigo=candidato).exists():
                    self.codigo = candidato
                    break
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