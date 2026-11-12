"""Single-use, hashed verification tokens and database-backed resend limits."""
import hashlib
import secrets
import smtplib
from datetime import timedelta
from urllib.parse import urlsplit

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.mail import EmailMessage
from django.db import transaction
from django.utils import timezone

from .models import EmailVerification, User


class VerificationRateLimited(Exception):
    pass


class VerificationDeliveryFailed(Exception):
    pass


def send_verification(user):
    origin = getattr(settings, 'FRONTEND_URL', '')
    try:
        parsed = urlsplit(origin)
    except (ValueError, TypeError):
        raise VerificationDeliveryFailed('Invalid frontend origin configuration.') from None
    if (parsed.scheme not in ('http', 'https') or not parsed.netloc or parsed.username
            or parsed.password or parsed.path not in ('', '/') or parsed.query or parsed.fragment):
        raise VerificationDeliveryFailed('Invalid frontend origin configuration.')
    # Lock in the same order as consume_verification. Limits survive worker restarts.
    failed = False
    with transaction.atomic():
        user = User.objects.select_for_update().get(pk=user.pk)
        if user.email_status != User.EmailStatus.PENDING:
            return
        verification, _ = EmailVerification.objects.get_or_create(user=user)
        now = timezone.now()
        if (verification.last_attempt_at and now - verification.last_attempt_at < timedelta(seconds=60)):
            raise VerificationRateLimited()
        if not verification.window_started_at or now - verification.window_started_at >= timedelta(hours=1):
            verification.window_started_at, verification.send_count = now, 0
        if verification.send_count >= 5:
            raise VerificationRateLimited()
        verification.last_attempt_at = now
        verification.send_count += 1
        verification.save()
        token = secrets.token_urlsafe(32)
        url = f'{origin.rstrip("/")}/verificar-correo/{user.pk}/{token}'
        message = EmailMessage(
            subject='Confirma tu correo en Go Jarol',
            body=f'¡Hola!\n\nConfirma tu correo para entrar a Go Jarol:\n{url}\n\n'
                 'El enlace caduca en 24 horas y solo puede usarse una vez. '
                 'Si no creaste esta cuenta, ignora el mensaje.\n\nGo Jarol',
            from_email=settings.DEFAULT_FROM_EMAIL, to=[user.email])
        try:
            if message.send(using='default') != 1:
                failed = True
        except (smtplib.SMTPException, OSError, ImproperlyConfigured, ValueError):
            failed = True
        if not failed:
            verification.token_hash = hashlib.sha256(token.encode()).hexdigest()
            verification.expires_at = now + timedelta(hours=24)
            verification.save(update_fields=['token_hash', 'expires_at'])
    # Preserve throttling on failure and keep the last successfully sent token valid.
    if failed:
        raise VerificationDeliveryFailed()


def consume_verification(uid, token):
    if not isinstance(uid, (str, int)) or isinstance(uid, bool) or not str(uid).isdigit() or len(str(uid)) > 18:
        return False
    if not isinstance(token, str) or not 32 <= len(token) <= 128:
        return False
    with transaction.atomic():
        user = User.objects.select_for_update().filter(pk=uid, is_active=True).first()
        if not user or user.email_status != User.EmailStatus.PENDING:
            return False
        verification = EmailVerification.objects.filter(user=user).first()
        if (not verification or not verification.token_hash or not verification.expires_at
                or timezone.now() >= verification.expires_at
                or not secrets.compare_digest(verification.token_hash, hashlib.sha256(token.encode()).hexdigest())):
            return False
        user.email_status, user.email_verified_at = User.EmailStatus.VERIFIED, timezone.now()
        user.save(update_fields=['email_status', 'email_verified_at'])
        verification.token_hash, verification.expires_at = '', None
        verification.save(update_fields=['token_hash', 'expires_at'])
        return True
