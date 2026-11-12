from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny

from .models import Subject
from .serializers import SubjectSerializer


class SubjectListView(ListAPIView):
    permission_classes = [AllowAny]
    queryset = Subject.objects.prefetch_related("topics")
    serializer_class = SubjectSerializer
    pagination_class = None