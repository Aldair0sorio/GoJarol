from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import User

from .models import Classroom, Enrollment
from .serializers import ClassroomSerializer


class ClassroomListCreateView(APIView):
    def get(self, request):
        user = request.user
        if user.rol == User.Rol.DOCENTE:
            clases = Classroom.objects.filter(docente=user)
        elif user.rol == User.Rol.ESTUDIANTE:
            clases = Classroom.objects.filter(enrollments__student=user)
        else:
            clases = Classroom.objects.none()
        return Response(ClassroomSerializer(clases, many=True).data)

    def post(self, request):
        if request.user.rol != User.Rol.DOCENTE:
            raise PermissionDenied("Solo los docentes pueden crear clases.")
        serializer = ClassroomSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(docente=request.user)
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
                {"error": {"code": "invalid_code",
                           "message": "El código no existe o ya no está activo."}},
                status=404,
            )
        Enrollment.objects.get_or_create(classroom=clase, student=request.user)
        return Response(ClassroomSerializer(clase).data)