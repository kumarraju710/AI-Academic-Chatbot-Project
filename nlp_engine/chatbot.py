"""
DEPRECATED MODULE
=================
This file used to contain the main chatbot implementation with a
mixture of ML and rule‑based code.  The project has since been rewritten
from the ground up using `chatbot_complete.py`, which is purely
deterministic and driven by JSON data.  

Do **not** import from this module in new code; instead use
`from nlp_engine.chatbot_complete import get_bot_response` or the
service wrapper in `nlp_engine/services_new.py`.

The ML model loading logic has been disabled to prevent warnings.

Deterministic Chatbot Entry Point
Imports unified logic from chatbot_v2.py
"""

import google.generativeai as genai
import os

# Load Gemini API key from Django settings or environment variable
GENAI_API_KEY = os.environ.get('GENAI_API_KEY', None)
if GENAI_API_KEY:
    genai.configure(api_key=GENAI_API_KEY)

def get_gemini_response(user_message):
    if not GENAI_API_KEY:
        return "Gemini API key not set. Please configure your API key (set GENAI_API_KEY environment variable)."

    # Allow configurable model name via environment variable `GENAI_MODEL`.
    env_model = os.environ.get('GENAI_MODEL')
    # Try order: env_model (if set) then recommended fallbacks
    fallbacks = [m for m in ([env_model] if env_model else []) + ['gemini-1.5-flash', 'gemini-pro', 'chat-bison@001'] if m]

    last_exc = None
    for model_name in fallbacks:
        try:
            model = genai.GenerativeModel(model_name)
            # The SDK may accept a simple string input or a dict depending on version
            try:
                response = model.generate_content(user_message)
            except TypeError:
                # older/newer SDKs might use generate or generate_text
                response = model.generate(user_message)

            # response may be an object with text attribute or a plain string
            if hasattr(response, 'text'):
                return response.text
            if isinstance(response, dict) and 'content' in response:
                return response['content']
            return str(response)
        except Exception as e:
            last_exc = e
            # Common failure modes: permission/billing/quota errors — detect keywords
            msg = str(e).lower()
            if 'billing' in msg or 'quota' in msg or 'permission' in msg or 'not authorized' in msg:
                return ("GenAI error: your Google Cloud project may not have billing enabled or the API access is not authorized for the requested model. "
                        "Enable billing and ensure the API key/service account has access to the model (or choose a smaller model like 'gemini-pro').")
            # otherwise try next fallback
            continue

    # If all attempts failed, return a helpful error including the last exception message
    return f"Gemini request failed for all models. Last error: {last_exc}"
import os
import json
import random
import re
from difflib import SequenceMatcher
from users.models import FAQ

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FAQ_PATH = os.path.join(BASE_DIR, 'knowledge_base', 'faq.json')
COLLEGE_DATA_PATH = os.path.join(BASE_DIR, 'knowledge_base', 'colleges_data.json')

with open(FAQ_PATH, 'r') as f:
    faq_data = json.load(f)
with open(COLLEGE_DATA_PATH, 'r') as f:
    colleges_data = json.load(f)

# model.pkl and sklearn-based inference are relics from the old
# machine‑learning implementation.  The project now uses a fully
# deterministic rule‑based engine (`chatbot_complete.py`) driven by
# JSON data, so nothing in this module should be used anymore.
#
# We keep the file around for backward compatibility, but disable any
# ML loading to avoid unnecessary warnings or security issues.
MODEL_PATH = os.path.join(BASE_DIR, 'nlp_engine', 'model.pkl')
ml_available = False  # intentionally ignore any existing model


def find_best_faq(user_message):
    faqs = FAQ.objects.all()
    best_match = None
    best_score = 0
    for faq in faqs:
        score = SequenceMatcher(None, user_message.lower(), faq.question.lower()).ratio()
        if score > best_score:
            best_score = score
            best_match = faq
    if best_score > 0.5:  # Threshold for match
        # Always return the first answer for consistency
        if isinstance(faq.answer, list):
            return faq.answer[0]
        elif isinstance(faq.answer, str):
            try:
                ans_list = json.loads(faq.answer)
                if isinstance(ans_list, list) and ans_list:
                    return ans_list[0]
                else:
                    return faq.answer
            except Exception:
                return faq.answer
        else:
            return str(faq.answer)
    return None


def respond_payment_methods():
    return "Fees can be paid online via the university portal using UPI, net banking, or credit/debit card, or offline via bank challan."


def respond_fee_deadlines():
    return "Semester fee payment is due by April 5. Late payments incur penalties."


def respond_late_fees():
    return "Late fee penalty is $50 per week after the deadline, with possible enrollment suspension."


def respond_refunds():
    return "Fee refunds are processed within the first two weeks of the semester, minus a $50 processing fee."


def respond_enrollment_status():
    return "Enrollment is confirmed after fee payment and document verification. Check status on the student portal."


def respond_course_registration():
    return "Course registration requires confirmed enrollment and full fee payment. Registration opens April 10."


def respond_admission_confirmation():
    return "Admission confirmation requires fee payment and document submission. Process takes 3-5 days."


def respond_installments_scholarships():
    return "Installment plans and scholarships are available for eligible students. Apply through the financial aid office."


def respond_ambiguous():
    return "Please specify if your query relates to admissions, enrollment, course registration, or fees."


def respond_general():
    return "This service handles admissions, enrollment, course registration, and fee-related queries."


def respond_out_of_scope():
    return "This service handles only admissions, enrollment, course registration, and fee-related queries."


def detect_intent(user_message):
    msg = user_message.lower()
    best_intent = None
    best_score = 0
    for intent, data in faq_data.items():
        keywords = data.get("keywords", [])
        matching_keywords = [keyword for keyword in keywords if keyword.lower() in msg]
        if matching_keywords:
            score = max(len(keyword) for keyword in matching_keywords)
            if score > best_score:
                best_score = score
                best_intent = intent
    
    if best_intent:
        return best_intent
    
    # Fallback to ML if available
    if ml_available:
        X = vectorizer.transform([user_message])
        predicted = model.predict(X)[0]
        return predicted
    
    # Fallback to rule-based
    if re.search(r'\b(fee|fees|cost|amount|structure|breakdown|total)\b', msg) and not re.search(r'\b(pay|payment|deadline|late|refund|installment|scholarship)\b', msg):
        return 'tuition_fees'
    # Add more rules if needed
    return 'general'


# --- helper utilities for college/intents processing ---

def format_college_list(colleges):
    """Return a numbered list of colleges with their locations."""
    lines = [f"These are the list of colleges which I give the information:"]
    for idx, col in enumerate(colleges, start=1):
        lines.append(f"{idx}. {col['name']} – {col['location']}")
    lines.append("----")
    return "\n".join(lines)


def format_college_details(college):
    """Return full details for a single college."""
    lines = []
    lines.append(f"College: {college['name']}")
    lines.append(f"Location: {college['location']}")
    lines.append(f"Courses & Fees:")
    for idx, c in enumerate(college['courses'], start=1):
        lines.append(f"{idx}. {c['name']} – ₹{c['fee']:,}")
    lines.append(f"Deadline: {college['deadline']}")
    lines.append(f"Late Fee: ₹{college['late_fee']} per week")
    return "\n".join(lines)


def format_fee_structure(college):
    """Return just the branch-wise fee structure of a college."""
    lines = [f"Fee structure for {college['name']}:"]
    for idx, c in enumerate(college['courses'], start=1):
        lines.append(f"{idx}. {c['name']} – ₹{c['fee']:,} per year")
    lines.append(f"Deadline: {college['deadline']}")
    lines.append(f"Late Fee: ₹{college['late_fee']} per week")
    return "\n".join(lines)


def calculate_semester_fee(amount):
    try:
        sem = amount / 2
        return int(sem)
    except Exception:
        return None


def find_college(msg, colleges):
    """Return a college object if its name (or a distinctive part of it) appears in the message.

    We first check for the full name as a substring. If that fails we look for
    non-generic tokens (like 'Aditya', 'Pragati', 'GMR', etc.) within the message.
    A loose fuzzy match is the last resort.
    """
    msg_lower = msg.lower()
    # direct substring match
    for col in colleges:
        if col['name'].lower() in msg_lower:
            return col
    # match on significant tokens (skip generic words)
    skip_tokens = {'college', 'engineering', 'institute', 'technology', 'of', '&', 'and'}
    for col in colleges:
        tokens = re.findall(r"\b[a-zA-Z0-9&]+\b", col['name'].lower())
        for tok in tokens:
            if tok in skip_tokens:
                continue
            if tok and tok in msg_lower:
                return col
    # try loose matching by overall string similarity
    best = None
    best_score = 0.0
    for col in colleges:
        score = SequenceMatcher(None, msg_lower, col['name'].lower()).ratio()
        if score > best_score:
            best_score = score
            best = col
    if best_score > 0.6:
        return best
    return None


def detect_intent_custom(user_message, intents):
    """Simple keyword-based intent detection using provided intent_data."""
    msg = user_message.lower()
    best_intent = None
    best_score = 0
    for intent, data in intents.items():
        for keyword in data.get('keywords', []):
            if keyword.lower() in msg:
                score = len(keyword)
                if score > best_score:
                    best_score = score
                    best_intent = intent
    if best_intent:
        return best_intent
    # fallback the original detect_intent rules if needed (using global faq_data)
    return detect_intent(user_message)


# The legacy implementation has been superseded by the deterministic
# engine in ``chatbot_complete``.  Rather than duplicate all of the logic
# here, we simply delegate so that fixes (like better keyword handling) are
# automatically available to any code still importing from this deprecated
# module.

from .chatbot_complete import get_chatbot_response as _complete_get_chatbot_response


def get_chatbot_response(user_message, colleges_data, intent_data):
    """Wrapper for the modern response generator.

    The parameters are kept for backwards compatibility even though the
    underlying implementation ignores them (it reads its own JSON files).
    """
    return _complete_get_chatbot_response(user_message, colleges_data, intent_data)


# delegate entirely to the newer, improved version
from .chatbot_complete import get_bot_response as _complete_get_bot_response

def get_bot_response(user_message):
    return _complete_get_bot_response(user_message)

