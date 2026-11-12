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

urlpatterns = [path('auth/', include('accounts.urls')), path('chat/messages/', ChatMessageView.as_view()),
               path('', include('progress.urls'))]


@pytest.fixture(autouse=True)
def environment(database, monkeypatch):
    # Message-ID/EHLO must not perform reverse DNS in an offline mail test.
    from django.core.mail.utils import DNS_NAME
    monkeypatch.setattr(DNS_NAME, '_fqdn', 'testhost.invalid', raising=False)
    cache.clear()
    mail.outbox = []
    with override_settings(ROOT_URLCONF=__name__, FRONTEND_URL='http://localhost:5173', DEBUG=True,
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


def register_pending(**changes):
    from accounts.email_verification import send_verification
    request = data(**changes)
    user = User.objects.create_user(
        username=request['username'],
        email=request['email'],
        password=request['password'],
        first_name=request['full_name'],
        alias=request['full_name'][:50],
        rol=request['rol'],
        nivel=request.get('nivel', '') if request['rol'] == 'estudiante' else '',
        grado=request.get('grado') if request['rol'] == 'estudiante' else None,
        estado=request['estado'],
        email_status=User.EmailStatus.PENDING,
    )
    send_verification(user)
    return request, user


def link():
    match = re.search(r'/verificar-correo/(\d+)/([A-Za-z0-9_-]+)', mail.outbox[-1].body)
    assert match
    return {'uid': match[1], 'token': match[2]}


@pytest.mark.parametrize('role', ['estudiante', 'docente'])
def test_register_direct_login_profile_chat_logout(role):
    request, response = register(rol=role)
    assert response.status_code == 201 and 'token' in response.data and 'user' in response.data
    user = User.objects.get(username=request['username'])
    assert user.email_status == 'verified' and user.email_verified_at is not None
    assert user.first_name == request['full_name'] and user.estado == '30'
    assert not user.is_staff and not user.is_superuser and Token.objects.filter(user=user).exists()
    assert user.check_password(request['password']) and user.password != request['password']
    if role == 'docente':
        assert user.nivel == '' and user.grado is None
    assert len(mail.outbox) == 0
    visitor = APIClient()
    credentials = {'username': request['email'], 'password': request['password']}
    login = visitor.post('/auth/login/', credentials, format='json')
    assert login.status_code == 200 and login.data['token'] == response.data['token']
    visitor.credentials(HTTP_AUTHORIZATION='Token ' + login.data['token'])
    profile = visitor.get('/auth/me/')
    assert profile.status_code == 200 and profile.data['estado'] == '30' and profile.data['email_status'] == 'verified'
    assert visitor.patch('/auth/me/', {'estado': '09'}, format='json').status_code == 200
    assert visitor.get('/auth/me/').data['estado'] == '09'
    chat = visitor.post('/chat/messages/', {'message': 'Explícame las fracciones'}, format='json')
    assert chat.status_code == 200 and chat.data['type'] == 'explanation_menu'
    assert visitor.post('/auth/logout/').status_code == 204
    assert visitor.get('/auth/me/').status_code == 401


def test_login_promotes_existing_pending_account_to_verified():
    user = User.objects.create_user(
        username='stuck_pending',
        email='stuck-pending@example.test',
        password='Aprender-con-Jarol-734!',
        email_status=User.EmailStatus.PENDING,
    )
    login = APIClient().post('/auth/login/', {'username': user.email, 'password': 'Aprender-con-Jarol-734!'}, format='json')
    assert login.status_code == 200 and 'token' in login.data
    user.refresh_from_db()
    assert user.email_status == User.EmailStatus.VERIFIED and user.email_verified_at is not None


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
    register_pending()
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
    request, _ = register_pending()
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


def test_register_succeeds_even_when_smtp_would_fail():
    with patch('accounts.email_verification.EmailMessage.send', side_effect=smtplib.SMTPAuthenticationError(535, b'rejected')):
        request, response = register()
    assert response.status_code == 201 and 'token' in response.data
    user = User.objects.get(username=request['username'])
    assert user.email_status == 'verified' and Token.objects.filter(user=user).exists()
    assert not mail.outbox


def test_failed_resend_preserves_last_successful_token_and_reports_failure():
    request, _ = register_pending()
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
    from accounts.email_verification import VerificationDeliveryFailed
    register_pending()
    assert 'http://localhost:5173/verificar-correo/' in mail.outbox[-1].body
    with override_settings(FRONTEND_URL='https://example.test@attacker.test/path'):
        with pytest.raises(VerificationDeliveryFailed):
            register_pending()


def test_resend_ip_throttle_rejects_excess_requests():
    c = APIClient()
    for _ in range(20):
        assert c.post('/auth/resend-verification/', {'email': 'unknown@example.test'}, format='json').status_code == 202
    assert c.post('/auth/resend-verification/', {'email': 'unknown@example.test'}, format='json').status_code == 429


def test_pending_accounts_cannot_authenticate_even_with_an_old_api_token():
    from accounts.authentication import VerifiedTokenAuthentication
    from rest_framework.exceptions import AuthenticationFailed
    _, user = register_pending()
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
        request, _ = register_pending()
    assert smtp.call_args.args == ('smtp.example.test', 587) and smtp.call_args.kwargs['timeout'] == 10
    connection = smtp.return_value
    connection.starttls.assert_called_once()
    connection.login.assert_called_once_with('test-user', 'test-password')
    assert connection.sendmail.call_args.args[:2] == ('no.reply.trees.25@gmail.com', [request['email']])
    implicit_ssl.assert_not_called()
    # This exercises Django's SMTP backend against a mock transport, not a real relay.


@pytest.mark.parametrize('failure', [smtplib.SMTPSenderRefused(550, b'Not permitted', 'sender@example.test'), TimeoutError('timeout')])
def test_smtp_transport_rejections_never_claim_delivery(failure):
    from accounts.email_verification import VerificationDeliveryFailed
    with override_settings(MAILERS=smtp_settings()), patch('smtplib.SMTP') as smtp:
        smtp.return_value.sendmail.side_effect = failure
        with pytest.raises(VerificationDeliveryFailed):
            register_pending()


@pytest.mark.parametrize('endpoint', ['register', 'login', 'google', 'verify-email', 'resend-verification'])
def test_public_auth_rejects_non_object_json(endpoint):
    result = APIClient().post(f'/auth/{endpoint}/', ['invalid'], format='json')
    assert result.status_code == 400 and 'token' not in result.data


def test_public_auth_config_reports_contract_and_public_google_id_only():
    with override_settings(GOOGLE_CLIENT_ID='configured.apps.googleusercontent.com', MAIL_PASSWORD='secret-canary'):
        response = APIClient().get('/auth/config/')
    assert response.status_code == 200 and response['Cache-Control'] == 'no-store'
    assert response.data == {'auth_contract_version': 2, 'registration_mode': 'direct',
                             'google_client_id': 'configured.apps.googleusercontent.com'}
    assert 'secret-canary' not in response.content.decode()


@pytest.mark.parametrize('origin', ['http://localhost:5173', 'https://127.0.0.1', 'http://app.example.test', 'https://app.example.test:bad'])
def test_production_rejects_nonpublic_or_insecure_verification_origins(origin):
    from accounts.email_verification import VerificationDeliveryFailed
    with override_settings(DEBUG=False, FRONTEND_URL=origin):
        with pytest.raises(VerificationDeliveryFailed):
            register_pending()
    assert not mail.outbox


@pytest.mark.parametrize('failure,code', [(smtplib.SMTPAuthenticationError(535, b'Secret-Canary-Auth'), 'smtp_authentication_failed'),
                                        (smtplib.SMTPSenderRefused(550, b'Secret-Canary-Sender', 'private@example.test'), 'smtp_sender_refused')])
def test_delivery_logs_classification_without_credentials_or_replies(caplog, failure, code):
    from accounts.email_verification import VerificationDeliveryFailed
    with patch('accounts.email_verification.EmailMessage.send', side_effect=failure):
        with pytest.raises(VerificationDeliveryFailed):
            register_pending()
    assert code in caplog.text and 'Secret-Canary' not in caplog.text and 'private@example.test' not in caplog.text


def test_auth_diagnostic_only_reports_presence_and_migration_status():
    from io import StringIO
    from django.core.management import call_command
    output = StringIO()
    with override_settings(MAILERS=smtp_settings(), GOOGLE_CLIENT_ID='test.apps.googleusercontent.com'), patch('smtplib.SMTP') as smtp:
        call_command('diagnose_auth', stdout=output)
    result = output.getvalue()
    assert 'MAIL_PASSWORD: present' in result and '0003_registration_verification: applied' in result
    assert 'test-password' not in result and 'smtp.example.test' not in result
    smtp.assert_not_called()


@pytest.mark.parametrize('send', [False, True])
def test_auth_diagnostic_smtp_connection_and_explicit_send(send):
    from io import StringIO
    from django.core.management import call_command
    output = StringIO()
    with override_settings(MAILERS=smtp_settings()), patch('smtplib.SMTP') as smtp:
        call_command('diagnose_auth', smtp_check=not send, send_to='controlled@example.test' if send else None, stdout=output)
    smtp.return_value.starttls.assert_called_once()
    smtp.return_value.login.assert_called_once_with('test-user', 'test-password')
    assert ('SMTP_MESSAGE: accepted' in output.getvalue()) is send
    assert smtp.return_value.sendmail.called is send
    assert 'test-password' not in output.getvalue()


def test_auth_diagnostic_redacts_smtp_failures():
    from io import StringIO
    from django.core.management import call_command, CommandError
    output = StringIO()
    with override_settings(MAILERS=smtp_settings()), patch('smtplib.SMTP') as smtp:
        smtp.return_value.login.side_effect = smtplib.SMTPAuthenticationError(535, b'Password-secret-canary')
        with pytest.raises(CommandError) as error:
            call_command('diagnose_auth', smtp_check=True, stdout=output)
    assert 'smtp_authentication_failed' in str(error.value)
    assert 'Password-secret-canary' not in str(error.value) + output.getvalue()


def test_registration_login_also_works_with_production_pbkdf2_hasher():
    with override_settings(PASSWORD_HASHERS=['django.contrib.auth.hashers.PBKDF2PasswordHasher']):
        request, result = register()
        assert result.status_code == 201 and 'token' in result.data
        user = User.objects.get(username=request['username'])
        assert user.password.startswith('pbkdf2_sha256$') and user.check_password(request['password'])
        assert APIClient().post('/auth/login/', {'username': request['username'], 'password': request['password']}, format='json').status_code == 200


def test_merged_chat_history_stays_private_and_does_not_duplicate_completed_attempts():
    from chat.services.runtime import get_runtime
    from progress.models import ExerciseAttempt, StudentProgress
    request, registration = register()
    assert registration.status_code == 201
    c = APIClient()
    login = c.post('/auth/login/', {'username': request['username'], 'password': request['password']}, format='json')
    user = User.objects.get(username=request['username'])
    c.credentials(HTTP_AUTHORIZATION='Token '+login.data['token'])
    exercise = c.post('/chat/messages/', {'message':'Ponme un ejercicio de ecuaciones'}, format='json')
    assert exercise.status_code == 200 and exercise.data['exercise']
    exercise_id = exercise.data['exercise']['id']
    runtime = get_runtime()
    expected = runtime.selector.get_expected_answer('mat_ecuaciones', exercise_id)
    wrong = c.post('/chat/messages/', {'message':'x = 1234567'}, format='json')
    assert wrong.data['evaluation']['correct'] is False
    correct = c.post('/chat/messages/', {'message':f'x = {expected}'}, format='json')
    assert correct.data['evaluation']['correct'] is True
    assert ExerciseAttempt.objects.filter(user=user, exercise_id=exercise_id).count() == 2
    progress = StudentProgress.objects.get(user=user)
    xp = progress.xp
    c.post('/chat/messages/', {'message':f'x = {expected}'}, format='json')
    progress.refresh_from_db()
    assert progress.xp == xp and ExerciseAttempt.objects.filter(user=user, exercise_id=exercise_id).count() == 2
    own = c.get('/progress/me/')
    assert len(own.data['recentAttempts']) == 2
    assert 'expected_answer' not in str(own.data)
    guest = APIClient().get('/progress/me/', HTTP_X_JAROL_USER_ID=str(user.pk), HTTP_X_JAROL_USER_EMAIL=user.email)
    assert guest.data['xp'] == 0 and guest.data['recentAttempts'] == []
