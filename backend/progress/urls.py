from django.urls import path

from .views import LeaderboardView, MyProgressView

urlpatterns = [
    path("progress/me/", MyProgressView.as_view(), name="progress_me"),
    path("progress/leaderboard/", LeaderboardView.as_view(), name="progress_leaderboard"),
]
