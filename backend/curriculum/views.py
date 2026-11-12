from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny

from .models import Subject, Topic
from .serializers import SubjectSerializer

CATALOG_SUBJECTS = [
    ("aritmetica", "Aritmética", True, 1),
    ("algebra", "Álgebra", True, 2),
    ("espanol", "Español y Lenguajes", True, 3),
    ("matematicas", "Geometría y Trigonometría", False, 4),
    ("historia", "Historia", False, 5),
    ("geografia", "Geografía", False, 6),
    ("fisica", "Física", False, 7),
    ("quimica", "Química", False, 8),
    ("biologia", "Biología", False, 9),
]

CATALOG_TOPICS = [
    ("aritmetica", "mat_fracciones", "Fracciones Equivalentes y Suma", True, 1),
    ("aritmetica", "mat_porcentajes", "Porcentajes y Proporcionalidad", True, 2),
    ("algebra", "mat_ecuaciones", "Ecuaciones Lineales de Primer Grado", True, 1),
    ("espanol", "esp_comprension", "Comprensión Lectora", True, 1),
    ("espanol", "esp_ortografia", "Ortografía Puntual y Grafías", True, 2),
    ("espanol", "esp_acentuacion", "Reglas de Acentuación", True, 3),
    ("matematicas", "teorema_de_pitagoras", "Teorema de Pitágoras", False, 1),
]


def _ensure_catalog_seeded():
    if Topic.objects.filter(slug="esp_comprension", disponible=True).exists():
        return

    subj_map = {}
    for slug, nombre, disp, orden in CATALOG_SUBJECTS:
        subj, _ = Subject.objects.update_or_create(
            slug=slug,
            defaults={"nombre": nombre, "disponible": disp, "orden": orden},
        )
        subj_map[slug] = subj

    # Limpiar slugs viejos de prueba si existían sin prefijo
    Topic.objects.filter(slug__in=["fracciones", "ecuaciones_lineales"]).delete()

    for subj_slug, topic_slug, nombre, disp, orden in CATALOG_TOPICS:
        subj = subj_map[subj_slug]
        Topic.objects.update_or_create(
            subject=subj,
            slug=topic_slug,
            defaults={"nombre": nombre, "disponible": disp, "orden": orden},
        )


class SubjectListView(ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = SubjectSerializer
    pagination_class = None

    def get_queryset(self):
        _ensure_catalog_seeded()
        return Subject.objects.prefetch_related("topics").all()
