from django.urls import path
from . import views

urlpatterns = [
    path("ui/", views.chatbot_ui),
    path("ask/", views.ask_question),
    # legacy endpoint used by the older frontend script; kept for compatibility
    path("chatbot-response/", views.ask_question),
    # generic "response" route if needed
    path("response/", views.ask_question),
]
