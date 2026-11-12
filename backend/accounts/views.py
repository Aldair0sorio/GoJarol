import base64
import json
import uuid
from django.contrib.auth import authenticate, get_user_model
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import RegisterSerializer, UserSerializer

User = get_user_model()


class RegisterView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)
        return Response({"token": token.key, "user": UserSerializer(user).data}, status=201)


class LoginView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        user = authenticate(
            username=request.data.get("username"),
            password=request.data.get("password"),
        )
        if user is None:
            return Response(
                {"error": {"code": "invalid_credentials", "message": "Usuario o contraseña incorrectos."}},
                status=401,
            )
        token, _ = Token.objects.get_or_create(user=user)
        return Response({"token": token.key, "user": UserSerializer(user).data})


class GoogleLoginView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        """
        Inicia sesión o registra un usuario con cuenta de Google.
        Acepta un JWT 'credential' de Google GIS o datos directos (email, name, picture, role).
        """
        credential = request.data.get("credential")
        email = request.data.get("email")
        name = request.data.get("name", "")
        role = request.data.get("role", User.Rol.ESTUDIANTE)
        picture = request.data.get("picture", "")
        grade_str = str(request.data.get("grade", "3"))

        # Decodificación segura de JWT payload de Google GIS
        if credential and not email:
            try:
                parts = credential.split(".")
                if len(parts) >= 2:
                    rem = len(parts[1]) % 4
                    padded = parts[1] + ("=" * ((4 - rem) % 4))
                    payload_raw = base64.urlsafe_b64decode(padded)
                    payload = json.loads(payload_raw.decode("utf-8"))
                    email = payload.get("email")
                    name = payload.get("name") or payload.get("given_name") or name
                    picture = payload.get("picture", picture)
            except Exception:
                pass

        if not email:
            return Response(
                {"error": {"code": "missing_email", "message": "Email de Google no proporcionado."}},
                status=400,
            )

        user_role = User.Rol.DOCENTE if role in ["docente", "teacher"] else User.Rol.ESTUDIANTE
        user = User.objects.filter(email=email).first()
        if not user:
            base_username = email.split("@")[0][:25].lower()
            username = base_username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}_{counter}"
                counter += 1

            grade_num = 3
            if "1" in grade_str:
                grade_num = 1
            elif "2" in grade_str:
                grade_num = 2

            user = User.objects.create_user(
                username=username,
                email=email,
                rol=user_role,
                alias=name if name else username,
                nivel=User.Nivel.SECUNDARIA if user_role == User.Rol.ESTUDIANTE else "",
                grado=grade_num if user_role == User.Rol.ESTUDIANTE else None,
            )

        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            "token": token.key,
            "user": UserSerializer(user).data,
            "picture": picture,
        })


class MeView(APIView):
    def get(self, request):
        return Response(UserSerializer(request.user).data)