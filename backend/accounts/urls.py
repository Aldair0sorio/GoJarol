from django.urls import path

from .views import DemoLoginView, GoogleLoginView, LoginView, MeView, RegisterView, SwitchRoleView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("google/", GoogleLoginView.as_view(), name="google-login"),
    path("demo/", DemoLoginView.as_view(), name="demo-login"),
    path("switch-role/", SwitchRoleView.as_view(), name="switch-role"),
    path("me/", MeView.as_view(), name="me"),
]
