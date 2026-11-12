from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed


class VerifiedTokenAuthentication(TokenAuthentication):
    """Legacy users remain compatible; pending registrations cannot use API tokens."""
    def authenticate_credentials(self, key):
        user, token = super().authenticate_credentials(key)
        if user.email_status == 'pending':
            raise AuthenticationFailed('Confirma tu correo antes de continuar.')
        return user, token
