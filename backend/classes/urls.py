from django.urls import path

from .views import (
    ClassroomAnnouncementDeleteView,
    ClassroomAnnouncementListCreateView,
    ClassroomChallengeDeleteView,
    ClassroomChallengeListCreateView,
    ClassroomDetailView,
    ClassroomListCreateView,
    ClassroomStudentManageView,
    JoinClassroomView,
    LeaveClassroomView,
    StudentAnalysisDetailView,
)

urlpatterns = [
    path("classes/", ClassroomListCreateView.as_view()),
    path("classes/join/", JoinClassroomView.as_view()),
    path("classes/<int:class_id>/", ClassroomDetailView.as_view()),
    path("classes/<int:class_id>/leave/", LeaveClassroomView.as_view()),
    path("classes/<int:class_id>/students/<int:student_id>/", ClassroomStudentManageView.as_view()),
    path("classes/<int:class_id>/students/<int:student_id>/analysis/", StudentAnalysisDetailView.as_view()),
    path("classes/<int:class_id>/challenges/", ClassroomChallengeListCreateView.as_view()),
    path("classes/<int:class_id>/challenges/<int:challenge_id>/", ClassroomChallengeDeleteView.as_view()),
    path("classes/<int:class_id>/announcements/", ClassroomAnnouncementListCreateView.as_view()),
    path("classes/<int:class_id>/announcements/<int:announcement_id>/", ClassroomAnnouncementDeleteView.as_view()),
]
