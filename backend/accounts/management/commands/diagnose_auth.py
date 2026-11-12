"""Operator-only diagnostics. No secrets, tokens or SMTP server replies printed."""
import smtplib
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.core.mail import EmailMessage, mailers
from django.core.management.base import BaseCommand, CommandError
from django.core.validators import validate_email
from django.db import connection, DatabaseError
from django.db.migrations.loader import MigrationLoader
from accounts.email_verification import verification_origin, VerificationDeliveryFailed, delivery_error_code
from accounts.models import User


class Command(BaseCommand):
    help = 'Report auth configuration presence; optionally test SMTP or send an explicitly requested diagnostic email.'

    def add_arguments(self, parser):
        parser.add_argument('--smtp-check', action='store_true', help='Connect, negotiate STARTTLS and authenticate; no email sent.')
        parser.add_argument('--send-to', help='Explicitly send a diagnostic message to an address controlled by the operator.')

    def handle(self, *args, **options):
        config = getattr(settings, 'MAILERS', {}).get('default', {})
        smtp = config.get('OPTIONS', {})
        for name, value in [('GOOGLE_CLIENT_ID', getattr(settings, 'GOOGLE_CLIENT_ID', '')),
                            ('MAIL_HOST', smtp.get('host')), ('MAIL_PORT', smtp.get('port')),
                            ('MAIL_USERNAME', smtp.get('username')), ('MAIL_PASSWORD', smtp.get('password')),
                            ('DEFAULT_FROM_EMAIL', getattr(settings, 'DEFAULT_FROM_EMAIL', ''))]:
            self.stdout.write(f'{name}: {"present" if value else "missing"}')
        is_smtp = config.get('BACKEND') == 'django.core.mail.backends.smtp.EmailBackend'
        self.stdout.write(f'MAILER: {"smtp" if is_smtp else "not_smtp"}')
        self.stdout.write(f'MAIL_USE_TLS: {"enabled" if smtp.get("use_tls") else "disabled"}')
        try:
            verification_origin()
            self.stdout.write('FRONTEND_URL: valid_origin')
        except VerificationDeliveryFailed:
            self.stdout.write('FRONTEND_URL: invalid_or_missing_public_origin')
        try:
            loader = MigrationLoader(connection)
            for name in ['0002_googleidentity', '0003_registration_verification']:
                self.stdout.write(f'{name}: {"applied" if ("accounts", name) in loader.applied_migrations else "pending"}')
            if ('accounts', '0003_registration_verification') in loader.applied_migrations:
                self.stdout.write(f'PENDING_ACCOUNTS: {User.objects.filter(email_status="pending").count()}')
        except DatabaseError:
            self.stdout.write('MIGRATIONS: database_unavailable')
        if not options['smtp_check'] and not options['send_to']:
            return
        if not is_smtp or not all(smtp.get(key) for key in ['host', 'port', 'username', 'password']):
            raise CommandError('SMTP test unavailable: configure the SMTP backend and all required MAIL_* variables.')
        if smtp.get('use_ssl') or not smtp.get('use_tls') or smtp.get('port') == 465:
            raise CommandError('SMTP test requires STARTTLS with use_ssl=False and the provider STARTTLS port.')
        if options['send_to']:
            try:
                validate_email(options['send_to'])
            except ValidationError:
                raise CommandError('Invalid diagnostic recipient.') from None
        backend = None
        try:
            backend = mailers['default']
            backend.open()
            self.stdout.write('SMTP_CONNECTION: STARTTLS/authentication completed (sender permission not yet tested).')
            if options['send_to']:
                message = EmailMessage('Prueba SMTP de Go Jarol',
                    'Mensaje de diagnóstico solicitado por el responsable de Go Jarol. No contiene enlaces ni tokens.',
                    settings.DEFAULT_FROM_EMAIL, [options['send_to']])
                if backend.send_messages([message]) != 1:
                    raise CommandError('SMTP_NOT_ACCEPTED: no delivery claimed.')
                self.stdout.write('SMTP_MESSAGE: accepted by relay; confirm receipt/spam and provider delivery logs.')
        except (smtplib.SMTPException, OSError, ImproperlyConfigured, ValueError) as error:
            raise CommandError(f'SMTP test failed: {delivery_error_code(error)}. No delivery claimed.') from None
        finally:
            if backend:
                try:
                    backend.close()
                except (smtplib.SMTPException, OSError):
                    pass
