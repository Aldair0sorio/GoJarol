"""Real HTTP contracts, isolated database and in-memory mail; never live SMTP."""
import re
import smtplib
from datetime import timedelta
from unittest.mock import patch

import pytest
from accounts.test_profile_api import database  # Reuse the existing isolated Django test setup.
from accounts.models import EmailVerification, User
from accounts.regions import STATES
from chat.views import ChatMessageView
from django.core import mail
from django.core.cache import cache
from django.db import IntegrityError, transaction
from django.test import override_settings
from django.urls import include, path
from django.utils import timezone
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

urlpatterns = [path('auth/', include('accounts.urls')), path('chat/messages/', ChatMessageView.as_view())]


@pytest.fixture(autouse=True)
def environment(database):
    cache.clear()
    mail.outbox = []
    with override_settings(ROOT_URLCONF=__name__, FRONTEND_URL='http://localhost:5173',
            DEFAULT_FROM_EMAIL='Go Jarol <no.reply.trees.25@gmail.com>',
            MAILERS={'default': {'BACKEND': 'django.core.mail.backends.locmem.EmailBackend'}},
            AUTH_PASSWORD_VALIDATORS=[{'NAME':'django.contrib.auth.password_validation.MinimumLengthValidator'},
                                      {'NAME':'django.contrib.auth.password_validation.NumericPasswordValidator'}]):
        yield


def payload(**changes):
    number = User.objects.count()
    return dict(username=f'new_{number}', email=f'new_{number}@example.test', full_name='Ana López',
                password='Aprender-con-Jarol-734!', password_confirm='Aprender-con-Jarol-734!',
                rol='estudiante', nivel='secundaria', grado=1, estado='30', **changes)


def data(**changes):
    result = payload()
    result.update(changes)
    return result


def register(**changes):
    request = data(**changes)
    response = APIClient().post('/auth/register/', request, format='json')
    return request, response


def link():
    match = re.search(r'/verificar-correo/(\d+)/([A-Za-z0-9_-]+)', mail.outbox[-1].body)
    assert match
    return {'uid': match[1], 'token': match[2]}


@pytest.mark.parametrize('role', ['estudiante', 'docente'])
def test_register_verify_login_profile_chat_logout(role):
    request, response = register(rol=role)
    assert response.status_code == 201 and response.data == {'verification_required': True, 'email_sent': True}
    user = User.objects.get(username=request['username'])
    assert user.email_status == 'pending' and user.email_verified_at is None
    assert user.first_name == request['full_name'] and user.estado == '30'
    assert not user.is_staff and not user.is_superuser and not Token.objects.filter(user=user).exists()
    assert user.check_password(request['password']) and user.password != request['password']
    if role == 'docente':
        assert user.nivel == '' and user.grado is None
    assert len(mail.outbox) == 1 and mail.outbox[0].to == [request['email']]
    assert mail.outbox[0].from_email == 'Go Jarol <no.reply.trees.25@gmail.com>'
    assert mail.outbox[0].body.startswith('¡Hola!')
    visitor = APIClient()
    credentials = {'username': request['email'], 'password': request['password']}
    pending = visitor.post('/auth/login/', credentials, format='json')
    assert pending.status_code == 403 and pending.data['verification_required'] and 'token' not in pending.data
    confirmation = link()
    assert confirmation['token'] != user.email_verification.token_hash
    assert visitor.post('/auth/verify-email/', confirmation, format='json').status_code == 200
    assert visitor.post('/auth/verify-email/', confirmation, format='json').status_code == 400
    user.refresh_from_db()
    assert user.email_status == 'verified' and user.email_verified_at
    login = visitor.post('/auth/login/', credentials, format='json')
    assert login.status_code == 200
    visitor.credentials(HTTP_AUTHORIZATION='Token ' + login.data['token'])
    profile = visitor.get('/auth/me/')
    assert profile.status_code == 200 and profile.data['estado'] == '30' and profile.data['email_status'] == 'verified'
    assert visitor.patch('/auth/me/', {'estado': '09'}, format='json').status_code == 200
    assert visitor.get('/auth/me/').data['estado'] == '09'
    chat = visitor.post('/chat/messages/', {'message': 'Explícame las fracciones'}, format='json')
    assert chat.status_code == 200 and chat.data['type'] == 'explanation'
    assert visitor.post('/auth/logout/').status_code == 204
    assert visitor.get('/auth/me/').status_code == 401


@pytest.mark.parametrize('estado', [code for code, _ in STATES])
def test_all_32_states_are_accepted(estado):
    request, response = register(estado=estado)
    assert response.status_code == 201
    assert User.objects.get(username=request['username']).estado == estado


def test_state_codes_are_unique_and_stable():
    assert len(STATES) == len(set(code for code, _ in STATES)) == 32
    assert set(code for code, _ in STATES) == {f'{number:02d}' for number in range(1, 33)}


@pytest.mark.parametrize('changes', [
    {'full_name': ''}, {'email': 'invalid'}, {'email': ''}, {'username': ''}, {'username': 'bad space'},
    {'estado': ''}, {'estado': '33'}, {'estado': 'Veracruz'}, {'rol': 'admin'},
    {'nivel': 'universidad'}, {'grado': 0}, {'grado': 4}, {'nivel': 'bachillerato', 'grado': 7},
    {'password_confirm': 'other'}, {'password': '123', 'password_confirm': '123'},
    {'password': '1234567890', 'password_confirm': '1234567890'},
    {'email_status': 'verified'}, {'is_staff': True}, {'school': 'hidden school'},
])
def test_registration_rejects_invalid_fields_without_creating_users(changes):
    before = User.objects.count()
    _, response = register(**changes)
    assert response.status_code == 400 and 'token' not in response.data
    assert User.objects.count() == before and not mail.outbox


def test_bachillerato_semester_six_is_saved():
    request, response = register(nivel='bachillerato', grado=6)
    assert response.status_code == 201
    assert User.objects.get(username=request['username']).grado == 6


def test_expired_invalid_and_other_account_tokens_are_rejected():
    _, response = register()
    assert response.status_code == 201
    confirmation = link()
    other_request, _ = register()
    other = User.objects.get(username=other_request['username'])
    visitor = APIClient()
    for invalid in [{**confirmation, 'token': 'x' * 43}, {**confirmation, 'uid': other.pk},
                    {'uid': [], 'token': 'x' * 43}, {'uid': '9' * 50, 'token': 'x' * 43}, {}]:
        assert visitor.post('/auth/verify-email/', invalid, format='json').status_code == 400
    verification = EmailVerification.objects.get(user_id=confirmation['uid'])
    verification.expires_at = timezone.now() - timedelta(seconds=1)
    verification.save()
    assert visitor.post('/auth/verify-email/', confirmation, format='json').status_code == 400
    assert User.objects.get(pk=confirmation['uid']).email_status == 'pending'


def test_resend_rotates_token_and_enforces_persistent_limits():
    request, _ = register()
    original = link()
    c = APIClient()
    assert c.post('/auth/resend-verification/', {'email': request['email']}, format='json').status_code == 429
    verification = EmailVerification.objects.get(user__username=request['username'])
    for _ in range(4):
        verification.last_attempt_at = timezone.now() - timedelta(seconds=61)
        verification.save(update_fields=['last_attempt_at'])
        assert c.post('/auth/resend-verification/', {'email': request['email']}, format='json').status_code == 202
        verification.refresh_from_db()
    assert len(mail.outbox) == 5 and verification.send_count == 5
    assert c.post('/auth/verify-email/', original, format='json').status_code == 400
    verification.last_attempt_at = timezone.now() - timedelta(seconds=61)
    verification.save()
    cache.clear()  # Account limits remain effective across cache/process resets.
    assert c.post('/auth/resend-verification/', {'email': request['email']}, format='json').status_code == 429
    verification.window_started_at = timezone.now() - timedelta(hours=2)
    verification.save()
    assert c.post('/auth/resend-verification/', {'email': request['email']}, format='json').status_code == 202
    assert c.post('/auth/verify-email/', link(), format='json').status_code == 200


def test_smtp_failure_retains_pending_account_without_claiming_delivery():
    with patch('accounts.email_verification.EmailMessage.send', side_effect=smtplib.SMTPAuthenticationError(535, b'rejected')):
        request, response = register()
    assert response.status_code == 503 and response.data['email_sent'] is False and response.data['account_created']
    user = User.objects.get(username=request['username'])
    assert user.email_status == 'pending' and not Token.objects.filter(user=user).exists()
    assert user.email_verification.send_count == 1 and not user.email_verification.token_hash
    assert not mail.outbox


def test_failed_resend_preserves_last_successful_token_and_reports_failure():
    request, _ = register()
    confirmation = link()
    verification = EmailVerification.objects.get(user__username=request['username'])
    verification.last_attempt_at = timezone.now() - timedelta(seconds=61)
    verification.save()
    with patch('accounts.email_verification.EmailMessage.send', return_value=0):
        response = APIClient().post('/auth/resend-verification/', {'email': request['email']}, format='json')
    assert response.status_code == 503 and response.data['email_sent'] is False
    assert APIClient().post('/auth/verify-email/', confirmation, format='json').status_code == 200


def test_resend_unknown_or_legacy_does_not_disclose_identity():
    legacy = User.objects.create_user(username=f'legacy_{User.objects.count()}', email='legacy-access@example.test', password='Existing-strong-274!')
    c = APIClient()
    missing = c.post('/auth/resend-verification/', {'email': 'unknown@example.test'}, format='json')
    existing = c.post('/auth/resend-verification/', {'email': legacy.email}, format='json')
    assert missing.status_code == existing.status_code == 202 and missing.data == existing.data
    assert not mail.outbox and legacy.email_status == 'legacy'
    assert c.post('/auth/login/', {'username': legacy.username, 'password': 'Existing-strong-274!'}, format='json').status_code == 200


def test_duplicate_email_is_case_insensitive_and_database_enforced():
    request, _ = register()
    _, response = register(email=request['email'].upper())
    assert response.status_code == 400
    with pytest.raises(IntegrityError), transaction.atomic():
        User.objects.create_user(username='concurrent-duplicate', email=request['email'].upper(), email_status='pending')


def test_host_header_never_controls_verification_url():
    register()
    assert 'http://localhost:5173/verificar-correo/' in mail.outbox[-1].body
    with override_settings(FRONTEND_URL='https://example.test@attacker.test/path'):
        _, response = register()
    assert response.status_code == 503 and not response.data['email_sent']


def test_resend_ip_throttle_rejects_excess_requests():
    c = APIClient()
    for _ in range(20):
        assert c.post('/auth/resend-verification/', {'email': 'unknown@example.test'}, format='json').status_code == 202
    assert c.post('/auth/resend-verification/', {'email': 'unknown@example.test'}, format='json').status_code == 429


def test_pending_accounts_cannot_authenticate_even_with_an_old_api_token():
    from accounts.authentication import VerifiedTokenAuthentication
    from rest_framework.exceptions import AuthenticationFailed
    request, _ = register()
    user = User.objects.get(username=request['username'])
    token = Token.objects.create(user=user)
    with pytest.raises(AuthenticationFailed):
        VerifiedTokenAuthentication().authenticate_credentials(token.key)
    c = APIClient()
    c.credentials(HTTP_AUTHORIZATION='Token '+token.key)
    assert c.get('/auth/me/').status_code == 401
    assert c.post('/chat/messages/', {'message':'Explícame las fracciones'}, format='json').status_code == 401
    assert APIClient().post('/auth/verify-email/', link(), format='json').status_code == 200
    assert VerifiedTokenAuthentication().authenticate_credentials(token.key)[0].pk == user.pk


def test_migrations_preserve_legacy_users_and_google_subjects():
    import subprocess
    import sys
    code = '''
import accounts.test_profile_api
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
executor = MigrationExecutor(connection)
executor.migrate([('accounts', '0002_googleidentity')])
apps = executor.loader.project_state([('accounts', '0002_googleidentity')]).apps
User = apps.get_model('accounts', 'User')
first = User.objects.create(username='old-one', email='same@example.test', rol='docente')
User.objects.create(username='old-two', email='same@example.test')
apps.get_model('accounts', 'GoogleIdentity').objects.create(subject='stable-sub', email=first.email, user_id=first.pk)
executor = MigrationExecutor(connection)
executor.migrate([('accounts', '0003_registration_verification')])
apps = executor.loader.project_state([('accounts', '0003_registration_verification')]).apps
user = apps.get_model('accounts', 'User').objects.get(pk=first.pk)
assert user.username == 'old-one' and user.rol == 'docente' and user.email_status == 'legacy' and user.estado == ''
assert apps.get_model('accounts', 'User').objects.count() == 2
assert apps.get_model('accounts', 'GoogleIdentity').objects.get(subject='stable-sub').user_id == user.pk
'''
    result = subprocess.run([sys.executable, '-c', code], capture_output=True, text=True, timeout=45)
    assert result.returncode == 0, result.stderr


def smtp_settings():
    return {'default': {'BACKEND':'django.core.mail.backends.smtp.EmailBackend', 'OPTIONS':{
        'host':'smtp.example.test', 'port':587, 'username':'test-user', 'password':'test-password',
        'use_tls':True, 'use_ssl':False, 'timeout':10}}}


def test_actual_smtp_backend_uses_starttls_authentication_and_requested_sender():
    with override_settings(MAILERS=smtp_settings()), patch('smtplib.SMTP') as smtp, patch('smtplib.SMTP_SSL') as implicit_ssl:
        request, response = register()
    assert response.status_code == 201
    assert smtp.call_args.args == ('smtp.example.test', 587) and smtp.call_args.kwargs['timeout'] == 10
    connection = smtp.return_value
    connection.starttls.assert_called_once()
    connection.login.assert_called_once_with('test-user', 'test-password')
    assert connection.sendmail.call_args.args[:2] == ('no.reply.trees.25@gmail.com', [request['email']])
    implicit_ssl.assert_not_called()
    # This exercises Django's SMTP backend against a mock transport, not a real relay.


@pytest.mark.parametrize('failure', [smtplib.SMTPSenderRefused(550, b'Not permitted', 'sender@example.test'), TimeoutError('timeout')])
def test_smtp_transport_rejections_never_claim_delivery(failure):
    with override_settings(MAILERS=smtp_settings()), patch('smtplib.SMTP') as smtp:
        smtp.return_value.sendmail.side_effect = failure
        request, response = register()
    assert response.status_code == 503 and response.data['email_sent'] is False
    assert User.objects.get(username=request['username']).email_status == 'pending'


@pytest.mark.parametrize('endpoint', ['register', 'login', 'google', 'verify-email', 'resend-verification'])
def test_public_auth_rejects_non_object_json(endpoint):
    result = APIClient().post(f'/auth/{endpoint}/', ['invalid'], format='json')
    assert result.status_code == 400 and 'token' not in result.data


def test_registration_send_race_reports_pending_account_without_server_error():
    from accounts.email_verification import VerificationRateLimited
    with patch('accounts.views.send_verification', side_effect=VerificationRateLimited):
        request, response = register()
    assert response.status_code == 429 and response.data['account_created'] and not response.data['email_sent']
    assert User.objects.get(username=request['username']).email_status == 'pending'
