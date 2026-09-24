from django.shortcuts import render
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import get_user_model
from chatbot.models import ChatSession, ChatMessage

User = get_user_model()

def admin_required(user):
    return user.is_staff or user.is_superuser


@user_passes_test(admin_required)
def dashboard(request):
    context = {
        "total_users": User.objects.count(),
        "total_sessions": ChatSession.objects.count(),
        "total_messages": ChatMessage.objects.count(),
        "recent_messages": ChatMessage.objects.order_by("-created_at")[:10]
    }
    return render(request, "admin_dashboard.html", context)
