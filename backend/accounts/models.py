from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Rol(models.TextChoices):
        ESTUDIANTE = "estudiante", "Estudiante"
        DOCENTE = "docente", "Docente"
        ADMIN = "admin", "Administrador"

    class Nivel(models.TextChoices):
        SECUNDARIA = "secundaria", "Secundaria"
        BACHILLERATO = "bachillerato", "Bachillerato"

    rol = models.CharField(max_length=20, choices=Rol.choices, default=Rol.ESTUDIANTE)
    nivel = models.CharField(max_length=20, choices=Nivel.choices, blank=True)
    grado = models.PositiveSmallIntegerField(null=True, blank=True)
    alias = models.CharField(max_length=50, blank=True)
    ranking_publico = models.BooleanField(default=False)

    def __str__(self):
        return self.username