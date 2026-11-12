import base64
import json
from django.contrib.auth import authenticate, get_user_model
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from progress.models import StudentProgress

from .serializers import RegisterSerializer, UserSerializer

User = get_user_model()

DEMO_PROFILES = {
    "student": {
        "username": "emiliano_valdes_demo",
        "email": "emiliano.valdes@estudiantes.sev.gob.mx",
        "alias": "Emiliano Valdés",
        "rol": User.Rol.ESTUDIANTE,
        "nivel": User.Nivel.SECUNDARIA,
        "grado": 3,
    },
    "teacher": {
        "username": "laura_mendoza_demo",
        "email": "laura.mendoza@docentes.sev.gob.mx",
        "alias": "Prof. Laura Mendoza",
        "rol": User.Rol.DOCENTE,
        "nivel": "",
        "grado": None,
    },
}


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
        raw_identifier = request.data.get("username", "")
        password = request.data.get("password", "")

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
        explicit_role = bool(request.data.get("explicit_role", False))
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
        user = User.objects.filter(email__iexact=email).first()
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
            StudentProgress.objects.get_or_create(user=user)
        elif explicit_role and user.rol != user_role:
            user.rol = user_role
            if user_role == User.Rol.ESTUDIANTE and not user.nivel:
                user.nivel = User.Nivel.SECUNDARIA
                user.grado = user.grado or 3
            user.save()

        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            "token": token.key,
            "user": UserSerializer(user).data,
            "picture": picture,
        })


class DemoLoginView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        profile_key = str(request.data.get("profile", "")).strip().lower()
        email_arg = str(request.data.get("email", "")).strip().lower()

        if profile_key not in DEMO_PROFILES:
            if email_arg == DEMO_PROFILES["teacher"]["email"]:
                profile_key = "teacher"
            elif email_arg == DEMO_PROFILES["student"]["email"]:
                profile_key = "student"

        if profile_key not in DEMO_PROFILES:
            return Response(
                {"error": {"code": "invalid_demo_profile", "message": "Perfil demo no válido."}},
                status=400,
            )

        spec = DEMO_PROFILES[profile_key]
        user = User.objects.filter(email__iexact=spec["email"]).first()
        if not user:
            user = User.objects.create_user(
                username=spec["username"],
                email=spec["email"],
                rol=spec["rol"],
                alias=spec["alias"],
                nivel=spec["nivel"],
                grado=spec["grado"],
            )
        elif user.rol != spec["rol"]:
            user.rol = spec["rol"]
            user.save()

        StudentProgress.objects.get_or_create(user=user)
        token, _ = Token.objects.get_or_create(user=user)
        return Response({"token": token.key, "user": UserSerializer(user).data})


class SwitchRoleView(APIView):
    def post(self, request):
        raw_role = str(request.data.get("role", "")).strip().lower()
        if raw_role in {"teacher", "docente"}:
            target_role = User.Rol.DOCENTE
        elif raw_role in {"student", "estudiante"}:
            target_role = User.Rol.ESTUDIANTE
        else:
            return Response(
                {"error": {"code": "invalid_role", "message": "Rol no válido."}},
                status=400,
            )

        user = request.user
        user.rol = target_role
        if target_role == User.Rol.ESTUDIANTE and not user.nivel:
            user.nivel = User.Nivel.SECUNDARIA
            user.grado = user.grado or 3
        user.save()
        return Response({"user": UserSerializer(user).data})


class MeView(APIView):
    def get(self, request):
        return Response(UserSerializer(request.user).data)
