from django.urls import path

from .views import ExerciseAnswerView, ExerciseHintView

urlpatterns = [
    path("exercises/<str:exercise_id>/answer/", ExerciseAnswerView.as_view(), name="exercise_answer"),
    path("exercises/<str:exercise_id>/hint/", ExerciseHintView.as_view(), name="exercise_hint"),
]
