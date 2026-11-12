from django.urls import path

from .views import GoogleLoginView, LoginView, MeView, RegisterView, LogoutView
from .views import VerifyEmailView, ResendVerificationView
from .views import AuthConfigView, DemoLoginView, SwitchRoleView

urlpatterns = [
    path('demo/', DemoLoginView.as_view(), name='demo-login'),
    path('switch-role/', SwitchRoleView.as_view(), name='switch-role'),
    path('config/', AuthConfigView.as_view(), name='auth-config'),
    path('verify-email/', VerifyEmailView.as_view(), name='verify-email'),
    path('resend-verification/', ResendVerificationView.as_view(), name='resend-verification'),
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("google/", GoogleLoginView.as_view(), name="google-login"),
    path("me/", MeView.as_view(), name="me"),
    path("logout/", LogoutView.as_view(), name="logout"),
]
