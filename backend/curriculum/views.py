from rest_framework.generics import ListAPIView

from .models import Subject
from .serializers import SubjectSerializer


class SubjectListView(ListAPIView):
    queryset = Subject.objects.prefetch_related("topics")
    serializer_class = SubjectSerializer
    pagination_class = None