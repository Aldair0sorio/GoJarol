"""Google ID-token verification; identity comes only from verified claims."""
import time
import math
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.validators import validate_email
from google.auth.transport.requests import Request
from google.oauth2 import id_token


class VerificationRequest(Request):
    def __call__(self, *args, **kwargs):
        kwargs['timeout'] = 10
        return super().__call__(*args, **kwargs)


def verify_google_identity(credential):
    audience = getattr(settings, 'GOOGLE_CLIENT_ID', '')
    if not isinstance(audience, str) or not audience.strip():
        raise ImproperlyConfigured('Google client ID is not configured.')
    if not isinstance(credential, str) or not 1 <= len(credential) <= 8192:
        raise ValueError('Missing or invalid credential.')
    claims = id_token.verify_oauth2_token(credential, VerificationRequest(), audience=audience)
    if (not isinstance(claims.get('iss'), str) or claims.get('iss') not in {'accounts.google.com', 'https://accounts.google.com'}
            or claims.get('aud') != audience or claims.get('email_verified') is not True
            or not isinstance(claims.get('sub'), str) or not 1 <= len(claims['sub']) <= 255):
        raise ValueError('Invalid identity claims.')
    now = time.time()
    if (type(claims.get('exp')) not in (int, float) or not math.isfinite(claims['exp']) or claims['exp'] <= now
            or type(claims.get('iat')) not in (int, float) or not math.isfinite(claims['iat']) or claims['iat'] > now):
        raise ValueError('Invalid token lifetime.')
    email = claims.get('email')
    if not isinstance(email, str) or len(email) > 254:
        raise ValueError('Invalid email.')
    validate_email(email)
    return claims
