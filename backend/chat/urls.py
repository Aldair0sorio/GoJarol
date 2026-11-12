from django.urls import path

from .views import ChatMessageView

urlpatterns = [
    path("chat/messages/", ChatMessageView.as_view(), name="chat_messages"),
]
