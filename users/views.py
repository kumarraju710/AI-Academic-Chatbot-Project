from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse

from .models import User, ChatLog, Feedback
# previously the old ML-backed chatbot was imported here.  
# switch to the completely deterministic rule‑based engine in chatbot_complete
# (wrapped by services_new) to guarantee consistent JSON‑only answers.
from nlp_engine.services_new import generate_response as get_bot_response


def admin_only(user):
    return user.is_authenticated and (user.role == 'admin' or user.is_superuser)


# =========================
# HOME PAGE
# =========================
def home(request):
    return render(request, 'home.html')


# =========================
# STUDENT REGISTER
# =========================
def student_register(request):
    error = ""

    if request.method == "POST":
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        confirm_password = request.POST.get('confirm_password', '').strip()

        if not name or not email or not username or not password or not confirm_password:
            error = "All fields are required."
        elif password != confirm_password:
            error = "Passwords do not match."
        elif User.objects.filter(username=username).exists():
            error = "Username already exists. Please choose another."
        else:
            User.objects.create_user(
                username=username,
                password=password,
                email=email,
                first_name=name,
                role='student'
            )
            return redirect('student_login')

    return render(request, 'student_register.html', {'error': error})


# =========================
# STUDENT LOGIN
# =========================
def student_login(request):
    error = ""

    if request.method == "POST":
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()

        user = authenticate(request, username=username, password=password)

        if user is not None and user.role == 'student':
            login(request, user)
            return redirect('chatbot')
        else:
            error = "Invalid credentials or not a student account."

    return render(request, 'student_login.html', {'error': error})


# =========================
# ADMIN REGISTER
# =========================
def admin_register(request):
    error = ""

    if request.method == "POST":
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()

        if not username or not password:
            error = "All fields are required."
        elif User.objects.filter(username=username).exists():
            error = "Username already exists."
        else:
            User.objects.create_user(
                username=username,
                password=password,
                role='admin'
            )
            return redirect('admin_login')

    return render(request, 'admin_register.html', {'error': error})


# =========================
# ADMIN LOGIN
# =========================
def admin_login(request):
    error = ""

    if request.method == "POST":
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()

        user = authenticate(request, username=username, password=password)

        if user is not None and (user.role == 'admin' or user.is_superuser):
            login(request, user)
            return redirect('admin_dashboard')
        else:
            error = "Invalid credentials or not an admin account."

    return render(request, 'admin_login.html', {'error': error})


# =========================
# ADMIN DASHBOARD
# =========================
@user_passes_test(admin_only)
def admin_dashboard(request):
    total_students = User.objects.filter(role='student').count()
    total_admins = User.objects.filter(role='admin').count()
    total_chat_logs = ChatLog.objects.count()
    
    context = {
        'total_students': total_students,
        'total_admins': total_admins,
        'total_chat_logs': total_chat_logs,
    }
    return render(request, 'admin_dashboard.html', context)


# =========================
# USER MANAGEMENT
# =========================
@user_passes_test(admin_only)
def user_management(request):
    users = User.objects.all().order_by('-date_joined')
    context = {
        'users': users,
    }
    return render(request, 'user_management.html', context)


@user_passes_test(admin_only)
def edit_user(request, user_id):
    user = User.objects.get(id=user_id)
    if request.method == 'POST':
        user.username = request.POST.get('username')
        user.email = request.POST.get('email')
        user.first_name = request.POST.get('first_name')
        user.role = request.POST.get('role')
        user.save()
        return redirect('user_management')
    context = {
        'user': user,
    }
    return render(request, 'edit_user.html', context)


@user_passes_test(admin_only)
def delete_user(request, user_id):
    user = User.objects.get(id=user_id)
    user.delete()
    return redirect('user_management')


# =========================
# ANALYTICS
# =========================
@user_passes_test(admin_only)
def analytics(request):
    # Simple analytics: chat logs over time, etc.
    chat_logs = ChatLog.objects.all().order_by('-timestamp')[:50]  # Recent 50
    context = {
        'chat_logs': chat_logs,
    }
    return render(request, 'analytics.html', context)


# =========================
# CHATBOT PAGE
# =========================
@login_required
def chatbot(request):
    return render(request, 'chatbot.html')


@login_required
def chatbot_response(request):
    # log and return a JSON response no matter what; catch unexpected errors
    if request.method == "POST":
        message = request.POST.get('message', '').strip()
        print(f"[chatbot_response] received message: '{message}'")

        if not message:
            print("[chatbot_response] empty message")
            return JsonResponse({'reply': "Please type a question."})

        try:
            # generate reply using the service layer; pass user id for context
            reply = get_bot_response(message, request.user.id if request.user.is_authenticated else None)
        except Exception as e:
            # fallback in case generation fails
            print(f"[chatbot_response] error generating reply: {e}")
            reply = "⚠️ Sorry, I'm having trouble right now. Please try again."  

        print(f"[chatbot_response] returning reply: '{reply[:100]}'")

        # log conversation separately; do not allow failures here to break response
        try:
            ChatLog.objects.create(
                user=request.user,
                message=message,
                response=reply
            )
        except Exception as e:
            print(f"[chatbot_response] chatlog save failed: {e}")

        return JsonResponse({'reply': reply})

    return JsonResponse({'reply': 'Invalid request'})


@login_required
def submit_feedback(request):
    if request.method == "POST":
        message = request.POST.get('message')
        response = request.POST.get('response')
        rating = request.POST.get('rating')
        comments = request.POST.get('comments', '')

        Feedback.objects.create(
            user=request.user,
            message=message,
            response=response,
            rating=rating,
            comments=comments
        )

        return JsonResponse({'status': 'success'})

    return JsonResponse({'status': 'error'})

# =========================
# LOGOUT
# =========================
def user_logout(request):
    logout(request)
    return redirect('home')
    