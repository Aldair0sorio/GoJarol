from rest_framework import serializers

from curriculum.models import Subject
from progress.models import StudentProgress
from progress.views import compute_user_diagnostics

from .models import Classroom


class ClassroomSerializer(serializers.ModelSerializer):
    subject = serializers.SlugRelatedField(
        slug_field="slug",
        queryset=Subject.objects.all(),
        required=False,
    )
    subject_nombre = serializers.CharField(source="subject.nombre", read_only=True)
    docente = serializers.SerializerMethodField()
    estudiantes = serializers.SerializerMethodField()
    students_detail = serializers.SerializerMethodField()

    class Meta:
        model = Classroom
        fields = [
            "id",
            "nombre",
            "nivel",
            "grado",
            "subject",
            "subject_nombre",
            "codigo",
            "codigo_activo",
            "docente",
            "estudiantes",
            "students_detail",
            "creada",
        ]
        read_only_fields = ["codigo", "codigo_activo", "creada"]

    def get_docente(self, obj):
        return obj.docente.alias or obj.docente.username

    def get_estudiantes(self, obj):
        return obj.enrollments.count()

    def get_students_detail(self, obj):
        details = []
        for enrollment in obj.enrollments.select_related("student").all():
            student = enrollment.student
            prog, _ = StudentProgress.objects.get_or_create(user=student)
            diag = compute_user_diagnostics(prog)
            needs_help = diag["needsHelpWith"]
            if not needs_help:
                # Si aún no tiene errores registrados, mostrar los temas en curso o por iniciar
                in_progress = [t["name"] for t in diag["topics"] if t["status"] == "En curso"]
                needs_help = in_progress[:2] if in_progress else ["Sin alertas activas"]
            details.append(
                {
                    "id": str(student.id),
                    "name": student.alias or student.username,
                    "email": student.email,
                    "completedExercises": diag["completedCount"],
                    "accuracy": diag["accuracy"],
                    "needsHelpWith": needs_help,
                    "xp": diag["xp"],
                    "streakDays": diag["streakDays"],
                    "lastActive": "Reciente",
                }
            )
        return details
