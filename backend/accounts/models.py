from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.functions import Lower
from .regions import STATES


class User(AbstractUser):
    class EmailStatus(models.TextChoices):
        LEGACY = 'legacy', 'Cuenta anterior'
        PENDING = 'pending', 'Pendiente de verificación'
        VERIFIED = 'verified', 'Correo verificado'

    estado = models.CharField(max_length=2, choices=STATES, blank=True)
    email_status = models.CharField(max_length=8, choices=EmailStatus.choices, default=EmailStatus.LEGACY)
    email_verified_at = models.DateTimeField(null=True, blank=True)

    class Meta(AbstractUser.Meta):
        constraints = [models.UniqueConstraint(
            Lower('email'), condition=~models.Q(email_status='legacy') & ~models.Q(email=''),
            name='accounts_verified_email_unique')]
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

class GoogleIdentity(models.Model):
    subject = models.CharField(max_length=255, primary_key=True)
    email = models.EmailField(unique=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='google_identity')


class EmailVerification(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='email_verification')
    token_hash = models.CharField(max_length=64, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    last_attempt_at = models.DateTimeField(null=True, blank=True)
    window_started_at = models.DateTimeField(null=True, blank=True)
    send_count = models.PositiveSmallIntegerField(default=0)
