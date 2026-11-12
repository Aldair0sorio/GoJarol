import uuid
from collections.abc import Mapping
from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.throttling import AnonRateThrottle
from rest_framework.exceptions import ValidationError as APIValidationError
from django.db import IntegrityError, transaction
from django.utils import timezone

from .serializers import RegisterSerializer, UserSerializer, ProfileUpdateSerializer
from .email_verification import send_verification, consume_verification, VerificationDeliveryFailed, VerificationRateLimited

User = get_user_model()


class PublicAuthView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        if not isinstance(request.data, Mapping):
            raise APIValidationError({'error': 'Envía un objeto JSON con los campos solicitados.'})


class RegistrationThrottle(AnonRateThrottle):
    scope = 'registration'
    rate = '10/hour'


class AuthConfigView(PublicAuthView):
    """Public contract and Google audience; never SMTP settings or credentials."""
    def get(self, request):
        response = Response({'auth_contract_version': 2, 'registration_mode': 'email_verification',
                             'google_client_id': getattr(settings, 'GOOGLE_CLIENT_ID', '') or None})
        response['Cache-Control'] = 'no-store'
        return response


class RegisterView(PublicAuthView):
    throttle_classes = [RegistrationThrottle]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            with transaction.atomic():
                user = serializer.save()
        except IntegrityError:
            return Response({'error': {'message': 'El usuario o correo ya está registrado.'}}, status=400)
        try:
            send_verification(user)
        except VerificationRateLimited:
            return Response({'verification_required': True, 'email_sent': False, 'account_created': True,
                'error': {'message': 'Tu cuenta se creó. Ya se solicitó un correo; espera un minuto antes de reenviar.'}}, status=429)
        except VerificationDeliveryFailed:
            return Response({'verification_required': True, 'email_sent': False, 'account_created': True,
                'error': {'message': 'Tu cuenta se creó, pero no pudimos enviar el correo. Solicita un reenvío en un minuto.'}}, status=503)
        return Response({'verification_required': True, 'email_sent': True}, status=201)


class LoginView(PublicAuthView):

    def post(self, request):
        raw_identifier = request.data.get("username", "")
        password = request.data.get("password", "")
        if not isinstance(raw_identifier, str) or not isinstance(password, str):
            return Response({'error': {'message': 'Credenciales inválidas.'}}, status=400)
        raw_identifier = raw_identifier.strip()

        user = authenticate(username=raw_identifier, password=password)
        if user is None and "@" in raw_identifier:
            user_by_email = User.objects.filter(email__iexact=raw_identifier).first()
            if user_by_email:
                user = authenticate(username=user_by_email.username, password=password)

        if user is None:
            return Response(
                {"error": {"code": "invalid_credentials", "message": "Usuario o contraseña incorrectos."}},
                status=401,
            )
        if user.email_status == User.EmailStatus.PENDING:
            return Response({'verification_required': True, 'error': {'message': 'Confirma tu correo antes de iniciar sesión.'}}, status=403)
        token, _ = Token.objects.get_or_create(user=user)
        return Response({"token": token.key, "user": UserSerializer(user).data})


class GoogleLoginView(PublicAuthView):

    def post(self, request):
        from django.core.exceptions import ImproperlyConfigured, ValidationError
        from django.db import IntegrityError, transaction
        from google.auth.exceptions import GoogleAuthError, TransportError
        from .google_identity import verify_google_identity
        from .models import GoogleIdentity

        def error(code, message, status):
            return Response({'error': {'code': code, 'message': message}}, status=status)

        credential = request.data.get('credential')
        if not isinstance(credential, str) or not 1 <= len(credential) <= 8192:
            return error('invalid_credential', 'Se requiere una credencial válida de Google.', 400)
        try:
            claims = verify_google_identity(credential)
        except (ImproperlyConfigured, TransportError):
            return error('google_unavailable', 'No se puede verificar Google en este momento. Usa tu contraseña o intenta más tarde.', 503)
        except (ValueError, ValidationError, GoogleAuthError):
            return error('invalid_google_token', 'La identidad de Google no pudo verificarse.', 401)

        email = claims['email'].strip().lower()
        subject = claims['sub']
        try:
            with transaction.atomic():
                identity = GoogleIdentity.objects.select_for_update().select_related('user').filter(subject=subject).first()
                if identity:
                    if identity.email != email:
                        return error('identity_changed', 'El correo asociado cambió. Se requiere revisar la vinculación de la cuenta.', 409)
                    user = identity.user
                else:
                    if User.objects.filter(email__iexact=email).exists() or GoogleIdentity.objects.filter(email=email).exists():
                        return error('account_link_required', 'Usa el acceso original de tu cuenta. No se vinculan cuentas automáticamente por correo.', 409)
                    role = request.data.get('role', User.Rol.ESTUDIANTE)
                    if not isinstance(role, str) or role not in {User.Rol.ESTUDIANTE, User.Rol.DOCENTE}:
                        return error('invalid_role', 'Selecciona un tipo de cuenta permitido.', 400)
                    level = request.data.get('nivel', User.Nivel.SECUNDARIA) if role == User.Rol.ESTUDIANTE else ''
                    grade = request.data.get('grado', 1) if role == User.Rol.ESTUDIANTE else None
                    if role == User.Rol.ESTUDIANTE and (not isinstance(level, str) or level not in User.Nivel.values or type(grade) is not int or not 1 <= grade <= (3 if level == User.Nivel.SECUNDARIA else 6)):
                        return error('invalid_grade', 'El nivel o grado no es válido.', 400)
                    user = User.objects.create_user(username='google_' + uuid.uuid4().hex, email=email,
                        first_name=str(claims.get('given_name') or '')[:150], last_name=str(claims.get('family_name') or '')[:150],
                        alias=str(claims.get('name') or '')[:50], rol=role, nivel=level, grado=grade,
                        email_status=User.EmailStatus.VERIFIED, email_verified_at=timezone.now())
                    GoogleIdentity.objects.create(subject=subject, email=email, user=user)
                if not user.is_active:
                    return error('inactive_account', 'Esta cuenta no está disponible.', 403)
                if user.email_status != User.EmailStatus.VERIFIED:
                    user.email_status, user.email_verified_at = User.EmailStatus.VERIFIED, timezone.now()
                    user.save(update_fields=['email_status', 'email_verified_at'])
                token, _ = Token.objects.get_or_create(user=user)
                return Response({'token': token.key, 'user': UserSerializer(user).data})
        except IntegrityError:
            return error('identity_conflict', 'La identidad ya se está registrando. Intenta de nuevo o usa tu acceso original.', 409)


class MeView(APIView):
    def get(self, request):
        return Response(UserSerializer(request.user).data)

    def patch(self, request):
        serializer = ProfileUpdateSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(UserSerializer(request.user).data)


class LogoutView(APIView):
    def post(self, request):
        from django.contrib.auth import logout
        if request.auth is not None:
            request.auth.delete()
        logout(request)
        return Response(status=204)


class VerificationThrottle(AnonRateThrottle):
    scope = 'email_verification'
    rate = '20/hour'


class VerifyEmailView(PublicAuthView):
    throttle_classes = [VerificationThrottle]

    def post(self, request):
        if not consume_verification(request.data.get('uid'), request.data.get('token')):
            return Response({'error': {'message': 'El enlace no es válido o ha caducado. Solicita otro correo.'}}, status=400)
        return Response({'email_verified': True})


class ResendVerificationView(PublicAuthView):
    throttle_classes = [VerificationThrottle]

    def post(self, request):
        from rest_framework import serializers
        serializer = serializers.EmailField(max_length=254)
        email = serializer.run_validation(request.data.get('email'))
        user = User.objects.filter(email__iexact=email, email_status=User.EmailStatus.PENDING, is_active=True).first()
        if user:
            try:
                send_verification(user)
            except VerificationRateLimited:
                return Response({'error': {'message': 'Espera un minuto entre envíos. El máximo es de cinco por hora.'}}, status=429)
            except VerificationDeliveryFailed:
                return Response({'email_sent': False, 'error': {'message': 'No pudimos enviar el correo. Inténtalo más tarde.'}}, status=503)
        return Response({'message': 'Si hay una cuenta pendiente con ese correo, enviamos un enlace de verificación.'}, status=202)


class DemoLoginView(PublicAuthView):
    """Compatibility route: public passwordless demo access is retired."""
    def post(self, request):
        return Response({'error': {'code': 'legacy_auth_disabled',
            'message': 'El acceso de demostración ya no está disponible. Inicia sesión con tu cuenta.'}}, status=410)


class SwitchRoleView(APIView):
    """Account roles cannot be changed by a student or teacher request."""
    def post(self, request):
        return Response({'error': {'code': 'role_change_not_allowed',
            'message': 'No puedes cambiar el rol de tu cuenta desde esta aplicación.'}}, status=403)
