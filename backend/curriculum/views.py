from django.core.management import call_command
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny

from .models import Subject, Topic
from .serializers import SubjectSerializer


def _ensure_catalog_seeded():
    if Topic.objects.filter(slug="esp_comprension").exists():
        return
    try:
        call_command("loaddata", "catalogo", verbosity=0)
    except Exception:
        pass


class SubjectListView(ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = SubjectSerializer
    pagination_class = None

    def get_queryset(self):
        _ensure_catalog_seeded()
        return Subject.objects.prefetch_related("topics").all()
