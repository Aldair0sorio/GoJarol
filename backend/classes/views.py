from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import User
from curriculum.models import Subject

from .models import Classroom, Enrollment
from .serializers import ClassroomSerializer


def _ensure_default_subject(slug_or_name: str | None) -> Subject:
    slug = (slug_or_name or "aritmetica").strip().lower()
    subj = Subject.objects.filter(slug=slug).first()
    if subj:
        return subj
    subj = Subject.objects.first()
    if subj:
        return subj
    return Subject.objects.create(
        slug="aritmetica",
        nombre="Aritmética y Matemáticas",
        disponible=True,
        orden=1,
    )


class ClassroomListCreateView(APIView):
    def get(self, request):
        user = request.user
        if user.rol == User.Rol.DOCENTE:
            clases = Classroom.objects.filter(docente=user).prefetch_related("enrollments__student")
        elif user.rol == User.Rol.ESTUDIANTE:
            clases = Classroom.objects.filter(enrollments__student=user).prefetch_related("enrollments__student")
        else:
            clases = Classroom.objects.none()
        return Response(ClassroomSerializer(clases, many=True).data)

    def post(self, request):
        if request.user.rol != User.Rol.DOCENTE:
            raise PermissionDenied("Solo los docentes pueden crear clases.")
        data = request.data.copy() if hasattr(request.data, "copy") else dict(request.data)
        subj = _ensure_default_subject(data.get("subject"))
        data["subject"] = subj.slug
        if not data.get("nivel"):
            data["nivel"] = User.Nivel.SECUNDARIA
        if not data.get("grado"):
            data["grado"] = 1
        serializer = ClassroomSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save(docente=request.user, subject=subj)
        return Response(serializer.data, status=201)


class JoinClassroomView(APIView):
    def post(self, request):
        if request.user.rol != User.Rol.ESTUDIANTE:
            raise PermissionDenied("Solo los estudiantes pueden unirse a una clase.")
        codigo = str(request.data.get("codigo", "")).strip().upper()
        try:
            clase = Classroom.objects.get(codigo=codigo, codigo_activo=True)
        except Classroom.DoesNotExist:
            return Response(
                {
                    "error": {
                        "code": "invalid_code",
                        "message": "El código no existe o ya no está activo.",
                    }
                },
                status=404,
            )
        Enrollment.objects.get_or_create(classroom=clase, student=request.user)
        return Response(ClassroomSerializer(clase).data)
