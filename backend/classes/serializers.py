from rest_framework import serializers

from curriculum.models import Subject

from .models import Classroom


class ClassroomSerializer(serializers.ModelSerializer):
    subject = serializers.SlugRelatedField(slug_field="slug", queryset=Subject.objects.all())
    docente = serializers.CharField(source="docente.username", read_only=True)
    estudiantes = serializers.SerializerMethodField()

    class Meta:
        model = Classroom
        fields = ["id", "nombre", "nivel", "grado", "subject", "codigo",
                  "codigo_activo", "docente", "estudiantes", "creada"]
        read_only_fields = ["codigo", "codigo_activo", "creada"]

    def get_estudiantes(self, obj):
        return obj.enrollments.count()