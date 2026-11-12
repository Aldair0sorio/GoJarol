from django.urls import path

from .views import ClassroomListCreateView, JoinClassroomView

urlpatterns = [
    path("classes/", ClassroomListCreateView.as_view()),
    path("classes/join/", JoinClassroomView.as_view()),
]