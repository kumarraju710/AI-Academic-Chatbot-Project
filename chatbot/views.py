from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

from nlp_engine.services import generate_response


@login_required(login_url='/users/login/')
def chatbot_ui(request):
    """
    Render the chatbot UI page
    """
    return render(request, "chatbot.html")


@login_required(login_url='/users/login/')
def ask_question(request):
    """
    Handle chatbot questions (GET or POST) and return enhanced contextual reply.

    Supports two request formats for backward compatibility:
      * GET  /chatbot/ask/?q=...        (legacy)
      * POST /chatbot-response/ with field `message` (current frontend)
    """
    # prefer POST message parameter, fall back to GET q
    if request.method == 'POST':
        question = request.POST.get('message', '').strip()
    else:
        question = request.GET.get('q', '').strip()

    if not question:
        return JsonResponse({"reply": "Please ask a question."})

    # Get user ID for context tracking
    user_id = request.user.id if request.user.is_authenticated else None
    
    # Generate response with context awareness
    reply = generate_response(question, user_id)

    return JsonResponse({"reply": reply})
