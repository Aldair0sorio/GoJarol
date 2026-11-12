"""Registro de eventos del tutor para las señales de copia.

Reglas de privacidad (alumnos menores de edad):
- Solo se guarda usuario, tema (opcional), tipo de evento y fecha. Nunca el texto del mensaje.
- Si el registro falla, la respuesta del chat sigue normal y el log no incluye texto del alumno.
"""
import logging

from django.db import transaction

from progress.models import TutorEvent

logger = logging.getLogger(__name__)

VALID_KINDS = {choice.value for choice in TutorEvent.Kind}


def record_event(user, kind, topic_id=None):
    if kind not in VALID_KINDS or user is None or not getattr(user, "is_authenticated", False):
        return
    try:
        with transaction.atomic():
            TutorEvent.objects.create(user=user, kind=kind, topic_id=str(topic_id or "")[:64])
    except Exception:  # Registrar nunca debe romper la respuesta del tutor.
        logger.warning("No se pudo registrar un evento del tutor (tipo=%s).", kind)


def record_events(user, kinds, topic_id=None):
    for kind in kinds or []:
        record_event(user, kind, topic_id)
